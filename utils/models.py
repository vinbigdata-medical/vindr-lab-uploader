import time
from datetime import date
from uuid import uuid4

import httpx
from dynaconf import settings
from loguru import logger

from connection import es
from dbal import es_store
from utils import common, consts

http = httpx.AsyncClient()


async def process_data(index_data, exist_study=None):
    try:
        tags = index_data["dicom_tags"]
        # logging.info(tags)

        creator_id = index_data["creator_id"]
        project_id = index_data["project_id"]

        exist_project = await es_store.get_exist_project(project_id)
        study_key = "STDY"

        if exist_project is not None:
            if ("key" in exist_project) and (exist_project["key"] != ""):
                study_key = exist_project["key"]
        else:
            raise consts.InstanceExistedException("Project does not exist")

        body = {"status": "UNASSIGNED", "project_id": project_id, "creator_id": creator_id}
        if exist_study:
            body["dicom_tags"] = common.normalize_tags(exist_study, tags)
            body["id"] = exist_study["_id"]
            await es.update(
                index=exist_study["_index"],
                id=exist_study["_id"],
                body={"doc": body},
                refresh=True,
            )

            compact_body = body.copy()
            compact_body["dicom_tags"] = common.compact_tags(exist_study, tags)
            # logger.info(compact_body)

            # await pass_dicom_object(compact_body, jwt_token)
            return compact_body
        else:
            counter_key = "study_" + project_id
            url = f"{settings.ID_GENERATOR_URI}/id_generator/{counter_key}/tap"

            res = await http.put(url=url)
            res.raise_for_status()
            seed = res.json().get("last_insert_id")
            today = date.today().strftime("%Y%m")
            index = f"{settings.ES_STUDIES_INDEX_PREFIX}_{today}"

            body["id"] = str(uuid4())
            body["time_inserted"] = int(time.time() * 1000)
            body["dicom_tags"] = tags
            body["code"] = study_key + "-" + str(seed)

            await es.index(index=index, id=body["id"], body=body, refresh=True)
            # await pass_dicom_object(body, jwt_token)

            return body
    except Exception as ex:
        logger.exception(ex)
        raise ex


async def pass_dicom_object(index_data, jwt_token):
    tags = index_data["dicom_tags"]
    dicom_object = {
        "project_id": index_data["project_id"],
        "study_id": index_data["id"],
        "list_study_instance_uid": tags["StudyInstanceUID"],
        "list_series_instance_uid": tags["SeriesInstanceUID"],
        "list_sop_instance_uid": tags["SOPInstanceUID"],
    }

    res = httpx.post(
        f"{settings.VINDR_LAB_URI}/objects",
        json=dicom_object,
        headers={
            "x-api-key": f"{settings.VINDR_LAB_API_KEY}",
            "Authorization": jwt_token,
        },
    )

    res.raise_for_status()
    return res.json()

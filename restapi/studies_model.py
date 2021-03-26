from fastapi.responses import JSONResponse
from connection import oc, oc2, redis
from utils import dcom_utils, models, common, consts
from pydicom import tag, dataset, valuerep
from loguru import logger
from dbal import es_store
import requests


async def process(origin_bytes, project_id, creator_id, jwt_token) -> Exception:
    def prefix(_value):
        return f"{project_id}.{_value}"

    try:
        original_dataset = dcom_utils.read_dicom(origin_bytes)

        data = dcom_utils.parse_dicom(original_dataset)

        sop_instance_uid = data.get("SOPInstanceUID")[0]
        study_instance_uid = data.get("StudyInstanceUID")[0]

        original_study_instance_uid = str(original_dataset["StudyInstanceUID"].value)
        original_series_instance_uid = str(original_dataset["SeriesInstanceUID"].value)
        original_sop_instance_uid = str(original_dataset["SOPInstanceUID"].value)

        lock_key = f"lock_{project_id}_{study_instance_uid}"
        async with await redis.lock(lock_key):
            existed_study = await es_store.get_study(study_instance_uid, project_id)

            if existed_study is not None:
                if (
                        sop_instance_uid
                        in existed_study["_source"]["dicom_tags"]["SOPInstanceUID"]
                ):
                    logger.info("{0} is already existed.", original_sop_instance_uid)
                    # return consts.InstanceExistedException("This instance is already existed.")
                    return None

            masked_dataset = dcom_utils.read_dicom(origin_bytes)
            logger.info("instance: {0}", original_sop_instance_uid)

            masked_dataset[0x0020, 0x000D].value = prefix(original_study_instance_uid)
            masked_dataset[0x0020, 0x000E].value = prefix(original_series_instance_uid)
            masked_dataset[0x0008, 0x0018].value = prefix(original_sop_instance_uid)

            # Mask referenced instance in a series
            if tag.Tag(0x0008, 0x1140) in masked_dataset:
                ref_image_sequence = masked_dataset[0x0008, 0x1140].value
                for ref_image in ref_image_sequence:
                    origin = str(ref_image[0x0008, 0x1155].value)
                    ref_image[0x0008, 0x1155].value = prefix(origin)

            # Mask referenced series in a study
            if tag.Tag(0x0008, 0x1115) in masked_dataset:
                ref_series_sequence = masked_dataset[0x0008, 0x1115].value
                for ref_series in ref_series_sequence:
                    origin = str(ref_series[0x0020, 0x000E].value)
                    ref_series[0x0020, 0x000E].value = prefix(origin)

            normalized_bytes = common.convert_dataset_to_bytes(masked_dataset)

            s = requests.sessions.Session()
            s.verify = False
            oc2.add_instance(normalized_bytes, session=s)

            dicom_tags = {}

            for tag_name, tag_hex in consts.merge_tags.items():
                if tag.Tag(tag_hex) in masked_dataset:
                    value = masked_dataset[tag_hex].value
                    dicom_tags[tag_name] = [str(value)]

            dicom_tags["StudyInstanceUID"] = [original_study_instance_uid]
            dicom_tags["SeriesInstanceUID"] = [original_series_instance_uid]
            dicom_tags["SOPInstanceUID"] = [original_sop_instance_uid]

            index_data = {
                "project_id": project_id,
                "dicom_tags": dicom_tags,
                "creator_id": creator_id,
            }

            create_object_body = await models.process_data(index_data, existed_study)
            # logger.info(create_object_body)

            await models.pass_dicom_object(create_object_body, jwt_token)

        return None
    except Exception as ex:
        logger.exception(ex)
        return ex


def dicom_dataset_to_dict(dicom_header):
    dicom_dict = {}
    repr(dicom_header)
    for dicom_value in dicom_header.values():
        if dicom_value.tag == (0x7fe0, 0x0010):
            # discard pixel data
            continue
        if type(dicom_value.value) == dataset.Dataset:
            dicom_dict[dicom_value.name] = dicom_dataset_to_dict(dicom_value.value)
        else:
            v = _convert_value(dicom_value.value)
            dicom_dict[dicom_value.name] = v

    return dicom_dict


def _sanitise_unicode(s):
    return s.replace(u"\u0000", "").strip()


def _convert_value(v):
    t = type(v)
    if t in (list, int, float):
        cv = v
    elif t == str:
        cv = _sanitise_unicode(v)
    elif t == bytes:
        s = v.decode('ascii', 'replace')
        cv = _sanitise_unicode(s)
    elif t == valuerep.DSfloat:
        cv = float(v)
    elif t == valuerep.PersonName:
        cv = str(v)
    elif t == valuerep.IS:
        cv = int(v)
    elif t == valuerep.UID:
        cv = v
    else:
        cv = repr(v)
    return cv

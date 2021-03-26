import time

from dynaconf import settings

from connection import es


async def check_exist_index(index):
    if await es.indices.exists(index=index):
        return True
    else:
        await es.indices.create(index=index)


async def get_study(study_instance_uid, project_id):
    """
    Check exist study or instance
    """
    query_string = (
        f"dicom_tags.StudyInstanceUID:{study_instance_uid} AND project_id: {project_id}"
    )

    body = {
        "size": 1,
        "query": {"query_string": {"query": query_string}},
    }

    index = f"{settings.ES_STUDIES_INDEX_PREFIX}_*"
    study = await es.search(index=index, body=body)
    if study["hits"]["total"]["value"] > 0:
        return study["hits"]["hits"][0]
    return None


async def get_exist_project(project_id):
    """
    Check exist ret or instance
    """
    query_string = f"id: {project_id}"

    body = {
        "size": 1,
        "query": {"query_string": {"query": query_string}},
    }

    index = f"{settings.ES_PROJECTS_INDEX_PREFIX}_*"
    ret = await es.search(index=index, body=body)
    if ret["hits"]["total"]["value"] > 0:
        return ret["hits"]["hits"][0]["_source"]
    return None


async def check_exist_counter(key):
    query_string = f"key.keyword:{key}"

    body = {
        "size": 1,
        "query": {"query_string": {"query": query_string}},
    }
    index = settings.ES_COUNTER_INDEX
    await check_exist_index(index)
    counter = await es.search(index=index, body=body)
    if counter["hits"]["total"]["value"] > 0:
        return counter["hits"]["hits"][0]
    return None


async def create_counter(counter_key):
    body = {"key": counter_key, "modified": str(int(time.time() * 1000)), "seed": 1}

    index = settings.ES_COUNTER_INDEX
    await check_exist_index(index)
    await es.index(index=index, body=body, refresh=True)
    return body["seed"]


async def increase_counter(counter_exist):
    exist_seed = counter_exist["_source"]["seed"]
    exist_key = counter_exist["_source"]["key"]
    new_seed = exist_seed + 1

    body = {
        "key": exist_key,
        "modified": str(int(time.time() * 1000)),
        "seed": new_seed,
    }
    # await check_exist_index(counter_exist["_index"])

    await es.update(
        index=counter_exist["_index"],
        id=counter_exist["_id"],
        body={"doc": body},
        refresh=True,
    )
    return new_seed

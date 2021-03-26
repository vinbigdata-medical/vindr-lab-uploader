from io import BytesIO

from loguru import logger

from utils import consts


def convert_dataset_to_bytes(dataset):
    try:
        buffer = BytesIO()
        dataset.save_as(buffer, write_like_original=True)
        buffer.seek(0)
        return buffer.read()
    except Exception as ex:
        logger.exception(ex)
        return ex


def get_update_type(field):
    if field in consts.merge_tags:
        return "MERGE"
    return "REPLACE"


def normalize_tags(exist_study, tags):
    old_tags = exist_study["_source"]["dicom_tags"]
    update_params = old_tags.copy()
    for field in tags:
        _type = get_update_type(field)
        if _type == "MERGE":
            if field in old_tags:
                update_params[field] = list(set(old_tags[field] + tags[field]))
            else:
                update_params[field] = tags[field]
        elif _type == "REPLACE":
            update_params[field] = tags[field]
    return update_params


def compact_tags(exist_study, tags):
    old_tags = exist_study["_source"]["dicom_tags"]
    update_params = old_tags.copy()

    for field in tags:
        update_params[field] = tags[field]
    return update_params

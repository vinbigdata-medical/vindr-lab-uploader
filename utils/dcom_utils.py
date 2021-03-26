from io import BytesIO

from loguru import logger
from pydicom import dcmread


def read_dicom(dicom_bytes):
    try:
        dicom_file = BytesIO(dicom_bytes)
        dataset = dcmread(dicom_file)
        return dataset
    except Exception as ex:
        logger.exception(ex)
        return ex


def parse_dicom(dataset):
    attributes = [
        "StudyInstanceUID",
        "SeriesInstanceUID",
        "SOPInstanceUID",
    ]
    body_params = {}

    for name in attributes:
        raw_value = dataset.get(name, None)
        if raw_value:
            body_params[name] = [str(raw_value)]
        else:
            body_params[name] = []

    return body_params

import pytest

from utils import common, dcom_utils


@pytest.mark.parametrize(
    "dataset, expected",
    [
        (
                {
                    "StudyInstanceUID": "study_test",
                    "Name": "name",
                    "SOPInstanceUID": "sop_test",
                    "SeriesInstanceUID": "series_test",
                },
                {"StudyInstanceUID": ["study_test"], "SeriesInstanceUID": ["series_test"],
                 "SOPInstanceUID": ["sop_test"]},
        ),
        (
                {"StudyInstanceUID": "", "SeriesInstanceUID": "", "SOPInstanceUID": ""},
                {"StudyInstanceUID": [], "SeriesInstanceUID": [], "SOPInstanceUID": []},
        ),
    ],
)
def test_parse_dicom(dataset, expected):
    assert dcom_utils.parse_dicom(dataset) == expected


@pytest.mark.parametrize(
    "exist_study, tags, expected",
    [
        (
                {
                    "_source": {
                        "dicom_tags": {
                            "StudyInstanceUID": [
                                "test"
                            ],
                            "StudyDate": [1, 2],
                        }
                    }
                },
                {
                    "StudyInstanceUID": [
                        "test"
                    ],
                    "StudyDate": [1],
                    "NewField": "abc",
                },
                {
                    "StudyInstanceUID": [
                        "test"
                    ],
                    "StudyDate": [1, 2],
                    "NewField": "abc",
                },
        )
    ],
)
def test_normalize_tags(exist_study, tags, expected):
    assert common.normalize_tags(exist_study, tags) == expected

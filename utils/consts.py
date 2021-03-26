merge_tags = {
    "StudyDate": 0x00080020,
    "StudyTime": 0x00080030,
    "AccessionNumber": 0x00080050,
    "ReferringPhysicianName": 0x00080090,
    "StudyInstanceUID": 0x0020000D,
    "StudyID": 0x00200010,
    "Modality": 0x00080060,
    # "ModalitiesInStudy": ,
    "SeriesInstanceUID": 0x0020000E,
    "SeriesNumber": 0x00200011,
    "SOPClassUID": 0x00080016,
    "SOPInstanceUID": 0x00080018,
    # "InstanceNumber": ,
    "PatientAge": 0x00101010,
    "PatientName": 0x00100010,
    "PatientID": 0x00100020,
    "PatientSex": 0x00100040,
    "StudyDate": 0x00080020,
    "NumberOfStudyRelatedSeries": 0x00201206,
    "NumberOfStudyRelatedInstances": 0x00201208,
    "BodyPartExamined": 0x00180015,
}


class InstanceExistedException(Exception):
    pass

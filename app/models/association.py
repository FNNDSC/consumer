from pydantic import BaseModel, Field, validator
from typing import List

class PACSqueryCore(BaseModel):
    """The PACS Query model"""
    StudyDescription: str = ""
    Modality: str = ""
    ModalitiesInStudy: str = ""
    PerformedStationAETitle: str = ""
    SeriesDescription: str = ""
    ProtocolName: str = ""
    AcquisitionProtocolDescription: str = ""
    AcquisitionProtocolName: str = ""

class Association(BaseModel):
    analysis_name: str = Field(...)
    tags: PACSqueryCore

class AssociationList(BaseModel):
    rules: List[Association] = []

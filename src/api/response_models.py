from pydantic import BaseModel
from src.models import ExtractorResult
from enum import Enum


class ErrorCode(Enum):
    MODEL_NOT_FOUND = 404


class ExtractorResponse(BaseModel):
    status: str
    msg: str
    result: list[ExtractorResult]


class ModelReloadResponse(BaseModel):
    status: str
    msg: str

from pydantic import BaseModel
from src.models import ExtractorResult
from enum import Enum


class ErrorCode(Enum):
    MODEL_NOT_FOUND = 404


class BaseResponse(BaseModel):
    status: str
    msg: str


class ExtractorResponse(BaseResponse):
    result: list[dict]

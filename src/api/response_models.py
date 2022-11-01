from pydantic import BaseModel
from enum import Enum


class ErrorCode(Enum):
    MODEL_NOT_FOUND = 404


class BaseResponse(BaseModel):
    status: str
    msg: str


class RecognitionResponse(BaseResponse):
    result: list[dict]

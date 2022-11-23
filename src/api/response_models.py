from pydantic import BaseModel
from enum import Enum


class ErrorCode(Enum):
    NOT_FOUND = 404
    UNPROCESSABLE_ENTITY = 422


class BaseResponse(BaseModel):
    status: str
    msg: str


class RecognitionResponse(BaseResponse):
    result: list[dict]


class LatestMentionsResponse(BaseResponse):
    result: list[dict]

from pydantic import BaseModel
from src.models import ExtractorResult


class ExtractorResponse(BaseModel):
    status: str
    msg: str
    result: list[ExtractorResult]

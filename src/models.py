from pydantic import BaseModel


class ExtractorResult(BaseModel):
    text: str
    start: int
    offset: int
    label: str

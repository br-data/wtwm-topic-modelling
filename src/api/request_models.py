from pydantic import BaseModel


class ExtractorRequestBody(BaseModel):
    text: str

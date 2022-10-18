from typing import Any, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

from fastapi import Query


class ExtractorRequestBody(BaseModel):
    text: str


class MDRUpdateRequest(BaseModel):
    from_: datetime
    to: datetime

    @staticmethod
    def query_template(
        from_: Optional[str] = Query(
            (datetime.now() - timedelta(days=30)).isoformat(),  # example value
            title="From",
            description="'From' timestamp for timerange (iso 8601)",
        ),
        to: Optional[str] = Query(
            datetime.now().isoformat(),  # example value
            title="To",
            description="'To' timestamp for timerange (iso 8601)",
        ),
    ) -> dict[str, str]:
        """Define api query parameters.

        :param : api query arguments

        Note: This query definition is used for swagger documentation.
        """
        return {"from": from_, "to": to}

    @classmethod
    def from_query(cls, query: dict[str, Any]) -> "MDRUpdateRequest":
        """Init from api arguments.

        :param query: api path query as dict
        """
        from_ = datetime.fromisoformat(query["from"])
        to = datetime.fromisoformat(query["to"])
        if to <= from_:
            raise ValueError(f"'to' value lays before 'from' value: {to} <= {from_}")

        return cls(from_=from_, to=to)

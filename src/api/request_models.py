from typing import Any, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

from fastapi import Query

DEFAULT_LOOKBACK = 12


class ExtractorRequestBody(BaseModel):
    text: str


class MDRUpdateRequest(BaseModel):
    from_: datetime
    to: datetime

    @staticmethod
    def query_template(
        from_: Optional[str] = Query(
            (
                datetime.now() - timedelta(hours=DEFAULT_LOOKBACK)
            ).isoformat(),  # example value
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
        try:
            to = datetime.fromisoformat(query["to"])
        except (KeyError, TypeError):
            to = datetime.now()

        try:
            from_ = datetime.fromisoformat(query["from"])
        except (KeyError, TypeError):
            from_ = to - timedelta(hours=DEFAULT_LOOKBACK)

        if to <= from_:
            raise ValueError(f"'to' value lays before 'from' value: {to} <= {from_}")

        return cls(from_=from_, to=to)


class BRUpdateRequest(BaseModel):
    lookback: int

    @staticmethod
    def query_template(
        lookback: Optional[str] = Query(
            DEFAULT_LOOKBACK,
            title="lookback",
            description="Lookback in hours for comments",
        )
    ) -> dict[str, str]:
        """Define api query parameters.

        :param : api query arguments

        Note: This query definition is used for swagger documentation.
        """
        return {"lookback": lookback}

    @classmethod
    def from_query(cls, query: dict[str, Any]) -> "MDRUpdateRequest":
        """Init from api arguments.

        :param query: api path query as dict
        """
        lookback = query.get("lookback", DEFAULT_LOOKBACK)
        return cls(lookback=lookback)

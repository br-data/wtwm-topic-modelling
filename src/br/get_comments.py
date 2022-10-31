from settings import BR_COMMENT_ENDPOINT, BR_COMMENT_ENDPOINT_TOKEN
from typing import Optional
from pydantic import BaseModel

from src.tools import request


class BRCommentGetter(BaseModel):
    """Get comment from br comment endpoint."""

    url: str = BR_COMMENT_ENDPOINT
    token: str = BR_COMMENT_ENDPOINT_TOKEN

    def get_comments(
        self,
        lookback: int
    ) -> list[Optional[dict]]:
        """Get commens for a specified timeframe.

        :param lookback: lookback from now in hours
        """
        query = {"lookback": lookback}
        headers = {"Authorization": f"Basic {self.token}"}
        response = request(self.url, method="Get", body=query, headers=headers)
        return response["result"]

    __call__ = get_comments

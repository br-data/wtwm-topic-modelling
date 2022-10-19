from settings import MDR_COMMENT_ENDPOINT, MDR_COMMENT_ENDPOINT_TOKEN
from datetime import datetime
from typing import Union
from pydantic import BaseModel

from src.tools import request


class MDRCommentGetter(BaseModel):
    """Get comment from mdr comment endpoint."""

    url: str = MDR_COMMENT_ENDPOINT
    token: str = MDR_COMMENT_ENDPOINT_TOKEN

    def get_comments(
        self,
        from_: datetime,
        to: datetime,
        size: int = 20,
        start_page: int = 1,
        max_pages: int = 2,
        verbose: bool = True
    ) -> list[dict[str, Union[int, list[dict[str, Union[str, int]]]]]]:
        """Get commens for a specified timeframe.

        :param from_: begin of timeframe
        :param to: end of timeframe
        :param size: max number of return comments
        :param start_page: start page for result iteration
        :param max_pages: max number of pages to iterate through
        """
        items = []
        query = self._get_filter(from_, to, size, start_page)
        headers = {"Authorization": f"Bearer {MDR_COMMENT_ENDPOINT_TOKEN}"}
        response = request(self.url, body=query, headers=headers)
        response_items = response["items"]
        while response_items and query["page"] < max_pages:
            if verbose:
                print(f"Got {len(response_items)} from page {query['page']}")

            items.extend(response["items"])
            query["page"] += 1
            response = request(self.url, body=query, headers=headers)
            response_items = response["items"]

        return items

    def _get_filter(
        self, from_: datetime, to: datetime, size: int = 20, page: int = 1
    ) -> dict:
        """Assemble filter for call of comment api for a specific timeframe.

        :param from_: begin of timeframe
        :param to: end of timeframe
        :param size: max number of return comments
        :param page: page number
        """
        return {
            "filter": {
                "must": [
                    {
                        "date_range": {
                            "created_at": {
                                "from": from_.strftime("%Y-%m-%y %H:%M:%S"),
                                "to": to.strftime("%Y-%m-%y %H:%M:%S"),
                            }
                        }
                    }
                ]
            },
            "sort": "-created_at",
            "size": size,
            "page": page,
        }

    __call__ = get_comments

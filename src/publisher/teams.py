from typing import Any
from requests.exceptions import HTTPError

from src.tools import request

from src.models import MediaHouse, Comment, Status
from src.storage.postgres import TableWriter


class TeamsConnector:
    def __init__(self, media_house: MediaHouse):
        self.media_house = media_house

    def send(self, comments: list[Comment]) -> None:
        """Publish a list of comments to teams.

        :param comments: list of comments to publish
        """
        request_body = _get_request_body(comments)
        _ = request(self.media_house.get_target(), body=request_body)

    __call__ = send


def _get_request_body(comments: list[Comment]) -> dict[str, list[dict[str, Any]]]:
    """Assemble request body for publication.

    :param comments: list of comments to publish
    """
    return {
        "data": [
            {
                "id": comment.id,
                "comment": comment.body.replace('"', "'"),
                "username": comment.username.replace('"', "'"),
                "asset_url": comment.asset_url,
            }
            for comment in comments
        ]
    }


def send_comments(
    connector: TeamsConnector,
    comments: list[Comment],
    writer: TableWriter,
    max_number_to_publish: int,
) -> None:
    """Send comments to teams.

    :param connector: teams connection interface
    :param comments: comments to send
    :param writer: database interface
    :param max_number_to_publish: max number of comments to publish each session
    """
    for comment_entry in comments[: max_number_to_publish + 1]:
        # send one comment at once for now to ensure db update of status
        try:
            connector.send([comment_entry])
        except HTTPError as exc:
            print(f"Error while sending to {connector.media_house.value} at {exc}")
            print(f"Skipping comments")
        else:
            comment_entry.status = Status.WAIT_FOR_EVALUATION
            # update status everytime to prevent status update fail in case of crash
            # if necessary build pub/sub after prototype phase
            writer.update(comment_entry)

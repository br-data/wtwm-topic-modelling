from typing import Union
from src.tools import request

from src.models import MediaHouse, Comment, Status
from src.storage.big_query import BigQueryWriter


class TeamsConnector:
    def __init__(self, media_house: MediaHouse):
        self.media_house = media_house

    def _get_message_card(self, body: str) -> dict[str, Union[str, bool]]:
        """Prepare publication in message card format

        :param body: comment body to publish

        Note: In order to send actionable messages one must use the legacy message card. Here is the documentation:

        https://learn.microsoft.com/en-us/outlook/actionable-messages/message-card-reference
        """
        return {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "summary": "Feedback",
            "title": "New direct mention was detected:",
            "text": body,
            "potentialAction": [
                {
                    "@type": "ActionCard",
                    "name": "Feedback",
                    "inputs": [
                        {
                            "@type": "MultichoiceInput",
                            "id": "HumanLabel",
                            "title": "In order to improve the detection, please give us feedback about the detection:",
                            "isMultiSelect": "False",
                            "style": "expanded",
                            "choices": [
                                {
                                    "display": "There is a direct mention and the exact text is bolded.",
                                    "value": "correct",
                                },
                                {
                                    "display": "There is not direct mention at all.",
                                    "value": "incorrect",
                                },
                                {
                                    "display": "There is a direct mention but the exact text is not bolded.",
                                    "value": "incorrect_bold",
                                },
                            ],
                        },
                        {
                            "@type": "TextInput",
                            "id": "mentionText",
                            "isMultiline": True,
                            "title": "exact mention text",
                        },
                    ],
                    "actions": [
                        {
                            "@type": "HttpPOST",
                            "name": "Submit",
                            "isPrimary": True,
                            "target": self.media_house.get_feedback_target(),
                        }
                    ],
                }
            ],
        }

    def send(self, comment_body: str) -> None:
        """Publish a comment to a teams channel.

        :param comment_body: comment body to publish
        """
        request_body = self._get_message_card(comment_body)
        _ = request(self.media_house.get_target(), body=request_body)

    __call__ = send


def send_comments(
    connector: TeamsConnector, comments: list[Comment], writer: BigQueryWriter
) -> None:
    """Send comments to teams.

    :param connector: teams connection interfacel
    :param comments: comments to send
    :param writer: database interface
    """
    for comment_entry in comments:
        connector.send(comment_entry.body)
        comment_entry.status = Status.TO_BE_EVALUATED
        # update status everytime to prevent status update fail in case of chrash
        # if necessary build pub/sub after prototype phase
        writer.update_comment(comment_entry)

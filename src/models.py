from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Union

from enum import Enum
from settings import TEST_TARGET, TEST_FEEDBACK_TARGET


class Status(Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    TO_BE_PROCESSED = "UNPROCESSED"
    TO_BE_EVALUATED = "UNPROCESSED"


class MediaHouse(Enum):
    MDR = "mdr"
    BR = "br"
    TEST = "test"

    @classmethod
    def from_id(cls, id_: str) -> "MediaHouse":
        """Init class from media house id.

        :param id_: media house id
        """
        if id_ == MediaHouse.MDR.value:
            return MediaHouse.MDR
        elif id_ == MediaHouse.BR.value:
            return MediaHouse.BR
        elif id_ == MediaHouse.TEST.value:
            return MediaHouse.TEST
        else:
            raise ValueError(f"Unknown media house id: '{id_}'")

    def get_target(self) -> str:
        """Return the channel target.

        Note: The target points to channel webhook to distribute to. It serves as a address to publish to.
        """
        if self == MediaHouse.TEST:
            return TEST_TARGET
        else:
            raise NotImplementedError(f"Target for {self.value} is not available.")

    def get_feedback_target(self) -> str:
        """Return the target to the feedback channel.

        Note: The feedback target specifies the endpoint for the feedback to be send to.
        """
        if self == MediaHouse.TEST:
            return TEST_FEEDBACK_TARGET
        else:
            raise NotImplementedError(f"Target for {self.value} is not available.")


class ExtractionType(Enum):
    ANNOTATION = "annotation"
    # TODO
    SPACY_MODEL_A = "spacy_model_name"


class ReportTimestamp(BaseModel):
    receiver: str
    timestamp: datetime


class ExtractorResult(BaseModel):
    body: str
    start: int
    offset: int
    label: str
    extracted_from: ExtractionType

    def as_dict(self) -> dict[str, Union[int, str]]:
        return dict(
            body=self.body,
            start=self.start,
            offset=self.offset,
            label=self.label,
            extracted_from=self.extracted_from.value,
        )


class Comment(BaseModel):
    id: str
    status: Status
    body: str
    asset_id: str  # article id the comment belongs to
    asset_url: str  # article url the comment belongs to
    author_id: str  # comment author
    username: str  # technical name of the comment author
    created_at: datetime
    last_updated_at: datetime  # meant as database update of this comment
    mentions: list[Optional[ExtractorResult]]
    media_house: MediaHouse

    @classmethod
    def dummy(cls) -> "Comment":
        now = datetime.now()
        return cls(
            id="testid",
            status=Status.ACCEPTED,
            body="Hallo Redaktion. Das ist ein Test.",
            asset_id="1",
            asset_url="www.mdr.de",
            author_id="Jaime",
            username="Jaime Again",
            created_at=now,
            last_updated_at=now,
            mentions=[
                ExtractorResult(
                    body="Hallo Redaktion",
                    start=0,
                    offset=16,
                    label="mention",
                    extracted_from=ExtractionType.SPACY_MODEL_A,
                )
            ],
            media_house=MediaHouse.TEST,
        )

    def as_dict(self) -> dict[str, Union[str, dict[str, Union[str, int]]]]:
        if self.mentions is not None:
            mentions = [m.as_dict() for m in self.mentions]
        else:
            mentions = None

        return dict(
            id=self.id,
            status=self.status.value,
            body=self.body,
            asset_id=self.asset_id,
            asset_url=self.asset_url,
            author_id=self.author_id,
            username=self.username,
            created_at=self.created_at.isoformat(),
            last_updated_at=self.last_updated_at.isoformat(),
            mentions=mentions,
            media_house=self.media_house.value,
        )

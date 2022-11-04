from pydantic import BaseModel
from datetime import datetime
from typing import Union
from enum import Enum
import uuid

from sqlalchemy.ext.declarative import declarative_base  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy import Enum as SQLEnum

from settings import MDR_TARGET, TEST_TARGET, TEST_FEEDBACK_TARGET, MDR_FEEDBACK_TARGET


BASE = declarative_base()


class Status(Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    TO_BE_PROCESSED = "TO_BE_PROCESSED"
    TO_BE_PUBLISHED = "TO_BE_PUBLISHED"
    NO_MENTIONS = "NO_MENTIONS"
    WAIT_FOR_EVALUATION = "WAIT_FOR_EVALUATION"
    ERROR = "ERROR"

    @staticmethod
    def from_choice(choice: str) -> "Status":
        """Map the choice.

        :param choice: raw choice to be mapped
        """
        if choice == "0":
            return Status.REJECTED
        elif choice == "1":
            return Status.ACCEPTED
        else:
            raise ValueError(f"Unknown choice: {choice}")


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
        elif self == MediaHouse.MDR:
            return MDR_TARGET
        else:
            raise NotImplementedError(f"Target for {self.value} is not available.")

    def get_feedback_target(self) -> str:
        """Return the target to the feedback channel.

        Note: The feedback target specifies the endpoint for the feedback to be send to.
        """
        if self == MediaHouse.TEST:
            return TEST_FEEDBACK_TARGET
        elif self == MediaHouse.MDR:
            return MDR_FEEDBACK_TARGET
        else:
            raise NotImplementedError(f"Target for {self.value} is not available.")


class RecognitionType(Enum):
    ANNOTATION = "annotation"
    SPACY_MODEL_A = "bugg_model_v1"
    PATTERN_RECOGNISER_A = "pattern_recogniser_v1"


class RecognitionResult(BASE):
    __tablename__ = "mentions"
    id = Column(Text, primary_key=True)
    comment_id = Column(Text, ForeignKey("comments.id", ondelete="CASCADE"))
    body = Column(Text, unique=False)
    start = Column(Integer, unique=False)
    offset = Column(Integer, unique=False)
    label = Column(Text, unique=False)
    extracted_from = Column(Text, unique=False)
    comment = relationship(
        "Comment",
        back_populates="mentions",
        passive_deletes=True,  # if True entry is delete if parent is deleted
    )

    @classmethod
    def dummy(cls) -> "RecognitionResult":
        return cls(
            id=str(uuid.uuid4()),
            comment_id="test_id",
            body="Hallo Redaktion",
            start=0,
            offset=16,
            label="mention",
            extracted_from=RecognitionType.SPACY_MODEL_A.value,
        )

    def as_dict(self) -> dict[str, Union[int, str]]:
        return dict(
            id=self.id,
            comment_id=self.comment_id,
            body=self.body,
            start=self.start,
            offset=self.offset,
            label=self.label,
            extracted_from=self.extracted_from,
        )


class ReportTimestamp(BaseModel):
    receiver: str
    timestamp: datetime


class Comment(BASE):
    __tablename__ = "comments"
    id = Column(Text, primary_key=True)
    status = Column(SQLEnum(Status), unique=False)
    body = Column(Text, unique=False)
    asset_id = Column(Text, unique=False)  # article id the comment belongs to
    asset_url = Column(Text, unique=False)  # article url the comment belongs to
    author_id = Column(Text, unique=False)  # comment author
    username = Column(Text, unique=False)  # technical name of the comment author
    created_at = Column(DateTime, unique=False)
    note = Column(Text, unique=False)
    last_updated_at = Column(
        DateTime, unique=False
    )  # meant as database update of this comment
    media_house = Column(SQLEnum(MediaHouse), unique=False)
    mentions = relationship(
        "RecognitionResult",
        back_populates="comment",
        cascade="all, delete",  # if this is delete, child object is also deleted
    )

    @classmethod
    def dummy(cls) -> "Comment":
        now = datetime.now()
        return cls(
            id="testid",
            status=Status.TO_BE_PROCESSED,
            body="Liebe Redaktion. Das ist ein Test.",
            asset_id="1",
            asset_url="www.mdr.de",
            author_id="Jaime",
            username="Jaime Again",
            created_at=now,
            last_updated_at=now,
            mentions=[],  # add dummy of RecognitionResult if needed
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

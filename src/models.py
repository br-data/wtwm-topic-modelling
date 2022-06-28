"""This collection of models servers the purpose to normalize all input data
and is meant to grow dynamically during the project."""

from typing import Any
from enum import Enum


class SourceLabel(Enum):
    """Fix source labels"""
    BR = "br"
    MDR = "mdr"


class Comment:
    def __init__(self, text: str, article_id: str, embed: Any, source_label: SourceLabel) -> None:
        """Init method.

        :param text: comment message
        :param article_id: provided external article id
        :param embed: message embedding
        :param source_label: comment source specification
        """
        self._internal_id = generate_unique_id()
        self._text = text
        self._article_id = article_id
        self._embed = embed
        self._source_label = source_label

    @classmethod
    def from_api(cls, raw: Any) -> "Comment":
        """Normalize comments from api output to fit Comment class.

        :param raw: comment as provided by api
        """
        # TODO maybe like this
        # return cls(preprocess_from_api(raw))
        pass

    @classmethod
    def from_file(cls, raw: Any) -> "Comment":
        """Normalize comments from file to fit Comment class.

        :param raw: comment as provided by api
        """
        # TODO
        pass


class Article:
    # TODO
    pass


class Topic:
    # TODO
    pass


def generate_unique_id() -> Any:
    """Generate a unique object id."""
    # TODO
    pass

import json
from typing import Any, Dict, List, Union, NewType

from src.models import Comment

Config = NewType("Config", Dict[str, Union[str, int, float]])


def load_config(path: str) -> Config:
    """Load config from file.

    :param path: location of config file
    """
    return json.loads(path)


def load_comments(config: Config) -> List[Comment]:
    """Load comments from external source (e.g. API, local, bucket).

    :param config: specification of source credentials
    """
    # TODO could be like this
    # return [Comment.import_from_api_format(c) for c in from_api(config)]
    pass


def store_comments(config: Config, comments: List[Comment]) -> None:
    """Store comments (e.g. DB, local, bucket).

    :param config: specification of storage credentials
    :param comments: items to store
    """
    # TODO add when we decided about storage
    pass

from typing import Any, Optional
import jsonlines
import requests
from requests.exceptions import JSONDecodeError
from datetime import datetime, timedelta
import json
import re
from re import Pattern

from src.exceptions import PreprocessingError
from src.models import Comment


def normalize_query_pattern(query: str, comment_id: str) -> str:
    """Normalize query string (for the use with a trie).

    :param query: query string to normalize
    :param comment_id: id of the object the query belongs to
    """
    if query is None:
        raise PreprocessingError(f"Got no body for comment: {comment_id}")

    query = query.lower()
    # only_letters: Pattern = re.compile(r"([^A-Za-z-.])+")
    # query = re.sub(only_letters, query, " ")
    return query


def write_jsonlines_to_bucket(path: str, lines: list[dict]) -> None:
    """Write list of dictionaries to file.

    :param path: path to data folder
    :param lines: content to write to file
    """
    with jsonlines.open(path, "w") as handle:
        for line in lines:
            handle.write(line)


def read_jsonlines(path: str) -> list[dict]:
    """Read jsonlines from file.

    :param path: path to file
    """
    with jsonlines.open(path, "r") as handle:
        return [line for line in handle]


def request(
    url: str,
    params: Optional[dict[str, Any]] = None,
    body: Optional[dict[str, Any]] = None,
    method: str = "Post",
    headers: Optional[dict[str, str]] = None,
) -> dict:
    """Request a given url.

    :param url: url to post to
    :param params: query params
    :param body: request body
    :param method: request type
    :param headers: header object
    """
    headers = headers or {}
    headers.update({"content-type": "application/json"})
    response = requests.request(method, url, json=body, params=params, headers=headers)
    response.raise_for_status()
    try:
        return response.json()
    except JSONDecodeError:
        return {}


def check_expiration_time(
    comments: list[Comment], lookback_minutes: int
) -> list[Comment]:
    """Filter all comments older than a lookback time.

    :param comments: list of comments to filter
    :param lookback_minutes: number of minutes to look back in time from now

    Note: Filter criteria is the timestamp 'created_at' because 'last_updated_at' by hold alot of comments updated
          the same second.
    """
    filtered_ = []
    now = datetime.utcnow()
    not_older_than = now - timedelta(minutes=lookback_minutes)
    for comment in comments:
        if comment.created_at >= not_older_than:
            filtered_.append(comment)

    return filtered_

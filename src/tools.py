from typing import Any, Optional
import jsonlines
import requests


def write_jsonlines_to_bucket(path: str, lines: list[dict]) -> None:
    """Write list of dictionaries to file.

    :param path: path to data folder
    :param lines: content to write to file
    """
    with jsonlines.open(path, "w") as handle:
        for line in lines:
            handle.write(line)


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
    return response.json()

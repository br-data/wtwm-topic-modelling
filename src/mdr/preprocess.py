from typing import Any
from datetime import datetime
from dateutil.parser import parse

from src.models import MediaHouse, Status


def preprocess_mdr_comment(raw: dict[str, Any]) -> dict[str, Any]:
    """Preprocess comment.

    :param raw: raw comment
    """
    return {
        "id": raw["id"],
        "status": Status.TO_BE_PROCESSED,
        "body": raw["body"],
        "asset_id": raw["asset_id"],
        "asset_url": raw["asset"]["url"],
        "author_id": raw["author_id"],
        "username": raw["author"]["username"],
        "created_at": parse(raw["created_at"]),
        "last_updated_at": datetime.now(),
        "mentions": [],
        "media_house": MediaHouse.MDR,
    }

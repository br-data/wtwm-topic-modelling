from typing import Optional, Union
from settings import BUGG_MODEL_V1_PATH

import spacy

from src.tools import normalize_query_pattern

SPACY_MODEL = spacy.load(BUGG_MODEL_V1_PATH)


def recognise_mer(
    text: str, comment_id: str, model: Optional[SPACY_MODEL] = None
) -> list[dict[str, Union[str, int]]]:
    """Recognise mentions in text.

    :param text: text, that might contain mentions
    :param comment_id: id of the object the query belongs to
    :param model: recognizer model
    """
    model = model or SPACY_MODEL
    text = normalize_query_pattern(text, comment_id)
    doc = model(text)
    return [
        dict(
            body=ent.text,
            label=ent.label_,
            start=ent.start,
            offset=len(ent.text),
        )
        for ent in doc.ents
    ]

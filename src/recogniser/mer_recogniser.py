from typing import Optional, Union
from settings import MODEL_PATH

import spacy

SPACY_MODEL = spacy.load(MODEL_PATH)


def recognise_mer(
        text: str,
        model: Optional[SPACY_MODEL] = None
) -> list[dict[str, Union[str, int]]]:
    """Recognise mentions in text.

    :param text: text, that might contain mentions
    :param model: recognizer model
    """
    model = model or SPACY_MODEL
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

from enum import Enum
import uuid

from sqlalchemy.orm import relationship  # type: ignore

from src.recogniser.mer_recogniser import recognise_mer
from src.recogniser.pattern_recogniser import MentionPatternRecogniser
from src.models import RecognitionResult

PATTERN_RECOGNISER = MentionPatternRecogniser.from_list()


class RecognitionType(Enum):
    ANNOTATION = "annotation"
    SPACY_MODEL_A = "bugg_model_v1"
    PATTERN_RECOGNISER_A = "pattern_recogniser_v1"


def recognise(type_: RecognitionType, text: str, comment_id: str) -> list[RecognitionResult]:
    """Recognise mentions in a text.

    :param type_: recognition type
    :param text: text, that might hold mentions
    :param comment_id: id of comment, that is related to text
    """
    if type_ == RecognitionType.PATTERN_RECOGNISER_A:
        results = PATTERN_RECOGNISER(text)
    elif type_ == RecognitionType.SPACY_MODEL_A:
        results = recognise_mer(text)
    else:
        raise NotImplementedError(f"Model type '{type_.value}' is not implemented yet.")

    return [
        RecognitionResult(
            id=str(uuid.uuid1()),
            comment_id=comment_id,
            extracted_from=type_,
            **result
        ) for result in results
    ]

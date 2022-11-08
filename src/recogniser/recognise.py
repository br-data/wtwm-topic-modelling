import uuid

from sqlalchemy.orm import relationship  # type: ignore

from src.recogniser.mer_recogniser import recognise_mer
from src.recogniser.pattern_recogniser import (
    MentionPatternRecogniser,
    MentionRegexRecogniser,
)
from src.models import RecognitionResult, RecognitionType
from settings import BASELINE_SOURCE, PATTERN_RECOGNISER_SOURCE

PATTERN_RECOGNISER = MentionPatternRecogniser.from_file(PATTERN_RECOGNISER_SOURCE)
BASELINE_RECOGNISER = MentionRegexRecogniser.from_file(BASELINE_SOURCE)


def recognise(
    type_: RecognitionType, text: str, comment_id: str
) -> list[RecognitionResult]:
    """Recognise mentions in a text.

    :param type_: recognition type
    :param text: text, that might hold mentions
    :param comment_id: id of comment, that is related to text
    """
    if type_ == RecognitionType.PATTERN_RECOGNISER_A:
        results = PATTERN_RECOGNISER(text, comment_id)
    elif type_ == RecognitionType.SPACY_MODEL_A:
        results = recognise_mer(text, comment_id)
    elif type_ == RecognitionType.PATTERN_BASELINE:
        results = BASELINE_RECOGNISER(text, comment_id)
    else:
        raise NotImplementedError(f"Model type '{type_.value}' is not implemented yet.")

    return [
        RecognitionResult(
            id=str(uuid.uuid4()),
            comment_id=comment_id,
            extracted_from=type_.value,
            **result,
        )
        for result in results
    ]

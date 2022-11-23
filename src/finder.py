import uuid

from sqlalchemy.orm import relationship  # type: ignore

from src.recogniser.mer_recogniser import recognise_mer
from src.recogniser.pattern_recogniser import  MentionRegexRecogniser
from src.classifier.gpt2 import GPT2
from src.models import RecognitionResult, ModelType
from settings import BASELINE_SOURCE

BASELINE_RECOGNISER = MentionRegexRecogniser.from_file(BASELINE_SOURCE)
GPT2_CLASSIFIER = GPT2()


def find_mention(type_: ModelType, text: str, comment_id: str) -> list[RecognitionResult]:
    """Recognise mentions in a text.

    :param type_: model type
    :param text: text, that might hold mentions
    :param comment_id: id of comment, that is related to text
    """
    if type_ == ModelType.SPACY_MODEL_A:
        results = recognise_mer(text, comment_id)
    elif type_ == ModelType.PATTERN_BASELINE:
        results = BASELINE_RECOGNISER(text, comment_id)
    elif type_ == ModelType.GPT2:
        got_mentions = GPT2_CLASSIFIER(text)
        results = []
        if got_mentions:
            # Classification doesn't point to text position but classifies the whole text.
            # We add a dummy text position to fit to allow the result format to fit recognition and classification
            results.append(
                {
                    "start": -1,
                    "offset": 0,
                    "body": "text",
                    "label": "MENTION"
                }
            )
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


def includes_mentions(type_: ModelType, text: str, comment_id: str) -> bool:
    """True, if least one mention is included in the text, false otherwise.

    :param type_: recognition type
    :param text: text, that might hold mentions
    :param comment_id: id of comment, that is related to text
    """
    return True if find_mention(type_, text, comment_id) else False

from spacy.lang.de import German as SpacyTrained

from src.models import ExtractorResult, ExtractionType
import uuid


def extract_mentions_from_text(
    model: SpacyTrained,
    comment_id: str,
    text: str,
    extracted_from: ExtractionType = ExtractionType.SPACY_MODEL_A,
) -> list[ExtractorResult]:
    """Extract mentions from text.

    :param model: trained model of mentions
    :param text: text that might contain mentions
    """
    doc = model(text)
    return [
        ExtractorResult(
            id=str(uuid.uuid1()),
            comment_id=comment_id,
            body=ent.text,
            label=ent.label_,
            start=ent.start,
            offset=len(ent.text),
            extracted_from=extracted_from,
        )
        for ent in doc.ents
    ]

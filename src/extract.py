from spacy.lang.de import German as SpacyTrained

from src.models import ExtractorResult


def extract_mentions_from_text(model: SpacyTrained, text: str) -> list[ExtractorResult]:
    """Extract mentions from text.

    :param model: trained model of mentions
    :param text: text that might contain mentions
    """
    doc = model(text)
    return [
        ExtractorResult(
            text=ent.text, label=ent.label_, start=ent.start, offset=len(ent.text)
        )
        for ent in doc.ents
    ]

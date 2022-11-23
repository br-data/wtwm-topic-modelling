from typing import Generator, Pattern
import re

from cleantext import clean

REMOVE_HTML = re.compile(r"<.*?>")
POINTS = re.compile(r"\.+")
LINES = re.compile(r"--+")
_200D = re.compile(r"\u200D")
FORMATTING_FRAGMENTS = [
    POINTS,              # as in "....bin auch schon " angespannt"....😖🤢"
    LINES,               # as in "---- "Der Ertrag"
    _200D,
]
GAP = re.compile(r"\s\s+")


def preprocess_comment_text(text: str) -> str:
    """Perform text preprocessing steps.

    :param text: text to normalise
    """
    text = remove_linebreaks(text)
    text = remove_html_tags(text)
    text = remove_emojis(text)
    text = remove_formatting_fragments(text)
    text = remove_gaps(text)
    text = text.strip()
    if text is None:
        raise TypeError(f"Text is None.")

    if not text:
        raise ValueError(f"Got empty text")

    return text


def remove_html_tags(text: str, regex: Pattern = REMOVE_HTML) -> str:
    """Remove html tags.

    :param text: text, that might include html tags
    :param regex: regex, fitting html tags
    """
    return re.sub(regex, " ", text)


def remove_formatting_fragments(text: str, regexes: list[Pattern] = FORMATTING_FRAGMENTS) -> str:
    """Remove formatting fragments from text.

    :param text: raw text
    :param regexes: list of regexes fitting various kinds of fragments
    """
    for regex in regexes:
        text = re.sub(regex, " ", text)

    return text


def remove_gaps(text: str, regex: Pattern = GAP) -> str:
    """Remove multiple adjacent space symbols.

    :param text: text, that might include sequences of space symbols
    :param regex: regex, fitting chains of space symbols
    """
    return re.sub(regex, " ", text)


def remove_linebreaks(text: str) -> str:
    """Remove linebreaks.

    :param text: text, that might contain linebreaks

    Note: There are certain configurations of linebreaks that differ in if they are replace with space or removed.
    """
    text = re.sub(r"\s\n\s", " ", text)
    text = re.sub(r"\s\n", " ", text)
    text = re.sub(r"\n\s", " ", text)
    text = re.sub(r"\n-", "", text)
    text = re.sub(r"\n", "", text)
    return text


def remove_emojis(text: str) -> str:
    """Remove emojis from the comments.

    :param text: text, that might contain emojis

    Note: We decided to remove emojis because they are not relevant for the task.
    Note: External library 'clean-text' works best for the task at hand
    """
    return clean(
        text,
        fix_unicode=False,
        to_ascii=True,
        lower=False,
        normalize_whitespace=False,
        no_line_breaks=False,
        strip_lines=False,
        keep_two_line_breaks=False,
        no_urls=True,
        no_emails=True,
        no_phone_numbers=True,
        no_numbers=False,
        no_digits=False,
        no_currency_symbols=True,
        no_punct=False,
        no_emoji=True,
        lang="de"
    )

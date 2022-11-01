import uuid

from typing import Optional, Tuple

import ahocorasick
from ahocorasick import Automaton
from spacy.lang.de import German as SpacyTrained

from src.models import ExtractorResult, ExtractionType
from src.tools import normalize_query_pattern

_PATTERNS = [
    ("BR", "unspecified"),
    ("MDR", "unspecified"),
]
PATTERNS = list(
    set(
        [
            (normalize_query_pattern(pattern), type_)
            for pattern, type_ in _PATTERNS
            if len(pattern) > 2
        ]
    )
)


class ExtractionType(Enum):
    ANNOTATION = "annotation"
    SPACY_MODEL_A = "bugg_model_v1"
    PATTERN_RECOGNISER_A = "pattern_recogniser_v1"



class MentionPatternExtractor:
    """
    Extract known mentioning patterns from text
    """

    def __init__(
        self,
        patterns: list[Tuple[str, str]],
        trie: Automaton,
        normalize=False,
    ) -> None:
        """Init MentionPatternExtractor.

        :param normalize:
        :param patterns: list of known patterns to find in the text
        :param trie: ahocorasick trie
        """
        self._patterns = patterns
        self.normalize: bool = normalize
        self._trie = trie

    @classmethod
    def from_list(cls, patterns: list[str] = PATTERNS) -> "MentionPatternExtractor":
        """Build trie from list of patterns.

        :param patterns: list of patterns to recognize in text
        """
        trie = ahocorasick.Automaton()
        for idx, (pattern, type_) in enumerate(patterns):
            trie.add_word(pattern, (idx, pattern, type_))

        trie.make_automaton()
        return cls(patterns, trie)

    def find_patterns(self, text: str) -> list[Optional[dict]]:
        """Find and return patterns found in paragraph.

        :param text: text might holding patterns
        """
        hits = []
        for end, (idx, pattern, type_) in list(self._trie.iter(text)):
            hits.append(
                {
                    "start": end - len(pattern) + 1,
                    "end": end + 1,  # given end is inclusive
                    "pattern": pattern,
                    "type": type_,
                }
            )

        longest_hits = leftmost_longest(hits) if hits else []
        longest_hits_filtered = filter_in_word_hits(longest_hits, text)

        return longest_hits_filtered

    __call__ = find_patterns()


def leftmost_longest(hits: list[dict]) -> list[dict]:
    """Filter the leftmost longest match.

        Example:

            from the matches

                'Fernsehsessel'
                'Fernsehsesseltisch'
                '.......sessel.....'
                '.............tisch'

            only keep

                'Fernsehsesseltisch'

    :param hits: list of substring matches
    """
    sorted_by_start = sort_by_start(hits)
    grouped_by_start = group_by_start(sorted_by_start)
    longest_per_group = [longest_in_group(group) for group in grouped_by_start]
    return filter_substrings(longest_per_group)


def filter_in_word_hits(hits: list[dict], text: str) -> list[dict]:
    """Filters out hits which appear within a word.

    :param hits: A list of hits as returned from pyahocorasik.Automaton.iter
    :param text: The input text, on which the hits are detected.
    :return: A list of hits without hits from within a word.
    """
    result = list()
    words = text.split(" ")
    for word in words:
        for hit in hits:
            if word.startswith(hit["pattern"].split(" ")[0]):
                result.append(hit)

    return result


def filter_substrings(longest: list[dict]) -> list[dict]:
    """Filter substring matches that are a substring of another element

    :param longest: list of longest substring matches
    """
    # REFACTORME
    filtered = []
    for e in longest:
        keep = True
        start = e["start"]
        end = e["end"]
        for e2 in longest:
            start2 = e2["start"]
            end2 = e2["end"]
            # e is substring of e2
            if all([start > start2, end <= end2]):
                keep = False
                break
            # prefix of e overlaps with previous hit
            elif all([start > start2, start < end2]):
                keep = False
                break

        if keep:
            filtered.append(e)

    return filtered


def group_by_start(l: list[dict]) -> list[list[dict]]:
    """Collect all substring matches with same start index into sublists

    :param l: list of substring matches
    """
    groups = []
    start = l[0]["start"]
    group = [l[0]]
    for e in l[1:]:
        curr_start = e["start"]
        if curr_start == start:
            group.append(e)
        else:
            groups.append(group)
            group = [e]
            start = curr_start

    groups.append(group)
    return groups


def longest_in_group(group: list[dict]) -> dict:
    """Return longest in substring match group

    :param group: group of substring matches
    """
    longest = group[0]
    for e in group[1:]:
        curr_end = e["end"]
        if curr_end >= longest["end"]:
            longest = e

    return longest


def sort_by_start(l: list[dict]) -> list[dict]:
    """Sort list of substring matches by start index increasingly

    :param l: list of substring matches
    """
    return sorted(l, key=lambda k: k["start"])


def extract_mentions_from_text(
        model: SpacyTrained,
        comment_id: str,
        text: str,
        extracted_from: ExtractionType = ExtractionType.PATTERN_RECOGNISER_A
) -> list[ExtractorResult]:
    """Extract mentions from text.

    :param model: trained model of mentions
    :param comment_id: id of the comment
    :param text: text that might contain mentions
    :param extracted_from: extractor model
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

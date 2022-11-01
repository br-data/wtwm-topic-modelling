from typing import Optional, Tuple

import ahocorasick
from ahocorasick import Automaton

from src.tools import normalize_query_pattern


_PATTERNS = [
    ("BR", "unspecified"),
    ("MDR", "unspecified"),
]
PATTERNS = list(
    set(
        [
            (normalize_query_pattern(pattern), type_)
            for pattern, type_ in _PATTERNS if len(pattern) > 2
        ]
    )
)


class MentionPatternRecogniser:
    """
    Extract known mentioning patterns from text
    """

    def __init__(
            self,
            patterns: list[Tuple[str, str]],
            trie: Automaton,
            normalize=False,
    ) -> None:
        """Init MentionPatternRecogniser.

        :param normalize:
        :param patterns: list of known patterns to find in the text
        :param trie: ahocorasick trie
        """
        self._patterns = patterns
        self.normalize: bool = normalize
        self._trie = trie

    @classmethod
    def from_list(cls, patterns: list[Tuple[str, str]] = PATTERNS) -> "MentionPatternRecogniser":
        """Build trie from list of patterns.

        :param patterns: list of patterns to recognize in text
        """
        trie = ahocorasick.Automaton()
        for idx, (pattern, type_) in enumerate(patterns):
            trie.add_word(pattern, (idx, pattern, type_))

        trie.make_automaton()
        return cls(patterns, trie)

    def find_patterns(self, text: str, label: str = "MENTION") -> list[Optional[dict]]:
        """Find and return patterns found in paragraph.

        :param text: text might holding patterns
        """
        hits = []
        query = normalize_query_pattern(text)
        for end, (idx, pattern, type_) in list(self._trie.iter(query)):
            hits.append(
                {
                    "start": end - len(pattern) + 1,
                    "offset": len(pattern),
                    "body": pattern,
                    "label": label
                }
            )

        longest_hits = leftmost_longest(hits) if hits else []
        longest_hits_filtered = filter_in_word_hits(longest_hits, query)
        return longest_hits_filtered

    __call__ = find_patterns


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
            if word.startswith(hit["body"].split(" ")[0]):
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
        end = start + e["offset"]
        for e2 in longest:
            start2 = e2["start"]
            end2 = start2 + e2["offset"]
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
    longest_end = longest["start"] + longest["offset"]
    for e in group[1:]:
        curr_end = e["start"] + e["end"]
        if curr_end >= longest_end:
            longest = e

    return longest


def sort_by_start(l: list[dict]) -> list[dict]:
    """Sort list of substring matches by start index increasingly

    :param l: list of substring matches
    """
    return sorted(l, key=lambda k: k["start"])

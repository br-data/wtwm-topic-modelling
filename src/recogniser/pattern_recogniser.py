import re
from typing import Pattern, Union

from src.tools import normalize_query_pattern


class MentionRegexRecogniser:
    """
    Extract known mentions by regex from text
    """

    def __init__(self, regexes: list[Pattern]) -> None:
        """Init MentionRegexRecogniser.

        :param regexes: list of regex patterns
        """
        self._regexes = regexes

    @classmethod
    def from_file(cls, path: str) -> "MentionRegexRecogniser":
        """Build trie from list of patterns.

        :param path: path to regex source file
        """
        regexes = []
        with open(path, "r") as handle:
            for pattern in handle.read().split("\n"):
                pattern = pattern.strip()
                if not pattern:
                    # empty line
                    continue

                if pattern.startswith("#"):
                    # is comment
                    continue

                regexes.append(re.compile(pattern, flags=re.IGNORECASE))

        return cls(regexes)

    def find_mentions(
        self,
        text: str,
        comment_id: str,
        label: str = "MENTION",
        apply_leftmost_longest: bool = True,
    ) -> list[dict[str, Union[str, int]]]:
        """Find and return patterns found in text.

        :param text: text might holding patterns
        :param comment_id: id of the object the query belongs to
        :param label: recognition type label
        :param apply_leftmost_longest: perform left modest longest postprocessing
        """
        hits = []
        query = normalize_query_pattern(text, comment_id)
        for regex in self._regexes:
            for match in regex.finditer(query):
                pattern = match.group()
                hits.append(
                    {
                        "start": match.start(),
                        "offset": len(pattern),
                        "body": pattern,
                        "label": label,
                    }
                )

        if apply_leftmost_longest:
            longest_hits = leftmost_longest(hits) if hits else []
            longest_hits_filtered = filter_in_word_hits(longest_hits, query)
            return longest_hits_filtered
        else:
            return hits

    def includes_mentions(
        self, text: str, comment_id: str, label: str = "MENTION"
    ) -> bool:
        """True, if text inclues mentions, false otherwise.

        :param text: text might holding patterns
        :param comment_id: id of the object the query belongs to
        :param label: recognition type label
        """
        return (
            True
            if self.find_mentions(text, comment_id, label, apply_leftmost_longest=False)
            else False
        )

    __call__ = find_mentions


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
        curr_end = e["start"] + e["offset"]
        if curr_end >= longest_end:
            longest = e

    return longest


def sort_by_start(l: list[dict]) -> list[dict]:
    """Sort list of substring matches by start index increasingly

    :param l: list of substring matches
    """
    return sorted(l, key=lambda k: k["start"])

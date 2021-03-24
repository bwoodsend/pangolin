# -*- coding: utf-8 -*-
"""
"""

import difflib
import re
from typing import List


def matching_blocks(s1, s2):
    matcher = difflib.SequenceMatcher(None, s1, s2)
    matches = [m for m in matcher.get_matching_blocks() if m.size]
    return matches


class ParseArchType(object):

    # These must be lowercase.
    SPECIFIERS = [
        ("maxillary", "U"),
        ("mandibular", "L"),
        ("maxilla", "U"),
        ("mandible", "L"),
        ("upper", "U"),
        ("lower", "L"),
        ("top", "U"),
        ("bottom", "L"),
    ]

    input: str
    matches: List[List[difflib.Match]]
    specifier: str
    arch_type: str
    best_matches: List[difflib.Match]

    def __init__(self, input):
        self.input = str(input)
        self._input = self.input.lower()

        self.matches = [
            matching_blocks(self._input, i[0]) for i in self.SPECIFIERS
        ]

        self._index = max(range(len(self.SPECIFIERS)),
                          key=lambda x: self.score(self.matches[x]))
        self.specifier, self.arch_type = self.SPECIFIERS[self._index]
        self.best_matches = self.matches[self._index]

    @property
    def before(self):
        return self.input[:self.best_matches[0].a]

    @property
    def after(self):
        return self.input[self.best_matches[-1].a + self.best_matches[-1].size:]

    @property
    def matched(self):
        return self.input[self.best_matches[0].a:
                          self.best_matches[-1].a + self.best_matches[-1].size]

    @staticmethod
    def score(matches):
        return sum(match.size ** 2 for match in matches)

    def show(self):
        bits = []
        for (specifier, _), matches in zip(self.SPECIFIERS, self.matches):
            bits += [
                highlight_matches(self.input, "a", *matches),
                "  |  ",
                highlight_matches(specifier, "b", *matches),
                " " * (12 - len(specifier)) + "|  ",
                str(self.score(matches)),
                "\n",
            ]
        return "".join(bits)


def split_arch_type(name):
    self = ParseArchType(name)
    return self.before, self.matched, self.after


def strip_arch_type(name, replace_with="", delimiter=" -_"):
    before, match, after = split_arch_type(name)
    if not replace_with:
        after = after.lstrip(delimiter)
    return before + replace_with + after


def arch_type(name):
    return ParseArchType(name).arch_type


def underscore(x):
    return re.sub("([^\u0332])(\u0332)?", "\\1\u0332", x)


def highlight_matches(x, a_or_b, *matches):
    bits = []
    end = 0
    for match in matches:
        start = getattr(match, a_or_b)
        bits += [
            x[end: start],
            underscore(x[start: start + match.size]),
        ]
        end = start + match.size
    bits.append(x[end:])
    return "".join(bits)

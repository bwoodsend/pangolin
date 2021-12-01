# -*- coding: utf-8 -*-
"""
"""

import difflib
import re
from typing import List
from collections import namedtuple


class Span(namedtuple("Span", ["start", "size"])):

    @property
    def end(self):
        return self.start + self.size


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
    specifier: str
    arch_type: str
    best_matches: List[difflib.Match]

    def __init__(self, input):
        self.input = str(input)
        self._input = self.input.lower()
        self._match()

    @staticmethod
    def _match_specifier_word(word_match, specifier):
        matcher = difflib.SequenceMatcher(None, word_match.group(), specifier)
        spans = [
            Span(i.a + word_match.start(), i.size)
            for i in matcher.get_matching_blocks()
        ]
        return spans

    def _match_specifier(self, specifier):
        return max((self._match_specifier_word(m, specifier)
                    for m in re.finditer("[a-z]+", self._input)),
                   key=self.score)

    def _match(self):
        self.specifier, self.arch_type, self._spans = max(
            ((specifier, arch_type, self._match_specifier(specifier))
             for specifier, arch_type in self.SPECIFIERS),
            key=lambda x: self.score(x[2]),
        )

    @property
    def start(self):
        return self._spans[0].start

    @property
    def end(self):
        return self._spans[-1].end

    @property
    def before(self):
        return self.input[:self.start]

    @property
    def after(self):
        return self.input[self.end:]

    @property
    def matched(self):
        return self.input[self.start:self.end]

    @staticmethod
    def score(spans):
        return sum(span.size**2 for span in spans)

    def show(self):
        bits = []
        for (specifier, _) in self.SPECIFIERS:
            spans = self._match_specifier(specifier)
            bits += [
                highlight_matches(self.input, *spans),
                "  |  ",
                specifier.ljust(12, " ") + "|  ",
                str(self.score(spans)),
                "\n",
            ]
        return "".join(bits)


def split_arch_type(name):
    self = ParseArchType(name)
    return self.before, self.matched, self.after


def substitute_arch_type(text, replace="", *, delimiter=r"[ \-_]"):
    """Remove or replace the arch type specifier from a string of text.

    Args:
        text:
            The text to modify.
        replace:
            The text to replace the arch type specifier with. This may be an
            empty string to strip the arch type specifier or a callable to map
            it to a value dependent on the original.
        delimiter:
            If **replace_with** is (or returns) an empty string and there is
            a delimiter both before and after the arch type specifier, then
            additionally strip the delimiter before so as to avoid a double
            delimiter.
    Returns:
        A modified copy of the input text.

    Examples::

        # Strip the arch type specifier.
        >>> substitute_arch_type("The maxillary jaw")
        'The jaw'

        # Normalize the arch type specifier.
        >>> substitute_arch_type(
        ...     "The maxilliaary jaw",
        ...     lambda arch_type, _: "upper" if arch_type == "U" else "lower")
        'The upper jaw'

        # Uppercase the arch type specifier.
        >>> substitute_arch_type("The maxillary jaw",
        ...                      lambda _, matched: matched.upper())
        'The MAXILLARY jaw'

    """
    parser = ParseArchType(text)
    after = parser.after

    if callable(replace):
        replace = replace(parser.arch_type, parser.matched)

    if not replace:
        m = re.match(delimiter, after)
        if m:
            after = after[m.end():]

    return parser.before + replace + after


def arch_type(name):
    return ParseArchType(name).arch_type


def highlight(x):
    """Replace all ASCII letters in a string with their bold unicode equivalents
    leaving all other characters unchanged."""
    return "".join(map(_highlight_character, x))


def _highlight_character(x):
    """Replace an ASCII letter with its bold unicode equivalent."""
    if ord('a') <= ord(x) <= ord('z'):
        return chr(ord(x) + 0x1D5EE - 0x61)
    if ord('A') <= ord(x) <= ord('Z'):
        return chr(ord(x) + 0x1D400 - 0x41)
    return x


def highlight_matches(x, *spans: Span):
    bits = []
    end = 0
    for span in spans:
        bits += [
            x[end:span.start],
            highlight(x[span.start:span.end]),
        ]
        end = span.end
    bits.append(x[end:])
    return "".join(bits)

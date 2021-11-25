# -*- coding: utf-8 -*-
"""
"""

from textwrap import dedent

from pangolin import ParseArchType, split_arch_type, strip_arch_type, arch_type


def test_highlight():
    from pangolin._arch_type_parser import highlight
    assert highlight("abc") == "𝗮𝗯𝗰"
    assert highlight("ABC") == "𝐀𝐁𝐂"
    assert highlight("123") == "123"


def test_basic():
    self = ParseArchType("I am an Upper jaw.")
    assert self.specifier == "upper"
    assert self.before == "I am an "
    assert self.matched == "Upper"
    assert self.after == " jaw."
    assert self.arch_type == "U"

    assert self.show() == dedent("""\
        𝐈 am an Upper jaw.  |  maxillary   |  1
        I am 𝗮𝗻 Upper jaw.  |  mandibular  |  4
        𝐈 am an Upper jaw.  |  maxilla     |  1
        I am 𝗮𝗻 Upper jaw.  |  mandible    |  4
        I am an 𝐔𝗽𝗽𝗲𝗿 jaw.  |  upper       |  25
        I am an Upp𝗲𝗿 jaw.  |  lower       |  4
        I am an U𝗽per jaw.  |  top         |  1
        I a𝗺 an Upper jaw.  |  bottom      |  1
    """)

    assert split_arch_type(self.input) == ("I am an ", "Upper", " jaw.")
    assert strip_arch_type(self.input) == "I am an jaw."
    assert strip_arch_type(self.input, "lower") == "I am an lower jaw."
    assert arch_type(self.input) == "U"


def test_word_boundaries():
    """Ensure that abbreviated keywords can't suck up characters from other
    words."""
    assert split_arch_type("A maxizlarry with a z") \
           == ("A ", "maxizlarry", " with a z")

    assert split_arch_type("A maxi llary with a space") \
        == ("A maxi ", "llary", " with a space")

    assert split_arch_type("A MAXI.LLARY with a '.'") \
        == ("A MAXI.", "LLARY", " with a '.'")


def test_fuzzy():
    assert arch_type("Bob maxil") == "U"
    assert arch_type("manible") == "L"
    assert arch_type("Max's manible jaw.") == "L"
    assert arch_type("Maxime's mangible is spelt wrong.") == "L"

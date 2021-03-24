# -*- coding: utf-8 -*-
"""
"""

from pangolin import ParseArchType, split_arch_type, strip_arch_type, arch_type


def test_basic():
    self = ParseArchType("I am an Upper jaw.")
    assert self.specifier == "upper"
    assert self.before == "I am an "
    assert self.matched == "Upper"
    assert self.after == " jaw."
    assert self.arch_type == "U"

    assert self.show() == """\
I̲ a̲m an Upper̲ jaw.  |  maxi̲lla̲r̲y   |  3
I am̲ a̲n̲ U̲pper̲ jaw.  |  m̲a̲n̲dibu̲lar̲  |  7
I̲ a̲m an Upper jaw.  |  maxi̲lla̲     |  2
I am̲ a̲n̲ Uppe̲r jaw.  |  m̲a̲n̲dible̲    |  6
I am an U̲p̲p̲e̲r̲ jaw.  |  u̲p̲p̲e̲r̲       |  25
I am an Uppe̲r̲ jaw.  |  lowe̲r̲       |  4
I am an Up̲per jaw.  |  top̲         |  1
I am̲ an Upper jaw.  |  bottom̲      |  1
"""

    assert split_arch_type(self.input) == ("I am an ", "Upper", " jaw.")
    assert strip_arch_type(self.input) == "I am an jaw."
    assert strip_arch_type(self.input, "lower") == "I am an lower jaw."
    assert arch_type(self.input) == "U"


def test_fuzzy():
    assert arch_type("Bob maxil") == "U"
    assert arch_type("manible") == "L"
    assert arch_type("Max's manible jaw.") == "L"
    assert arch_type("Maxime's mangible is spelt wrong.") == "L"

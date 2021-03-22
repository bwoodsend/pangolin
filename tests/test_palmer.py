# -*- coding: utf-8 -*-
"""
"""

import pytest
from pangolin import Palmer

pytestmark = pytest.mark.order(3)


def test_init():
    """Assert that __init__ arguments are in the right order and work."""
    code = Palmer.__init__.__code__
    args = code.co_varnames[:code.co_argcount]
    assert args == ("self", "arch_type", "side", "index", "sub_index",
                    "primary", "species")

    self = Palmer("U", "R", 3)
    assert self.arch_type == "U"
    assert self.side == "R"
    assert self.index == 3
    assert self.primary is False
    assert self.species == "human"

    assert str(self) == "UR3"
    assert Palmer("UR3") == self

    assert Palmer(self).arch_type == "U"
    assert Palmer(self) == self

    with pytest.raises(ValueError,
                       match=r"Could not parse the palmer 'An UR3\.'\."):
        Palmer("An UR3.")
    assert Palmer(Palmer.regex.search("An UR3.")) == self


@pytest.mark.parametrize("species", ["human", "sausage-monster"])
@pytest.mark.parametrize("index", [3, 12, "*"])
@pytest.mark.parametrize("sub_index", [1, None])
@pytest.mark.parametrize("primary", [False, True])
@pytest.mark.parametrize("side", ["L", "R", "*"])
@pytest.mark.parametrize("arch_type", ["L", "U", "*"])
def test_parse_str(species, index, sub_index, primary, side, arch_type):
    kwargs = locals().copy()
    palmer = Palmer(**kwargs)
    assert str(palmer) in repr(palmer)
    assert palmer.to_dict() == kwargs
    assert palmer == str(palmer)
    assert str(palmer) == palmer
    assert palmer == Palmer(str(palmer))
    assert palmer == Palmer(palmer)
    assert palmer.with_(**kwargs) == palmer
    assert Palmer().with_(**kwargs) == palmer
    assert Palmer(*(kwargs[i] for i in Palmer.keys())) == palmer


def test_negative():
    assert -Palmer("UR3") == "UL3"
    assert -Palmer("*L*") == "*R*"

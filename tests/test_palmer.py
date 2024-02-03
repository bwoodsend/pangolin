# -*- coding: utf-8 -*-
"""
"""

import pytest
from pangolin import Palmer, JawType


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

    assert Palmer("orc-LLC").jaw_type == JawType("L", True, "orc")


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


def test_kinds():
    assert Palmer("LR2").kind == "I"
    assert Palmer("UL5").kind == "P"
    assert Palmer("ULE").kind == "M"
    assert Palmer("**1").kind == "I"

    with pytest.raises(ValueError,
                       match=r"Can't determine .* 'UR\*'\. Don't .*"):
        Palmer("UR*").kind

    assert Palmer("sheep-LL10").kind == "M"

    with pytest.raises(ValueError):
        assert Palmer("sheep-*L10").kind


def test_range():
    # Basic.
    assert Palmer.range("UR2", "UR4") == ["UR2", "UR3", "UR4"]

    # Use 0 to mean center.
    assert Palmer.range(0, "LRC") == ["LRA", "LRB", "LRC"]
    assert Palmer.range("*L2", 0) == ["*L2", "*L1"]

    # Conflicting jaw types. Priorities are kwargs > start > end.
    assert Palmer.range("ULE", "LL3", arch_type="L") == ["LLE", "LLD", "LLC"]
    # Under-defined jaw type. Use defaults which aren't overridden by kwargs.
    assert Palmer.range(0, primary=True) == Palmer.range(0, "*RE")

    # Cross the middle. Should be no LL0 or LR0.
    assert Palmer.range("*L2", "LRB") == ["*L2", "*L1", "*R1", "*R2"]

    # Default to extremes if either start or end is undefined.
    assert Palmer.range("URC") == ["URC", "URD", "URE"]

    # Unknown jaw types should still work.
    assert Palmer.range("monster-LL2", 0) == ["monster-LL2", "monster-LL1"]
    # Unless the number of teeth is needed.
    with pytest.raises(ValueError, match="No tooth kinds"):
        Palmer.range("monster-LL2")

    # Going backwards silently returns an empty list.
    assert Palmer.range("LR2", "*L2") == []

    # Wildcards in the wrong places.
    with pytest.raises(ValueError, match=r" '\*\*3' is ambiguous"):
        Palmer.range("**3")
    with pytest.raises(ValueError):
        Palmer.range("UL*")


def test_hash():
    """Ensure that ``palmer`` and ``str(palmer)`` are
    considered equivalent when used as dict keys or in sets.
    """
    palmers = Palmer.range()

    set_ = set(palmers)
    assert len(set_) == len(palmers)

    for i in palmers:
        assert i in set_
        assert str(i) in set_


def test_sort():
    assert Palmer("UR2") < Palmer("UR3")
    assert "UR2" < Palmer("UR3")
    assert Palmer("UR2") < "UR3"
    assert Palmer("LL3") < "LL2"
    assert Palmer("LL3.0") < "LL3"
    assert Palmer("LL3.1") < "LL3.0"
    assert Palmer("LL4") < "LL3.9"
    assert Palmer("LR*") < "LR1"
    assert Palmer("LL*") < "LR*"
    assert Palmer("LR*") < "LR*.0"

    palmers = Palmer.range(primary=True)
    assert sorted(palmers[::-1]) == palmers

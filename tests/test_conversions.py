# -*- coding: utf-8 -*-
"""
"""

import pytest
from pangolin import Palmer


@pytest.mark.parametrize("primary", [False, True])
def test_universal(primary):
    """Universal ADA notation enumerates counterclockwise around the mouth from
    UR8 to LR8. For baby teeth (primary==True) the enumeration uses capital
    letters instead of numbers.
    """
    assert Palmer("UR8").to_universal() == "1"
    assert Palmer("LR8").to_universal() == "32"

    palmers = Palmer.range(primary=primary, arch_type="U")[::-1] \
            + Palmer.range(primary=primary, arch_type="L")

    # Putting `palmers` in the order above should mean that `universal` is just
    # numbers 1-32 inclusive in order or the first 20 letters of the alphabet.
    universal = [i.to_universal() for i in palmers]

    if not primary:
        target = [str(i) for i in range(1, 33)]
    else:
        from string import ascii_uppercase
        target = list(ascii_uppercase[:20])

    with pytest.raises(ValueError):
        Palmer("*L3").to_universal()

    assert universal == target


FDI_ADULT = """\
18 17 16 15 14 13 12 11 21 22 23 24 25 26 27 28
48 47 46 45 44 43 42 41 31 32 33 34 35 36 37 38"""

FDI_BABY = """\
55 54 53 52 51 61 62 63 64 65
85 84 83 82 81 71 72 73 74 75"""


@pytest.mark.parametrize("primary", [False, True])
def test_FDI(primary):
    palmers = [
        Palmer.range(primary=primary, arch_type="U")[::-1],
        Palmer.range(primary=primary, arch_type="L")[::-1]
    ]
    fdi = "\n".join(" ".join(i.to_FDI() for i in j) for j in palmers)
    if primary:
        assert fdi == FDI_BABY
    else:
        assert fdi == FDI_ADULT

    with pytest.raises(ValueError, match=r"Palmer 'U\*2' containing"):
        Palmer("U*2").to_FDI()
    with pytest.raises(ValueError):
        Palmer("troll-LL1").to_FDI()
    assert Palmer("UL*").with_(primary=False).to_FDI() == "2*"


ADULT_SYMBOLS = """\
8⏌ 7⏌ 6⏌ 5⏌ 4⏌ 3⏌ 2⏌ 1⏌ ⎿1 ⎿2 ⎿3 ⎿4 ⎿5 ⎿6 ⎿7 ⎿8
8⏋ 7⏋ 6⏋ 5⏋ 4⏋ 3⏋ 2⏋ 1⏋ ⎾1 ⎾2 ⎾3 ⎾4 ⎾5 ⎾6 ⎾7 ⎾8"""
BABY_SYMBOLS = """\
E⏌ D⏌ C⏌ B⏌ A⏌ ⎿A ⎿B ⎿C ⎿D ⎿E
E⏋ D⏋ C⏋ B⏋ A⏋ ⎾A ⎾B ⎾C ⎾D ⎾E"""

# This will probably look like gibberish unless you set your editor's font
# to FreePalmer or FreeMono.
ADULT_TRUE_TYPE = """\
               
               """
BABY_TRUE_TYPE = """\
         
         """


@pytest.mark.parametrize("primary", [False, True])
def test_symbolic(primary):
    """Symbolic palmers should form a big + shape if all written out together
    from **the examiner's perspective**. This means that we start at right and
    go left."""
    # All palmers but flip left and right.
    palmers = [Palmer.range(primary=primary, arch_type="U")[::-1],
               Palmer.range(primary=primary, arch_type="L")[::-1]] #yapf: disable

    symbols = "\n".join(" ".join(i.to_symbol() for i in j) for j in palmers)
    if primary:
        assert symbols == BABY_SYMBOLS
    else:
        assert symbols == ADULT_SYMBOLS

    # --- True typed ---

    symbols = "\n".join(
        " ".join(i.to_symbol(true_type=True) for i in j) for j in palmers)

    if primary:
        assert symbols == BABY_TRUE_TYPE
    else:
        assert symbols == ADULT_TRUE_TYPE

    with pytest.raises(ValueError):
        Palmer("*R2").to_symbol()
    with pytest.raises(ValueError):
        Palmer("LL3.0").to_symbol()


def test_numpy():
    """numpy.array(Palmer()) must create a single-item object array - not unpack
    the palmer as it would a tuple."""
    np = pytest.importorskip("numpy")
    self = Palmer()
    arr = np.array(self)
    assert arr.shape == ()
    assert arr.dtype == object
    assert arr.item() == self
    assert np.array(Palmer.range()).shape == (16,)

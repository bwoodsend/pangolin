# -*- coding: utf-8 -*-
"""
"""

import pytest

from pangolin import tooth_kinds, TOOTH_KINDS, JawType


def test():
    """Test :func:`pangolin.tooth_kinds`."""

    # Plain lookup.
    assert tooth_kinds(JawType()) == TOOTH_KINDS[JawType()] == "IICPPMMM"

    # The `arch_type` doesn't matter for humans.
    assert tooth_kinds(JawType(arch_type="U")) == TOOTH_KINDS[JawType()]
    # But does for sheep.
    assert tooth_kinds(JawType(arch_type="U", species="sheep")) \
           == TOOTH_KINDS[JawType(arch_type="U", species="sheep")]
    with pytest.raises(ValueError, match=r"for JawType\(.*\)\."):
        tooth_kinds(JawType(species="sheep"))

    # `primary` should not be a wildcard because it's ambiguous.
    with pytest.raises(ValueError):
        tooth_kinds(JawType(primary="*"))

    # Haha, I'm hilarious.
    assert tooth_kinds(JawType(species="pangolin")) == ''

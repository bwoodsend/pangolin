# -*- coding: utf-8 -*-
"""
"""
from ._jaw_type import JawType

TOOTH_KINDS = {
    JawType(): "IICPPMMM",
    JawType(primary=True): "IICMM",
    JawType(arch_type="U", species="sheep"): "PPPMMM",
    JawType(arch_type="L", species="sheep"): "IIIIPPPMMM",
    JawType(species="pangolin", primary="*"): "",
}


def tooth_kinds(jaw_type=JawType()) -> str:
    """Get dental formula for a given :class:`JawType`.

    Args:
        jaw_type:
            The type of arch.
    Returns:
        The tooth types in one quadrant.

    Examples:

         The following tells us that each quadrant of a baby's mouth contains
         two incisors, one canine and two molars::

            >>> tooth_kinds(JawType(primary=True))
            'IICMM'

    """
    if jaw_type in TOOTH_KINDS:
        return TOOTH_KINDS[jaw_type]
    for jaw_type_ in TOOTH_KINDS.keys():
        if jaw_type_.match(jaw_type, strict=True):
            return TOOTH_KINDS[jaw_type_]
    raise ValueError(f"No tooth kinds data is available for {repr(jaw_type)}. "
                     "You can add it to `pangolin.TOOTH_KINDS`.")


from ._palmer import Palmer
from ._arch_type_parser import (ParseArchType, split_arch_type,
                                substitute_arch_type, arch_type)

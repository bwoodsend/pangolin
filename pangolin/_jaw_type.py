# -*- coding: utf-8 -*-
"""
"""

from collections.abc import Mapping
from typing import Union
import attr


@attr.attrs(slots=True, frozen=True)
class BaseBucket(Mapping):
    """A custom bucket class which acts a bit like a dictionary."""

    def with_(self, **values):
        """Return a modified copy. Arguments can be any of the core attributes
        in :attr:`!__slots__`. Multiple modifications can be done at once.
        Use :py:`...` to indicate *unchanged*.
        """
        out = self.to_dict()
        for (key, val) in values.items():
            if val is not None:
                out[key] = val
        return type(self)(**out)

    def to_dict(self, skip_wildcard=False) -> dict:
        """Returns attributes as a dict.

        Args:
             skip_wildcard:
                Wildcard attributes are excluded if true.

        Without **skip_wildcard**, this can also be achieved by passing this
        object directly to :class:`dict`.

         """
        if skip_wildcard:
            return {i: j for (i, j) in self.to_dict().items() if j != "*"}
        return {i: getattr(self, i) for i in self}

    def match(self, other, strict=False):
        """Perform soft equality testing respecting wildcards.

        Args:
            other:
                Another instance to compare to.
            strict:
                If true, wildcards in **other** are not skipped.
        Returns:
            ``True`` if they match, ``False`` if they don't.

        Similar to regular equality testing except it skips any fields
        containing wildcards.

        """
        self, other = (jaw if isinstance(jaw, dict) else jaw.to_dict(
            skip_wildcard=True) for jaw in (self, other))
        for key in self.keys():
            value_0, value_1 = self[key], other.get(key, "*")
            if value_0 == "*":
                continue
            if value_1 == "*" and not strict:
                continue
            if value_0 != value_1:
                return False
        return True

    # --- Definitions to keep the Mapping ABC happy. ---

    def __iter__(self):
        return iter(self.keys())

    def __getitem__(self, k):
        return getattr(self, k)

    def __len__(self):
        return len(self.__slots__)

    def keys(self):
        return self.__slots__

    @classmethod
    def from_obj(cls, obj):
        """Extract attributes from an object (usually of the same type)."""
        return cls(**{key: getattr(obj, key) for key in cls.__slots__})


@attr.attrs(slots=True, frozen=True, auto_attribs=True)
class JawType(BaseBucket):
    """The :class:`JawType` bucket class contains the attributes:

    - :attr:`arch_type`
    - :attr:`primary`
    - :attr:`species`

    """

    arch_type: str = "*"
    """Specifies upper or lower jaw:

    - For a maxillary (upper) jaw: :py:`'U'`,
    - For a mandibular (lower) jaw: :py:`'L'`,
    - For unspecified use :py:`'*'`.

    """

    primary: Union[bool, str] = False
    """Specifies deciduous dentition (A.K.A baby teeth).
    Either :py:`True` or :py:`False` or :py:`'*'`.
    """

    species: str = "human"
    """Specifies the species. Defaults to, and will likely always be,
    :py:`'human'`. It is highly recommended that you use '-' instead of spaces
    to delimite multiple words.
    """

    def with_(self, arch_type=None, primary=None, species=None):
        return super().with_(arch_type=arch_type, primary=primary,
                             species=species)

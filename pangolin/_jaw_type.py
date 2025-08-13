from collections.abc import Mapping
import sys
from typing import Union


class BaseBucket(Mapping):
    """A custom bucket class which acts a bit like a dictionary."""

    def __init__(self, **kwargs):
        for (key, value) in kwargs.items():
            setattr(self, "_" + key, value)

    def __hash__(self):
        return hash(tuple(getattr(self, i) for i in self.__slots__))

    def __repr__(self):
        arguments = ", ".join(
            f"{key}={repr(value)}" for (key, value) in self.items())
        return f"{type(self).__name__}({arguments})"

    def with_(self, **values):
        """Return a modified copy. Arguments can be any of the core attributes
        in :attr:`!__slots__`. Multiple modifications can be done at once.
        Use :py:`...` to indicate *unchanged*.
        """
        out = self.to_dict()
        for (key, val) in values.items():
            if val is not ...:
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

    def __array__(self, dtype=None, copy=None):  # pragma: needs-numpy
        # Doing this prevents numpy.array(JawType()) from becoming:
        #   array(['arch_type', 'primary', 'species'], dtype='<U9')
        # Avoid using `import numpy` to prevent PyInstaller thinking pangolin
        # depends on NumPy.
        out = sys.modules["numpy"].empty((), object)
        out[()] = self
        return out

    @classmethod
    def keys(self):
        return [i[1:] for i in self.__slots__]

    @classmethod
    def from_obj(cls, obj):
        """Extract attributes from an object (usually of the same type)."""
        return cls(**{key: getattr(obj, key) for key in cls.keys()})


class JawType(BaseBucket):
    """The :class:`JawType` bucket class contains the attributes:

    - :attr:`arch_type`
    - :attr:`primary`
    - :attr:`species`

    """
    __slots__ = ("_arch_type", "_primary", "_species")

    def __init__(self, arch_type="*", primary=False, species="human"):
        if isinstance(arch_type, Mapping):
            BaseBucket.__init__(self, **arch_type)
        elif isinstance(arch_type, str) and arch_type in "LU*":
            BaseBucket.__init__(**locals())
        else:
            raise ValueError(f"Invalid arch_type {repr(arch_type)}. "
                             f"Must be one of 'LU*'.")

    @property
    def arch_type(self) -> str:
        """Specifies upper or lower jaw:

        - For a maxillary (upper) jaw: :py:`'U'`,
        - For a mandibular (lower) jaw: :py:`'L'`,
        - For unspecified use :py:`'*'`.

        """
        return self._arch_type

    @property
    def primary(self) -> Union[bool, str]:
        """Specifies deciduous dentition (A.K.A baby teeth).
        Either :py:`True` or :py:`False` or :py:`'*'`.
        """
        return self._primary

    @property
    def species(self) -> str:
        """Specifies the species. Defaults to, and will likely always be,
        :py:`'human'`. It is highly recommended that you use '-' instead of
        spaces to delimit multiple words.
        """
        return self._species

    def with_(self, arch_type=..., primary=..., species=...):
        return BaseBucket.with_(**locals())

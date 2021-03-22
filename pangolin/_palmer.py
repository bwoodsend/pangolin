# -*- coding: utf-8 -*-
"""
"""

import re
from typing import Union

from pangolin._jaw_type import JawType, BaseBucket
from pangolin import tooth_kinds


_palmer_regex = re.compile(r"""

# species: optional, requires but excludes a trailing - or _ delimiter.
(?:([\w-]+)[_-])?

# arch_type: 'U', 'L' or * for unspecified.
([UL*])

# side: 'L', 'R' or '*' for unspecified.
([LR*])

# index: a number, single A-Z character or '*'.
(\d+|[A-Z]|\*)

# subindex: optional single-digit number, ignores but requires a preceding '.'.
(?:[.](\d))?

""", re.VERBOSE)  # yapf: disable

PalmerLike = Union['Palmer', str, re.Match]


class Palmer(JawType):
    """The `letters and numbers variation` of the Palmer tooth labelling system.
    See the Palmer column from `here
    <https://support.clearcorrect.com/hc/article_attachments/360054874894/Dental_Notation_Systems_1_-_EN.jpg>`_\\ .
    In dentistry, palmers are composed of 3 characters:

    #.  **L** or **U** for lower or upper jaw.
    #.  **L** or **R** for left or right half (patient's perspective).
    #.  The tooth index from **1-8**, starting from the centre. Or for baby
        teeth, an uppercase letter from **A-E**.

    Examples of a Palmer are **UR4** or **LR5** or **LLC**.

    This bucket class contains the core attributes
    :attr:`arch_type`, :attr:`side`, :attr:`index`, :attr:`sub_index`
    :attr:`primary`, :attr:`species`.

    """

    @property
    def side(self) -> str:
        """The side the tooth is on.

        Either :py:`'L'` for left, :py:`'R'` or :py:`'*'` for unknown.
        Left and right are from the patient's perspective -- not the examiner's.
        """
        return self._side

    @property
    def index(self) -> Union[str, int]:
        """The tooth number. The center-most tooth has index 1.

        This is still an integer for baby teeth. The only valid :class:`str`
        value this attribute may have is wildcard :py:`'*'`.
        """
        return self._index

    @property
    def sub_index(self) -> int:
        """An optional sub-enumeration usable to specify indivual cusps."""
        return self._sub_index

    __slots__ = ("_arch_type", "_side", "_index", "_sub_index", "_primary",
                 "_species")
    regex = _palmer_regex

    def __init__(self, arch_type="*", side="*", index="*", sub_index=None,
                 primary=False, species="human"):
        """A Palmer (say **URC**) may be initialised in one of three ways:

        1.  Explicitly: :py:`Palmer('U', 'R', 3, primary=True)`.
        2.  From a string: :py:`Palmer('URC')`.
        3.  From a pattern match given by the :attr:`regex` attribute.

        When parsing from a string, the string is full-matched meaning that the
        string must contain the palmer with no additional characters::

            >>> Palmer("UR3")
            Palmer('UR3')
            >>> Palmer("This tooth is an UR3.")
            ValueError: Could not parse the palmer 'This tooth is an UR3.'.

        To parser palmers embeded in longer strings use form 3: the
        :attr:`regex` pattern::

            >>> Palmer(Palmer.regex.search("This is an UR3."))
            Palmer('UR3')

        """
        if isinstance(arch_type, re.Match):
            # Form 3: from regex match. Unpack it then initialise explicitly.
            self.__init__(*unpack_match(arch_type))

        elif not isinstance(arch_type, str):
            # Presumably this is another Palmer.
            self.__init__(**arch_type)

        elif len(arch_type) > 1:
            # Form 2: Parse from string.
            # The only way it knows this isn't form 1 is because `arch_type`
            # would have to be a single character.
            match = Palmer.regex.fullmatch(arch_type)
            if not match:
                raise ValueError(f"Could not parse the palmer '{arch_type}'.")
            self.__init__(match)

        else:
            # Initialise explicitly (just set each attribute).
            BaseBucket.__init__(**locals())

    def __eq__(self, x):
        return (self is x) or str(self) == x

    def __neg__(self):
        return self.with_(side={"L": "R", "R": "L", "*": "*"}[self.side])

    def __repr__(self):
        return "{}('{}')".format(self.__class__.__name__, str(self))

    def __str__(self):
        if self.species == "human":
            species = ""
        else:
            species = self.species + "-"

        if self.index == "*":
            index = "*"
        elif self.primary:
            index = digit_to_char(self.index)
        else:
            index = str(self.index)

        if self.sub_index is not None:
            sub_index = "." + str(self.sub_index)
        else:
            sub_index = ""

        return species + self.arch_type + self.side + index + sub_index

    @property
    def jaw_type(self) -> JawType:
        """Export the :class:`JawType` properties of the arch that this tooth
        belongs to."""
        return JawType.from_obj(self)

    @property
    def kind(self):
        """Returns the tooth's sub-type as one the typical dental abbreviations
        listed below:

        - :py:`'I'`: Incisor
        - :py:`'C'`: Canine
        - :py:`'P'`: Premolar
        - :py:`'M'`: Molar

        This table is stored in :attr:`Palmer.KINDS`.

        """
        if self.index == "*":
            raise ValueError(f"Can't determine tooth kind of '{self}'. Don't "
                             f"know which tooth it is!")
        return tooth_kinds(self.jaw_type)[self.index - 1]

    KINDS = dict(zip("ICPM", ("incisor", "canine", "premolar", "molar")))

    def with_(self, arch_type=..., side=..., index=..., sub_index=...,
              primary=..., species=...):
        return BaseBucket.with_(**locals())


def unpack_match(match: re.Match) -> tuple:
    """Convert a match from :attr:`Palmer.regex` into explicit palmer arguments.
    """

    species, arch_type, side, index, sub_index = match.groups()
    if species is None:
        species = "human"

    if index == "*":
        primary = "*"
    elif index.isdigit():
        primary = False
        index = int(index)
    else:
        index = char_to_digit(index)
        primary = True

    if sub_index is not None:
        sub_index = int(sub_index)

    return arch_type, side, index, sub_index, primary, species


def char_to_digit(char):
    return ord(char.upper()) - ord("A") + 1


def digit_to_char(index):
    return chr(int(index) - 1 + ord("A"))

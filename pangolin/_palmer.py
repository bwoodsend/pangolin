# -*- coding: utf-8 -*-
"""
"""

import re
from typing import Union, List, Match

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

PalmerLike = Union['Palmer', str, Match]


class Palmer(JawType):
    """A fancy bucket class representing *letters and numbers variation* of the
    `Palmer tooth labelling system`_.

    Palmers are composed of 3 characters:

    #.  **L** or **U** for lower or upper jaw.
    #.  **L** or **R** for left or right half (patient's perspective).
    #.  The tooth index from **1-8**, starting from the centre. Or for baby
        teeth, an uppercase letter from **A-E**.

    Examples of a Palmer are **UR4** or **LR5** or **LLC**.

    This bucket class contains the core attributes
    :attr:`arch_type`, :attr:`side`, :attr:`index`, :attr:`sub_index`
    :attr:`primary`, :attr:`species`.

    .. _`Palmer tooth labelling system`:
        https://support.clearcorrect.com/hc/article_attachments/360054874894/Dental_Notation_Systems_1_-_EN.jpg

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
        if isinstance(arch_type, Match):
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

    def __gt__(self, x):
        if isinstance(x, (str, Match)):
            x = Palmer(x)
        return self._sort_key() > x

    def __hash__(self):
        # Defining hash like this allows `{Palmer("LR2"): value}["LR2"]`.
        return hash(str(self))

    def __lt__(self, x):
        if isinstance(x, (str, Match)):
            x = Palmer(x)
        return self._sort_key() < x

    def __neg__(self):
        return self.with_(side={"L": "R", "R": "L", "*": "*"}[self.side])

    def _pre_conversion_check(self, type_name, wildcards=False, sub_index=False,
                              human_only=False):

        ext = " can't be converted to {}.".format(type_name)

        if wildcards and (self.side == "*" or self.arch_type == "*"):
            raise ValueError(f"Palmer '{self}' containing wildcards" + ext)
        if sub_index and self.sub_index is not None:
            raise ValueError(f"Palmer '{self}' containing sub_indices" + ext)
        if human_only and (self.species != "human"):
            raise ValueError(f"Non-human palmer '{self}'" + ext)

    def __repr__(self):
        return "{}('{}')".format(self.__class__.__name__, str(self))

    def _sort_key(self):
        """Convert to a number which may be used for sorting."""
        out = self.index
        if out == "*":
            # Not really sure if there is a right answer for a wildcard index.
            # This puts it in the middle: UL1 < UL* < UR* < UR1
            out = 0.01
        if self.sub_index is not None:
            # Sub-enumerates are always considered more distal (further from the
            # center): UL1.1 < UL1.0 < UL1 < UR1 < UR1.0 < UR1.1
            out += (self.sub_index + 1) * 0.001
        if self.side == "L":
            # Mirror if left. Treat `side == "*"` as `side == "R"`.
            return -out
        return out

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

    @property
    def quadrant(self) -> str:
        """Quadrant is a standard dental enumeration derived from :attr:`side`
        and :attr:`arch_type`.

        ========  =============  ============
        ``side``  ``arch_type``  ``quadrant``
        ========  =============  ============
        ``'R'``   ``'U'``        1
        ``'L'``   ``'U'``        2
        ``'L'``   ``'L'``        3
        ``'R'``   ``'L'``        4
        ========  =============  ============

        """
        self._pre_conversion_check("quadrant", wildcards=True)
        if self.arch_type == "U":
            return 2 if self.side == "L" else 1
        else:
            return 3 if self.side == "L" else 4

    @classmethod
    def range(cls, start: PalmerLike = None, end: PalmerLike = None,
              **jaw_type) -> List['Palmer']:
        """Generate a range of consecutive Palmers.

        Args:
            start:
                Left-most tooth to include.
            end:
                Right-most tooth to include.
            jaw_type:
                Overide the jaw type of the output.
                Defaults to mirroring :attr:`start.jaw_type <Palmer.jaw_type>`.
        Returns:
            Consecutive tooth types ordered from left to right.

        ::

            >>> Palmer.range("LL2", "LR3")
            [Palmer('LL2'), Palmer('LL1'), Palmer('LR1'), Palmer('LR2'), Palmer('LR3')]

        If either **start** or **end** are unspecified then they default to the
        left-most and right-most possible tooth types

        .. code-block:: python

            >>> Palmer.range(primary=True, arch_type="U")
            [Palmer('ULE'), Palmer('ULD'), Palmer('ULC'), Palmer('ULB'), Palmer('ULA'), Palmer('URA'), Palmer('URB'), Palmer('URC'), Palmer('URD'), Palmer('URE')]

        """
        _jaw_type = jaw_type
        for x in (start, end):
            if isinstance(x, (str, Match)):
                x = cls(x)
            if isinstance(x, cls):
                _jaw_type = dict(x.jaw_type)
                break

        _jaw_type.update(jaw_type)
        jaw_type = JawType(**_jaw_type)

        if start is None or end is None:
            max_index = len(tooth_kinds(jaw_type))
        else:
            # This value never gets used.
            max_index = 0

        start = _normalise_range_bound(start, -max_index)
        end = _normalise_range_bound(end, max_index)

        return cls._range(start, end, jaw_type)

    @classmethod
    def _range(cls, start: int, end: int, jaw_type: JawType):
        """Create a range from *signed* indices. Negative sign means left."""
        end += 1
        out = []
        base = cls(**jaw_type)
        for index in range(start, min(0, end)):
            out.append(base.with_(side="L", index=-index))
        for index in range(max(start, 1), end):
            out.append(base.with_(side="R", index=index))
        return out

    def to_FDI(self) -> str:
        """Convert to `FDI International Standard
        <https://support.clearcorrect.com/hc/article_attachments/360054874894/Dental_Notation_Systems_1_-_EN.jpg>`_.

        """
        self._pre_conversion_check("FDI Index", sub_index=True, human_only=True)
        quadrant = self.quadrant

        if self.primary:
            quadrant += 4
        return str(quadrant) + str(self.index)

    def to_symbol(self, true_type: bool = False) -> str:
        """Convert to special Palmer unicode symbols which match the traditional
        handwritten syntax.

        Args:
            true_type:
                Use true dedicated Palmer glyphs from the special Palmer font.
                Otherwise just draw a corner and the index using more standard
                unicode characters.
        Returns:
            The symbol(s) as a string.

        True Palmer symbols exist only in special dedicated font libraries.

            Daniel Johnson has put together a Palmer Tooth Notation TrueType
            font called FreePalmer. It can be downloaded from
            `FreePalmer TrueType Font <http://www.markpreston.co.uk/fonts/FreePalmer.ttf>`_.
            It is covered by the GPL 3 license. This font is descended from
            FreeSans, part of the `Freefont project <https://www.gnu.org/software/freefont/>`_.

            --- This excerpt was nicked from
                `Wikipedia <https://en.Wikipedia.org/wiki/Palmer_notation>`_

        .. warning::

            Please don't waste too much time on the font - it's not worth it.

        """
        self._pre_conversion_check("formatted palmer", wildcards=True,
                                   sub_index=True)
        #TODO: There is existing notation for 'unspecified' (wildcard) components.
        #      These could be supported in the future.
        if true_type:
            return chr(0xE036 + (self.index - 1) + 8 * self.primary + 14 *
                       (2 * (self.arch_type == "L") + (self.side == "L")))

        quadrant = "⏌⎿⎾⏋"[self.quadrant - 1]

        if self.primary:
            index = digit_to_char(self.index)
        else:
            index = str(self.index)

        if self.side == "L":
            return quadrant + index
        else:
            return index + quadrant

    def to_universal(self) -> str:
        """Convert to `Universal ADA Standard
        <https://support.clearcorrect.com/hc/article_attachments/360054874894/Dental_Notation_Systems_1_-_EN.jpg>`_.
        For consistency when dealing with primary or supernumerary teeth, the
        returned value is always a string.
        """

        self._pre_conversion_check("Universal System", human_only=True,
                                   wildcards=True, sub_index=True)

        # Which muppet thought this was a sensible form of notation???
        # See the link in the class docstring for what this is all about.

        if self.primary:
            max_ = 20
        else:
            max_ = 32

        out = self.index

        if self.side == "R":
            out = (1 + max_ // 4) - out
        else:
            out = max_ // 4 + out

        if self.arch_type == "L":
            out = (max_ + 1) - out

        if self.primary:
            out = digit_to_char(out)
        else:
            out = str(out)

        return out

    def with_(self, arch_type=..., side=..., index=..., sub_index=...,
              primary=..., species=...):
        return BaseBucket.with_(**locals())


def unpack_match(match: Match) -> tuple:
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


def _normalise_range_bound(x, default):
    if x is None:
        return default
    if isinstance(x, int) and x == 0:
        return x
    x = Palmer(x)
    if x.side == "*" or x.index == "*":
        raise ValueError(f"The side and/or index of '{x}' is ambiguous.")
    return x.index * (-1 if x.side == "L" else 1)

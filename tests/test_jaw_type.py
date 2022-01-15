# -*- coding: utf-8 -*-
"""
"""

import pytest

from pangolin import JawType

pytestmark = pytest.mark.order(1)


def test_basics():
    self = JawType()

    assert self.species == "human"
    assert self.primary is False
    assert self.arch_type == "*"
    assert self["arch_type"] == "*"

    assert self.to_dict() == \
           {"species": "human", "primary": False, "arch_type": "*"}
    assert self.to_dict(skip_wildcard=True) == \
           {"species": "human", "primary": False}

    with pytest.raises(AttributeError):
        self.species = "something else"

    assert JawType(species="cat").species == "cat"
    assert JawType(primary=True).primary is True

    self = JawType("U", False, "orc")
    assert self == self
    assert self == JawType("U", False, "orc")
    assert self.with_(primary=True).primary is True
    assert self == self.with_()
    assert self.with_(primary=True) != self

    assert len(self) == 3
    assert JawType(**self) == self
    assert JawType.from_obj(self) == self


def test_jaw_type_match():
    assert JawType("*", "*", "*").match(JawType("L", False, "tree"))
    assert JawType.match({}, {"primary": True})
    assert JawType(primary=False).match(JawType("U", "*"))
    assert JawType.match(dict(arch_type="*"), dict(arch_type="L"))
    assert not JawType(primary=False).match(JawType("U", "*"), strict=True)
    assert not JawType("L", True).match(JawType("*", False, "*"))


def test_awkward_inputs():
    self = JawType("L", True, "troll")
    assert JawType(self) == self
    assert JawType(**self) == self
    assert JawType(dict(self)) == self

    with pytest.raises(ValueError):
        JawType("z")
    with pytest.raises(ValueError):
        JawType(10)
    with pytest.raises(ValueError):
        self.with_(arch_type=10)

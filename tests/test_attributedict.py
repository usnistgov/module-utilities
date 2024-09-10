from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from module_utilities import attributedict

if TYPE_CHECKING:
    from module_utilities.typing import NestedMap


@pytest.fixture
def data() -> NestedMap:
    return {
        "a": "a_val",
        "b": "b_val",
        "c": "c_val",
        "b0": {"b1": "b0b1_val", "c0": {"c1": "c0c1_val"}},
    }


@pytest.fixture
def ref_values() -> list[str]:
    return ["a_val", "b_val", "c_val", "b0b1_val", "c0c1_val"]


@pytest.fixture
def adata(data: NestedMap) -> attributedict.AttributeDict:
    return attributedict.AttributeDict(data)


def test_get_nested(data: NestedMap, ref_values: list[str]) -> None:
    assert attributedict._get_nested_values(data, join_string=None) == ref_values
    assert attributedict._get_nested_values(data) == "\n".join(ref_values)


def test_creating() -> None:
    a = attributedict.AttributeDict({"a": "1"})
    b = attributedict.AttributeDict([("a", "1")])  # type: ignore[arg-type]

    assert a == b


def test_methods(adata: attributedict.AttributeDict, data: NestedMap) -> None:
    assert adata["b0"] == data["b0"]

    # slice
    s = slice("a", "b")
    assert adata[s] == "a_val\nb_val"
    assert adata["a":"b"] == "a_val\nb_val"  # type: ignore[misc]

    assert adata[:"b"] == "a_val\nb_val"  # type: ignore[misc]

    dnum = attributedict.AttributeDict({key: str(val) for val, key in enumerate("abc")})

    assert dnum[slice("b", None)] == "1\n2"

    # integer
    assert dnum[1:] == "1\n2"

    # commas
    assert adata["a,c"] == "a_val\nc_val"

    # with missing keys
    assert adata["d"] == "{d}"

    # without missing keys
    d = attributedict.AttributeDict(data, allow_missing=False)

    with pytest.raises(KeyError):
        d["d"]

    # delete item
    del dnum["a"]
    assert dnum._entries == {"b": "1", "c": "2"}

    assert list(dnum._items()) == [("b", "1"), ("c", "2")]

    dnum._update(d="3")

    assert dnum._entries == {"b": "1", "c": "2", "d": "3"}

    # test __getattr__

    assert adata.a == "a_val"

    assert adata.b0._entries == data["b0"]

    # missing keys
    with pytest.raises(AttributeError):
        adata.thing  # noqa: B018

from __future__ import annotations

from module_utilities import attributedict
from module_utilities.typing import NestedMap
import pytest


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
    b = attributedict.AttributeDict([("a", "1")])  # type: ignore

    assert a == b


def test_methods(adata: attributedict.AttributeDict, data: NestedMap) -> None:
    assert adata["b0"] == data["b0"]

    # slice
    s = slice("a", "b")
    assert adata[s] == "\n".join(["a_val", "b_val"])
    assert adata["a":"b"] == "\n".join(["a_val", "b_val"])  # type: ignore

    assert adata[:"b"] == "\n".join(["a_val", "b_val"])  # type: ignore

    dnum = attributedict.AttributeDict({key: str(val) for val, key in enumerate("abc")})

    assert dnum[slice("b", None)] == "\n".join(["1", "2"])

    # interger
    assert dnum[1:] == "\n".join(["1", "2"])

    # commas
    assert adata["a,c"] == "\n".join(["a_val", "c_val"])

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
        adata.thing

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast, overload

from module_utilities import cached

if TYPE_CHECKING:
    from module_utilities._typing_compat import Self

R = TypeVar("R")
T = TypeVar("T", bound="Base[R]")  # type: ignore[valid-type]


class Athing(Generic[T, R]):
    def __init__(self, parent: T) -> None:
        self.parent = parent

    @overload
    def __getitem__(self, index: int) -> R: ...

    @overload
    def __getitem__(self, index: slice) -> T: ...

    def __getitem__(self, index: int | slice) -> R | T:
        if isinstance(index, int):
            return self.parent.val  # pyright: ignore[reportReturnType]

        return self.parent

    @property
    def output(self) -> R:
        return self.parent.val  # pyright: ignore[reportReturnType]

    @property
    def other(self) -> T:
        return self.parent


class Base(Generic[R]):
    def __init__(self) -> None:
        self._cache: dict[str, Any] = {}

    @property
    def val(self) -> R:
        return cast(R, 1)

    @cached.prop
    def athing(self) -> Self:
        return self

    @cached.prop
    def there(self) -> Athing[Self, R]:
        return Athing(self)

    @property
    def prop_property(self) -> R:
        return self.val

    @cached.prop
    def prop_cached(self) -> R:
        return self.val

    @property
    def prop_cached2(self) -> R:
        return self.val

    def meth(self, x: R) -> R:
        return x

    @cached.meth
    def meth_cached(self, x: R) -> R:
        return x


class Derived(Base[int]):
    @property
    def prop_property(self) -> int:
        return 1

    @cached.prop
    def prop_cached(self) -> int:  # type: ignore[override]
        return self.val

    @property
    @cached.meth  # this lie works
    def prop_cached2(self) -> int:
        return self.val

    @cached.prop
    def prop_derived(self) -> int:
        return self.prop_cached

    @cached.meth
    def meth_cached(self, x: int) -> int:
        return x

    def derived(self) -> None:
        # reveal_type(self.there.output)
        # reveal_type(self.there.other)
        # reveal_type(self.there.__getitem__(0))
        # reveal_type(self.there[:])
        pass


b: Base[str] = Base()
d = Derived()

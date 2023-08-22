from __future__ import annotations

from module_utilities import cached

from typing import Any, TypeVar, Generic, cast, overload
from typing_extensions import Self


R = TypeVar("R")
T = TypeVar("T", bound="Base[R]")  # type: ignore


class Athing(Generic[T, R]):
    def __init__(self, parent: T) -> None:
        self.parent = parent

    @overload
    def __getitem__(self, index: int) -> R:
        ...

    @overload
    def __getitem__(self, index: slice) -> T:
        ...

    def __getitem__(self, index: int | slice) -> R | T:
        if isinstance(index, int):
            return self.parent.val
        else:
            return self.parent

    @property
    def output(self) -> R:
        return self.parent.val

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

# if TYPE_CHECKING:
#     reveal_type(b.athing)
#     reveal_type(d.athing)
#     reveal_type(b.there.output)
#     reveal_type(d.there.output)
#     reveal_type(b.there.other)
#     reveal_type(d.there.other)
#     reveal_type(b.prop_cached)
#     reveal_type(d.prop_cached)
#     reveal_type(d.prop_derived)

#     reveal_type(b.there[0])
#     reveal_type(d.there[0])

#     reveal_type(b.there[:])
#     reveal_type(d.there[:])


# T = TypeVar("T", bound="Base") # type: ignore


# class Athing(Generic[T]):
#     def __init__(self, parent: T) -> None:
#         self.parent = parent

#     @property
#     def other(self) -> T:
#         return self.parent


# class Base:
#     def __init__(self) -> None:
#         self._cache: dict[str, Any] = {}


#     @cached.prop
#     def athing(self) -> Self:
#         return self

#     @cached.prop
#     def there(self) -> Athing[Self]:
#         return Athing(self)

#     @property
#     def prop_property(self) -> int:
#         return 1

#     @cached.prop
#     def prop_cached(self) -> int:
#         return 1

#     def meth(self, x: int) -> int:
#         return x

#     @cached.meth
#     def meth_cached(self, x: int) -> int:
#         return x


# class Derived(Base):

#     @property
#     def prop_property(self) -> int:
#         return 1

#     @cached.prop # type: ignore
#     def prop_cached(self) -> int:
#         return 1


#     @cached.meth
#     def meth_cached(self, x: int) -> int:
#         return x


# b = Base()
# d = Derived()

# if TYPE_CHECKING:
#     reveal_type(b.athing)
#     reveal_type(d.athing)
#     reveal_type(b.there.other)
#     reveal_type(d.there.other)

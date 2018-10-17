"""Generic Tree type."""

from abc import ABCMeta, abstractmethod
from typing import Callable, Generic, Sequence, TypeVar

T = TypeVar('T')
U = TypeVar('U')
T_co = TypeVar('T_co', covariant=True)
U_co = TypeVar('U_co', covariant=True)
V = TypeVar('V')


class Either(Generic[T, U], metaclass=ABCMeta):
    @abstractmethod
    def match(self,
              on_left: Callable[[T], V],
              on_right: Callable[[U], V]) -> V:
        ...

    def map(self, function: Callable[[U], V]) -> 'Either[T, V]':
        return self.match(Left, lambda x: Right(function(x)))


class Left(Generic[T_co, U_co], Either[T_co, U_co]):
    def __init__(self, value: T_co) -> None:
        self._value = value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Left) and self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def match(self, on_left: Callable[[T_co], V], _) -> V:
        return on_left(self._value)


class Right(Generic[T_co, U_co], Either[T_co, U_co]):
    def __init__(self, value: U_co) -> None:
        self._value = value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Right) and self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def match(self, _, on_right: Callable[[U_co], V]) -> V:
        return on_right(self._value)


class TreeF(Generic[T_co, U_co]):
    """Tree pattern functor."""

    __slots__ = (
        '_root',
        '_children',
    )

    def __init__(self, root: T_co,
                 children: Sequence[Either[T_co, U_co]]) -> None:
        self._root = root
        self._children = children

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, TreeF)
                and self._root == other._root
                and self._children == other._children)

    def __hash__(self) -> int:
        return hash((self._root, self._children))

    def __repr__(self):
        return '{}({}, {})'.format(
            Tree.__name__,
            repr(self._root),
            repr(self._children),
        )


class Tree(Generic[T_co]):
    """Tree containing a single value and many children at each node."""

    __slots__ = (
        '_value',
    )

    def __init__(self, value: TreeF[T_co, 'Tree[T_co]']) -> None:
        self._value = value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Tree) and self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__,
            repr(self._value),
        )

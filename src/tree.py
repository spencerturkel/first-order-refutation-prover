"""Generic Tree type."""

from typing import Generic, Tuple, TypeVar, Union

T_co = TypeVar('T_co', covariant=True)


class Tree(Generic[T_co]):
    """Tree containing a single value and many children at each node."""

    __slots__ = (
        '_value',
        '_children',
    )

    def __init__(self, value: T_co,
                 children: Tuple[Union[T_co, 'Tree[T_co]'], ...]) -> None:
        self._value = value
        self._children = children

    def __repr__(self):
        return '{}({}, {})'.format(
            Tree.__name__,
            repr(self._value),
            repr(self._children),
        )

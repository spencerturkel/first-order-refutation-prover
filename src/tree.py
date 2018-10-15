"""Generic Tree type."""

from typing import Generic, Tuple, TypeVar, Union

T_co = TypeVar('T_co', covariant=True)
U = TypeVar('U')


class Tree(Generic[T_co]):
    __slots__ = '_data',

    def __init__(self, data: Tuple[Union[T_co, 'Tree'], ...]) -> None:
        self._data = data

    def __iter__(self):
        return iter(self._data)

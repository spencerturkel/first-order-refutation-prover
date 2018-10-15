"""Generic Tree type."""

from typing import Generic, Tuple, TypeVar, Union

T_co = TypeVar('T_co', covariant=True)
U = TypeVar('U')


class Tree(Generic[T_co]):
    """An iterable of values and sub-trees."""

    __slots__ = '_data',

    def __init__(self, data: Tuple[Union[T_co, 'Tree[T_co]'], ...]) -> None:
        self._data = data

    def __iter__(self):
        return iter(self._data)

    def __repr__(self):
        return 'Tree({})'.format(repr(self._data))


class SymbolTree(Tree[str]):
    """Tree of strings.

    MyPy cannot currently infer the instantiated type of Tree in expressions
    created nested Trees, and instead types those expressions as Tree[object].
    The primary use-case of Trees in this project is to represent the symbol
    trees in formulas, and this class allows us to create those with minimal
    boilerplate and minimal fiddling with the type-checker.

    >>> SymbolTree('a', SymbolTree('p', 'x'), 'b')
    Tree(('a', Tree(('p', 'x')), 'b'))
    """

    def __init__(self, *data: Union[str, 'SymbolTree']) -> None:
        super().__init__(data)

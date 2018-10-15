"""Conjunctive Normal Form formula typing."""

from typing import FrozenSet, Union

from .tree import Tree


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


class CnfFormula:
    """Conjunctive Normal Form formula."""

    __slots__ = (
        'formula',
        'variables',
    )

    def __init__(self,
                 formula: FrozenSet[FrozenSet[Tree[str]]],
                 variables: FrozenSet[str],
                 ) -> None:
        self.formula = formula
        self.variables = variables

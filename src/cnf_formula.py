"""Conjunctive Normal Form formula typing."""

from typing import FrozenSet, Tuple, Union

from .tokens import NotToken
from .tree import Tree

Term = Union[Tuple[NotToken, Tree[str]], Tree[str]]
Clause = FrozenSet[Term]


class CnfFormula:
    """Conjunctive Normal Form formula."""

    __slots__ = (
        'formula',
        'variables',
    )

    def __init__(self,
                 formula: FrozenSet[Clause],
                 variables: FrozenSet[str],
                 ) -> None:
        self.formula = formula
        self.variables = variables


class SymbolTree(Tree[str]):
    """Tree of symbols.

    MyPy cannot currently infer the instantiated type of Tree in expressions
    creating nested Trees, and instead types those expressions as Tree[object].
    The primary use-case of Trees in this project is to represent the symbol
    trees in formulas, and this class allows us to create those with minimal
    boilerplate and minimal fiddling with the type-checker.

    >>> SymbolTree('a', SymbolTree('p', 'x'), 'b')
    Tree('a', (Tree('p', ('x',)), 'b'))
    """

    def __init__(
        self, value: str, *children: Union[str, 'SymbolTree']
    ) -> None:
        super().__init__(value, children)

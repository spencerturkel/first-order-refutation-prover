"""Conjunctive Normal Form formula typing."""

from typing import FrozenSet, Tuple, Union

from .tokens import NotToken
from .tree import Tree

Literal = Union[Tuple[NotToken, Tree[str]], Tree[str]]
Clause = FrozenSet[Literal]


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

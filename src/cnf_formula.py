"""Conjunctive Normal Form formula typing."""

from typing import FrozenSet

from .tree import Tree


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

"""Conjunctive Normal Form formula typing."""

from typing import FrozenSet

from .tree import Tree


class Literal:
    __slots__ = (
        'is_positive',
        'term',
    )

    def __init__(self, is_positive: bool, term: Tree[str]) -> None:
        self.is_positive = is_positive
        self.term = term

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, Literal)
                and self.is_positive == other.is_positive
                and self.term == other.term)

    def __hash__(self) -> int:
        return hash((self.is_positive, self.term))

    def __repr__(self) -> str:
        return '{}({}, {})'.format(
            self.__class__.__name__,
            self.is_positive,
            self.term,
        )


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

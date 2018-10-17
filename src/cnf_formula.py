"""Conjunctive Normal Form formula typing."""

from typing import FrozenSet, Tuple, Union

from .ast import Term
from .tokens import NotToken

Literal = Union[Tuple[NotToken, Term], Term]
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

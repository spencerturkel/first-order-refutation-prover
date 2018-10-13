"""Abstract Syntax Tree typing.

This module defines the type of the abstract syntax tree.
The AST is expressed as the Formula and Object types.

The Formula type is a Union of Tuple types and the Contradiction token.

When analyzing a formula, check for a contradiction.
If the formula is not a contradiction, then it is a tuple.
The first field of the tuple will uniquely identify the kind of formula.

Since mypy cannot currently express recursive types, there is a hack
to preserve type-safety for one level deep of each type.
For example, we can safely inspect objects of formulas, or vice-versa.
However, deeper inspection replaces the recursive types with Any,
effectively removing typechecking for deeper inspection.
If deeper inspection is required, more types can be added.
There must be 2^n types for n layers of safety.
"""

from enum import Enum, unique
from typing import Any, Optional, Tuple, Union


@unique
class QuantifierToken(Enum):
    FORALL = 0
    EXISTS = 1


@unique
class BinaryToken(Enum):
    AND = 0
    OR = 1
    IMPLIES = 2


@unique
class NotToken(Enum):
    NOT = 0


@unique
class ContradictionToken(Enum):
    CONTR = 0


ObjectAny = Union[str, Any]
Object = Union[str, 'FormulaObjectAny']

FormulaAny = Union[
    Tuple[QuantifierToken, str, Any],
    Tuple[BinaryToken, Any, Any],
    Tuple[NotToken, Any],
    ContradictionToken,
    Tuple[str, Tuple[ObjectAny, ...]]
]

FormulaAnyObject = Union[
    Tuple[QuantifierToken, str, Any],
    Tuple[BinaryToken, Any, Any],
    Tuple[NotToken, Any],
    ContradictionToken,
    Tuple[str, Tuple[Object, ...]]
]

FormulaObjectAny = Union[
    Tuple[QuantifierToken, str, FormulaAny],
    Tuple[BinaryToken, FormulaAny, FormulaAny],
    Tuple[NotToken, FormulaAny],
    ContradictionToken,
    Tuple[str, Tuple[ObjectAny, ...]]
]

Formula = Union[
    Tuple[QuantifierToken, str, FormulaAny],
    Tuple[BinaryToken, FormulaAny, FormulaAny],
    Tuple[NotToken, FormulaAny],
    ContradictionToken,
    Tuple[str, Tuple[Object, ...]]
]

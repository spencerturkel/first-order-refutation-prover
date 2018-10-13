"""Abstract Syntax Tree typing.

This module defines the type of the abstract syntax tree.
The AST is expressed as the Formula and Object types.

The Formula type is a Union of Tuple types and the Contradiction token.

When analyzing a formula, check for a contradiction.
If the formula is not a contradiction, then it is a tuple.
The first field of the tuple is an identifying token.

Since mypy cannot currently express recursive types, there is a hack
to preserve type-safety for one level deep of each type.
For example, we can safely inspect objects of formulas, or vice-versa.
However, deeper inspection replaces the recursive types with Any,
effectively removing typechecking for deeper inspection.
If deeper inspection is required, more types can be added.
There must be 2^n types for n layers of safety.
"""

from typing import Any, Tuple, Union

from .tokens import BinaryToken, ContradictionToken, NotToken, QuantifierToken

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

"""Abstract Syntax Tree typing.

This module defines the type of the abstract syntax tree.
The AST is expressed as the FormulaF.

The FormulaF type is a Union of Tuple types and the Contradiction token.

When analyzing a FormulaF, check for a contradiction.
If the FormulaF is not a contradiction, then it is a tuple.
The first field of the tuple is an identifying token.

Since mypy cannot currently express recursive types, there is a hack
to preserve type-safety at each level of recursion.

FormulaF types the recursive formula fields as Any.
FormulaF[FormulaF] preserves type-safety through one layer of recursion.
FormulaF[FormulaF[FormulaF]] preserves two layers of type-safety.
And so on.

There are some pre-defined types aliasing these layers of recursion.
Formula0 = FormulaF
Formula3 = FormulaF[Formula2]
And so on.
"""

from typing import Tuple, TypeVar, Union

from .tokens import BinaryToken, ContradictionToken, NotToken, QuantifierToken

T_co = TypeVar('T_co', covariant=True)

FormulaF = Union[
    Tuple[QuantifierToken, str, T_co],
    Tuple[BinaryToken, T_co, T_co],
    Tuple[NotToken, T_co],
    ContradictionToken,
    Tuple[str, Tuple[Union[str, T_co], ...]],
]

Formula0 = FormulaF
Formula1 = FormulaF[Formula0]
Formula2 = FormulaF[Formula1]
Formula3 = FormulaF[Formula2]
Formula4 = FormulaF[Formula3]
Formula = Formula4

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

from typing import Callable, Sequence, Tuple, TypeVar, Union, cast

from .tokens import BinaryToken, ContradictionToken, NotToken, QuantifierToken

T = TypeVar('T')


class FormulaC:
    __slots__ = 'tag', 'first_arg', 'second_arg'

    # TODO: improve typing
    def __init__(self, *args) -> None:
        count_args = len(args)
        if count_args == 1:
            self.tag = cast(Union[ContradictionToken, NotToken, None,
                                  BinaryToken, QuantifierToken],
                            ContradictionToken.CONTR)
        elif count_args == 2:
            if args[0] == NotToken.NOT:
                self.tag = NotToken.NOT
                self.first_arg = args[1]
            else:
                # predicate
                self.tag = None
                self.first_arg, self.second_arg = args
        else:
            # quantifier or binary operation
            self.tag = args[0]
            self.first_arg = args[1]
            self.second_arg = args[2]

    def visit(
        self,
        on_quantifier: Callable[[QuantifierToken, str, 'FormulaC'], T],
        on_binary: Callable[[BinaryToken, 'FormulaC', 'FormulaC'], T],
        on_negation: Callable[['FormulaC'], T],
        on_contradiction: Callable[[], T],
        on_predicate: Callable[[str, Sequence[Union[str, 'FormulaC']]], T],
    ) -> T:
        if isinstance(self.tag, QuantifierToken):
            return on_quantifier(self.tag, self.first_arg, self.second_arg)
        if isinstance(self.tag, BinaryToken):
            return on_binary(self.tag, self.first_arg, self.second_arg)
        if self.tag == NotToken.NOT:
            return on_negation(self.first_arg)
        if self.tag == ContradictionToken.CONTR:
            return on_contradiction()
        return on_predicate(self.first_arg, self.second_arg)


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

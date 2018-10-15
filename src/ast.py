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

from abc import ABCMeta, abstractmethod
from typing import Generic, Sequence, Tuple, TypeVar, Union, cast

from .tokens import BinaryToken, ContradictionToken, NotToken, QuantifierToken

T = TypeVar('T')


class FormulaVisitor(Generic[T], metaclass=ABCMeta):

    @abstractmethod
    def visit_quantifier(self,
                         token: QuantifierToken,
                         variable: str,
                         sub_formula: 'FormulaC') -> T:
        ...

    @abstractmethod
    def visit_binary(self,
                     token: BinaryToken,
                     variable: str,
                     sub_formula: 'FormulaC') -> T:
        ...

    @abstractmethod
    def visit_negation(self,
                       sub_formula: 'FormulaC') -> T:
        ...

    @abstractmethod
    def visit_contradiction(self) -> T:
        ...

    @abstractmethod
    def visit_predicate(self,
                        predicate: str,
                        args: Sequence[Union[str, 'FormulaC']]) -> T:
        ...


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
        visitor: FormulaVisitor[T]
    ) -> T:
        if isinstance(self.tag, QuantifierToken):
            return visitor.visit_quantifier(self.tag,
                                            self.first_arg,
                                            self.second_arg)
        if isinstance(self.tag, BinaryToken):
            return visitor.visit_binary(self.tag,
                                        self.first_arg,
                                        self.second_arg)
        if self.tag == NotToken.NOT:
            return visitor.visit_negation(self.first_arg)
        if self.tag == ContradictionToken.CONTR:
            return visitor.visit_contradiction()
        return visitor.visit_predicate(self.first_arg, self.second_arg)


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

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
from typing import Callable, Generic, Sequence, TypeVar, Union, cast

from .tokens import BinaryToken, ContradictionToken, NotToken, QuantifierToken

T = TypeVar('T')
U = TypeVar('U')


class FormulaFVisitor(Generic[T, U], metaclass=ABCMeta):

    @abstractmethod
    def visit_quantifier(self,
                         token: QuantifierToken,
                         variable: str,
                         sub_formula: T) -> U:
        ...

    @abstractmethod
    def visit_binary(self,
                     token: BinaryToken,
                     variable: str,
                     sub_formula: T) -> U:
        ...

    @abstractmethod
    def visit_negation(self,
                       sub_formula: T) -> U:
        ...

    @abstractmethod
    def visit_contradiction(self) -> U:
        ...

    @abstractmethod
    def visit_predicate(self,
                        predicate: str,
                        args: Sequence[Union[str, T]]) -> U:
        ...


class FormulaF(Generic[T]):
    __slots__ = '_tag', '_first_arg', '_second_arg'

    # TODO: improve typing
    def __init__(self, *args) -> None:
        count_args = len(args)
        if count_args == 1:
            self._tag = cast(Union[ContradictionToken, NotToken, None,
                                   BinaryToken, QuantifierToken],
                             ContradictionToken.CONTR)
        elif count_args == 2:
            if args[0] == NotToken.NOT:
                self._tag = NotToken.NOT
                self._first_arg = args[1]
            else:
                # predicate
                self._tag = None
                self._first_arg, self._second_arg = args
        else:
            # quantifier or binary operation
            self._tag = args[0]
            self._first_arg = args[1]
            self._second_arg = args[2]

    def map(self, func: Callable[[T], U]) -> 'FormulaF[U]':
        pass  # TODO:

    def visit(self, visitor: FormulaFVisitor[T, U]) -> U:
        if isinstance(self._tag, QuantifierToken):
            return visitor.visit_quantifier(self._tag,
                                            self._first_arg,
                                            self._second_arg)
        if isinstance(self._tag, BinaryToken):
            return visitor.visit_binary(self._tag,
                                        self._first_arg,
                                        self._second_arg)
        if self._tag == NotToken.NOT:
            return visitor.visit_negation(self._first_arg)
        if self._tag == ContradictionToken.CONTR:
            return visitor.visit_contradiction()
        return visitor.visit_predicate(self._first_arg, self._second_arg)


class Formula(FormulaF['Formula']):
    def fold(self, visitor: FormulaFVisitor[T, U]) -> U:
        pass  # TODO:

    @staticmethod
    def unfold(seed: T, func: Callable[[T], FormulaF[T]]) -> 'Formula':
        pass  # TODO:

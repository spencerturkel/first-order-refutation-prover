"""Abstract Syntax Tree typing.

This module defines the type of the abstract syntax tree.
The AST is expressed as the Formula type.
"""

from abc import ABCMeta, abstractmethod
from typing import (Callable, Generic, Sequence, Type, TypeVar, Union, cast,
                    overload)

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
                     first_arg: T,
                     second_arg: T) -> U:
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
    """Formula with sub-formulas of an arbitrary type."""

    __slots__ = '_tag', '_first_arg', '_second_arg'

    @overload
    def __init__(self, contradiction: ContradictionToken) -> None:
        pass

    @overload
    def __init__(self, negation: NotToken, arg: T) -> None:
        pass

    @overload
    def __init__(self,
                 first_arg: str,
                 second_arg: Sequence[Union[str, T]]) -> None:
        pass

    @overload
    def __init__(self, token: BinaryToken,
                 first_arg: T, second_arg: T) -> None:
        pass

    @overload
    def __init__(self, token: QuantifierToken,
                 first_arg: str, second_arg: T) -> None:
        pass

    def __init__(self,
                 token,
                 first_arg=None,
                 second_arg=None):
        if isinstance(token, ContradictionToken):
            self._tag = token
            self._first_arg = None
            self._second_arg = None
        elif isinstance(token, NotToken):
            self._tag = token
            self._first_arg = first_arg
            self._second_arg = None
        elif isinstance(token, (BinaryToken, QuantifierToken)):
            self._tag = token
            self._first_arg = first_arg
            self._second_arg = second_arg
        else:
            self._tag = token
            self._first_arg = first_arg
            self._second_arg = None

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, FormulaF)
                and self._tag == other._tag
                and self._first_arg == other._first_arg
                and self._second_arg == other._second_arg)

    def visit(self, visitor: FormulaFVisitor[T, U]) -> U:
        """Apply a function matching the type of this formula."""
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
        return visitor.visit_predicate(self._tag, self._first_arg)

    class _MapVisitor(FormulaFVisitor[T, 'FormulaF[U]']):
        def __init__(self, function: Callable[[T], U]) -> None:
            self.function = function

        def visit_quantifier(self,
                             token: QuantifierToken,
                             var: str,
                             predicate: T) -> 'FormulaF[U]':
            return FormulaF(token, var, self.function(predicate))

        def visit_binary(self,
                         token: BinaryToken,
                         first_arg: T,
                         second_arg: T) -> 'FormulaF[U]':
            return FormulaF(token,
                            self.function(first_arg),
                            self.function(second_arg))

        def visit_negation(self, arg: T) -> 'FormulaF[U]':
            return FormulaF(NotToken.NOT, self.function(arg))

        def visit_contradiction(self) -> 'FormulaF[U]':
            return FormulaF(ContradictionToken.CONTR)

        def visit_predicate(self,
                            predicate: str,
                            args: Sequence[Union[str, T]]) -> 'FormulaF[U]':
            return FormulaF(predicate, tuple(
                cast(Union[str, U],
                     arg if isinstance(arg, str) else self.function(arg))
                for arg in args
            ))

    def map(self, function: Callable[[T], U]) -> 'FormulaF[U]':
        """Apply a function to all sub-formulas."""
        return self.visit(self._MapVisitor(function))


class FormulaVisitor(Generic[T], FormulaFVisitor[T, T]):
    pass


class Formula:
    """Formula with recursive sub-formulas."""

    def __init__(self, formula: FormulaF['Formula']) -> None:
        self.formula = formula

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Formula) and self.formula == other.formula

    def fold(self, visitor: FormulaVisitor[T]) -> T:
        """Consume the formula tree bottom-up."""
        return self.formula.map(lambda x: x.fold(visitor)).visit(visitor)

    @classmethod
    def unfold(cls: Type['Formula'], seed: T,
               function: Callable[[T], FormulaF[T]]) -> 'Formula':
        """Generate the formula tree top-down."""
        return Formula(function(seed).map(lambda x: cls.unfold(x, function)))

    @overload
    @staticmethod
    def of(contradiction: ContradictionToken) -> 'Formula':
        pass

    @overload
    @staticmethod
    def of(negation: NotToken, arg: 'Formula') -> 'Formula':
        pass

    @overload
    @staticmethod
    def of(first_arg: str, second_arg: Sequence[Union[str, 'Formula']]) -> 'Formula':
        pass

    @overload
    @staticmethod
    def of(token: BinaryToken,
           first_arg: 'Formula', second_arg: 'Formula') -> 'Formula':
        pass

    @overload
    @staticmethod
    def of(token: QuantifierToken,
           first_arg: str, second_arg: 'Formula') -> 'Formula':
        pass

    @staticmethod
    def of(token, *rest):
        return Formula(FormulaF(token, *rest))

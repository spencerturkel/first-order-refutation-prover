"""Abstract Syntax Tree typing.

This module defines the type of the abstract syntax tree.
The AST is expressed as the Formula type.
"""

from abc import ABCMeta, abstractmethod
from typing import Callable, Generic, Sequence, Type, TypeVar, Union, cast

from .tokens import BinaryToken, QuantifierToken
from .tree import Either, Left, Right, Tree, TreeF

T = TypeVar('T')
U = TypeVar('U')


class Term(Tree[str]):
    """Tree of strings.

    MyPy cannot currently infer the instantiated type of Tree in expressions
    creating nested Trees, and instead types those expressions as Tree[object].
    The primary use-case of Trees in this project is to represent the symbol
    trees in formulas. This class allows us to easily create and view those.
    """

    __slots__ = ()

    def __init__(self, root: str, *children: Union[str, Tree[str]]) -> None:
        super().__init__(TreeF(
            root,
            tuple(cast(Either[str, Tree[str]],
                       Left(child) if isinstance(child, str) else Right(child))
                  for child in children)
        ))

    def __repr__(self) -> str:
        return '{}({}, {})'.format(
            self.__class__.__name__,
            self._value._root,
            ', '.join(child.match(repr, repr)
                      for child in self._value._children),
        )


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
    def visit_predicate(self, predicate: str, terms: Sequence[Tree[str]]) -> U:
        ...


class FormulaF(Generic[T], metaclass=ABCMeta):
    """Formula with sub-formulas of an arbitrary type."""

    @abstractmethod
    def visit(self, visitor: FormulaFVisitor[T, U]) -> U:
        ...

    class _MapVisitor(FormulaFVisitor[T, 'FormulaF[U]']):
        def __init__(self, function: Callable[[T], U]) -> None:
            self.function = function

        def visit_quantifier(self,
                             token: QuantifierToken,
                             var: str,
                             predicate: T) -> 'FormulaF[U]':
            return QuantifiedFormulaF(token, var, self.function(predicate))

        def visit_binary(self,
                         token: BinaryToken,
                         first_arg: T,
                         second_arg: T) -> 'FormulaF[U]':
            return BinaryFormulaF(token,
                                  self.function(first_arg),
                                  self.function(second_arg))

        def visit_negation(self, arg: T) -> 'FormulaF[U]':
            return NegatedFormulaF(self.function(arg))

        def visit_contradiction(self) -> 'FormulaF[U]':
            return ContradictionFormulaF()

        def visit_predicate(self, predicate: str,
                            terms: Sequence[Tree[str]]) -> 'FormulaF[U]':
            return PredicateFormulaF(predicate, terms)

    def map(self, function: Callable[[T], U]) -> 'FormulaF[U]':
        """Apply a function to all sub-formulas."""
        return self.visit(self._MapVisitor(function))


class QuantifiedFormulaF(Generic[T], FormulaF[T]):
    __slots__ = (
        '_token',
        '_variable',
        '_formula',
    )

    def __init__(self, token: QuantifierToken,
                 variable: str, formula: T) -> None:
        self._token = token
        self._variable = variable
        self._formula = formula

    def visit(self, visitor: FormulaFVisitor[T, U]) -> U:
        return visitor.visit_quantifier(
            self._token, self._variable, self._formula)


class BinaryFormulaF(Generic[T], FormulaF[T]):
    __slots__ = (
        '_token',
        '_first_arg',
        '_second_arg',
    )

    def __init__(self, token: BinaryToken,
                 first_arg: T, second_arg: T) -> None:
        self._token = token
        self._first_arg = first_arg
        self._second_arg = second_arg

    def visit(self, visitor: FormulaFVisitor[T, U]) -> U:
        return visitor.visit_binary(
            self._token, self._first_arg, self._second_arg)


class ContradictionFormulaF(Generic[T], FormulaF[T]):
    def visit(self, visitor: FormulaFVisitor[T, U]) -> U:
        return visitor.visit_contradiction()


class NegatedFormulaF(Generic[T], FormulaF[T]):
    __slots__ = (
        '_formula',
    )

    def __init__(self, formula: T) -> None:
        self._formula = formula

    def visit(self, visitor: FormulaFVisitor[T, U]) -> U:
        return visitor.visit_negation(self._formula)


class PredicateFormulaF(Generic[T], FormulaF[T]):
    __slots__ = (
        '_predicate',
        '_terms',
    )

    def __init__(self, predicate, terms: Sequence[Tree[str]]) -> None:
        self._predicate = predicate
        self._terms = terms

    def visit(self, visitor: FormulaFVisitor[T, U]) -> U:
        return visitor.visit_predicate(self._predicate, self._terms)


class FormulaVisitor(Generic[T], FormulaFVisitor['Formula', T]):
    pass


class FormulaFoldVisitor(Generic[T], FormulaFVisitor[T, T]):
    pass


class Formula:
    """Formula with recursive sub-formulas."""

    def __init__(self, formula: FormulaF['Formula']) -> None:
        self.formula = formula

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Formula) and self.formula == other.formula

    def fold(self, visitor: FormulaFoldVisitor[T]) -> T:
        """Consume the formula tree bottom-up."""
        return self.formula.map(lambda x: x.fold(visitor)).visit(visitor)

    def visit(self, visitor: FormulaVisitor[T]) -> T:
        """Consume the formula tree bottom-up."""
        return self.formula.visit(visitor)

    @classmethod
    def unfold(cls: Type['Formula'], seed: T,
               function: Callable[[T], FormulaF[T]]) -> 'Formula':
        """Generate the formula tree top-down."""
        return Formula(function(seed).map(lambda x: cls.unfold(x, function)))

    @classmethod
    def quantify(cls: Type['Formula'],
                 token: QuantifierToken,
                 variable: str,
                 formula: 'Formula') -> 'Formula':
        return cls(QuantifiedFormulaF(token, variable, formula))

    @classmethod
    def binary(cls: Type['Formula'],
               token: BinaryToken,
               first_arg: 'Formula',
               second_arg: 'Formula') -> 'Formula':
        return Formula(BinaryFormulaF(token, first_arg, second_arg))

    @classmethod
    def contradiction(cls: Type['Formula']) -> 'Formula':
        return cls(ContradictionFormulaF())

    @classmethod
    def negate(cls: Type['Formula'], formula: 'Formula') -> 'Formula':
        return cls(NegatedFormulaF(formula))

    @classmethod
    def predicate(cls: Type['Formula'], predicate: str,
                  *terms: Tree[str]) -> 'Formula':
        return cls(PredicateFormulaF(predicate, terms))

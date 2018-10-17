from typing import Callable, List, TypeVar

import pytest

from .ast import (BinaryFormulaF, ContradictionFormulaF, Formula, FormulaF,
                  FormulaFoldVisitor, FormulaVisitor, NegatedFormulaF,
                  PredicateFormulaF, QuantifiedFormulaF, Term)
from .tokens import BinaryToken, QuantifierToken

T = TypeVar('T')
U = TypeVar('U')


def test_formulas() -> List[Formula]:
    return [
        Formula.binary(BinaryToken.IMPLIES,
                       Formula.contradiction(),
                       Formula.predicate('a')),
        Formula.binary(BinaryToken.AND,
                       Formula.negate(Formula.predicate('a')),
                       Formula.predicate('a')),
        Formula.binary(BinaryToken.OR,
                       Formula.predicate('12'),
                       Formula.predicate('a1')),
        Formula.quantify(QuantifierToken.FORALL, 'x',
                         Formula.predicate('p', Term('x'))),
        Formula.quantify(QuantifierToken.EXISTS, 'x',
                         Formula.predicate('p', Term('f', 'x'))),
    ]


class TermCountingVisitor(FormulaFoldVisitor[int]):
    def visit_quantifier(self, _, _1, n):
        return n

    def visit_binary(self, _, n, m):
        return n + m

    def visit_negation(self, n):
        return n

    def visit_contradiction(self):
        return 0

    def visit_predicate(self, _, terms):
        return len(terms)


class VariableCollectingVisitor(FormulaFoldVisitor[List[str]]):
    def visit_quantifier(self, _, var, others: List[str]):
        others.insert(0, var)
        return others

    def visit_binary(self, _, left, right):
        left.extend(right)
        return left

    def visit_negation(self, inner):
        return inner

    def visit_contradiction(self):
        return []

    def visit_predicate(self, _1, _2):
        return []


@pytest.mark.parametrize('formula, visitor, result', [
    (Formula.binary(
        BinaryToken.IMPLIES,
        Formula.contradiction(),
        Formula.predicate('p', Term('x'), Term('y')),
    ), TermCountingVisitor(), 2),
    (Formula.binary(
        BinaryToken.AND,
        Formula.predicate('p', Term('x'), Term('y')),
        Formula.predicate('p', Term('q', Term('x', 'y')), Term('z')),
    ), TermCountingVisitor(), 4),
    (Formula.quantify(
        QuantifierToken.FORALL,
        'x',
        Formula.quantify(
            QuantifierToken.EXISTS,
            'y',
            Formula.predicate('p', Term('q', Term('x', 'y')), Term('z'))),
    ), VariableCollectingVisitor(), ['x', 'y']),
])
def test_fold(formula: Formula, visitor: FormulaFoldVisitor[T], result: T):
    assert formula.fold(visitor) == result


def test_unfold():
    def generator(num):
        if num == 2:
            return BinaryFormulaF(BinaryToken.IMPLIES, 1, 1)
        if num == 1:
            return QuantifiedFormulaF(QuantifierToken.FORALL, 'x', 0)
        return ContradictionFormulaF()

    assert Formula.unfold(2, generator) == Formula.binary(
        BinaryToken.IMPLIES,
        Formula.quantify(QuantifierToken.FORALL, 'x',
                         Formula.contradiction()),
        Formula.quantify(QuantifierToken.FORALL, 'x',
                         Formula.contradiction()),
    )


@pytest.mark.parametrize('formula, mapping, result', [
    (BinaryFormulaF(BinaryToken.IMPLIES, 1, 2), str,
        BinaryFormulaF(BinaryToken.IMPLIES, '1', '2')),
    (QuantifiedFormulaF(QuantifierToken.FORALL, 'x', 5,), lambda x: x + 3,
     QuantifiedFormulaF(QuantifierToken.FORALL, 'x', 8)),
    (NegatedFormulaF(3), lambda x: str(x - 1),
        NegatedFormulaF('2')),
    (PredicateFormulaF('p', [Term('f', 'y', 'z')]), lambda x: x - 1,
        PredicateFormulaF('p', [Term('f', 'y', 'z')])),
    (ContradictionFormulaF(), lambda x: x - 1,
        ContradictionFormulaF()),
])
def test_map(formula: FormulaF[T], mapping: Callable[[T], U],
             result: FormulaF[U]):
    assert formula.map(mapping) == result


class ContradictionFindingVisitor(FormulaVisitor[bool]):
    def visit_quantifier(self, _, _1, formula: Formula) -> bool:
        return formula.visit(self)

    def visit_binary(self, _, left: Formula, right: Formula) -> bool:
        return left.visit(self) or right.visit(self)

    def visit_negation(self, formula: Formula) -> bool:
        return formula.visit(self)

    def visit_contradiction(self) -> bool:
        return True

    def visit_predicate(self, _1, _2) -> bool:
        return False


@pytest.mark.parametrize(
    'formula, visitor, result', [
        (Formula.binary(
            BinaryToken.IMPLIES,
            Formula.contradiction(),
            Formula.predicate('p', Term('x', 'y')),
        ), ContradictionFindingVisitor(), True),
        (Formula.quantify(
            QuantifierToken.FORALL,
            'x',
            Formula.predicate('p', Term('f', 'x', 'y'), Term('z')),
        ), ContradictionFindingVisitor(), False),
    ]
)
def test_visit(formula: Formula, visitor: FormulaVisitor[T], result: T):
    assert formula.visit(visitor) == result

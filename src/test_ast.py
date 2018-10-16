from typing import Callable, List, TypeVar

import pytest

from .ast import Formula, FormulaF, FormulaVisitor
from .tokens import BinaryToken, ContradictionToken, NotToken, QuantifierToken

T = TypeVar('T')
U = TypeVar('U')


def test_formulas() -> List[Formula]:
    return [
        Formula.of(BinaryToken.IMPLIES,
                   Formula.of(ContradictionToken.CONTR),
                   Formula.of('a', ())),
        Formula.of(BinaryToken.AND, Formula.of(
            NotToken.NOT, Formula.of('a', ())), Formula.of('a', ())),
        Formula.of(BinaryToken.OR, Formula.of('12', ()), Formula.of('a1', ())),
        Formula.of(QuantifierToken.FORALL, 'x', Formula.of('p', ('x',))),
        Formula.of(QuantifierToken.EXISTS, 'x', Formula.of('p', ('x',))),
    ]


class DepthCountingVisitor(FormulaVisitor[int]):
    def visit_quantifier(self, _, _1, n):
        return 1 + n

    def visit_binary(self, _, n, m):
        return 1 + max(n, m)

    def visit_negation(self, n):
        return 1 + n

    def visit_contradiction(self):
        return 1

    def visit_predicate(self, _, args):
        return 1 + max(
            map(lambda x: x if isinstance(x, int) else 1, args),
            default=0)


class SymbolCollectingVisitor(FormulaVisitor[List[str]]):
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

    def visit_predicate(self, predicate, args):
        result = [predicate]
        for item in args:
            if isinstance(item, str):
                result.append(item)
            else:
                result.extend(item)
        return result


@pytest.mark.parametrize('formula, visitor, result', [
    (Formula.of(
        BinaryToken.IMPLIES,
        Formula.of(ContradictionToken.CONTR),
        Formula.of('p', ('x', 'y')),
    ), DepthCountingVisitor(), 3),
    (Formula.of(
        QuantifierToken.FORALL,
        'x',
        Formula.of('p', (Formula.of('q', ('x', 'y')), 'z')),
    ), DepthCountingVisitor(), 4),
    (Formula.of(
        QuantifierToken.FORALL,
        'x',
        Formula.of('p', (Formula.of('q', ('x', 'y')), 'z')),
    ), SymbolCollectingVisitor(), ['x', 'p', 'q', 'x', 'y', 'z']),
])
def test_fold(formula: Formula, visitor: FormulaVisitor[T], result: T):
    assert formula.fold(visitor) == result


def test_unfold():
    def generator(num):
        if num == 2:
            return FormulaF(BinaryToken.IMPLIES, 1, 1)
        if num == 1:
            return FormulaF(QuantifierToken.FORALL, 'x', 0)
        return FormulaF(ContradictionToken.CONTR)
    assert Formula.unfold(2, generator) == Formula.of(
        BinaryToken.IMPLIES,
        Formula.of(QuantifierToken.FORALL, 'x',
                   Formula.of(ContradictionToken.CONTR)),
        Formula.of(QuantifierToken.FORALL, 'x',
                   Formula.of(ContradictionToken.CONTR)),
    )


@pytest.mark.parametrize('formula, mapping, result', [
    (FormulaF(BinaryToken.IMPLIES, 1, 2), str,
        FormulaF(BinaryToken.IMPLIES, '1', '2')),
    (FormulaF(QuantifierToken.FORALL, 'x', 5,), lambda x: x + 3,
     FormulaF(QuantifierToken.FORALL, 'x', 8)),
    (FormulaF(NotToken.NOT, 3), lambda x: str(x - 1),
        FormulaF(NotToken.NOT, '2')),
    (FormulaF('p', ('x', 3, 2)), lambda x: x - 1,
        FormulaF('p', ('x', 2, 1))),
    (FormulaF(ContradictionToken.CONTR), lambda x: x - 1,
        FormulaF(ContradictionToken.CONTR)),
])
def test_map(formula: FormulaF[T], mapping: Callable[[T], U],
             result: FormulaF[U]):
    assert formula.map(mapping) == result

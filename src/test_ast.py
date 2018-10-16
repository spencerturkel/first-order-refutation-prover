from typing import List

import pytest

from .ast import Formula, FormulaVisitor
from .tokens import BinaryToken, ContradictionToken, NotToken, QuantifierToken


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
def test_fold(formula, visitor, result):
    assert formula.fold(visitor) == result

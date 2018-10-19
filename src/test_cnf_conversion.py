import pytest

from .ast import Formula
from .cnf_conversion import normalize_negations
from .tokens import BinaryToken, QuantifierToken


@pytest.mark.parametrize('formula, normalized', [
    (
        Formula.binary(
            BinaryToken.IMPLIES,
            Formula.predicate('p'),
            Formula.predicate('q')),
        Formula.binary(
            BinaryToken.OR,
            Formula.negate(Formula.predicate('p')),
            Formula.predicate('q'))),
    (
        Formula.negate(Formula.binary(
            BinaryToken.IMPLIES,
            Formula.predicate('p'),
            Formula.predicate('q'))),
        Formula.binary(
            BinaryToken.AND,
            Formula.predicate('p'),
            Formula.negate(Formula.predicate('q')))),
    (
        Formula.negate(Formula.binary(
            BinaryToken.OR,
            Formula.predicate('p'),
            Formula.predicate('q'))),
        Formula.binary(
            BinaryToken.AND,
            Formula.negate(Formula.predicate('p')),
            Formula.negate(Formula.predicate('q')))),
    (
        Formula.negate(Formula.binary(
            BinaryToken.AND,
            Formula.predicate('p'),
            Formula.predicate('q'))),
        Formula.binary(
            BinaryToken.OR,
            Formula.negate(Formula.predicate('p')),
            Formula.negate(Formula.predicate('q')))),
])
def test_normalize_negations(formula: Formula, normalized: Formula):
    assert normalize_negations(formula) == normalized

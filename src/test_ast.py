from typing import List

from .ast import Formula
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

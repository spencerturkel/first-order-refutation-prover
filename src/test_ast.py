from typing import List

from .ast import Formula
from .tokens import BinaryToken, ContradictionToken, NotToken, QuantifierToken


def test_formulas() -> List[Formula]:
    return [
        (BinaryToken.IMPLIES, ContradictionToken.CONTR, ('a', ())),
        (BinaryToken.AND, (NotToken.NOT, ('a', ())), ('a', ())),
        (BinaryToken.OR, ('12', ()), ('a1', ())),
        (QuantifierToken.FORALL, 'x', ('p', ('x',))),
        (QuantifierToken.EXISTS, 'x', ('p', ('x',))),
    ]

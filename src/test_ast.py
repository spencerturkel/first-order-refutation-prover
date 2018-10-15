from typing import List

from .ast import Formula, FormulaF
from .tokens import BinaryToken, ContradictionToken, NotToken, QuantifierToken


def test_formulas() -> List[Formula]:
    return [
        Formula(FormulaF(BinaryToken.IMPLIES,
                         Formula(FormulaF(ContradictionToken.CONTR)),
                         Formula(FormulaF('a', ())))),
        # FormulaF(BinaryToken.AND, (NotToken.NOT, ('a', ())), ('a', ())),
        # FormulaF(BinaryToken.OR, ('12', ()), ('a1', ())),
        # FormulaF(QuantifierToken.FORALL, 'x', ('p', ('x',))),
        # FormulaF(QuantifierToken.EXISTS, 'x', ('p', ('x',))),
    ]

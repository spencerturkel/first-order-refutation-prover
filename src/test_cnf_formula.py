from typing import List, cast

from .ast import Term
from .cnf_formula import Clause, CnfFormula
from .tokens import NotToken


def test_simple_formulas() -> List[CnfFormula]:
    return [
        # {}
        CnfFormula(
            # no clauses
            formula=frozenset(),
            # no variables
            variables=frozenset(),
        ),
        # {{}}
        CnfFormula(
            frozenset([
                # an empty clause
                cast(Clause, frozenset()),
            ]),
            frozenset(),
        ),
        # {{P x}, {~ P y}, {Q}}
        CnfFormula(
            frozenset([
                frozenset([
                    Term('P', 'x'),
                ]),
                frozenset([
                    (NotToken.NOT, Term('P', 'y')),
                ]),
                frozenset([
                    Term('Q'),
                ]),
            ]),
            frozenset(),
        ),
        # [(P(x) ∨ Q(x)) ∧ ∀ y, Q(f(y))] = > {{P x, Q x}, {Q (f y)}}
        CnfFormula(
            frozenset([
                frozenset([
                    Term('P', 'x'),
                    Term('Q', 'x'),
                ]),
                frozenset([
                    Term('Q', Term('f', 'y')),
                ]),
            ]),
            frozenset(['y']),
        ),
        # [ ∀ x, ∃ y, P(x, y) ] => {{P x (f_y x)}}
        CnfFormula(
            formula=frozenset([
                frozenset([
                    Term('P', 'x', Term('f_y', 'x')),
                ]),
            ]),
            variables=frozenset(['x']),
        ),
    ]

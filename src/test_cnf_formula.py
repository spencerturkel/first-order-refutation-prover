from typing import List, cast

from .ast import term
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
                    term('P', 'x'),
                ]),
                frozenset([
                    (NotToken.NOT, term('P', 'y')),
                ]),
                frozenset([
                    term('Q'),
                ]),
            ]),
            frozenset(),
        ),
        # [(P(x) ∨ Q(x)) ∧ ∀ y, Q(f(y))] = > {{P x, Q x}, {Q (f y)}}
        CnfFormula(
            frozenset([
                frozenset([
                    term('P', 'x'),
                    term('Q', 'x'),
                ]),
                frozenset([
                    term('Q', term('f', 'y')),
                ]),
            ]),
            frozenset(['y']),
        ),
        # [ ∀ x, ∃ y, P(x, y) ] => {{P x (f_y x)}}
        CnfFormula(
            formula=frozenset([
                frozenset([
                    term('P', 'x', term('f_y', 'x')),
                ]),
            ]),
            variables=frozenset(['x']),
        ),
    ]

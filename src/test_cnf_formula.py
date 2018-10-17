from typing import List, cast

from .ast import Term
from .cnf_formula import Clause, CnfFormula, Literal


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
                    Literal(True, Term('P', 'x')),
                ]),
                frozenset([
                    Literal(False, Term('P', 'y')),
                ]),
                frozenset([
                    Literal(True, Term('Q')),
                ]),
            ]),
            frozenset(),
        ),
        # [(P(x) ∨ Q(x)) ∧ ∀ y, Q(f(y))] = > {{P x, Q x}, {Q (f y)}}
        CnfFormula(
            frozenset([
                frozenset([
                    Literal(True, Term('P', 'x')),
                    Literal(True, Term('Q', 'x')),
                ]),
                frozenset([
                    Literal(True, Term('Q', Term('f', 'y'))),
                ]),
            ]),
            frozenset(['y']),
        ),
        # [ ∀ x, ∃ y, P(x, y) ] => {{P x (f_y x)}}
        CnfFormula(
            formula=frozenset([
                frozenset([
                    Literal(True, Term('P', 'x', Term('f_y', 'x'))),
                ]),
            ]),
            variables=frozenset(['x']),
        ),
    ]

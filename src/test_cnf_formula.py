from typing import FrozenSet, List, cast

from .cnf_formula import CnfFormula
from .tree import SymbolTree, Tree


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
                cast(FrozenSet[Tree[str]], frozenset()),
            ]),
            frozenset(),
        ),
        # {{P x}, {P y}, {Q}}
        CnfFormula(
            frozenset([
                frozenset([
                    SymbolTree('P', 'x'),
                ]),
                frozenset([
                    SymbolTree('P', 'y'),
                ]),
                frozenset([
                    SymbolTree('Q'),
                ]),
            ]),
            frozenset(),
        ),
        # [(P(x) ∨ Q(x)) ∧ ∀ y, Q(f(y))] = > {{P x, Q x}, {Q (f y)}}
        CnfFormula(
            frozenset([
                frozenset([
                    SymbolTree('P', 'x'),
                    SymbolTree('Q', 'x'),
                ]),
                frozenset([
                    SymbolTree(
                        'Q',
                        SymbolTree('f', 'y'),
                    ),
                ]),
            ]),
            frozenset(['y']),
        ),
        # [ ∀ x, ∃ y, P(x, y) ] => {{P x (f_y x)}}
        CnfFormula(
            formula=frozenset([
                frozenset([
                    SymbolTree(
                        'P',
                        'x',
                        # Skolemized y
                        SymbolTree('f_y', 'x'),
                    ),
                ]),
            ]),
            variables=frozenset(['x']),
        ),
    ]

from typing import FrozenSet, Sequence, Tuple

from .ast import (BinaryFormulaF, Formula, FormulaF, FormulaFoldVisitor,
                  FormulaVisitor, NegatedFormulaF, PredicateFormulaF,
                  QuantifiedFormulaF)
from .tokens import BinaryToken, QuantifierToken
from .tree import Tree


class _NegationNormalizingVisitor(FormulaVisitor[FormulaF[Formula]]):
    def visit_quantifier(self, token: QuantifierToken,
                         var: str, formula: Formula) -> FormulaF[Formula]:
        return QuantifiedFormulaF(token, var, formula)

    def visit_binary(self, token: BinaryToken,
                     left: Formula, right: Formula) -> FormulaF[Formula]:
        if token == BinaryToken.IMPLIES:
            return BinaryFormulaF(BinaryToken.OR,
                                  Formula.negate(left), right)

        return BinaryFormulaF(token, left, right)

    class _InnerNegationVisitor(FormulaVisitor[FormulaF[Formula]]):
        def visit_quantifier(self, token, var, formula: Formula) -> FormulaF[Formula]:
            return QuantifiedFormulaF(
                QuantifierToken.FORALL if token == QuantifierToken.EXISTS
                else QuantifierToken.EXISTS,
                var, Formula.negate(formula))

        def visit_binary(self, token, left: Formula,
                         right: Formula) -> FormulaF[Formula]:
            if token == BinaryToken.AND:
                return BinaryFormulaF(BinaryToken.OR,
                                      Formula.negate(left),
                                      Formula.negate(right))
            if token == BinaryToken.OR:
                return BinaryFormulaF(BinaryToken.AND,
                                      Formula.negate(left),
                                      Formula.negate(right))
            # token == BinaryToken.IMPLIES
            return BinaryFormulaF(BinaryToken.AND, left, Formula.negate(right))

        def visit_negation(self, formula: Formula) -> FormulaF[Formula]:
            return formula.formula

        def visit_predicate(self, predicate, terms) -> FormulaF[Formula]:
            return NegatedFormulaF(Formula.predicate(predicate, *terms))

    _innerNegationVisitor = _InnerNegationVisitor()

    def visit_negation(self, formula: Formula) -> FormulaF[Formula]:
        return formula.visit(self._innerNegationVisitor)

    def visit_predicate(self, predicate, terms) -> FormulaF[Formula]:
        return PredicateFormulaF(predicate, terms)


_negationNormalizingVisitor = _NegationNormalizingVisitor()


def normalize_negations(formula: Formula) -> Formula:
    return Formula.unfold(formula,
                          lambda f: f.visit(_negationNormalizingVisitor))


class _StandardizeVisitor(FormulaFoldVisitor[Tuple[Formula, FrozenSet[str]]]):
    def visit_quantifier(self,
                         token: QuantifierToken,
                         variable: str,
                         sub_formula: Tuple[Formula, FrozenSet[str]]
                         ) -> Tuple[Formula, FrozenSet[str]]:
        pass  # TODO:

    def visit_binary(self,
                     token: BinaryToken,
                     first_arg: Tuple[Formula, FrozenSet[str]],
                     second_arg: Tuple[Formula, FrozenSet[str]]
                     ) -> Tuple[Formula, FrozenSet[str]]:
        pass  # TODO:

    def visit_negation(self,
                       sub_formula: Tuple[Formula, FrozenSet[str]]
                       ) -> Tuple[Formula, FrozenSet[str]]:
        pass  # TODO:

    def visit_predicate(self, predicate: str,
                        terms: Sequence[Tree[str]]
                        ) -> Tuple[Formula, FrozenSet[str]]:
        pass  # TODO:


_standardizeVisitor = _StandardizeVisitor()


def standardize(formula: Formula) -> Formula:
    return formula.fold(_standardizeVisitor)[0]

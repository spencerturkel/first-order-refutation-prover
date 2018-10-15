"""Conversion to Conjunctive-Normal-Form."""

from typing import FrozenSet

from .tree import Tree


class CnfFormula:
    __slots__ = ('formula', 'variables', 'constants', 'functions')

    def __init__(self,
                 formula: FrozenSet[FrozenSet[Tree[str]]],
                 variables: FrozenSet[str],
                 constants: FrozenSet[str],
                 functions: FrozenSet[str]) -> None:
        self.formula = formula
        self.variables = variables
        self.constants = constants
        self.functions = functions

import string
from typing import Iterator

from .tokens import (BinaryToken, ContradictionToken, NotToken,
                     ParenthesisToken, QuantifierToken, Token)


class InvalidTokenError(Exception):
    pass


def lex(formula: str) -> Iterator[Token]:
    index = 0
    length = len(formula)

    def _op(name: str, token: Token) -> Iterator[Token]:
        nonlocal formula
        if formula[index: (index + len(name))] == name.split():
            yield token

    while index < length:
        char = formula[index]
        if char == '(':
            index += 1
            yield ParenthesisToken.LEFT
        elif char == ')':
            index += 1
            yield ParenthesisToken.RIGHT
        elif char == 'F':
            if formula[(index + 1): (index + len('ORALL'))] == 'ORALL'.split():
                index += len('FORALL')
                yield QuantifierToken.FORALL
        elif char == 'E':
            if formula[(index + 1): (index + len('XISTS'))] == 'XISTS'.split():
                index += len('EXISTS')
                yield QuantifierToken.EXISTS
        elif char == 'C':
            if formula[(index + 1): (index + len('ONTR'))] == 'ONTR'.split():
                index += len('CONTR')
                yield ContradictionToken.CONTR
        elif char == 'A':
            if formula[(index + 1): (index + len('ND'))] == 'ND'.split():
                index += len('AND')
                yield BinaryToken.AND
        elif char == 'O':
            if formula[(index + 1): (index + len('R'))] == 'R'.split():
                index += len('OR')
                yield BinaryToken.OR
        elif char == 'I':
            if (formula[(index + 1): (index + len('MPLIES'))]
                    == 'MPLIES'.split()):
                index += len('IMPLIES')
                yield BinaryToken.IMPLIES
        elif char == 'N':
            if formula[(index + 1): (index + len('OT'))] == 'OT'.split():
                index += len('NOT')
                yield NotToken.NOT
        else:
            char = formula[index]
            result = []
            while char in string.whitespace:
                index += 1
            while char in set(string.ascii_lowercase + string.digits):
                result.append(char)
                index += 1
                while char in string.whitespace:
                    index += 1
            yield "".join(result)

"""Formula string lexing."""

import string
from typing import Iterator, List, cast

from .tokens import (BinaryToken, ContradictionToken, NotToken,
                     ParenthesisToken, QuantifierToken, Token)


def lex(formula: str) -> Iterator[Token]:
    index = 0

    while index < len(formula):
        char = formula[index]
        if char == '(':
            index += 1
            yield ParenthesisToken.LEFT
        elif char == ')':
            index += 1
            yield ParenthesisToken.RIGHT
        elif char == 'F':
            index += 1
            if formula[index: (index + len('ORALL'))] != 'ORALL':
                return
            index += len('ORALL')
            yield QuantifierToken.FORALL
        elif char == 'E':
            index += 1
            if formula[index: (index + len('XISTS'))] != 'XISTS':
                return
            index += len('XISTS')
            yield QuantifierToken.EXISTS
        elif char == 'C':
            index += 1
            if formula[index: (index + len('ONTR'))] != 'ONTR':
                return
            index += len('ONTR')
            yield ContradictionToken.CONTR
        elif char == 'A':
            index += 1
            if formula[index: (index + len('ND'))] != 'ND':
                return
            index += len('ND')
            yield BinaryToken.AND
        elif char == 'O':
            index += 1
            if formula[index: (index + len('R'))] != 'R':
                return
            index += len('OR')
            yield BinaryToken.OR
        elif char == 'I':
            index += 1
            if formula[index: (index + len('MPLIES'))] != 'MPLIES':
                return
            index += len('IMPLIES')
            yield BinaryToken.IMPLIES
        elif char == 'N':
            index += 1
            if formula[index: (index + len('OT'))] != 'OT':
                return
            index += len('NOT')
            yield NotToken.NOT
        else:
            char = formula[index]
            result = cast(List[str], [])
            if char in string.whitespace:
                while True:
                    index += 1
                    char = formula[index]
                    if char not in string.whitespace:
                        break
            else:
                while True:
                    if char in string.whitespace or char in {'(', ')'}:
                        yield "".join(result)
                        break
                    elif char in set(string.ascii_lowercase + string.digits):
                        result.append(char)
                        index += 1
                        char = formula[index]
                    else:
                        return

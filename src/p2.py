"""Main file that will be executed by the grader."""

import string


def lex(formula):
    index = 0

    while index < len(formula):
        char = formula[index]
        if char == '(':
            index += 1
            yield '('
        elif char == ')':
            index += 1
            yield ')'
        elif char == 'F':
            token = 'FORALL'
            length = len(token)
            if formula[index + 1: (index + length)] != 'ORALL':
                return
            index += length
            yield token
        elif char == 'E':
            token = 'EXISTS'
            length = len(token)
            if formula[index + 1: (index + length)] != 'XISTS':
                return
            index += length
            yield token
        elif char == 'A':
            token = 'AND'
            length = len(token)
            if formula[index + 1: (index + length)] != 'ND':
                return
            index += length
            yield token
        elif char == 'O':
            token = 'OR'
            length = len(token)
            if formula[index + 1: (index + length)] != 'R':
                return
            index += length
            yield token
        elif char == 'I':
            token = 'IMPLIES'
            length = len(token)
            if formula[index + 1: (index + length)] != 'MPLIES':
                return
            index += length
            yield token
        elif char == 'N':
            token = 'NOT'
            length = len(token)
            if formula[index + 1: (index + length)] != 'OT':
                return
            index += length
            yield token
        elif char in string.whitespace:
            while True:
                index += 1
                char = formula[index]
                if char not in string.whitespace:
                    break
        else:
            result = []
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


def findIncSet(fSets):  # noqa
    """Find indices of inconsistent formula lists.

    Given a list of lists of first-order logic formulas,
    finds the zero-indexed indices of inconsistent lists of formulas.
    See README.md for detailed specification.

    :param fSets: list of formula lists
    :return: returns the list of inconsistent zero-indexed indices
    """
    return []  # TODO:

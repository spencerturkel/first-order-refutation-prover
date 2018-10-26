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


class ParseError(Exception):
    pass


class _Parser:
    __slots__ = (
        'peek_token',
        'tokens',
    )

    def __init__(self, tokens):
        self.peek_token = None
        self.tokens = tokens

    def formula(self):
        self._expect('(')
        expr = self._expr()
        self._expect(')')
        return expr

    def _expect(self, token):
        if self._next() != token:
            raise ParseError

    def _expr(self):
        token = self._next()
        if token in {'FORALL', 'EXISTS'}:
            return token, self._next(), self.formula()
        if token in {'AND', 'OR', 'IMPLIES'}:
            return token, self.formula(), self.formula()
        if token == 'NOT':
            return token, self.formula()
        return token, self._terms()

    def _next(self):
        if self.peek_token is not None:
            token = self.peek_token
            self.peek_token = None
            return token

        return next(self.tokens)

    def _terms(self):
        terms = []
        while True:
            token = self._peek()
            if token == ')':
                return terms
            if token == '(':
                self._next()
                terms.append(self._sub_term())
            else:
                self._next()
                terms.append(token)

    def _peek(self):
        if self.peek_token is None:
            try:
                self.peek_token = next(self.tokens)
            except StopIteration as e:
                raise ParseError from e
        return self.peek_token

    def _sub_term(self):
        root = self._next()
        if root in {'(', ')'}:
            raise ParseError
        terms = []
        while True:
            token = self._next()
            if token == ')':
                return root, terms
            if token == '(':
                terms.append(self._sub_term())
            else:
                terms.append(token)


def parse(formula_tokens):
    """Parse the formula tokens into an abstract syntax tree."""
    return _Parser(formula_tokens).formula()


def findIncSet(fSets):  # noqa
    """Find indices of inconsistent formula lists.

    Given a list of lists of first-order logic formulas,
    finds the zero-indexed indices of inconsistent lists of formulas.
    See README.md for detailed specification.

    :param fSets: list of formula lists
    :return: returns the list of inconsistent zero-indexed indices
    """
    return []  # TODO:

"""Formula string parsing module."""

from typing import Iterator, Tuple, cast

from .ast import Formula, Object
from .tokens import (BinaryToken, ContradictionToken, NotToken,
                     ParenthesisToken, QuantifierToken, Token)


def parse(formula_tokens: Iterator[Token]) -> Formula:
    """Parse the formula tokens into an abstract syntax tree."""
    return _Parser(formula_tokens).formula()


class ParseError(Exception):
    pass


class _Parser:
    def __init__(self, tokens: Iterator[Token]) -> None:
        self.tokens = tokens

    def formula(self) -> Formula:
        self._expect(ParenthesisToken.LEFT)
        expr = self._expr()
        self._expect(ParenthesisToken.RIGHT)
        return expr

    def _expect(self, token: Token) -> None:
        if self._next() != token:
            raise ParseError

    def _expr(self) -> Formula:
        token = self._next()
        if isinstance(token, QuantifierToken):
            return token, self._symbol(), self.formula()
        if isinstance(token, BinaryToken):
            return token, self.formula(), self.formula()
        if isinstance(token, NotToken):
            return token, self.formula()
        if isinstance(token, ContradictionToken):
            return token
        return cast(str, token), self._objects()

    def _next(self) -> Token:
        return next(self.tokens)

    def _symbol(self) -> str:
        sym = self._next()
        if not isinstance(sym, str):
            raise ParseError
        return sym

    def _objects(self) -> Tuple[Object, ...]:
        objs = []
        while True:
            token = self._next()
            if isinstance(token, str):
                objs.append(token)
            elif token == ParenthesisToken.LEFT:
                expr = self._expr()
                self._expect(ParenthesisToken.RIGHT)
                objs.append(expr)
            else:
                raise ParseError
        return tuple(objs)

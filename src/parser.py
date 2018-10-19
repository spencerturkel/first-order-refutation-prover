"""Formula string parsing module."""

from typing import Iterator, List, Optional, Sequence, Union, cast

from .ast import Formula, Term
from .tokens import (BinaryToken, NotToken, ParenthesisToken, QuantifierToken,
                     Token)
from .tree import Tree


def parse(formula_tokens: Iterator[Token]) -> Formula:
    """Parse the formula tokens into an abstract syntax tree."""
    return _Parser(formula_tokens).formula()


class ParseError(Exception):
    pass


class _Parser:
    __slots__ = (
        'peek_token',
        'tokens',
    )

    def __init__(self, tokens: Iterator[Token]) -> None:
        self.peek_token = cast(Optional[Token], None)
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
            return Formula.quantify(token, self._symbol(), self.formula())
        if isinstance(token, BinaryToken):
            return Formula.binary(token, self.formula(), self.formula())
        if isinstance(token, NotToken):
            return Formula.negate(self.formula())
        return Formula.predicate(cast(str, token), *self._terms())

    def _next(self) -> Token:
        if self.peek_token is not None:
            token = self.peek_token
            self.peek_token = None
            return token

        return next(self.tokens)

    def _symbol(self) -> str:
        sym = self._next()
        if not isinstance(sym, str):
            raise ParseError
        return sym

    def _terms(self) -> Sequence[Tree[str]]:
        terms = cast(List[Tree[str]], [])
        while True:
            token = self._peek()
            if isinstance(token, str):
                self._next()
                terms.append(Term(token))
            elif token == ParenthesisToken.LEFT:
                self._next()
                terms.append(self._sub_term())
            else:
                return terms

    def _peek(self) -> Token:
        if self.peek_token is None:
            try:
                self.peek_token = next(self.tokens)
            except StopIteration:
                raise ParseError
        return self.peek_token

    def _sub_term(self) -> Tree[str]:
        root = self._next()
        if not isinstance(root, str):
            raise ParseError
        children = cast(List[Union[str, Tree[str]]], [])
        while True:
            token = self._next()

            if token == ParenthesisToken.RIGHT:
                return Term(root, *children)

            if isinstance(token, str):
                children.append(token)
                continue

            if token == ParenthesisToken.LEFT:
                children.append(self._sub_term())
                continue

            raise ParseError

"""Formula string parsing module."""

from ast import Formula
from typing import Iterator, Optional

from tokens import ParenthesisToken, Token


def parse(formula_tokens: Iterator[Token]) -> Optional[Formula]:
    """Parse the formula tokens into an abstract syntax tree."""
    return None if formula_tokens else None  # TODO:


class _Parser:
    def __init__(self, tokens: Iterator[Token]) -> None:
        self.tokens = tokens


def _formula(tokens: Iterator[Token]) -> Optional[Formula]:
    if next(tokens) != ParenthesisToken.LEFT:
        return None
    return None
    # TODO:
    # expr = _expr(tokens)
    # if next(tokens) != ParenthesisToken.RIGHT:
    #     return None
    # return expr

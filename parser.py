"""Formula string parsing module."""

from ast import Formula
from typing import Iterator, Optional

from tokens import ParenthesisToken, Token


def parse(formula_tokens: Iterator[Token]) -> Optional[Formula]:
    """Parse the formula tokens into an abstract syntax tree."""
    return None if formula_tokens else None  # TODO:


def _formula(tokens: Iterator[Token]) -> Optional[Formula]:
    if next(tokens) != ParenthesisToken.LEFT:
        return None
    return None
    #  TODO:
    # expr = _expr(tokens)
    # if next(tokens) != ParenthesisToken.RIGHT:
    #     return None
    # return expr

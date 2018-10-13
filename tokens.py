"""Enums for non-symbol tokens."""

from enum import Enum, unique
from typing import Union


@unique
class ParenthesisToken(Enum):
    LEFT = 0
    RIGHT = 0


@unique
class QuantifierToken(Enum):
    FORALL = 0
    EXISTS = 1


@unique
class BinaryToken(Enum):
    AND = 0
    OR = 1
    IMPLIES = 2


@unique
class NotToken(Enum):
    NOT = 0


@unique
class ContradictionToken(Enum):
    CONTR = 0


Token = Union[
    ParenthesisToken,
    QuantifierToken,
    BinaryToken,
    NotToken,
    ContradictionToken
]

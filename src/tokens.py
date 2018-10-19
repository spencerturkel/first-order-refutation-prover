"""Enums and types for tokens."""

from enum import Enum, unique
from typing import Union


class _RepresentableEnum(Enum):
    def __repr__(self):
        return type(self).__name__ + '.' + self.name


@unique
class ParenthesisToken(_RepresentableEnum):
    LEFT = 0
    RIGHT = 1


@unique
class QuantifierToken(_RepresentableEnum):
    FORALL = 0
    EXISTS = 1


@unique
class BinaryToken(_RepresentableEnum):
    AND = 0
    OR = 1
    IMPLIES = 2


@unique
class NotToken(_RepresentableEnum):
    NOT = 0


Token = Union[
    ParenthesisToken,
    QuantifierToken,
    BinaryToken,
    NotToken,
    str,
]

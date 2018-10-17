from typing import Iterable

import pytest

from .ast import Formula, Term
from .parser import parse
from .tokens import (BinaryToken, ContradictionToken, NotToken,
                     ParenthesisToken, QuantifierToken, Token)


@pytest.mark.parametrize('tokens, ast', [
    ([ParenthesisToken.LEFT,
      QuantifierToken.FORALL, 'x',
      ParenthesisToken.LEFT, 'p', 'x', ParenthesisToken.RIGHT,
      ParenthesisToken.RIGHT],
     Formula.quantify(QuantifierToken.FORALL, 'x',
                      Formula.predicate('p', Term('x')))),
    ([ParenthesisToken.LEFT,
      BinaryToken.IMPLIES,
      ParenthesisToken.LEFT, 'p', 'x', ParenthesisToken.RIGHT,
      ParenthesisToken.LEFT, QuantifierToken.EXISTS, 'y',
      ParenthesisToken.LEFT, 'p', 'y', ParenthesisToken.RIGHT,
      ParenthesisToken.RIGHT,
      ParenthesisToken.RIGHT],
     Formula.binary(BinaryToken.IMPLIES,
                    Formula.predicate('p', Term('x')),
                    Formula.quantify(QuantifierToken.EXISTS, 'y',
                                     Formula.predicate('p', Term('y'))))),
    ([ParenthesisToken.LEFT,
      BinaryToken.IMPLIES,
      ParenthesisToken.LEFT, 'p',
      ParenthesisToken.LEFT, 'f', 'x',
      ParenthesisToken.LEFT, 'g', 'y', ParenthesisToken.RIGHT,
      'z', ParenthesisToken.RIGHT,
      ParenthesisToken.RIGHT,
      ParenthesisToken.LEFT, ContradictionToken.CONTR, ParenthesisToken.RIGHT,
      ParenthesisToken.RIGHT],
     Formula.binary(BinaryToken.IMPLIES,
                    Formula.predicate(
                        'p', Term('f', 'x', Term('g', 'y'), 'z')),
                    Formula.contradiction())),
    ([ParenthesisToken.LEFT,
      BinaryToken.AND,
      ParenthesisToken.LEFT, 'p', ParenthesisToken.RIGHT,
      ParenthesisToken.LEFT, 'p', ParenthesisToken.RIGHT,
      ParenthesisToken.RIGHT],
     Formula.binary(BinaryToken.AND,
                    Formula.predicate('p'),
                    Formula.predicate('p'))),
    ([ParenthesisToken.LEFT,
      BinaryToken.OR,
      ParenthesisToken.LEFT, 'p', ParenthesisToken.RIGHT,
      ParenthesisToken.LEFT, 'p', ParenthesisToken.RIGHT,
      ParenthesisToken.RIGHT],
     Formula.binary(BinaryToken.OR,
                    Formula.predicate('p'),
                    Formula.predicate('p'))),
    ([ParenthesisToken.LEFT,
      BinaryToken.AND,
      ParenthesisToken.LEFT,
      NotToken.NOT, ParenthesisToken.LEFT, 'a', ParenthesisToken.RIGHT,
      ParenthesisToken.RIGHT,
      ParenthesisToken.LEFT, 'a', ParenthesisToken.RIGHT,
      ParenthesisToken.RIGHT],
     Formula.binary(
        BinaryToken.AND,
        Formula.negate(Formula.predicate('a')),
        Formula.predicate('a')
    ))
])
def test_good_parses(tokens: Iterable[Token], ast: Formula):
    assert parse(iter(tokens)) == ast

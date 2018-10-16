from typing import Iterable

import pytest

from .ast import Formula
from .parser import parse
from .tokens import (BinaryToken, ContradictionToken, NotToken,
                     ParenthesisToken, QuantifierToken, Token)


@pytest.mark.parametrize('tokens, ast', [
    ([ParenthesisToken.LEFT,
      QuantifierToken.FORALL, 'x',
      ParenthesisToken.LEFT, 'p', 'x', ParenthesisToken.RIGHT,
      ParenthesisToken.RIGHT],
     Formula.of(QuantifierToken.FORALL, 'x', Formula.of('p', ('x',)))),
    ([ParenthesisToken.LEFT,
      BinaryToken.IMPLIES,
      ParenthesisToken.LEFT, 'p', 'x', ParenthesisToken.RIGHT,
      ParenthesisToken.LEFT, QuantifierToken.EXISTS, 'y',
      ParenthesisToken.LEFT, 'p', 'y', ParenthesisToken.RIGHT,
      ParenthesisToken.RIGHT,
      ParenthesisToken.RIGHT],
     Formula.of(BinaryToken.IMPLIES,
                Formula.of('p', ('x',)),
                Formula.of(QuantifierToken.EXISTS, 'y',
                           Formula.of('p', ('y',))))),
    ([ParenthesisToken.LEFT,
      BinaryToken.IMPLIES,
      ParenthesisToken.LEFT, 'p',
      ParenthesisToken.LEFT, 'f',
      ParenthesisToken.LEFT, NotToken.NOT,
      ParenthesisToken.LEFT, 'x', ParenthesisToken.RIGHT,
      ParenthesisToken.RIGHT,
      ParenthesisToken.RIGHT,
      ParenthesisToken.RIGHT,
      ParenthesisToken.LEFT, ContradictionToken.CONTR, ParenthesisToken.RIGHT,
      ParenthesisToken.RIGHT],
     Formula.of(BinaryToken.IMPLIES,
                Formula.of(
                    'p',
                    (Formula.of(
                        'f',
                        (Formula.of(
                            NotToken.NOT,
                            Formula.of('x', ())
                        ),)
                    ),)
                ),
                Formula.of(ContradictionToken.CONTR))),
    ([ParenthesisToken.LEFT,
      BinaryToken.AND,
      ParenthesisToken.LEFT, 'p', ParenthesisToken.RIGHT,
      ParenthesisToken.LEFT, 'p', ParenthesisToken.RIGHT,
      ParenthesisToken.RIGHT],
     Formula.of(BinaryToken.AND, Formula.of('p', ()), Formula.of('p', ()))),
    ([ParenthesisToken.LEFT,
      BinaryToken.OR,
      ParenthesisToken.LEFT, 'p', ParenthesisToken.RIGHT,
      ParenthesisToken.LEFT, 'p', ParenthesisToken.RIGHT,
      ParenthesisToken.RIGHT],
     Formula.of(BinaryToken.OR, Formula.of('p', ()), Formula.of('p', ()))),
    ([ParenthesisToken.LEFT,
      BinaryToken.AND,
      ParenthesisToken.LEFT,
      NotToken.NOT, ParenthesisToken.LEFT, 'a', ParenthesisToken.RIGHT,
      ParenthesisToken.RIGHT,
      ParenthesisToken.LEFT, 'a', ParenthesisToken.RIGHT,
      ParenthesisToken.RIGHT],
     Formula.of(
        BinaryToken.AND,
        Formula.of(NotToken.NOT, Formula.of('a', ())),
        Formula.of('a', ())
    ))
])
def test_good_parses(tokens: Iterable[Token], ast: Formula):
    assert parse(iter(tokens)) == ast

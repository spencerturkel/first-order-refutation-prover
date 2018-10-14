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
      ParenthesisToken.RIGHT], (QuantifierToken.FORALL, 'x', ('p', ('x',)))),
    ([ParenthesisToken.LEFT,
      BinaryToken.IMPLIES,
      ParenthesisToken.LEFT, 'p', 'x', ParenthesisToken.RIGHT,
      ParenthesisToken.LEFT, QuantifierToken.EXISTS, 'y',
      ParenthesisToken.LEFT, 'p', 'y', ParenthesisToken.RIGHT,
      ParenthesisToken.RIGHT,
      ParenthesisToken.RIGHT],
     (BinaryToken.IMPLIES,
      ('p', ('x',)),
      (QuantifierToken.EXISTS, 'y', ('p', ('y',))))),
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
      ParenthesisToken.RIGHT], (BinaryToken.IMPLIES,
                                ('p', (('f', ((NotToken.NOT, ('x', ())),)),)),
                                ContradictionToken.CONTR)),
    ([ParenthesisToken.LEFT,
      BinaryToken.AND,
      ParenthesisToken.LEFT, 'p', ParenthesisToken.RIGHT,
      ParenthesisToken.LEFT, 'p', ParenthesisToken.RIGHT,
      ParenthesisToken.RIGHT],
     (BinaryToken.AND, ('p', ()), ('p', ()))),
    ([ParenthesisToken.LEFT,
      BinaryToken.OR,
      ParenthesisToken.LEFT, 'p', ParenthesisToken.RIGHT,
      ParenthesisToken.LEFT, 'p', ParenthesisToken.RIGHT,
      ParenthesisToken.RIGHT],
     (BinaryToken.OR, ('p', ()), ('p', ()))),
])
def test_good_parses(tokens: Iterable[Token], ast: Formula):
    assert parse(iter(tokens)) == ast

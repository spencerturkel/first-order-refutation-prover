import pytest

from .lexer import lex
from .tokens import (BinaryToken, ContradictionToken, NotToken,
                     ParenthesisToken, QuantifierToken)


@pytest.mark.parametrize('formula, symbols', [
    ('(FORALL 3ab4 (pq12b 3ab4))', [
        ParenthesisToken.LEFT,
        QuantifierToken.FORALL, '3ab4',
        ParenthesisToken.LEFT, 'pq12b', '3ab4', ParenthesisToken.RIGHT,
        ParenthesisToken.RIGHT,
    ]),
    ('(EXISTS xx (11 xx))', [
        ParenthesisToken.LEFT,
        QuantifierToken.EXISTS, 'xx',
        ParenthesisToken.LEFT, '11', 'xx', ParenthesisToken.RIGHT,
        ParenthesisToken.RIGHT,
    ]),
    ('(IMPLIES (CONTR) (p (f x)))', [
        ParenthesisToken.LEFT,
        BinaryToken.IMPLIES,
        ParenthesisToken.LEFT, ContradictionToken.CONTR, ParenthesisToken.RIGHT,
        ParenthesisToken.LEFT, 'p',
        ParenthesisToken.LEFT, 'f', 'x', ParenthesisToken.RIGHT,
        ParenthesisToken.RIGHT,
        ParenthesisToken.RIGHT,
    ]),
    ('(AND (NOT (a)) (OR (a) (a)))', [
        ParenthesisToken.LEFT, BinaryToken.AND,
        ParenthesisToken.LEFT, NotToken.NOT,
        ParenthesisToken.LEFT, 'a', ParenthesisToken.RIGHT,
        ParenthesisToken.RIGHT,
        ParenthesisToken.LEFT,  BinaryToken.OR,
        ParenthesisToken.LEFT, 'a', ParenthesisToken.RIGHT,
        ParenthesisToken.LEFT, 'a', ParenthesisToken.RIGHT,
        ParenthesisToken.RIGHT,
        ParenthesisToken.RIGHT,
    ]),
])
def test_symbols(formula, symbols):
    assert list(lex(formula)) == symbols

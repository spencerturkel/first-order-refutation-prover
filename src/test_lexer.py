import pytest

from .lexer import lex
from .tokens import BinaryToken, NotToken, ParenthesisToken, QuantifierToken


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
    ('(IMPLIES (q) (p (f x)))', [
        ParenthesisToken.LEFT,
        BinaryToken.IMPLIES,
        ParenthesisToken.LEFT, 'q', ParenthesisToken.RIGHT,
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
def test_valid_strings(formula, symbols):
    assert list(lex(formula)) == symbols


@pytest.mark.parametrize('formula, symbols', [
    ('(FORaLL 3ab4 (pq12b 3ab4))', [
        ParenthesisToken.LEFT,
    ]),
    ('(eXISTS xx (11 xx))', [
        ParenthesisToken.LEFT,
    ]),
    ('(IMPLIES (CONTR) (p (f x)))', [
        ParenthesisToken.LEFT,
        BinaryToken.IMPLIES,
        ParenthesisToken.LEFT]),
    ('(IMPLIES (CoNTR) (p (fF x)))', [
        ParenthesisToken.LEFT,
        BinaryToken.IMPLIES,
        ParenthesisToken.LEFT,
    ]),
    ('(AND (NOT (&)) (OR (a) (a)))', [
        ParenthesisToken.LEFT, BinaryToken.AND,
        ParenthesisToken.LEFT, NotToken.NOT,
        ParenthesisToken.LEFT,
    ]),
    ('(AND (NOT (P)) (OR (a) (a)))', [
        ParenthesisToken.LEFT, BinaryToken.AND,
        ParenthesisToken.LEFT, NotToken.NOT,
        ParenthesisToken.LEFT,
    ]),
    ('(aND (NOT (a)) (OR (a) (a)))', [
        ParenthesisToken.LEFT,
    ]),
    ('(AND (nOT (a)) (OR (a) (a)))', [
        ParenthesisToken.LEFT, BinaryToken.AND,
        ParenthesisToken.LEFT,
    ]),
    ('(AND (NOT (a)) (oR (a) (a)))', [
        ParenthesisToken.LEFT, BinaryToken.AND,
        ParenthesisToken.LEFT, NotToken.NOT,
        ParenthesisToken.LEFT, 'a', ParenthesisToken.RIGHT,
        ParenthesisToken.RIGHT,
        ParenthesisToken.LEFT,
    ]),
])
def test_invalid_strings(formula, symbols):
    assert list(lex(formula)) == symbols

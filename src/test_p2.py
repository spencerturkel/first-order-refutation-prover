"""Test p2.py"""

import pytest

from . import p2


@pytest.mark.parametrize('formula, symbols', [
    ('(FORALL 3ab4 (pq12b 3ab4))', '( FORALL 3ab4 ( pq12b 3ab4 ) )'),
    ('(EXISTS xx (11 xx))', '( EXISTS xx ( 11 xx ) )'),
    ('(IMPLIES (q) (p (f x)))', '( IMPLIES ( q ) ( p ( f x ) ) )'),
    ('(AND (NOT p) (OR (a) (a)))', '( AND ( NOT p ) ( OR ( a ) ( a ) ) )'),
])
def test_valid_strings(formula, symbols):
    assert list(p2.lex(formula)) == symbols.split(' ')

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


@pytest.mark.parametrize('tokens, ast', [
    ('( FORALL x ( p x y ) )', ('FORALL', 'x', ('p', ['x', 'y']))),
    ('( IMPLIES ( p x ) ( EXISTS y ( p y ) ) )',
     ('IMPLIES', ('p', ['x']), ('EXISTS', 'y', ('p', ['y'])))),
    ('( IMPLIES ( p ( f x ( g y ) z ) ) ( h ) )',
     ('IMPLIES', ('p', [('f', ['x', ('g', ['y']), 'z'])]), ('h', []))),
    ('( AND ( p ) ( p ) )', ('AND', ('p', []), ('p', []))),
    ('( OR ( p ) ( p ) )', ('OR', ('p', []), ('p', []))),
    ('( AND ( NOT ( a ) ) ( a ) )', ('AND', ('NOT', ('a', [])), ('a', []))),
    ('( p ( f x ) ( g ( h y y ) z ) )',
     ('p', [('f', ['x']), ('g', [('h', ['y', 'y']), 'z'])])),
])
def test_good_parses(tokens, ast):
    assert p2.parse(iter(tokens.split(' '))) == ast

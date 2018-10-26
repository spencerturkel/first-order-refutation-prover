"""Test p2.py"""

import pytest

from . import p2


@pytest.mark.parametrize('formula, symbols', [
    ('(FORALL 3ab4 (pq12b 3ab4))', '( FORALL 3ab4 ( pq12b 3ab4 ) )'),
    ('(EXISTS xx (11 xx))', '( EXISTS xx ( 11 xx ) )'),
    ('(IMPLIES (q) (p (f x)))', '( IMPLIES ( q ) ( p ( f x ) ) )'),
    ('(AND (NOT p) (OR (a) (a)))', '( AND ( NOT p ) ( OR ( a ) ( a ) ) )'),
])
def test_lexing(formula, symbols):
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
def test_parsing(tokens, ast):
    assert p2.parse(iter(tokens.split(' '))) == ast


@pytest.mark.parametrize('formula, normalized', [
    (('p', []), ('p', [])),
    (('NOT', ('p', [])), ('NOT', ('p', []))),
    (('NOT', ('NOT', ('p', []))), ('p', [])),
    (('NOT', ('FORALL', 'x', ('EXISTS', 'y', ('p', [])))),
     ('EXISTS', 'x', ('FORALL', 'y', ('NOT', ('p', []))))),
    (('NOT', ('IMPLIES', ('IMPLIES', ('p', []), ('q', [])), ('q', []))),
     ('AND', ('OR', ('NOT', ('p', [])), ('q', [])), ('NOT', ('q', [])))),
    (('NOT', ('AND', ('OR', ('p', []), ('q', [])), ('z', []))),
     ('OR', ('AND', ('NOT', ('p', [])), ('NOT', ('q', []))), ('NOT', ('z', []))))
])
def test_normalization(formula, normalized):
    assert p2.normalize(formula) == normalized


@pytest.mark.parametrize('formula, standardized', [
    (('OR', ('AND', ('NOT', ('p', [])), ('NOT', ('q', []))), ('NOT', ('z', []))),
     ('OR', ('AND', ('NOT', ('p', [])), ('NOT', ('q', []))), ('NOT', ('z', [])))),
    (('EXISTS', 'x', ('FORALL', 'y', ('NOT', ('p', [])))),
     ('EXISTS', 'x', ('FORALL', 'y', ('NOT', ('p', []))))),
    (('EXISTS', 'x', ('FORALL', 'x', ('p', ['x', ('f', ['y', 'x'])]))),
     ('EXISTS', 'x', ('FORALL', '-1', ('p', ['-1', ('f', ['y', '-1'])])))),
    (('OR', ('EXISTS', 'x', ('p', [])), ('EXISTS', 'x', ('q', []))),
        ('OR', ('EXISTS', 'x', ('p', [])), ('EXISTS', '-1', ('q', [])))),
    (('EXISTS', 'x',
        ('AND', ('FORALL', 'x', ('p', [])), ('FORALL', 'x', ('q', [])))),
        ('EXISTS', 'x',
         ('AND', ('FORALL', '-1', ('p', [])), ('FORALL', '-2', ('q', []))))),
])
def test_standardized(formula, standardized):
    assert p2.standardize(formula) == standardized

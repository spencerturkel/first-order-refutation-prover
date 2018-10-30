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
    ('( FORALL x ( p x y ) )', ('FORALL', 'x', ('p', ('x', 'y')))),
    ('( IMPLIES ( p x ) ( EXISTS y ( p y ) ) )',
     ('IMPLIES', ('p', ('x', )), ('EXISTS', 'y', ('p', ('y', ))))),
    ('( IMPLIES ( p ( f x ( g y ) z ) ) ( h ) )',
     ('IMPLIES', ('p', (('f', ('x', ('g', ('y', )), 'z', )), )), ('h', ()))),
    ('( AND ( p ) ( p ) )', ('AND', ('p', ()), ('p', ()))),
    ('( OR ( p ) ( p ) )', ('OR', ('p', ()), ('p', ()))),
    ('( AND ( NOT ( a ) ) ( a ) )', ('AND', ('NOT', ('a', ())), ('a', ()))),
    ('( p ( f x ) ( g ( h y y ) z ) )',
     ('p', (('f', ('x', )), ('g', (('h', ('y', 'y', )), 'z', )), ))),
    ('( NOT ( AND ( OR ( p ) ( EXISTS q ( r ) ) ) ( z ) ) )',
     ('NOT', ('AND', ('OR', ('p', ()), ('EXISTS', 'q', ('r', ()))), ('z', ()))))
])
def test_parsing(tokens, ast):
    assert p2.parse(iter(tokens.split(' '))) == ast


@pytest.mark.parametrize('tokens, ast', [
    ('( FORALL x ( p x y ) )', frozenset({
        frozenset({('p', ('x', ('y', ())))})
    })),
    ('( FORALL x ( IMPLIES ( p ( f x y ) z ) ( EXISTS y ( p y ) ) ) )',
     frozenset({
         frozenset({
             ('NOT', ('p', (('f', ('x', ('y', ()))), ('z', ())))),
             ('p', (('y', ('x',)),)),
         })
     })),
    ('( NOT ( AND ( OR ( p ) ( EXISTS q ( r ) ) ) ( z ) ) )',
     frozenset({
         frozenset({('NOT', ('p', ())), ('NOT', ('z', ()))}),
         frozenset({('NOT', ('r', ())), ('NOT', ('z', ()))}),
     }))
])
def test_smart_parsing(tokens, ast):
    assert p2.smart_parse(iter(tokens.split(' '))) == ast


@pytest.mark.parametrize('formula, normalized', [
    (('p', ()), ('p', ())),
    (('NOT', ('p', ())), ('NOT', ('p', ()))),
    (('NOT', ('NOT', ('p', ()))), ('p', ())),
    (('NOT', ('FORALL', 'x', ('EXISTS', 'y', ('p', ())))),
     ('EXISTS', 'x', ('FORALL', 'y', ('NOT', ('p', ()))))),
    (('NOT', ('IMPLIES', ('IMPLIES', ('p', ()), ('q', ())), ('q', ()))),
     ('AND', ('OR', ('NOT', ('p', ())), ('q', ())), ('NOT', ('q', ())))),
    (('NOT', ('AND', ('OR', ('p', ()), ('q', ())), ('z', ()))),
     ('OR', ('AND', ('NOT', ('p', ())), ('NOT', ('q', ()))), ('NOT', ('z', ()))))
])
def test_normalization(formula, normalized):
    assert p2.normalize(formula) == normalized


@pytest.mark.parametrize('formula, standardized', [
    (('OR', ('AND', ('NOT', ('p', ())), ('NOT', ('q', ()))), ('NOT', ('z', ()))),
     ('OR', ('AND', ('NOT', ('p', ())), ('NOT', ('q', ()))), ('NOT', ('z', ())))),
    (('EXISTS', 'x', ('FORALL', 'y', ('NOT', ('p', ())))),
     ('EXISTS', 'x', ('FORALL', 'y', ('NOT', ('p', ()))))),
    (('EXISTS', 'x', ('FORALL', 'x', ('p', ('x', ('f', ('y', 'x')))))),
     ('EXISTS', 'x', ('FORALL', '-1', ('p', ('-1', ('f', ('y', '-1'))))))),
    (('OR', ('EXISTS', 'x', ('p', ())), ('EXISTS', 'x', ('q', ()))),
        ('OR', ('EXISTS', 'x', ('p', ())), ('EXISTS', '-1', ('q', ())))),
    (('EXISTS', 'x',
        ('AND', ('FORALL', 'x', ('p', ())), ('FORALL', 'x', ('q', ())))),
        ('EXISTS', 'x',
         ('AND', ('FORALL', '-1', ('p', ())), ('FORALL', '-2', ('q', ()))))),
])
def test_standardized(formula, standardized):
    assert p2.standardize(formula) == standardized


@pytest.mark.parametrize('formula, prenex', [
    (('OR', ('AND', ('NOT', ('p', ())), ('NOT', ('q', ()))), ('NOT', ('z', ()))),
     ('OR', ('AND', ('NOT', ('p', ())), ('NOT', ('q', ()))), ('NOT', ('z', ())))),
    (('EXISTS', 'x', ('FORALL', 'y', ('NOT', ('p', ())))),
     ('EXISTS', 'x', ('FORALL', 'y', ('NOT', ('p', ()))))),
    (('OR', ('EXISTS', 'x', ('p', ())), ('EXISTS', '-1', ('q', ()))),
        ('EXISTS', 'x', ('EXISTS', '-1', ('OR', ('p', ()), ('q', ()))))),
    (('EXISTS', 'x',
      ('AND', ('FORALL', '-1', ('p', ())), ('FORALL', '-2', ('q', ())))),
        ('EXISTS', 'x',
         ('FORALL', '-1', ('FORALL', '-2', ('AND', ('p', ()), ('q', ())))))),
    (('FORALL', 'x',
      ('AND', ('EXISTS', '-1', ('p', ())), ('FORALL', '-2', ('q', ())))),
        ('FORALL', 'x',
         ('EXISTS', '-1', ('FORALL', '-2', ('AND', ('p', ()), ('q', ())))))),
])
def test_prenex(formula, prenex):
    assert p2.prenex(formula) == prenex


@pytest.mark.parametrize('formula, skolemized', [
    (('OR', ('AND', ('NOT', ('p', ())), ('NOT', ('q', ()))), ('NOT', ('z', ()))),
     ('OR', ('AND', ('NOT', ('p', ())), ('NOT', ('q', ()))), ('NOT', ('z', ())))),
    (('EXISTS', 'x', ('FORALL', 'y', ('NOT', ('p', ())))),
     ('NOT', ('p', ()))),
    (('EXISTS', 'x', ('EXISTS', '-1', ('OR', ('p', ()), ('q', ())))),
        ('OR', ('p', ()), ('q', ()))),
    (('FORALL', 'x', ('EXISTS', 'y', ('p', ('x', 'y')))),
     ('p', ('x', ('y', ('x',))))),
    (('FORALL', 'x',
      ('EXISTS', '-1', ('FORALL', '-2', ('AND', ('p', ('-1',)), ('q', ()))))),
        ('AND', ('p', (('-1', ('x',)),)), ('q', ()))),
    (('FORALL', 'x',
      ('FORALL', '-1', ('EXISTS', '-2', ('AND', ('p', ('-1',)), ('q', ('-2',)))))),
     ('AND', ('p', ('-1',)), ('q', (('-2', ('x', '-1')),)))),
])
def test_skolemize(formula, skolemized):
    assert p2.skolemize(formula) == skolemized


@pytest.mark.parametrize('zol, cnf', [
    (('OR', ('AND', ('NOT', ('p', ())), ('NOT', ('q', ()))), ('NOT', ('z', ()))),
     frozenset((frozenset((('NOT', ('p', ())), ('NOT', ('z', ())))),
                frozenset((('NOT', ('q', ())), ('NOT', ('z', ()))))))),
    (('NOT', ('p', ())), frozenset((frozenset((('NOT', ('p', ())),)),))),
    (('OR', ('p', ()), ('q', ())),
     frozenset((frozenset((('p', ()), ('q', ()))),))),
    (('OR',
      ('AND', ('p', ()), ('NOT', ('q', ()))),
        ('AND', ('r', ()), ('s', ()))),
        frozenset((
            frozenset((('p', ()), ('r', ()))),
            frozenset((('NOT', ('q', ())), ('r', ()))),
            frozenset((('p', ()), ('s', ()))),
            frozenset((('NOT', ('q', ())), ('s', ())))))),
])
def test_to_cnf(zol, cnf):
    assert p2.to_cnf(zol) == cnf


@pytest.mark.parametrize('s, cnf', [
    ('(NOT (AND (OR (p) (EXISTS q (r))) (z)))',
     frozenset({
         frozenset({('NOT', ('p', ())), ('NOT', ('z', ()))}),
         frozenset({('NOT', ('r', ())), ('NOT', ('z', ()))})
     })),
    ('(OR (FORALL x (AND (p x) (NOT (q)))) (EXISTS y (AND (p y) (q))))',
        frozenset({
            frozenset({('p', ('x',)), ('p', (('y', ()),))}),
            frozenset({('p', ('x',)), ('q', ())}),
            frozenset({('NOT', ('q', ())), ('p', (('y', ()),))}),
            frozenset({('NOT', ('q', ())), ('q', ())})
        })),
    ('(FORALL x (IMPLIES (P x) (Q x)))',
     frozenset({frozenset({('NOT', ('P', ('x',))), ('Q', ('x',))})})),
    ('(P (f a))',
     frozenset({frozenset({('P', (('f', (('a', ()),)),))})})),
    ('(NOT (Q (f a)))',
     frozenset({frozenset({('NOT', ('Q', (('f', (('a', ()),)),)))})})),
    ('(FORALL x (P x))',
     frozenset({frozenset({('P', ('x',))})})),
    ('(NOT (FORALL x (Q x)))',
     frozenset({frozenset({('NOT', ('Q', (('x', ()),)))})})),
    ('(EXISTS x (AND (P x) (Q b)))',
     frozenset({
         frozenset({('Q', (('b', ()),))}),
         frozenset({('P', (('x', ()),))})
     })),
    ('(NOT (NOT (P a)))',
     frozenset({frozenset({('P', (('a', ()),))})})),
    ('(FORALL a (FORALL b (FORALL c (big_f (f a b) (f b c)))))',
     frozenset({frozenset({('big_f', (('f', ('a', 'b')), ('f', ('b', 'c'))))})})),
    ('(NOT (big_f (f a b) (f b c)))',
     frozenset({frozenset({
         ('NOT',
          ('big_f', (
              ('f', (('a', ()), ('b', ()))),
              ('f', (('b', ()), ('c', ()))))))
     })})),
    ('''(FORALL X (FORALL Y (FORALL Z
            (IMPLIES (AND (big_f X Y) (big_f Y Z)) (big_f X Z))
        )))''',
     frozenset({frozenset({
         ('NOT', ('big_f', ('X', 'Y'))),
         ('NOT', ('big_f', ('Y', 'Z'))),
         ('big_f', ('X', 'Z')),
     })})),
])
def test_str_to_cnf(s, cnf):
    assert p2.str_to_cnf(s) == cnf


@pytest.mark.parametrize('substitutions, term, result', [
    ({'x': 'a'}, ('P', ('a',)), ('P', ('a',))),
    ({'x': 'a'}, ('P', ('x',)), ('P', ('a',))),
    ({'x': ('a', ())}, ('P', ('x',)), ('P', (('a', ()),))),
    ({'x': ('a', ())}, ('P', ('x',)), ('P', (('a', ()),))),
    (
        {'x': ('a', ()), 'y': ('g', ('b',)), 'z': ('f', (('g', ('b',)),))},
        ('f', ('x', 'z', 'y')),
        ('f', (('a', ()), ('f', (('g', ('b',)),)), ('g', ('b',))))),
])
def test_substitute(substitutions, term, result):
    assert p2.substitute(substitutions, term) == result

# Terms = find_disagreement_term(('P', (('a', ()), 'y')), ('P', ['x', {'c', ()}]))
# Term = str | str * Tuple[Term]
# 'x'
# ('x', ())
# ('f', ('x',))
# ('f', ('x', 'y'))
# ('f', (('a', ()), 'y'))
# ('f', (('a', ('x',)), 'y'))
# ('f', (('a', (('b', ()),)), 'y')) = f(a(b()), y) (by the way, y is a var) = FUNCTION f (FUNCTION a (FUNCTION b ()), VARIABLE y)


@pytest.mark.parametrize('first_term, second_term, result', [
    ('P', 'Q', ('P', 'Q')),
    (('f', ('x',)), 'x', (('f', ('x',)), 'x')),
    (('f', ('c', ('b', ()))), 'x', (('f', ('c', ('b', ()))), 'x')),
    (('f', ('x',)), ('f', ('y',)), ('x', 'y')),
    (('g', ('x',)), ('f', ('y',)), False),
    (('b', ()), ('c', ()), False),
    (('b', ()), ('b', ()), True),
])
def test_find_disagreement(first_term, second_term, result):
    assert p2.find_disagreement(first_term, second_term) == result


@pytest.mark.parametrize('first_term, second_term, result', [
    ('x', 'y', {'x': 'y'}),
    (('a', ()), ('b', ()), None),
    (('a', ()), ('a', ()), dict()),
    ('x', ('a', ()), {'x': ('a', ())}),
    (
        ('f', ('x',)),
        ('f', (('a', ()),)),
        {'x': ('a', ())}
    ),
    (
        ('P', (('a', ()), 'y')),
        ('P', ('x', ('f', (('b', ()),)))),
        {'x': ('a', ()), 'y': ('f', (('b', ()),))},
    ),
    (
        ('Q', (('f', (('a', ()),)), ('g', ('x',)))),
        ('Q', ('y', 'y')),
        None,
    ),
    (
        ('P', (('a', ()), 'x', ('f', (('g', ('y',)),)))),
        ('P', ('z', ('f', ('z',)), ('f', ('u',)))),
        {'z': ('a', ()), 'x': ('f', (('a', ()),)), 'u': ('g', ('y',))},
    ),
    (
        'x', ('f', ('x',)), None
    )
])
def test_unify(first_term, second_term, result):
    assert p2.unify(first_term, second_term) == result


@pytest.mark.parametrize('clause_one, clause_two, result', [
    (frozenset({
        ('P', ('x',)),
        ('NOT', ('Q', ('x',))),
    }),
        frozenset({
            ('Q', (('a', ()),))
        }),
        frozenset({
            ('P', (('a', ()),))
        })),
    (frozenset({
        ('P', ('x',)),
        ('Q', (('a', ()),))
    }),
        frozenset({
            ('NOT', ('Q', ('x',))),
        }),
        frozenset({
            ('P', (('a', ()),))
        })),
    (frozenset({
        ('Q', (('a', ()),))
    }),
        frozenset({
            ('NOT', ('Q', ('x',))),
            ('P', ('x',)),
        }),
        frozenset({
            ('P', (('a', ()),))
        })),
    (frozenset({
        ('P', ('x',)),
        ('NOT', ('Q', ('x',))),
    }),
        frozenset({
            ('Q', (('b', ()),))
        }),
        frozenset({
            ('P', (('b', ()),))
        })),
    (frozenset({
        ('P', (('a', ()),)),
    }),
        frozenset({
            ('NOT', ('P', (('a', ()),))),
        }),
        frozenset()),
    (frozenset({
        ('P', (('a', ()),)),
    }),
        frozenset({
            ('NOT', ('P', (('b', ()),))),
        }),
        None),
    (frozenset({
        ('P', (('a', ()),)),
    }),
        frozenset({
            ('NOT', ('P', (('a', ()),))),
            ('NOT', ('P', (('b', ()),))),
        }),
        frozenset({
            ('NOT', ('P', (('b', ()),))),
        })),
    (frozenset({
        ('P', (('a', ()),)),
    }),
        frozenset({
            ('NOT', ('Q', (('a', ()),))),
        }),
        None),
    (frozenset({
        ('P', (('a', ()),)),
    }),
        frozenset({
            ('Q', (('a', ()),)),
        }),
        None),
])
def test_resolve(clause_one, clause_two, result):
    assert p2.resolve(clause_one, clause_two) == result


@pytest.mark.parametrize('clauses, seconds', [
    (frozenset({
        frozenset({
            ('P', ('x',)),
            ('NOT', ('Q', ('x',)))
        }),
        frozenset({
            ('Q', (('a', ()),))
        }),
        frozenset({
            ('NOT', ('P', (('a', ()),)))
        }),
        frozenset({
            ('Q', (('b', ()),))
        })
    }), 0),
    (frozenset({
        frozenset({
            ('P', ('x',)),
            ('NOT', ('Q', ('x',)))
        }),
        frozenset({
            ('Q', (('a', ()),))
        }),
        frozenset({
            ('NOT', ('P', (('a', ()),)))
        }),
    }), 0),
])
def test_find_contradiction(clauses, seconds):
    with p2.timeout(seconds, lambda: pytest.fail('Timed out')):
        assert p2.find_contradiction(clauses)


@pytest.mark.parametrize('clauses, seconds', [
    (frozenset({
        frozenset({
            ('P', ('x',)),
            ('NOT', ('Q', ('x',)))
        }),
        frozenset({
            ('Q', (('a', ()),))
        }),
        frozenset({
            ('Q', (('b', ()),))
        })
    }), 1),
])
def test_find_contradiction_failure(clauses, seconds):
    with p2.timeout(seconds):
        assert not p2.find_contradiction(clauses)

#                 __  __    ______  _____   ____     __    __
#                /\ \/\ \  /\  _  \/\  _ `\/\  _`\  /\ \  /\ \
#                \ \ \_\ \ \ \ \L\ \ \ \L\ \ \ \L\ \\ `\`\\/'/
#                 \ \  _  \ \ \  __ \ \ ,__/\ \ ,__/ `\ `\ /'
#                  \ \ \ \ \ \ \ \/\ \ \ \/  \ \ \/    `\ \ \
#                   \ \_\ \_\ \ \_\ \_\ \_\   \ \_\      \ \_\
#                    \/_/\/_/  \/_/\/_/\/_/    \/_/       \/_/


#  __  __  ______  __      __      _____   __      __  _____  _____  __  __
# /\ \/\ \/\  _  \/\ \    /\ \    /\  __`\/\ \  __/\ \/\  __\/\  __\/\ \/\ \
# \ \ \_\ \ \ \L\ \ \ \   \ \ \   \ \ \/\ \ \ \/\ \ \ \ \ \_/_ \ \_/_ \ `\\ \
#  \ \  _  \ \  __ \ \ \  _\ \ \  _\ \ \ \ \ \ \ \ \ \ \ \  __\ \  __\ \ , ` \
#   \ \ \ \ \ \ \/\ \ \ \_\ \ \ \_\ \ \ \_\ \ \ \_/ \_\ \ \ \/__ \ \/__ \ \`\ \
#    \ \_\ \_\ \_\ \_\ \____/\ \____/\ \_____\ `\___x___/\ \____\ \____\ \_\ \_\
#     \/_/\/_/\/_/\/_/\/___/  \/___/  \/_____/'\/__//__/  \/____/\/____/\/_/\/_/

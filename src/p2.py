"""Main file that will be executed by the grader."""

import string


def lex(formula):
    """Stream tokens from the given formula."""
    index = 0

    while index < len(formula):
        char = formula[index]
        if char == '(':
            index += 1
            yield '('
        elif char == ')':
            index += 1
            yield ')'
        elif char == 'F':
            token = 'FORALL'
            length = len(token)
            if formula[index + 1: (index + length)] != 'ORALL':
                return
            index += length
            yield token
        elif char == 'E':
            token = 'EXISTS'
            length = len(token)
            if formula[index + 1: (index + length)] != 'XISTS':
                return
            index += length
            yield token
        elif char == 'A':
            token = 'AND'
            length = len(token)
            if formula[index + 1: (index + length)] != 'ND':
                return
            index += length
            yield token
        elif char == 'O':
            token = 'OR'
            length = len(token)
            if formula[index + 1: (index + length)] != 'R':
                return
            index += length
            yield token
        elif char == 'I':
            token = 'IMPLIES'
            length = len(token)
            if formula[index + 1: (index + length)] != 'MPLIES':
                return
            index += length
            yield token
        elif char == 'N':
            token = 'NOT'
            length = len(token)
            if formula[index + 1: (index + length)] != 'OT':
                return
            index += length
            yield token
        elif char in string.whitespace:
            while True:
                index += 1
                char = formula[index]
                if char not in string.whitespace:
                    break
        else:
            result = []
            while True:
                if char in string.whitespace or char in {'(', ')'}:
                    yield ''.join(result)
                    break

                result.append(char)
                index += 1
                char = formula[index]


class ParseError(Exception):
    pass


class _Parser:
    __slots__ = (
        'peek_token',
        'tokens',
    )

    def __init__(self, tokens):
        self.peek_token = None
        self.tokens = tokens

    def formula(self):
        token = self._next()

        if token != '(':
            return token

        expr = self._expr()
        self._expect(')')
        return expr

    def _expect(self, token):
        if self._next() != token:
            raise ParseError

    def _expr(self):
        token = self._next()
        if token in {'FORALL', 'EXISTS'}:
            return token, self._next(), self.formula()
        if token in {'AND', 'OR', 'IMPLIES'}:
            return token, self.formula(), self.formula()
        if token == 'NOT':
            return token, self.formula()
        return token, self._terms()

    def _next(self):
        if self.peek_token is not None:
            token = self.peek_token
            self.peek_token = None
            return token

        return next(self.tokens)

    def _terms(self):
        terms = []
        while True:
            token = self._peek()
            if token == ')':
                return tuple(terms)
            if token == '(':
                self._next()
                terms.append(self._sub_term())
            else:
                self._next()
                terms.append(token)

    def _peek(self):
        if self.peek_token is None:
            try:
                self.peek_token = next(self.tokens)
            except StopIteration as e:
                raise ParseError from e
        return self.peek_token

    def _sub_term(self):
        root = self._next()
        if root in {'(', ')'}:
            raise ParseError
        terms = []
        while True:
            token = self._next()
            if token == ')':
                return root, tuple(terms)
            if token == '(':
                terms.append(self._sub_term())
            else:
                terms.append(token)


def parse(formula_tokens):
    """Parse the formula tokens into an abstract syntax tree."""
    return _Parser(formula_tokens).formula()


def normalize(formula):
    """Get the normalized form of the formula."""
    def positive(formula):
        tag, *args = formula

        if tag in {'FORALL', 'EXISTS'}:
            return tag, args[0], positive(args[1])
        if tag == 'IMPLIES':
            return 'OR', negative(args[0]), positive(args[1])
        if tag in {'AND', 'OR'}:
            return tag, positive(args[0]), positive(args[1])
        if tag == 'NOT':
            return negative(args[0])
        return formula

    def negative(formula):
        tag, *args = formula

        if tag == 'FORALL':
            return 'EXISTS', args[0], negative(args[1])
        if tag == 'EXISTS':
            return 'FORALL', args[0], negative(args[1])
        if tag == 'IMPLIES':
            return 'AND', positive(args[0]), negative(args[1])
        if tag == 'AND':
            return 'OR', negative(args[0]), negative(args[1])
        if tag == 'OR':
            return 'AND', negative(args[0]), negative(args[1])
        if tag == 'NOT':
            return positive(args[0])
        return 'NOT', formula

    return positive(formula)


def standardize(formula):
    """Generate an equivalent normalized formula with unique variables."""
    fresh = -1  # negative since input cannot have '-' character
    variables = set()

    def substitute(term, substitutions):
        if isinstance(term, tuple):
            return (term[0], tuple(substitute(subterm, substitutions)
                                   for subterm in term[1]))

        return substitutions.get(term, term)

    def recur(formula, substitutions):
        nonlocal fresh
        tag, *args = formula

        if tag in {'FORALL', 'EXISTS'}:
            var = args[0]

            if var in variables:
                new_var = str(fresh)
                fresh -= 1
                substitutions = substitutions.copy()
                substitutions[var] = new_var
                var = new_var

            variables.add(var)
            return tag, var, recur(args[1], substitutions)

        if tag in {'AND', 'OR'}:
            return (tag,
                    recur(args[0], substitutions),
                    recur(args[1], substitutions))

        if tag == 'NOT':
            return tag, recur(args[0], substitutions)

        if isinstance(formula, str):
            return formula

        return tag, tuple(substitute(term, substitutions) for term in args[0])

    return recur(formula, dict())


def prenex(formula):
    """Generate an equivalent prenex formula."""
    tag, *args = formula

    if tag in {'FORALL', 'EXISTS'}:
        return tag, args[0], prenex(args[1])

    if tag in {'AND', 'OR'}:
        fst, snd = map(prenex, args)
        fst_tag = fst[0]
        snd_tag = snd[0]
        if fst_tag in {'FORALL', 'EXISTS'}:
            if snd_tag in {'FORALL', 'EXISTS'}:
                return fst_tag, fst[1], (snd_tag, snd[1], (tag, fst[2], snd[2]))
            return fst_tag, fst[1], (tag, fst[2], snd)
        if snd_tag in {'FORALL', 'EXISTS'}:
            return snd_tag, snd[1], (tag, fst, snd[2])
        return formula

    return formula


def skolemize(formula):
    """Generate an equivalent skolemized formula."""
    def substitute(term, substitutions):
        if isinstance(term, tuple):
            return (term[0], tuple(substitute(subterm, substitutions)
                                   for subterm in term[1]))

        return substitutions.get(term, term)

    def recur(formula, quantifiers, substitutions):
        tag, *args = formula

        if tag == 'FORALL':
            var = args[0]

            return (tag, var,
                    recur(args[1],
                          (quantifiers + (var,)) if var not in quantifiers
                          else quantifiers,
                          substitutions))

        if tag == 'EXISTS':
            var = args[0]

            substitutions = substitutions.copy()
            substitutions[var] = (var, quantifiers)

            return recur(args[1], quantifiers, substitutions)

        if tag in {'AND', 'OR'}:
            return (tag,
                    recur(args[0], quantifiers, substitutions),
                    recur(args[1], quantifiers, substitutions))

        if tag == 'NOT':
            return tag, recur(args[0], quantifiers, substitutions)

        if isinstance(formula, str):
            return formula

        return tag, tuple(substitute(term, substitutions) for term in args[0])

    return recur(formula, (), dict())


def drop_universals(formula):
    """Generate an equivalent ZOL formula and its set of universals."""
    universals = set()

    while formula[0] == 'FORALL':
        universals.add(formula[1])
        formula = formula[2]

    return formula, frozenset(universals)


def to_cnf(formula):
    """Generate an equivalent CNF formula from a ZOL formula."""
    tag, *args = formula

    if tag == 'AND':
        return to_cnf(args[0]) | to_cnf(args[1])

    if tag == 'OR':
        return frozenset(fst | snd
                         for fst in to_cnf(args[0])
                         for snd in to_cnf(args[1]))

    return frozenset((frozenset((formula,)),))


def str_to_cnf_universals(string):
    """Parse an input string into a CNF formula and its universals."""
    formula, universals = drop_universals(
        skolemize(
            prenex(
                standardize(
                    normalize(
                        parse(lex(string))
                    )
                )
            )
        )
    )
    return to_cnf(formula), universals


def unify(clause_one, clause_two, variables):
    """Unify each clause, producing the result clause or None."""


def findIncSet(fSets):  # noqa
    """Find indices of inconsistent formula lists.

    Given a list of lists of first-order logic formulas,
    finds the zero-indexed indices of inconsistent lists of formulas.
    See README.md for detailed specification.

    :param fSets: list of formula lists
    :return: returns the list of inconsistent zero-indexed indices
    """
    return []  # TODO:

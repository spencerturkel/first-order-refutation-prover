"""Main file that will be executed by the grader."""

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

import signal
import string
from contextlib import contextmanager
from itertools import chain


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


class _CnfParser:
    __slots__ = (
        'fresh_num',
        'negated',
        'peek_token',
        'tokens',
        'substitutions',
        'universal_context',
        'variables',
    )

    def __init__(self, tokens):
        self.fresh_num = -1
        self.negated = False
        self.peek_token = None
        self.tokens = tokens
        self.universal_context = []
        self.substitutions = dict()
        self.variables = set()

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
        if self.negated:
            if token == 'FORALL':
                # ~ forall x, p x = exists x, ~ p x
                return self._existential()
            if token == 'EXISTS':
                # ~ exists x, p x = forall x, ~ p x
                return self._universal()
            if token == 'AND':
                # ~ (p /\ q) = ~ p \/ ~ q
                left = self.formula()
                right = self.formula()
                return frozenset(l | r for l in left for r in right)
            if token == 'OR':
                # ~ (p \/ q) = ~ p /\ ~ q
                return self.formula() | self.formula()
            if token == 'IMPLIES':
                # ~ (p -> q) = ~ (~ p \/ q) = p /\ ~ q
                self.negated = False
                antecedent = self.formula()
                self.negated = True
                return antecedent | self.formula()
            if token == 'NOT':
                # ~ ~ p = p
                self.negated = False
                formula = self.formula()
                self.negated = True
                return formula
            return frozenset((
                frozenset((
                    ('NOT', (token, self._terms())),
                )),
            ))

        if token == 'FORALL':
            return self._universal()
        if token == 'EXISTS':
            return self._existential()
        if token == 'AND':
            return self.formula() | self.formula()
        if token == 'OR':
            left = self.formula()
            right = self.formula()
            return frozenset(l | r for l in left for r in right)
        if token == 'IMPLIES':
            # p -> q = ~ p \/ q
            self.negated = True
            antecedent = self.formula()
            self.negated = False
            consequent = self.formula()
            return frozenset(l | r for l in antecedent for r in consequent)
        if token == 'NOT':
            self.negated = True
            formula = self.formula()
            self.negated = False
            return formula
        return frozenset((
            frozenset((
                (token, self._terms()),
            )),
        ))

    def _next(self):
        if self.peek_token is not None:
            token = self.peek_token
            self.peek_token = None
            return token

        return next(self.tokens)

    def _existential(self):
        ex_quantifier = self._quantified_variable()
        self.substitutions[ex_quantifier] = (
            ex_quantifier, tuple(self.universal_context))
        formula = self.formula()
        del self.substitutions[ex_quantifier]
        return formula

    def _universal(self):
        quantifier = self._quantified_variable()
        self.variables.add(quantifier)
        self.universal_context.append(quantifier)
        formula = self.formula()
        self.universal_context.pop()
        return formula

    def _quantified_variable(self):
        var = self._next()
        if var in self.variables:
            var = str(self.fresh_num)
            self.fresh_num -= 1
        return var

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
                terms.append(token if token in self.variables
                             else self.substitutions.get(token, (token, ())))

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
                terms.append(token if token in self.variables
                             else self.substitutions.get(token, (token, ())))


def parse(formula_tokens):
    """Parse the token stream into CNF."""
    return _CnfParser(formula_tokens).formula()


def str_to_cnf(string):
    """Parse the input string into CNF."""
    return parse(lex(string))


def find_disagreement(first_term, second_term):
    """Finds the disagreement set of the terms."""
    term_pair_queue = [(first_term, second_term)]

    while term_pair_queue:
        first_term, second_term = term_pair_queue.pop(0)

        if isinstance(first_term, tuple) and isinstance(second_term, tuple):

            if first_term[0] == second_term[0]:
                term_pair_queue.extend(zip(first_term[1], second_term[1]))
                continue

            return False

        if first_term == second_term:
            continue

        return (first_term, second_term)

    return True


def variable_in_term(variable, term):
    term_stack = [term]
    while term_stack:
        term = term_stack.pop()
        if isinstance(term, str):
            if term == variable:
                return True
        else:
            term_stack.extend(term[1])
    return False


def substitute(substitutions, term):
    """Substitutes the given substitution dict into the term."""
    if isinstance(term, str):
        return substitutions.get(term, term)

    fun, arguments = term
    return fun, tuple(substitute(substitutions, arg) for arg in arguments)


def unify(term_one, term_two):
    """Unifies the terms, producing the most general unifier or None."""
    substitutions = dict()

    while True:
        disagreement = find_disagreement(term_one, term_two)

        if disagreement is False:
            return None

        if disagreement is True:
            return substitutions

        if isinstance(disagreement[0], str):
            variable, term = disagreement
        else:
            term, variable = disagreement

        if variable_in_term(variable, term):
            return None

        new_substitution = {variable: term}
        substitutions.update(new_substitution)
        term_one = substitute(new_substitution, term_one)
        term_two = substitute(new_substitution, term_two)


def resolve(left_clause, right_clause):
    """Resolve the clauses, producing the resolvent clause or None."""
    for literal in left_clause:
        if literal[0] == 'NOT':
            literal = literal[1]
            predicate = literal[0]
            match = next((l for l in right_clause if l[0] == predicate), None)
            if match is None:
                continue

            unifier = unify(literal, match)

            if unifier is None:
                continue

            result = frozenset(
                (('NOT', substitute(unifier, lit[1]))
                 if lit[0] == 'NOT'
                 else substitute(unifier, lit))
                for lit in chain(left_clause, right_clause)
                if lit not in (('NOT', literal), match)
            )

            return result

        predicate = literal[0]
        match = next((l[1] for l in right_clause
                      if l[0] == 'NOT' and l[1][0] == predicate), None)
        if match is None:
            continue

        unifier = unify(literal, match)

        if unifier is None:
            continue

        result = frozenset(
            (('NOT', substitute(unifier, lit[1]))
                if lit[0] == 'NOT'
                else substitute(unifier, lit))
            for lit in chain(left_clause, right_clause)
            if lit not in (('NOT', match), literal)
        )

        return result

    for literal in right_clause:
        if literal[0] == 'NOT':
            literal = literal[1]
            predicate = literal[0]
            match = next(
                (l for l in left_clause if l[0] == predicate), None)
            if match is None:
                continue

            unifier = unify(literal, match)

            if unifier is None:
                continue

            result = frozenset(
                (('NOT', substitute(unifier, lit[1]))
                 if lit[0] == 'NOT'
                 else substitute(unifier, lit))
                for lit in chain(left_clause, right_clause)
                if lit not in (('NOT', literal), match)
            )

            return result

        predicate = literal[0]
        match = next((l for l in left_clause
                      if l[0] == 'NOT' and l[1][0] == predicate), None)
        if match is None:
            continue

        unifier = unify(literal, match)

        if unifier is None:
            continue

        result = frozenset(
            (('NOT', substitute(unifier, lit[1]))
                if lit[0] == 'NOT'
                else substitute(unifier, lit))
            for lit in chain(left_clause, right_clause)
            if lit not in (literal, ('NOT', match))
        )

        return result

    return None


def find_contradiction(clauses):
    clause_stack = list(clauses)
    while clause_stack:
        left_clause = clause_stack.pop()
        new_clauses = []
        for right_clause in clauses:
            resolvent = resolve(left_clause, right_clause)
            if resolvent is not None:
                if resolvent == frozenset():
                    return True
                new_clauses.append(resolvent)
        if new_clauses:
            clause_stack.extend(new_clauses)

    return False


@contextmanager
def timeout(seconds, on_timeout=lambda: None):
    """Run a context for a certain number of seconds.

    An optional handler callback will be called if the context times out.
    """
    def on_signal():
        raise TimeoutError
    signal.signal(signal.SIGALRM, lambda _1, _2: on_signal())
    # signal.alarm(seconds)
    try:
        yield
    except TimeoutError:
        on_timeout()
    finally:
        signal.alarm(0)


def is_inconsistent(formulae, limit_seconds):
    cnf = set()
    for formula in formulae:
        cnf |= str_to_cnf(formula)
    with timeout(limit_seconds):
        return find_contradiction(cnf)


def findIncSet(fSets):  # noqa
    """Find indices of inconsistent formula lists.

    Given a list of lists of first-order logic formulas,
    finds the zero-indexed indices of inconsistent lists of formulas.
    See README.md for detailed specification.

    :param fSets: list of formula lists
    :return: returns the list of inconsistent zero-indexed indices
    """
    result_indices = []
    for index, formulae in enumerate(fSets):
        try:
            if is_inconsistent(formulae, 10):
                result_indices.append(index)
        except:  # noqa
            continue

    return result_indices

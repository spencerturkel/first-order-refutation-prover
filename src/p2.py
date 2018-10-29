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

import string
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

    while formula[0] == 'FORALL':
        formula = formula[2]

    return formula


def to_cnf(formula):
    # """Generate an equivalent CNF formula from a ZOL formula."""
    tag, *args = formula

    if tag == 'AND':
        return to_cnf(args[0]) | to_cnf(args[1])

    if tag == 'OR':
        return frozenset(fst | snd
                         for fst in to_cnf(args[0])
                         for snd in to_cnf(args[1]))
    return frozenset((frozenset((formula,)),))


def str_to_cnf(string):
    """Parse an input string into a CNF formula."""
    return to_cnf(drop_universals(skolemize(prenex(standardize(normalize(
        parse(lex(string))))))))

# brute force resoluton, calls unification until empty clause is given or time limit is reached


def substitute(substitutions, term):
    """Substitutes the given substitution dict into the term."""
    if isinstance(term, str):
        return substitutions.get(term, term)

    fun, arguments = term
    return fun, tuple(substitute(substitutions, arg) for arg in arguments)


def find_disagreement(first_term, second_term):
    """Finds the disagreement set of the terms."""
    # TODO: make this iterative rather than recursive
    if isinstance(first_term, tuple) and isinstance(second_term, tuple):
        if first_term[0] == second_term[0]:
            for a1, a2 in zip(first_term[1], second_term[1]):
                sub_result = find_disagreement(a1, a2)
                if sub_result is False:
                    return False
                if sub_result is True:
                    continue
                return sub_result
            return True
        else:
            return False
    elif first_term == second_term:
        return True
    else:
        return (first_term, second_term)


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
            predicate, first_arg_list = literal
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
                if lit != ('NOT', literal) and lit != match
            )

            return result
        else:
            predicate, first_arg_list = literal
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
                if lit != literal and lit != ('NOT', match)
            )

            return result
    for literal in right_clause:
        if literal[0] == 'NOT':
            literal = literal[1]
            predicate, first_arg_list = literal
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
                if lit != ('NOT', literal) and lit != match
            )

            return result
        else:
            predicate, first_arg_list = literal
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
                if lit != literal and lit != ('NOT', match)
            )

            return result

    return None


def find_contradiction(clauses):
    return False

# def find_contradiction(setOfClauses):
    # # returns true if inconsistent, returns false if no empty clause is found
    # somethingUnified = False
    # for indexClause, clause in enumerate(setOfClauses):
    #     for indexTerm, term in enumerate(clause):
    #         # finds all positive predicates counterpart to a negative predicate
    #         if term == 'NOT':
    #             currentTerm = clause[indexTerm+1][0]
    #             indexCheckClause = indexClause+1
    #             # loops through rest of clauses to find any stuff to unify
    #             while indexCheckClause < len(setOfClauses):
    #                 for indexCheckTerm, checkTerm in enumerate(setOfClauses[indexCheckClause]):
    #                     if checkTerm[0] == currentTerm:
    #                         newClause = unification(
    #                             setOfClauses[indexClause]), setOfClauses[indexCheckCLause]
    #                         # return True if inconsistent
    #                         # comment these out if you want to see what two clauses will be unified
    #                         if newClause == []:
    #                             return True
    #                         elif newClause == None:
    #                             pass
    #                         else:
    #                             setOfClauses = setOfClauses + newClause
    #                             somethingUnified = True
    #                         # print(
    #                             # "RESOLVE THESE2",  setOfClauses[indexClause], setOfClauses[indexCheckClause])
    #                 indexCheckClause += 1
    #         # finds all negative predicate counterparts to a positive predicate
    #         else:
    #             if term[0] != 'NOT':
    #                 currentTerm = term[0]
    #                 indexCheckClause = indexClause+1
    #                 # loops through rest of clauses to find any stuff to unify
    #                 while indexCheckClause < len(setOfClauses):
    #                     for indexCheckTerm, checkTerm in enumerate(setOfClauses[indexCheckClause]):
    #                         if checkTerm == 'NOT':
    #                             checkTerm = setOfClauses[indexCheckClause][indexCheckTerm+1][0]
    #                             if checkTerm == currentTerm:
    #                                 newClause = unification(
    #                                     setOfClauses[indexClause]), setOfClauses[indexCheckCLause]
    #                                 # return True if inconsistent
    #                                 # comment these out if you want to see what two clauses will be unified
    #                                 if newClause == []:
    #                                     return True
    #                                 elif newClause == None:
    #                                     pass
    #                                 else:
    #                                     setOfClauses = setOfClauses + newClause
    #                                     somethingUnified = True
    #                                 # print(
    #                                     # "RESOLVED3",  setOfClauses[indexClause], setOfClauses[indexCheckClause])

    #                         elif checkTerm[0] == 'NOT':
    #                             if checkTerm[1] == currentTerm:
    #                                 newClause = unification(
    #                                     setOfClauses[indexClause]), setOfClauses[indexCheckCLause]
    #                                 # return True if inconsistent
    #                                 # comment these out if you want to see what two clauses will be unified
    #                                 if newClause == []:
    #                                     return True
    #                                 elif newClause == None:
    #                                     pass
    #                                 else:
    #                                     setOfClauses = setOfClauses + newClause
    #                                     somethingUnified = True
    #                                 # print(
    #                                     # "RESOLVED4",  setOfClauses[indexClause], setOfClauses[indexCheckClause])
    #                     indexCheckClause += 1
    # # if a new clause was added, resolve new list of clauses
    # if somethingUnified:
    #     if find_contradiction(setOfClauses):
    #         return True
    #     else:
    #         return False
    # else:
    #     return False


def findIncSet(fSets):  # noqa
    """Find indices of inconsistent formula lists.

    Given a list of lists of first-order logic formulas,
    finds the zero-indexed indices of inconsistent lists of formulas.
    See README.md for detailed specification.

    :param fSets: list of formula lists
    :return: returns the list of inconsistent zero-indexed indices
    """
    return []  # TODO:

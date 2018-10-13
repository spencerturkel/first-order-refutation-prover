[![Build Status](https://travis-ci.com/spencerturkel/first-order-refutation-prover.svg?token=gm1zuwtz6yWqd9Rwapxf&branch=master)](https://travis-ci.com/spencerturkel/first-order-refutation-prover)

# Introduction

This project was the second project for the Computationally Modelling Reasoning course at the University of South Florida taught by Dr. Licato.
It is released under the MIT License, with the copyright attributed to Spencer Turkel, Jacob Schioppo, Matthew Monnik, and Zachary Meyer.

Our assignment is to identify inconsistent sets of of formulae in
[First-Order Logic](https://en.wikipedia.org/wiki/First-order_logic).

# Assignment - Due 11/1 (Presentations 10/30)

## Requirements

- You will write a refutation prover for FOL using first-order resolution (described in next lecture)
- You will solve the “find inconsistent sets” task, but have some clever innovation(s) to make it better.
- Must work in Python 3.4+ without any special libraries to be installed
- Submit a file p2.py with no outputting code (print or any similar statements) at any level. This file should have a function findIncSet(fSets), where:
  - fSets: A list (the master list) containing lists (the formula sets) of strings.
  - Each string is an S-expression of a well-formed FOL formula.
    - All non-operator symbols will be lower-case alphanumberic strings
    - All formulae are well-formed; all non-quantified objects are actually objects (and vice versa)
    - Roughly 50 percent of the formula sets are inconsistent
    - The number of formula sets will be between 2 and 10,000,000.
  - Your code will return a list of integers:
    - These integers correspond to the indices of the formula sets that you believe are inconsistent.
    - Indices should be zero-indexed: the first formula set in the master list has the index ‘0’.
    - No whitespace, newline characters, etc. Just integers (not strings!) separated by commas.
  - Grading:
    - You start with 100 points (see rubric on next slide; this component is approximately 65% of the grade for this project)
- **It is crucial that you work together intelligently on this**. Perhaps one person can write the convertor to CNF, one can write the unification algorithm, one can do rigorous testing of all modules, one can design the selection heuristic, etc. **There is a lot of work to do for this project --- avoid working alone!**

## Rubric

- Groups of up to 4
- Your group will also give a 10-minute presentation explaining your algorithm’s uniqueness---do not waste time explaining basics!
- At the end of the day, there will be a competition for the fastest FOL prover; winner will get bonus points
  - My code will import your “p2.py” once, and call the function `findIncSet()` multiple times
  - If it fails on any instance (exception or wrong answer), it’s disqualified
  - The fastest overall time wins
- RUBRIC:
  - 75% - Code quality
    - 65% - Code is a variant of FO-resolution, satisfies all requirements in previous slide, runs correctly
      - This component is calculated by starting with 100 points:
        - Let n be the number of formula sets in the input
        - If you output the index of a formula set that is not inconsistent, then you lose 100/n points.
        - If you fail to output the index of a formula set that is inconsistent, then you lose 100/n points.
        - If you output an invalid index, a string in an invalid format, or generate an exception, then you lose 100 points. **TEST YOUR CODE!**
    - 10% - Your variant of FO-resolution must be clever; creative; non-trivial (or if you take this idea from somewhere, properly cite it)
  - 25% - Presentation
    - 5% - Time limit (not too short or long)
    - 5% - Workload appeared shared
    - 15% - Presentation was clear, algorithm easy to understand (peer reviewed)
  - 10% - Bonus for winning competition

## Recommended Timeline

- **10/12** - Unification algorithm complete
- **10/19** - FOL-to-CNF algorithm complete, Resolution algorithm complete
- **10/26** - Novel heuristic and presentation complete, testing complete
- **10/31** - 11/1 - Presentations
- **11/1** - Submit code

# Formula Specification

## Tokens

- `(`
- `)`
- `UCONST`
- `ECONST`
- `FORALL`
- `EXISTS`
- `CONTR`
- `AND`
- `OR`
- `IMPLIES`
- `NOT`
- `[a-z0-9]+`

## Grammar

Let `ε` be the empty string.

```
formula = ( expr )
expr = FORALL symbol formula
     | EXISTS symbol formula
     | AND formula formula
     | OR formula formula
     | IMPLIES formula formula
     | NOT formula
     | CONTR
     | UCONST symbol
     | ECONST symbol formula
     | symbol objects
indices = index trailing-indices | ε
objects = symbol objects | formula objects | ε
```

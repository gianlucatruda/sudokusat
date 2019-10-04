# Sudokusat

A general-purpose SAT solver with tools for investigating the properties of sudoku puzzles encoded in clausal normal form.

## Contents
* [Installation](#installation)
* [Usage](#usage)
* [Implementation](#implementation)

## Installation
There are two ways you can install and use *Sudokusat*

### A simple SAT solver CLI

To use *Sudokusat* as a simple CLI SAT solver, there are only a few requirements.

Ensure you have `Python 3.5+` and the `pip` package manager installed, then install the base-requirements with the following command:

```bash
python3 -m pip install -r requirements.txt
```

### A comprehensive testing suite

To use *Sudokusat* to its full potential as an experimental tool, you need to install more libraries. For this, we recommend using a python virtual environment and the `pipenv` tool, then running.

Create a new project:

```bash
cd sudokusat
pipenv --three
```
Then install all dependencies (in dev mode):

```bash
pipenv install --dev
```

You'll now want to check out `tester.py` and its options by running:

```bash
python3 tester.py -h
```


## Usage

The `SAT.py` file is the primary command-line interface for *Sudokusat*. 

### Sudoku example

Try solving a sample sudoku (with rules) in CNF form:

```bash
python3 SAT.py test-sat.txt --sudoku
```

This will generate the solution using the random splitting heuristic (default). You should get an output like this:

```
Using random_split heuristic
2019-10-04 13:26:20.880 | WARNING  | algorithm:solve:60 - SAT
Satisfiable
[[7 9 4 5 8 2 1 3 6]
 [2 6 8 9 3 1 7 4 5]
 [3 1 5 4 7 6 9 8 2]
 [6 8 9 7 1 5 3 2 4]
 [4 3 2 8 6 9 5 7 1]
 [1 5 7 2 4 3 8 6 9]
 [8 2 1 6 5 7 4 9 3]
 [9 4 3 1 2 8 6 5 7]
 [5 7 6 3 9 4 2 1 8]]
2019-10-04 13:26:20.892 | WARNING  | __main__:<module>:73 - <algorithm.Solver metrics={'heuristic': 'random_split', 'simplifications': 39, 'splits': 1, 'backtracks': 0, 'calls:': 3}
```

### General SATs

The following command solves a uniform SAT problem using MOMS heuristic and outputs the variable states to a specified file.

```bash
python3 SAT.py -S2 data/satlib/uniform/uf50-218/uf50-0897.cnf -o uf50-0897.out
``` 

NOTE: You would need to download the `uf50-218` dataset from SATLIB for this to work.

### Full Sudokusat options

You can view all the *Sudokusat* options at any time with the following command:

```bash
python3 SAT.py -h
```

You should get this help message:

```
usage: SAT.py [-h] [-o O] [-S {1,2,3}] [-b B] [--sudoku]
              [-l {DEBUG,INFO,WARNING}]
              input_file

General purpose SAT solver for sukoku applications.

positional arguments:
  input_file            The path of a DIMACS file to solve.

optional arguments:
  -h, --help            show this help message and exit
  -o O                  The path to write the DIMACS output to.
  -S {1,2,3}            Specify which heuristic strategy to use. (1) Random,
                        (2) MOMs, (3) 2-sided JW. Default is 1.
  -b B                  Specify after how many backtracks the solver should
                        timeout. Default 400.
  --sudoku              If the SAT problem is a sudoku, then print the
                        solution in a grid format.
  -l {DEBUG,INFO,WARNING}
                        The log level to use for stdout.
```



## Implementation

Sudokusat implements the DPLL algorithm to solve CNF expressions using the Python 3 language. The `Solver` class contains a private `__dpll()` function which can be recursively called to divide the SAT problem into a binary tree search space. The Solver instance is provided with some CNF expression `sigma` in the form of a 2-dimensional List of integers. This is used to construct a dictionary of `literal:value` pairs for the absolute value of each unique variable seen in the clauses. The value of each literal is initially set to `None` but is updated to a Boolean value through the DPLL procedure. 

The `Solver` class stores the counts of the total function calls, simplifications, split steps, and backtracks over the course of a single problem. This facilitates seamless persistence of performance metrics whilst executing the recursive `__dpll()` function.

*Sudokusat* is comprised of a number of modules:

-   `algorithm.py` houses the `Solver` class and a pure function
    `verifysat()` that is used to ensure the values returned from the
    solver instance satisfy the original PL expression.
-   `heuristics.py` contains the splitting heuristics as pure functions.
    Each takes in the expression and the current literal:value lookup
    and returns a predicate and proposed value.
-   `iotools.py` holds functions for reading DIMACS files and sudoku
    data files and constructing PL expressions from them in the form of
    a 2D List of positive and negative integers.
-   `SAT.py` is a command-line interface to allow easy usage of
    *Sudokusat* with a variety of options.
-   `simplifications.py` contains three impure functions for performing
    the simplifications necessary under the DPLL procedure: detection
    and removal of (1) tautologies, (2) unit clauses, and (3) pure
    literals. These functions are able to modify the values stored in
    the literal:value lookup.
-   `sudokuverifier.py` is used for sudoku-specific checks. It contains
    a function that verifies that a solution returned by *Sudokusat*
    complies with all sudoku rules and does not override the starting
    cells. Another function makes use of *numpy* matrices to build a
    spacial representation of the sudoku solution for visual inspection.

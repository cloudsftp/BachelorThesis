# Quantum Computing for Smart Energy Systems

This is the code for the bachelor thesis "Quantum Computing for Smart Energy Systems".
It contains Python code to run the experiments described in the document and produce the figures that compare the performance of the different solvers.

### Contents

1. Requirements
1. How to set everything up
1. How to run the experiments
1. How to generate the figures

## Requirements

- Linux (Code tested on Ubuntu 20.04 and CentOS 8).
- Preferably `bash` as the terminal (default on most distributions).
- The Python packages are managed by Anaconda. So please go ahead and install Anaconda from the official [website](https://www.anaconda.com/products/individual#Downloads).


## Setup

1. Install Python packages via `./install_conda_environment.sh`. This sets up the Anaconda environment `opt`.
2. Install Couenne if you want to execute the experiments on a classial computer. Refer to [this](Classical/COIN-OR/README.md) document for instructions.
1. Activate the environment and environment variables for Couenne via `source setup.sh`.


TODO: rewrite rest of document

## Standards

The result of experiments will be saved in files that follow the rule:

`(classical|annealing|gatebased)_\d{3}_\d{3}.json`

Where the first number indicates the number of loads and the second number indicates the number of power plants.

### Experiment Runners

The experiment runners have the following command line options:
- `--one-shot` Turns off range mode. Lower bounds are used as parameters.
- `-ll --lower-loads` Lower bound of number of loads. (standard: 2)
- `-ul --upper-loads` Upper bound of number of loads. (standard: 20)
- `-sl --step-loads` Steps size of range of number of loads. (standard: 2)
- `-lp --lower-plants` Lower bound of number of plants. (standard: 2)
- `-up --upper-plants` Upper bound of number of plants. (standard: 20)
- `-sp --step-plants` Step size of range of number of plants. (standard: 2)

TODO: list runners and execution

## Experiment Runners

The experiment result analyzer has the following command line options:
- `--solutions-dir` Directory where the solutions are stored.
- `--solutions-name` Name of solutions.
- `--num` Specifies number of plants for the data.
- `--lower-loads` Specifies lower bound of loads for the data.
- `--upper-loads` Specifies the upper bound of loads for the data.
- `--skip-loads` Specifies the step size of loads for the data.
- `-p --plot` Outputs plot of the time needed for optimization.
- `-t --table` Outputs a table of the time needed for optimization in LaTeX-format.
- `-o --output` Specifies output file for the table or the plot or table.

## Classical Solver

[Couenne](https://projects.coin-or.org/Couenne) is used for solving the optimization problem as
a MINLP (mixed integer non-linear problem) on a classical computer.


The experiments can be performed by running the module `Classical.perform_experiments`.
The results will be saved in `Classical/Solutions/` in files according to the standard defined [above](#Standards).

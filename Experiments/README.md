# Experiments

## Setup Conda Environment

All required packages are listed in `conda_environment.yml`

The environment is called `opt` and can be installed via `./install_conda_env.sh`

It is setup by running `source setup.sh`

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
[Installation](Classical/COIN-OR/README.md)

The experiments can be performed by running the module `Classical.perform_experiments`.
The results will be saved in `Classical/Solutions/` in files according to the standard defined [above](#Standards).

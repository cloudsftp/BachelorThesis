# Quantum Computing for Smart Energy Systems

This is the code for the bachelor thesis "Quantum Computing for Smart Energy Systems".
It contains Python code to run the experiments described in the document and produce the figures that compare the performance of the different solvers.

### Contents

1. Requirements
1. How to set everything up
1. How to run the experiments

## Requirements

- Linux (Code tested on Ubuntu 20.04 and CentOS 8).
- Preferably `bash` as the terminal (default on most distributions).
- The Python packages are managed by Anaconda. So please go ahead and install Anaconda from the official [website](https://www.anaconda.com/products/individual#Downloads).


## Setup

1. Install Python packages via `./install_conda_environment.sh`. This sets up the Anaconda environment `opt`.
2. Install Couenne if you want to execute the experiments on a classial computer. Refer to [this](Classical/COIN-OR/README.md) document for instructions.
1. Activate the environment and environment variables for Couenne via `source setup.sh`.
1. Insert API token for D-Wave in the experiment runner (`Annealing_DQM/perform_experiments.py`)
1. Setup local IBMQ account with this [tutorial](https://quantum-computing.ibm.com/docs/manage/account/ibmq)

## Run Experiments

### Runners

There are 4 Runners for
- Classical `Classical.perform_experiments`
- Hybrid Annealing DQM `Annealing_DQM.perform_experiments`
- Direct Annealing QUBO `Annealing_QUBO.perform_experiments`
- Gate-based QUBO `Gatebased.perform_experiments` (only runs one very small experiment, no command-line options available)

optimization

### Options

All runners have these command-line options:
- `--one-shot` Turns off range mode. Lower bounds are used as parameters.
- `--lower-loads` Lower bound of the number of loads. (standard: 2)
- `--upper-loads` Upper bound of the number of loads. (standard: 20)
- `--step-loads` Steps size of the range of the number of loads. (standard: 2)
- `--lower-plants` Lower bound of the number of plants. (standard: 2)
- `--upper-plants` Upper bound of the number of plants. (standard: 20)
- `--step-plants` Step size of the range of the number of plants. (standard: 2)

### Output

The result of experiments will be saved in files that follow the rule:

`(classical|annealing|gatebased)_\d{3}_\d{3}\.json`

Where the first number indicates the number of loads and the second number indicates the number of power plants.

The location is the folder where `perform_experiments` is located `/Solutions`.
When executing the runners, the results that are already there will be overwritten.

### Example:

If you want to perform the experiments on the annealing hardware using the DQM approach:

`python -m Annealing_DQM.perform_experiments --lower-plants 4 --upper-plants 4 --lower-loads 2 --upper-loads 50 --step-loads 2`

If you only want to perform the first experiment on the classical hardware:

`python -m Classical.perform_experiments --one-shot --lower-plants 4 --lower-loads 2`

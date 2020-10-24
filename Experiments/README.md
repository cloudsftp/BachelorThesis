# Experiments

## Packages

All packages can be installed by executing `install.sh`

### Linux

All required linux packages are listed in `packages.list`
and can be installed via `grep -vE '^#' packages.list | xargs sudo apt install -y`

### Python

All required packages are lsited in `conda_environment.yml`
and can be installed via `conda env create -f conda_environment.yml`

## Data

[Pandas](https://pandas.pydata.org/) is used for extracting the data

#### Packages

- `numpy` (python)
- `pandas` (python)

## Classical Solver

[Couenne](https://projects.coin-or.org/Couenne) is used for solving the optimization problem as
a MINLP (mixed integer non-linear problem) on a classical computer

[Installation](Classical/README.md)

#### Packages

- `pyomo` (python)

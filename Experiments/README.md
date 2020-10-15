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

[Pandas]() is used for extracting the data

#### Packages

- `numpy` (python)
- `pandas` (python)

## Classical Solver

[CLP]() is used for solving the optimization problem
as a MILP (mixed integer linear problem) on a classical computer

[IPOPT]() is used for solving the optimization problem as
a MINLP (mixed integer non-linear problem) on a classical computer

#### Packages

- `coinor-clp` (linux)
- `pulp` (python)
- `coinor-libipopt-dev` (linux)
- `autograd` (python)
- `ipopt` (python)

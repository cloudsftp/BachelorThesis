#!/bin/python3.8

from Annealing_QUBO.qubo import UCP_QUBO
from Data.build_ucp import build_ucp
from UCP.unit_commitment_problem import ExperimentParameters


if __name__ == "__main__":
  ucp = build_ucp(ExperimentParameters(2, 4))
  qubo = UCP_QUBO(ucp)

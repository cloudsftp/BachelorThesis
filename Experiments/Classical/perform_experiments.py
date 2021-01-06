#!/bin/python3.8


import os
from sys import argv
from Classical.minlp import UCP_MINLP
from UCP.experiments import experiments_main
from UCP.unit_commitment_problem import ExperimentParameters, UCP, UCP_Solution


def optimize_classical(ucp: UCP) -> UCP_Solution:
    minlp: UCP_MINLP = UCP_MINLP(ucp)
    return minlp.optimize()


if __name__ == "__main__":
  experiments_main(optimize_classical, os.path.join('Classical', 'Solutions'), *argv[1:])
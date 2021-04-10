#!/bin/python
# version 3.8 required

import os
from sys import argv
from Classical.minlp import UCP_MINLP
from UCP.experiments import experiments_main
from UCP.unit_commitment_problem import UCP, UCPSolution

'''
this file is the experiment runner for the classical optimizations
'''

def optimize_classical(ucp: UCP) -> UCPSolution:
  '''
  performs the classical optimization for an UCP

  :ucp: UCP instance
  '''
  minlp: UCP_MINLP = UCP_MINLP(ucp)
  return minlp.optimize()


if __name__ == "__main__":
  '''
  calls the experiment runner with
  - the optimization function,
  - the path and prefix for the result files, and
  - the command-line arguments
  '''
  experiments_main(optimize_classical, os.path.join('Classical', 'Solutions'), 'classical', *argv[1:])

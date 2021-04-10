#!/bin/python
# version 3.8 required

import os
from sys import argv
from Annealing_QUBO.qubo import UCP_QUBO
from UCP.unit_commitment_problem import UCP, UCPSolution
from UCP.experiments import experiments_main
from uqo.client.config import Config # type: ignore
from uqo.client.connection import Connection # type: ignore

'''
this file is the experiment runner for the annealing optimizations using the UQO framework
'''

def optimize_annealing_qubo_uqo(ucp: UCP) -> UCPSolution:
  '''
  initializes a connection to the UQO server
  and then performs the classical optimization for an UCP

  :ucp: UCP instance
  '''
  config: Config = Config(configpath='uqo_config.json')
  connection: Connection = config.create_connection()

  ucp_qubo: UCP_QUBO = UCP_QUBO(ucp)
  solution: UCPSolution = ucp_qubo.optimize(config, 'Advantage_system1.1')
  solution.check_validity()

  return solution


if __name__ == "__main__":
  '''
  calls the experiment runner with
  - the optimization function,
  - the path and prefix for the result files, and
  - the command-line arguments
  '''
  experiments_main(
    optimize_annealing_qubo_uqo,
    os.path.join('Annealing_QUBO', 'Solutions'),
    'annealing',
    *argv[1:]
  )

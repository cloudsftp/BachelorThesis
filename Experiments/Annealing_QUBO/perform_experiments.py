#!/bin/python3.8

import os
from sys import argv
from Annealing_QUBO.qubo import UCP_QUBO
from UCP.unit_commitment_problem import UCP, UCPSolution
from UCP.experiments import experiments_main
from uqo.client.config import Config
from uqo.client.connection import Connection

def optimize_annealing_qubo_uqo(ucp: UCP) -> UCPSolution:
  config: Config = Config(configpath='uqo_config.json')
  connection: Connection = config.create_connection()

  ucp_qubo: UCP_QUBO = UCP_QUBO(ucp)
  solution: UCPSolution = ucp_qubo.optimize(connection, 'Advantage_system1.1')
  solution.check_validity()

  return solution


if __name__ == "__main__":
  experiments_main(
    optimize_annealing_qubo_uqo,
    os.path.join('Annealing_QUBO', 'Solutions'),
    'annealing',
    *argv[1:]
  )

#!/bin/python
# version 3.8 required

import os
from sys import argv
from dwave.cloud.client import Client # type: ignore
from dwave.system.samplers.leap_hybrid_sampler import LeapHybridDQMSampler # type: ignore
from Annealing_DQM.dqm import UCP_DQM
from UCP.experiments import experiments_main
from UCP.unit_commitment_problem import UCP, UCPSolution
from Util.logging import debug_msg_time

'''
this file is the experiment runner for the hybrid annealing optimizations using DQMs
'''

def optimize_annealing(ucp: UCP) -> UCPSolution:
  '''
  performs the hybrid annealing optimizatin using DQMs for an UCP

  :ucp: UCP instance
  '''
  ucp_dqm: UCP_DQM = UCP_DQM(ucp)
  solution: UCPSolution = ucp_dqm.optimize(LeapHybridDQMSampler())
  solution.check_validity()
  return solution

if __name__ == "__main__":
  '''
  initializes the dwave client
  and then calls the ecperiment runner with
  - the optimization function,
  - the path and prefix for the result files, and
  - the command-line arguments
  '''
  client: Client = Client.from_config(token='DEV-eef9bd1d1d722708bf268e55471ac662896f8d79')

  experiments_main(
    optimize_annealing,
    os.path.join('Annealing_DQM', 'Solutions'),
    'annealing',
    *argv[1:]
  )

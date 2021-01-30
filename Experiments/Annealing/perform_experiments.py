#!/bin/python3.8

import os
import logging
from sys import argv
from dwave.cloud.client import Client # type: ignore
from dwave.system.samplers.leap_hybrid_sampler import LeapHybridDQMSampler # type: ignore
from Annealing.dqm import UCP_DQM
from UCP.experiments import experiments_main
from UCP.unit_commitment_problem import UCP, UCPSolution
from Util.logging import debug_msg_time


def optimize_annealing(ucp: UCP) -> UCPSolution:
  ucp_dqm: UCP_DQM = UCP_DQM(ucp)
  solution: UCPSolution = ucp_dqm.optimize(LeapHybridDQMSampler())
  solution.check_validity()
  return solution

def optimize_annealing_measure_quality(ucp: UCP) -> UCPSolution:
  debug_msg_time('Start Converting UCP')
  ucp_dqm: UCP_DQM = UCP_DQM(ucp, y_c=10, y_s=1, y_d=50)

  debug_msg_time('Finished Converting UCP')

  solution: UCPSolution = ucp_dqm.optimize(LeapHybridDQMSampler(), adjust=False)

  solution.check_validity()

  return solution


if __name__ == "__main__":
  client: Client = Client.from_config(token='DEV-eef9bd1d1d722708bf268e55471ac662896f8d79')

  experiments_main(
    optimize_annealing,
    os.path.join('Annealing', 'Solutions'),
    'annealing',
    *argv[1:]
  )

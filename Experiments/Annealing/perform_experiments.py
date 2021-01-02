#!/bin/python3.8

import os
from sys import argv
from dwave.cloud.client import Client
from dwave.system.samplers.leap_hybrid_sampler import LeapHybridDQMSampler
from Annealing.dqm import UCP_DQM
from Data.build_ucp import build_ucp
from UCP.experiments import experiments_main
from UCP.unit_commitment_problem import ExperimentParameters, UCP, UCP_Solution


def optimize_annealing(ucp: UCP) -> UCP_Solution:
  ucp_dqm: UCP_DQM = UCP_DQM(ucp, y_d=200)
  solution: UCP_Solution = ucp_dqm.optimize(LeapHybridDQMSampler())
  return solution

if __name__ == "__main__":
  client: Client = Client.from_config(token='DEV-eef9bd1d1d722708bf268e55471ac662896f8d79')

  experiments_main(optimize_annealing, os.path.join('Annealing', 'Solutions'), 'annealing', *argv[1:])

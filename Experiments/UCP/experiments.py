#!/bin/python3.8


import os
import argparse
from typing import Callable
from Data.build_ucp import build_ucp
from UCP.unit_commitment_problem import UCP, UCPSolution, ExperimentParameters
from Util.logging import debug_msg_time


def write_solution(solution: UCPSolution, parameters: ExperimentParameters, path: str, prefix: str) -> None:
  file_name = parameters.to_file_name(prefix)

  if not os.path.exists(path):
    os.makedirs(path)

  solution.save_to(os.path.join(path, file_name))

def perform_experiment(parameters: ExperimentParameters, optimize_fun: Callable, path: str, prefix: str) -> None:
    debug_msg_time(
      'Experiment: {:3} loads, {:3} plants'
      .format(parameters.num_loads, parameters.num_plants)
    )
    ucp: UCP = build_ucp(parameters)

    solution = optimize_fun(ucp)

    write_solution(solution, parameters, path, prefix)

    debug_msg_time(
      'Optimization Time: {:15.3f} seconds\n'
      .format(solution.time)
    )

def perform_experiments(num_loads_start: int, num_loads_end: int, num_loads_step, \
                        num_plants_start: int, num_plants_end: int, num_plants_step, \
                        optimize_fun: Callable, path: str, prefix: str) -> None:

  for num_plants in range(num_plants_start, num_plants_end + 1, num_plants_step):
    for num_loads in range(num_loads_start, num_loads_end + 1, num_loads_step):

      parameters = ExperimentParameters(num_loads, num_plants)
      perform_experiment(parameters, optimize_fun, path, prefix)

def experiments_main(optimize_fun: Callable, path: str, prefix: str, *argv) -> None:
  parser: argparse.ArgumentParser = argparse.ArgumentParser(description='Perform optimization experiments.')
  parser.add_argument('-o', '--one-shot', help='Perform one experiment only, range disabled. Lower bound is used.',
                      action='store_true')

  parser.add_argument('-ll', '--lower-loads', help='Lower bound of number of loads.', type=int, default=2)
  parser.add_argument('-ul', '--upper-loads', help='Upper bound of number of loads.', type=int, default=20)
  parser.add_argument('-sl', '--step-loads', help='Step size of range of numbers of loads.', type=int, default=2)

  parser.add_argument('-lp', '--lower-plants', help='Lower bound of number of plants.', type=int, default=2)
  parser.add_argument('-up', '--upper-plants', help='Upper bound of number of plants.', type=int, default=20)
  parser.add_argument('-sp', '--step-plants', help='Step size of range of numbers of plants.', type=int, default=2)

  args = parser.parse_args(argv)

  num_loads_start: int = args.lower_loads
  num_loads_end: int = args.upper_loads
  num_loads_step: int = args.step_loads

  num_plants_start: int = args.lower_plants
  num_plants_end: int = args.upper_plants
  num_plants_step: int = args.step_plants

  if args.one_shot:
    num_loads_end = num_loads_start
    num_plants_end = num_plants_start

  perform_experiments(num_loads_start, num_loads_end, num_loads_step, \
                      num_plants_start, num_plants_end, num_plants_step, \
                      optimize_fun, path, prefix)

#!/bin/python3.8


import os
from Classical.minlp import UCP_MINLP
from Data.build_ucp import ExperimentParameters, build_ucp
from UCP.unit_commitment_problem import UCP_Solution


path: str = os.path.join('Classical', 'Solutions')

def write_solution(solution: UCP_Solution, parameters: ExperimentParameters) -> None:
  file_name = 'classical_{:03}_{:03}.json' \
    .format(parameters.num_loads, parameters.num_plants)

  solution.save_to(os.path.join(path, file_name))

def perform_experiment(parameters: ExperimentParameters) -> None:
    print(
      'Experiment: {:3} loads, {:3} plants'
      .format(parameters.num_loads, parameters.num_plants)
    )

    minlp: UCP_MINLP = UCP_MINLP(build_ucp(parameters))
    solution = minlp.optimize()
    write_solution(solution, parameters)

    print(
      'Time: {:5.3f}\n'
      .format(solution.time)
    )

def perform_experiments() -> None:
  for num_plants in range(2, 11, 2):
    for num_loads in range(2, 21, 2):
      parameters = ExperimentParameters(num_loads, num_plants)
      perform_experiment(parameters)


if __name__ == "__main__":
  perform_experiments()
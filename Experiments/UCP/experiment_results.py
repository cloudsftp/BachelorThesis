#!/bin/python3.8


import os
from typing import List

from UCP.unit_commitment_problem import UCP_Solution


def read_experiment_result(solution_file_name: str) -> UCP_Solution:
  return UCP_Solution.load_from(solution_file_name)


def read_expertiment_results(solution_dir_name: str) -> List[UCP_Solution]:
  solution_file_names: List[str] = os.listdir(solution_dir_name)
  solutions: List[UCP_Solution] = []

  for solution_file_name in solution_file_names:
    solutions.append(read_experiment_result(os.path.join(solution_dir_name, solution_file_name)))

  return solutions


if __name__ == "__main__":
  print(read_expertiment_results(os.path.join('Classical', 'Solutions'))[3])

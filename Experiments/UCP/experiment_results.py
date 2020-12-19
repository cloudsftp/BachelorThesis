#!/bin/python3.8


import os
import argparse
from typing import Dict, List, Optional

import matplotlib.pyplot as plt # type: ignore
import pandas as pd # type: ignore
from UCP.unit_commitment_problem import UCP_Solution


class ExperimentResults(object):
  def __init__(self, solution_dir_name: str) -> None:
    self.solution_dir_name: str = solution_dir_name
    self.load_expertiment_results()
    self.sort_experiment_results()


  def load_experiment_result(self, solution_file_name: str) -> UCP_Solution:
    return UCP_Solution.load_from(solution_file_name)

  def load_expertiment_results(self) -> None:
    solution_file_names: List[str] = os.listdir(self.solution_dir_name)
    self.solutions: List[UCP_Solution] = []

    for solution_file_name in solution_file_names:
      self.solutions.append(
        self.load_experiment_result(
          os.path.join(self.solution_dir_name, solution_file_name)
        )
      )


  def sort_experiment_results(self) -> None:
    self.experiments_by_plants: Dict[int, List[UCP_Solution]] = {}

    for solution in self.solutions:
      num_plants: int = solution.ucp.parameters.num_plants
      solutions_list: Optional[List[UCP_Solution]] = self.experiments_by_plants.get(num_plants)

      if not solutions_list:
        self.experiments_by_plants[num_plants] = []
        solutions_list = self.experiments_by_plants[num_plants]

      solutions_list.append(solution)


  def plot_time(self, num_plants: int, output_file_name: str) -> None:
    solutions_list: Optional[List[UCP_Solution]] = self.experiments_by_plants.get(num_plants)

    if not solutions_list:
      raise RuntimeError('No experiment results with {} power plants'.format(num_plants))

    times: Dict[int, float] = {}

    for solution in solutions_list:
      times[solution.ucp.parameters.num_loads] = solution.time

    time_series: pd.Series = pd.Series(times).sort_index()

    time_series.plot()
    plt.savefig(output_file_name)


if __name__ == "__main__":
  parser: argparse.ArgumentParser = argparse.ArgumentParser(description='Visualize results')

  parser.add_argument('-s', '--solutions-dir', type=str)

  parser.add_argument('-p', '--plot', action='store_true')
  parser.add_argument('-n', '--num', type=int)

  parser.add_argument('-t', '--table', action='store_true')
  parser.add_argument('-o', '--output', type=str)

  args = parser.parse_args()

  solutions_dir: str = args.solutions_dir
  if solutions_dir == '':
    raise argparse.ArgumentError(args.solutions_dir, message='Please provide a directory where the solutions are stored')

  output_file_name: str = args.output
  if output_file_name == '':
    raise argparse.ArgumentError(args.output, message='Please provide an output file name')

  results: ExperimentResults = ExperimentResults(solutions_dir)

  if args.plot:
    results.plot_time(args.num, output_file_name)


  # TODO: Implement table generator

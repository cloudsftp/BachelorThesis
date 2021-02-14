#!/bin/python3.8


import os
import argparse
from typing import Dict, List, Optional

import matplotlib.pyplot as plt # type: ignore
import pandas as pd # type: ignore
from UCP.unit_commitment_problem import UCPSolution


class ExperimentResults(object):
  def __init__(self, solution_dir_name: str) -> None:
    self.solution_dir_name: str = solution_dir_name
    self.load_expertiment_results()
    self.sort_experiment_results()


  @staticmethod
  def load_experiment_result(solution_file_name: str) -> UCPSolution:
    return UCPSolution.load_from(solution_file_name)

  def load_expertiment_results(self) -> None:
    solution_file_names: List[str] = os.listdir(self.solution_dir_name)
    self.solutions: List[UCPSolution] = []

    for solution_file_name in solution_file_names:
      self.solutions.append(
        ExperimentResults.load_experiment_result(
          os.path.join(self.solution_dir_name, solution_file_name)
        )
      )


  def sort_experiment_results(self) -> None:
    self.experiments_by_plants: Dict[int, List[UCPSolution]] = {}

    for solution in self.solutions:
      num_plants: int = solution.ucp.parameters.num_plants
      solutions_list: Optional[List[UCPSolution]] = self.experiments_by_plants.get(num_plants)

      if not solutions_list:
        self.experiments_by_plants[num_plants] = []
        solutions_list = self.experiments_by_plants[num_plants]

      solutions_list.append(solution)


  def get_experiments(self, num_plants: int) -> List[UCPSolution]:
    solutions_list: Optional[List[UCPSolution]] = self.experiments_by_plants.get(num_plants)

    if not solutions_list:
      raise RuntimeError('No experiment results with {} power plants'.format(num_plants))

    return solutions_list


  def plot_time(self, num_plants: int, loads: List[int], output_file_name: str) -> None:
    solutions_list: List[UCPSolution] = self.get_experiments(num_plants)

    times: Dict[int, float] = {}

    for solution in solutions_list:
      if solution.ucp.parameters.num_loads in loads:
        times[solution.ucp.parameters.num_loads] = solution.time

    time_series: pd.Series = pd.Series(times).sort_index()

    time_series.plot()

    plt.xlabel('number of loads')
    plt.ylabel('t in seconds')

    plt.tight_layout()
    plt.savefig(output_file_name)


  def generate_table(self, num_plants: int, loads: List[int], output_file_name: str) -> None:
    solutions_list: List[UCPSolution] = self.get_experiments(num_plants)

    with open(output_file_name, 'w') as file:
      file.write('\\begin{tabular}{| r | r | r |}\n')
      file.write('  \hline \n')
      file.write('  Number of Loads & Objective function & Time (in seconds) \\\\ \n')
      file.write('  \hline \hline \n')

      for solution in solutions_list:
        if solution.ucp.parameters.num_loads in loads:
          file.write('  {} & {:.3f} & {:.3f} \\\\ \hline \n'.format(
            solution.ucp.parameters.num_loads,
            solution.o,
            solution.time
          ))

      file.write('\\end{tabular}\n')

if __name__ == "__main__":
  parser: argparse.ArgumentParser = argparse.ArgumentParser(description='Visualize results')

  parser.add_argument('--solutions-dir', type=str)

  parser.add_argument('-p', '--plot', action='store_true')
  parser.add_argument('--num', type=int)
  parser.add_argument('--lower-load', type=int, default=0)
  parser.add_argument('--upper-load', type=int, default=500)
  parser.add_argument('--skip-loads', type=int, default=1)

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

  index_range: range = range(args.lower_load, args.upper_load + 1)
  loads: List[int] = []
  for i in range(len(index_range)):
    if i % args.skip_loads == 0:
      loads.append(index_range[i])

  if args.plot:
    results.plot_time(args.num, loads, output_file_name)
  elif args.table:
    results.generate_table(args.num, loads, output_file_name)

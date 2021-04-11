##!/bin/python
# versino 3.8 required

import os
import argparse
from typing import Dict, List, Optional

import matplotlib.pyplot as plt # type: ignore
import pandas as pd # type: ignore
from UCP.unit_commitment_problem import UCPSolution

'''
this file is used to create the figures comparing the experiment results
it is not part of the experiments
'''

class ExperimentResults(object):
  '''
  class to wrap the experiment results
  '''
  def __init__(self, solution_dir_name: str, solutions_name: str) -> None:
    self.solution_dir_name: str = solution_dir_name
    self.solutions_name: str = solutions_name
    self.load_expertiment_results()
    self.sort_experiment_results()

  @staticmethod
  def load_experiment_result(solution_file_name: str) -> UCPSolution:
    '''
    load a single experiment result

    :solution_file_name: name of the file to read from
    '''
    return UCPSolution.load_from(solution_file_name)

  def load_expertiment_results(self) -> None:
    '''
    load all experiment results
    '''
    solution_file_names: List[str] = os.listdir(self.solution_dir_name)
    self.solutions: List[UCPSolution] = []

    for solution_file_name in solution_file_names:
      self.solutions.append(
        ExperimentResults.load_experiment_result(
          os.path.join(self.solution_dir_name, solution_file_name)
        )
      )

  def sort_experiment_results(self) -> None:
    '''
    put experiments in lists that are elements of a dictionary
    the dictionary holds the lists as elements for a specific number of power plants that are used in the experiment
    '''
    self.experiments_by_plants: Dict[int, List[UCPSolution]] = {}

    for solution in self.solutions:
      num_plants: int = solution.ucp.parameters.num_plants
      solutions_list: Optional[List[UCPSolution]] = self.experiments_by_plants.get(num_plants)

      if not solutions_list:
        self.experiments_by_plants[num_plants] = []
        solutions_list = self.experiments_by_plants[num_plants]

      solutions_list.append(solution)

  def get_experiments(self, num_plants: int) -> List[UCPSolution]:
    '''
    returns a list of experiment results with the specified number of power plants

    :num_plants: number of plants
    '''
    solutions_list: Optional[List[UCPSolution]] = self.experiments_by_plants.get(num_plants)

    if not solutions_list:
      raise RuntimeError('No experiment results with {} power plants'.format(num_plants))

    return solutions_list


  def plot_time(self, num_plants: int, loads: List[int], output_file_name: str) -> None:
    '''
    plots the computing time for the specific number of power plants and specified numbers of loads

    :num_plants: number of plants
    :loads: list of the numbers of loads
    :output_file_name: name of the output file
    '''
    solutions_list: List[UCPSolution] = self.get_experiments(num_plants)

    times: Dict[int, float] = {}

    for solution in solutions_list:
      if solution.ucp.parameters.num_loads in loads:
        times[solution.ucp.parameters.num_loads] = solution.time

    time_series: pd.Series = pd.Series(times).sort_index()

    time_series.plot()

    plt.legend((self.solutions_name,))

    plt.xlabel('Number of Loads')
    plt.ylabel('Computation Time (s)')

    plt.tight_layout()
    plt.savefig(output_file_name)

  def generate_table(self, num_plants: int, loads: List[int], output_file_name: str) -> None:
    '''
    generates a table of the computing time for the specific number of power plants and specified numbers of loads

    :num_plants: number of plants
    :loads: list of the numbers of loads
    :output_file_name: name of the output file
    '''
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
  '''
  reads the arguments and calls the functions above to either plot or generate tables of the experiments
  '''
  parser: argparse.ArgumentParser = argparse.ArgumentParser(description='Visualize results')

  solutions_dir_action: argparse.Action = parser.add_argument('--solutions-dir', type=str)
  solutions_name_action: argparse.Action = parser.add_argument('--solutions-name', type=str)

  plant_number_action: argparse.Action = parser.add_argument('--num', type=int)
  parser.add_argument('--lower-loads', type=int, default=0)
  parser.add_argument('--upper-loads', type=int, default=500)
  parser.add_argument('--skip-loads', type=int, default=1)

  plot_action: argparse.Action = parser.add_argument('-p', '--plot', action='store_true')
  parser.add_argument('-t', '--table', action='store_true')
  output_action: argparse.Action = parser.add_argument('-o', '--output', type=str)

  args = parser.parse_args()

  solutions_dir: Optional[str] = args.solutions_dir
  if not solutions_dir:
    raise argparse.ArgumentError(solutions_dir_action, message='Please provide a directory where the solutions are stored')

  solutions_name: Optional[str] = args.solutions_name
  if not solutions_name:
    raise argparse.ArgumentError(solutions_name_action, message='Please provide a name for the solutions')

  output_file_name: Optional[str] = args.output
  if not output_file_name:
    raise argparse.ArgumentError(output_action, message='Please provide an output file name')

  plant_number: Optional[int] = args.num
  if not plant_number:
    raise argparse.ArgumentError(plant_number_action, message='Please provide the number of plants')

  results: ExperimentResults = ExperimentResults(solutions_dir, solutions_name)

  index_range: range = range(args.lower_loads, args.upper_loads + 1)
  loads: List[int] = []
  for i in range(len(index_range)):
    if i % args.skip_loads == 0:
      loads.append(index_range[i])

  if args.plot:
    results.plot_time(args.num, loads, output_file_name)
  elif args.table:
    results.generate_table(args.num, loads, output_file_name)
  else:
    raise argparse.ArgumentError(plot_action, message='Please either specify --plot or --table')

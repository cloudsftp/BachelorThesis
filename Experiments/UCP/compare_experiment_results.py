#!/bin/python3.8


import argparse
from typing import Dict, List, Optional

import matplotlib.pyplot as plt # type: ignore
import pandas as pd # type: ignore
from UCP.experiment_results import ExperimentResults
from UCP.unit_commitment_problem import UCPSolution


def plot_time_comparison(experiment_results_list: List[ExperimentResults],
                    loads: List[int], num_plants: int, output_file_name: str) -> None:
  for experiment_results in experiment_results_list:
    solutions_list: List[UCPSolution] = experiment_results.get_experiments(num_plants)

    times: Dict[int, float] = {}

    for solution in solutions_list:
      if solution.ucp.parameters.num_loads in loads:
        times[solution.ucp.parameters.num_loads] = solution.time

    time_series: pd.Series = pd.Series(times).sort_index()

    time_series.plot()

  plt.legend([experiment_results.solutions_name for experiment_results in experiment_results_list])

  plt.xlabel('Number of Loads')
  plt.ylabel('Computation Time (s)')

  plt.tight_layout()
  plt.savefig(output_file_name)


def plot_error_comparison(experiment_results_list: List[ExperimentResults],
                    loads: List[int], num_plants: int, output_file_name: str) -> None:
  result_base: pd.DataFrame
  result_comp: pd.DataFrame

  for i in range(len(experiment_results_list)):
    solutions_list: List[UCPSolution] = experiment_results_list[i].get_experiments(num_plants)

    results: Dict[int, float] = {}

    for solution in solutions_list:
      if solution.ucp.parameters.num_loads in loads:
        results[solution.ucp.parameters.num_loads] = solution.o

    if i == 0:
      result_base = pd.Series(results).sort_index()
    else:
      result_comp = pd.Series(results).sort_index()

  error: pd.DataFrame = (result_comp - result_base) / result_comp / 100
  error.plot()
  plt.legend(('Relative Error',))

  plt.xlabel('Number of Loads')
  plt.ylabel('Relative Error (%)')

  plt.tight_layout()
  plt.savefig(output_file_name)


if __name__ == "__main__":
  parser: argparse.ArgumentParser = argparse.ArgumentParser(description='Visualize comparison of results')

  solutions_dir_action: argparse.Action = parser.add_argument('--solutions-dir', nargs="+", type=str, default=[])
  solutions_name_action: argparse.Action = parser.add_argument('--solutions-name', nargs="+", type=str, default=[])

  plant_number_action: argparse.Action = parser.add_argument('--num', type=int)
  parser.add_argument('--lower-loads', type=int, default=0)
  parser.add_argument('--upper-loads', type=int, default=500)
  parser.add_argument('--skip-loads', type=int, default=1)

  performance_action: argparse.Action = parser.add_argument('-p', '--performance', action='store_true')
  parser.add_argument('-e', '--error', action='store_true')

  output_action: argparse.Action = parser.add_argument('-o', '--output', type=str)

  args = parser.parse_args()

  solutions_dirs: List[str] = args.solutions_dir
  if not solutions_dirs:
    raise argparse.ArgumentError(solutions_dir_action, message='Please provide at least one directory where the solutions are stored')

  solutions_names: List[str] = args.solutions_name
  if len(solutions_dirs) != len(solutions_names):
    raise argparse.ArgumentError(
      solutions_name_action,
      message='Number of solution names does not match number of solution directories: {} != {}' \
        .format(len(solutions_names), len(solutions_dirs))
    )

  output_file_name: Optional[str] = args.output
  if not output_file_name:
    raise argparse.ArgumentError(output_action, message='Please provide an output file name')

  plant_number: Optional[int] = args.num
  if not plant_number:
    raise argparse.ArgumentError(plant_number_action, message='Please provide the number of plants')

  experiment_results_list: List[ExperimentResults] = []
  for i in range(len(solutions_dirs)):
    experiment_results_list.append(ExperimentResults(solutions_dirs[i], solutions_names[i]))

  index_range: range = range(args.lower_loads, args.upper_loads + 1)
  loads: List[int] = []
  for i in range(len(index_range)):
    if i % args.skip_loads == 0:
      loads.append(index_range[i])

  if args.performance:
    plot_time_comparison(experiment_results_list, loads, plant_number, output_file_name)
  elif args.error:
    if not len(experiment_results_list) == 2:
      raise argparse.ArgumentError(performance_action, 'When --error is specified, please only use 2 sources of experiment results')

    plot_error_comparison(experiment_results_list, loads, plant_number, output_file_name)
  else:
    raise argparse.ArgumentError(performance_action, 'Pleace specify either --performance or --error')


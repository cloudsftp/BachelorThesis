#!/bin/python3.8


import os
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
      num_plants: int = solution.parameters.num_plants
      solutions_list: Optional[List[UCP_Solution]] = self.experiments_by_plants.get(num_plants)

      if not solutions_list:
        self.experiments_by_plants[num_plants] = []
        solutions_list = self.experiments_by_plants[num_plants]

      solutions_list.append(solution)


  def plot_time(self, num_plants: int) -> None:
    solutions_list: Optional[List[UCP_Solution]] = self.experiments_by_plants.get(num_plants)

    if not solutions_list:
      raise RuntimeError('No experiment results with {} power plants'.format(num_plants))

    times: Dict[int, float] = {}

    for solution in solutions_list:
      times[solution.parameters.num_loads] = solution.time

    time_series: pd.Series = pd.Series(times).sort_index()

    time_series.plot()
    plt.show()


if __name__ == "__main__":
  results: ExperimentResults = ExperimentResults(os.path.join('Classical', 'Solutions'))
  results.plot_time(4)

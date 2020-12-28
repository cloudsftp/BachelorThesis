#!/bin/python3.8


import math
from typing import Any, List
from dimod import DiscreteQuadraticModel # type: ignore
import numpy as np # type: ignore

from Data.build_ucp import build_ucp
from UCP.unit_commitment_problem import CombustionPlant, ExperimentParameters, UCP


class UCP_DQM(object):
  model: DiscreteQuadraticModel
  p: List[List[Any]] # variables of model

  P: List[np.ndarray] # discretizised power levels

  def discretizise_plants(self, ucp: UCP, max_h: float = 10) -> None:
    self.P = []

    for plant in ucp.plants:
      spectrum: float = plant.Pmax - plant.Pmin
      n: int = math.ceil(math.log(spectrum / max_h + 2, 2))
      h: float = spectrum / (2 ** n - 2)

      P_i: List[float] = [0]
      for k in range(2 ** n - 1):
        P_i.append(plant.Pmin + k * h)

      self.P.append(np.array(P_i))

  def init_variables(self, ucp: UCP) -> None:
    self.p = []

    for i in range(ucp.parameters.num_plants):
      p_i: List[Any] = []
      var_size: int = len(self.P[i])

      for t in range(ucp.parameters.num_loads):
        p_i.append(self.model.add_variable(var_size))

      self.p.append(p_i)


  def calculate_F_i(self, plant: CombustionPlant, i: int) -> np.array:
    P_i: np.ndarray = self.P[i]
    F_i: List[float] = [0]

    for k in range(1, len(P_i)):
      F_i.append(plant.A + plant.B * P_i[k] + plant.C * (P_i[k] ** 2))

    return np.array(F_i)

  def set_linear(self, ucp: UCP, y_c: float, y_d: float) -> None:
    for i in range(len(self.p)):
      P_i: np.ndarray = self.P[i]
      plant: CombustionPlant = ucp.plants[i]
      F_i: np.ndarray = self.calculate_F_i(plant, i)

      for t in range(len(self.p[i])):
        linear_biases: np.ndarray = y_c * F_i + y_d * (
          P_i * P_i - ucp.loads[t] * P_i
        )

        if t == 0 and not plant.initially_on:
          for k in range(1, len(linear_biases)):
            linear_biases[k] += plant.AU

        self.model.set_linear(self.p[i][t], linear_biases)


  def set_quadratic_startup(self, ucp: UCP, y_s: float) -> None:
    for i in range(ucp.parameters.num_plants):
      plant: CombustionPlant = ucp.plants[i]
      num_cases: int = len(self.P[i])
      quadratic_biases: np.ndarray = np.zeros((num_cases, num_cases))

      for k in range(1, num_cases):
        quadratic_biases[0, k] = plant.AU
        quadratic_biases[k, 0] = plant.AD

      quadratic_biases *= y_s

      for t in range(1, ucp.parameters.num_loads):
        self.model.set_quadratic(self.p[i][t-1], self.p[i][t], quadratic_biases)


  def set_quadratic_demand(self, ucp: UCP, y_d: float) -> None:
    for j in range(1, ucp.parameters.num_plants):
      for i in range(j):
        quadratic_biases: np.ndarray = np.tensordot(self.P[i], self.P[j], axes=0)
        quadratic_biases *= y_d

        for t in range(ucp.parameters.num_loads):
          self.model.set_quadratic(self.p[i][t], self.p[j][t], quadratic_biases)


  def __init__(self, ucp: UCP, y_c: float = 1, y_s: float = 1, y_d: float = 1) -> None:
      self.model = DiscreteQuadraticModel()

      self.discretizise_plants(ucp)
      self.init_variables(ucp)

      self.set_linear(ucp, y_c, y_d)
      self.set_quadratic_startup(ucp, y_s)
      self.set_quadratic_demand(ucp, y_d)


if __name__ == "__main__":
  dqm = UCP_DQM(build_ucp(ExperimentParameters(2, 4)))

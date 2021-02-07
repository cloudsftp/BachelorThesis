#!/bin/python3.8


from typing import Any, List
from dimod import DiscreteQuadraticModel # type: ignore
from dimod.sampleset import SampleSet # type: ignore
import numpy as np # type: ignore

from UCP.unit_commitment_problem import CombustionPlant, UCP, UCPSolution
from Util.logging import debug_msg_time


class UCP_DQM(object):
  model: DiscreteQuadraticModel
  ucp: UCP
  p: List[List[Any]] # variables of model

  P: List[np.ndarray] # discretizised power levels


  def indices_to_index(self, i: int, t: int) -> int:
    return i * self.ucp.parameters.num_loads + t


  def discretizise_plants(self, max_h: float) -> None:
    self.P = self.ucp.get_discretized_power_levels()

  def init_variables(self) -> None:
    self.p = []

    for i in range(self.ucp.parameters.num_plants):
      p_i: List[Any] = []
      var_size: int = len(self.P[i])

      for t in range(self.ucp.parameters.num_loads):
        p_i.append(self.model.add_variable(var_size))
      self.p.append(p_i)

  def calculate_F_i(self, plant: CombustionPlant, i: int) -> np.array:
    P_i: np.ndarray = self.P[i]
    F_i: List[float] = [0]

    for k in range(1, len(P_i)):
      F_i.append(plant.A + plant.B * P_i[k] + plant.C * (P_i[k] ** 2))

    return np.array(F_i)

  def set_linear(self, y_c: float, y_s: float, y_d: float) -> None:
    for i in range(len(self.p)):
      P_i: np.ndarray = self.P[i]
      plant: CombustionPlant = self.ucp.plants[i]
      F_i: np.ndarray = self.calculate_F_i(plant, i)

      for t in range(len(self.p[i])):
        linear_biases: np.ndarray = y_c * F_i + y_d * (
          P_i * P_i - self.ucp.loads[t] * P_i
        )

        if t == 0:
          if plant.initially_on:
            linear_biases[0] += y_s * plant.AD

          else:
            for k in range(1, len(linear_biases)):
              linear_biases[k] += y_s * plant.AU

        self.model.set_linear(self.p[i][t], linear_biases)


  def set_quadratic_startup(self, y_s: float) -> None:
    for i in range(self.ucp.parameters.num_plants):
      plant: CombustionPlant = self.ucp.plants[i]
      num_cases: int = len(self.P[i])
      quadratic_biases: np.ndarray = np.zeros((num_cases, num_cases))

      for k in range(1, num_cases):
        quadratic_biases[0, k] = plant.AU
        quadratic_biases[k, 0] = plant.AD

      quadratic_biases *= y_s

      for t in range(1, self.ucp.parameters.num_loads):
        self.model.set_quadratic(self.p[i][t-1], self.p[i][t], quadratic_biases)


  def set_quadratic_demand(self, y_d: float) -> None:
    for j in range(1, self.ucp.parameters.num_plants):
      for i in range(j):
        quadratic_biases: np.ndarray = np.tensordot(self.P[i], self.P[j], axes=0)
        quadratic_biases *= y_d

        for t in range(self.ucp.parameters.num_loads):
          self.model.set_quadratic(self.p[i][t], self.p[j][t], quadratic_biases)


  def __init__(self, ucp: UCP, y_c: float = 1, y_s: float = 1, y_d: float = 1, max_h: float = 10) -> None:
    self.model = DiscreteQuadraticModel()
    self.ucp = ucp

    self.discretizise_plants(max_h)
    self.init_variables()

    self.set_linear(y_c, y_s, y_d)
    self.set_quadratic_startup(y_s)
    self.set_quadratic_demand(y_d)


  def get_variables_from_sample(self, sample: List[float], u: List[List[bool]], p: List[List[float]]) -> None:
    for i in range(self.ucp.parameters.num_plants):
      u.append([])
      p.append([])

      for t in range(self.ucp.parameters.num_loads):
        value_index: int = int(sample[self.indices_to_index(i, t)])
        value: float = self.P[i][value_index]

        p[i].append(value)
        u[i].append((bool) (p[i][t] > 0))

  def optimize(self, sampler, adjust: bool = True) -> UCPSolution:
    debug_msg_time('Start Solver')
    samples: SampleSet = sampler.sample_dqm(self.model)
    sample: List[float] = samples.record[0][0]
    debug_msg_time('Solver Finished')

    u: List[List[bool]] = []
    p: List[List[float]] = []

    self.get_variables_from_sample(sample, u, p)

    time: float = samples.info['run_time'] / (10 ** 6)
    solution: UCPSolution = UCPSolution(self.ucp, time, True, self.ucp.calculate_o(u, p), u, p)

    if adjust:
      solution.adjust_variables()

    return solution

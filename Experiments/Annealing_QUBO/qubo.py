#!/bin/python3.8


from typing import Dict, List, Tuple
import numpy as np # type: ignore

from UCP.unit_commitment_problem import CombustionPlant, UCP, UCPSolution
from uqo.Problem import Qubo # type: ignore
from uqo.Response import Response # type: ignore
from uqo.client.config import Config # type: ignore
from Util.logging import debug_msg, debug_msg_time


class UCP_QUBO(object):
  model: Dict[Tuple[int, int], float]
  ucp: UCP
  m: Dict[Tuple[int, int, int], int] # indices of variables
  P: List[np.ndarray] # discretized power levels

  ''' Discretization and Mapping '''

  def discretizise_plants(self, max_h: float) -> None:
    self.P = self.ucp.get_discretized_power_levels(max_h)

  def init_indices_mapping(self) -> None:
    self.m = {}
    current_m: int = 0
    for i in range(self.ucp.parameters.num_plants):
      num_power_levels: int = len(self.P[i])
      for t in range(self.ucp.parameters.num_loads):
        for k in range(num_power_levels):
          self.m[i, t, k] = current_m
          current_m += 1

  ''' Quadratic Biases '''

  def add_quadratic_bias(self,
                         i1: int, t1: int, k1: int,
                         i2: int, t2: int, k2: int,
                         value: float) -> None:
    m1: int = self.m[i1, t1, k1]
    m2: int = self.m[i2, t2, k2]

    bias: float = self.model.get((m1, m2), 0)
    self.model[m1, m2] = bias + value

  def add_quadratic_startup_shutdown(self, y_s: float) -> None:
    for i in range(self.ucp.parameters.num_plants):
      AU: float = self.ucp.plants[i].AU
      AD: float = self.ucp.plants[i].AD

      for t in range(1, self.ucp.parameters.num_loads):
        for k in range(1, len(self.P[i])):
          self.add_quadratic_bias(i, t-1, 0, i, t, k, AU * y_s)
          self.add_quadratic_bias(i, t-1, k, i, t, 0, AD * y_s)

  def add_quadratic_demand(self, y_d: float) -> None:
    for j in range(self.ucp.parameters.num_plants):
      for i in range(j):
        for l in range(len(self.P[j])):
          for k in range(len(self.P[i])):
            value: float = self.P[j][l] * self.P[i][k]
            for t in range(self.ucp.parameters.num_loads):
              self.add_quadratic_bias(i, t, k, j, t, l, value * y_d)

  def add_quadratic_discretized(self, y_d: float) -> None:
    for i in range(self.ucp.parameters.num_plants):
      for t in range(self.ucp.parameters.num_loads):
        for l in range(len(self.P[i])):
          for k in range(l):
            self.add_quadratic_bias(i, t, k, i, t, l, y_d)

  ''' Linear Biases '''

  def add_linear_bias(self,
                      i: int, t: int, k: int,
                      value: float) -> None:
    m: int = self.m[i, t, k]

    bias: float = self.model.get((m, m), 0)
    self.model[m, m] = bias + value

  def add_linear(self, y_c: float, y_d: float, y_p: float) -> None:
    for i in range(self.ucp.parameters.num_plants):
      plant: CombustionPlant = self.ucp.plants[i]
      for t in range(self.ucp.parameters.num_loads):
        for k in range(1, len(self.P[i])):
          value: float = 0

          value += y_c * (plant.A + plant.B * self.P[i][k] + plant.C * (self.P[i][k] ** 2))
          value += y_d * (self.P[i][k] ** 2 - self.ucp.loads[t] * self.P[i][k])

          self.add_linear_bias(i, t, k, value)

  def add_linear_startup_shutdown(self, y_s: float) -> None:
    for i in range(self.ucp.parameters.num_plants):
      is_initially_on: bool = self.ucp.plants[i].initially_on

      if is_initially_on:
        A_D: float = self.ucp.plants[i].AD
        self.add_linear_bias(i, 0, 0, y_s * A_D)

      else:
        A_U: float = self.ucp.plants[i].AU
        for k in range(1, len(self.P[i])):
          self.add_linear_bias(i, 0, k, y_s * A_U)

  ''' Initialization '''

  def __init__(self, ucp: UCP, y_c: float = 1, y_s: float = 1, y_d: float = 1, y_p: float = 1, max_h: float = 10) -> None:
    self.model = {}
    self.ucp = ucp

    self.discretizise_plants(max_h)
    self.init_indices_mapping()

    self.add_quadratic_startup_shutdown(y_s)
    self.add_quadratic_demand(y_d)
    self.add_quadratic_discretized(y_p)

    self.add_linear(y_c, y_d, y_p)
    self.add_linear_startup_shutdown(y_s)

  ''' Optimization '''

  def get_variables_from_result(self, result: List[int], u: List[List[bool]], p: List[List[float]]) -> None:
    for i in range(self.ucp.parameters.num_plants):
      u.append([])
      p.append([])

      for t in range(self.ucp.parameters.num_loads):
        value_indices: List[int] = []
        for k in range(len(self.P[i])):
          if result[self.m[i, t, k]] == 1:
            value_indices.append(k)

        value: float = 0
        num_indices: int = len(value_indices)
        if num_indices > 0:
          value = self.P[i][value_indices[(int) (num_indices / 2)]]
          if num_indices > 1:
            debug_msg('Warning: {} possible power levels for plant {} detected'.format(num_indices, i))

        p[i].append(value)
        u[i].append((bool) (p[i][t] > 0))

  def optimize(self, config: Config, solver: str, shots: int = 1, adjust: bool = True):
    problem: Qubo = Qubo(config, self.model).with_platform('dwave').with_solver(solver)
    print(problem.find_pegasus_embedding())
    debug_msg_time('Start Solver')
    self.answer: Response = problem.solve(shots)
    debug_msg_time('Solver finished')

    sample: List[int] = self.answer.solutions[0]

    u: List[List[bool]] = []
    p: List[List[float]] = []

    self.get_variables_from_result(sample, u, p)

    time: float = -1 #answer.timing / (10 ** 6)
    solution: UCPSolution = UCPSolution(self.ucp, time, True, self.ucp.calculate_o(u, p), u, p)

    if adjust:
      solution.check_validity()
      solution.adjust_variables()

    return solution

  def find_embedding(self, config: Config) -> None:
    problem: Qubo = Qubo(config, self.model).with_platform('dwave').with_solver('Advantage_system1.1')
    debug_msg_time('Sending embedding request')
    embedding = problem.find_pegasus_embedding()
    print(embedding)

#!/bin/python3.8

import math
from typing import Dict, List, Tuple
import numpy as np # type: ignore
from qiskit.optimization import QuadraticProgram # type: ignore
from qiskit.optimization.problems.variable import Variable # type: ignore
from qiskit.optimization.algorithms import OptimizationResult # type: ignore

from UCP.unit_commitment_problem import CombustionPlant, UCP, UCPSolution


class UCP_QUBO(object):
  model: QuadraticProgram
  ucp: UCP
  p: List[List[List[Variable]]] # variables of model
  P: List[np.ndarray] # discretizised power levels

  def discretizise_plants(self, max_h: float) -> None:
    self.P = []

    for plant in self.ucp.plants:
      spectrum: float = plant.Pmax - plant.Pmin
      n: int = math.ceil(math.log(spectrum / max_h + 2, 2))
      h: float = spectrum / (2 ** n - 2)

      P_i: List[float] = [0]
      for k in range(2 ** n - 1):
        P_i.append(plant.Pmin + k * h)

      self.P.append(np.array(P_i))

  def init_variables(self) -> None:
    self.p = []

    for i in range(self.ucp.parameters.num_plants):
      p_i: List[List[Variable]] = []
      num_power_levels: int = len(self.P[i])

      for t in range(self.ucp.parameters.num_loads):
        p_i_t: List[Variable] = []

        for k in range(num_power_levels):
          var: Variable = self.model.binary_var('p_{}_{}_{}'.format(i, t, k))
          p_i_t.append(var)
        p_i.append(p_i_t)
      self.p.append(p_i)

  def add_quadratic(self, quadratic: Dict[Tuple[str, str], float],
                    i1: int, t1: int, k1: int,
                    i2: int, t2: int, k2: int,
                    val: float) -> None:
    index: Tuple[str, str] = (self.p[i1][t1][k1].name, self.p[i2][t2][k2].name)
    if not quadratic.get(index):
      quadratic[index] = val
    else:
      print('Quadratic constraint overwritten')

  def quadratic_startup_shutdown(self, quadratic: Dict[Tuple[str, str], float], y_s: float) -> None:
    for i in range(self.ucp.parameters.num_plants):
      AU: float = self.ucp.plants[i].AU
      AD: float = self.ucp.plants[i].AD

      for t in range(1, self.ucp.parameters.num_loads):
        for k in range(1, len(self.P[i])):
          self.add_quadratic(quadratic, i, t-1, 0, i, t, k, AU * y_s)
          self.add_quadratic(quadratic, i, t-1, k, i, t, 0, AD * y_s)

  def quadratic_demand(self, quadratic: Dict[Tuple[str, str], float], y_d: float) -> None:
    for j in range(self.ucp.parameters.num_plants):
      for i in range(j):
        for l in range(len(self.P[j])):
          for k in range(len(self.P[i])):
            value: float = self.P[j][l] * self.P[i][k]
            for t in range(self.ucp.parameters.num_loads):
              self.add_quadratic(quadratic, i, t, k, j, t, l, value * y_d)

  def quadratic_discretized(self, quadratic: Dict[Tuple[str, str], float], y_o: float) -> None:
    for i in range(self.ucp.parameters.num_plants):
      for t in range(self.ucp.parameters.num_loads):
        for l in range(len(self.P[i])):
          for k in range(l):
            self.add_quadratic(quadratic, i, t, k, i, t, l, y_o)

  def get_quadratic(self, y_s: float, y_d: float, y_o: float) -> Dict[Tuple[str, str], float]:
    quadratic: Dict[Tuple[str, str], float] = {}

    self.quadratic_startup_shutdown(quadratic, y_s)
    self.quadratic_demand(quadratic, y_d)
    self.quadratic_discretized(quadratic, y_o)

    return quadratic

  def add_linear( self, linear: Dict[str, float],
                  i: int, t: int, k: int,
                  val: float) -> None:
    index: str = self.p[i][t][k].name
    if not linear.get(index):
      linear[index] = val
    else:
      print('Linear constraint overwritten')

  def get_linear(self, y_c: float, y_s: float, y_d: float, y_o: float) -> Dict[str, float]:
    linear: Dict[str, float] = {}

    for i in range(self.ucp.parameters.num_plants):
      plant: CombustionPlant = self.ucp.plants[i]
      for t in range(self.ucp.parameters.num_loads):
        for k in range(len(self.P[i])):
          value: float = 0

          value += y_c * (plant.A + plant.B * self.P[i][k] + plant.C * (self.P[i][k] ** 2))
          value += y_d * (self.P[i][k] ** 2 - self.ucp.loads[t] * self.P[i][k])
          value -= y_o

          self.add_linear(linear, i, t, k, value)

    return linear

  def get_constant(self, y_o: float) -> float:
    value: float = y_o
    for t in range(self.ucp.parameters.num_loads):
      value += self.ucp.loads[t]

    return value


  def __init__(self, ucp, y_c: float = 1, y_s: float = 1, y_d: float = 1, y_o: float = 1, max_h: float = 10) -> None:
    self.model = QuadraticProgram()
    self.ucp = ucp

    self.discretizise_plants(max_h)
    self.init_variables()

    quadratic: Dict[Tuple[str, str], float] = self.get_quadratic(y_s, y_d, y_o)
    linear: Dict[str, float] = self.get_linear(y_c, y_s, y_d, y_o)
    constant: float = self.get_constant(y_o)
    self.model.minimize(constant, linear, quadratic)


  def get_variables_from_result(self, result: OptimizationResult, u: List[List[bool]], p: List[List[float]]) -> None:
    for i in range(self.ucp.parameters.num_plants):
      u.append([])
      p.append([])

      for t in range(self.ucp.parameters.num_loads):
        value_indices: List[int] = []
        for k in range(len(self.P[i])):
          if result[self.p[i][t][k].name] == 1:
            value_indices.append(k)

        value: float = 0
        num_indices: int = len(value_indices)
        if num_indices > 0:
          value = self.P[i][value_indices[(int) (num_indices / 2)]]
          if num_indices > 1:
            print('Warning: {} possible power levels for plant {} detected'.format(num_indices, i))

        p[i].append(value)
        u[i].append(p[i][t] > 0)

  def optimize(self, solver, adjust: bool = True) -> UCPSolution:
    result: OptimizationResult = solver.solve(self.model)

    u: List[List[bool]] = []
    p: List[List[float]] = []

    self.get_variables_from_result(result, u, p)

    time: float = -1
    solution: UCPSolution = UCPSolution(self.ucp, time, True, self.ucp.calculate_o(u, p), u, p)

    if adjust:
      solution.adjust_variables()

    return solution

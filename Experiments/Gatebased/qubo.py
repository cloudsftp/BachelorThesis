#!/bin/python3.8

from typing import Dict, List, Tuple
import numpy as np # type: ignore
from qiskit.optimization import QuadraticProgram # type: ignore
from qiskit.optimization.problems.variable import Variable # type: ignore
from qiskit.optimization.algorithms import OptimizationResult # type: ignore

from UCP.unit_commitment_problem import CombustionPlant, UCP, UCPSolution
from Util.logging import debug_msg


class UCP_QUBO(object):
  '''
  handles the generation of a QUBO using IBM's Qiskit given an UCP
  '''
  model: QuadraticProgram
  ucp: UCP
  p: List[List[List[Variable]]] # variables of model
  P: List[np.ndarray] # discretizised power levels

  def discretizise_plants(self, max_h: float) -> None:
    '''
    discretizes the power levels of all plants

    :max_h: maximum difference of non-zero power levels, default: 10
    '''
    self.P = self.ucp.get_discretized_power_levels(max_h)

  def init_variables(self) -> None:
    '''
    instanciates the variables of the QUBO
    '''
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

  def get_constant(self, y_d: float) -> float:
    '''
    generates the constant bias for the QUBO
    '''
    value: float = y_d
    for t in range(self.ucp.parameters.num_loads):
      value += self.ucp.loads[t]

    return value

  def add_linear( self, linear: Dict[str, float],
                  i: int, t: int, k: int,
                  val: float) -> None:
    '''
    adds a linear bias to the QUBO

    :linear: linear biases (output variable)
    :i: unit index
    :t: time index
    :k: power level index
    :value: weight of the bias
    '''
    index: str = self.p[i][t][k].name
    if not linear.get(index):
      linear[index] = val
    else:
      debug_msg('Linear constraint overwritten')

  def get_linear(self, y_c: float, y_s: float, y_d: float, y_p: float) -> Dict[str, float]:
    '''
    generates the linear biases for the QUBO
    '''
    linear: Dict[str, float] = {}

    for i in range(self.ucp.parameters.num_plants):
      plant: CombustionPlant = self.ucp.plants[i]
      for t in range(self.ucp.parameters.num_loads):
        for k in range(len(self.P[i])):
          value: float = 0

          value += y_c * (plant.A + plant.B * self.P[i][k] + plant.C * (self.P[i][k] ** 2))
          value += y_d * (self.P[i][k] ** 2 - self.ucp.loads[t] * self.P[i][k])
          value -= y_p

          self.add_linear(linear, i, t, k, value)

    return linear

  def add_quadratic(self, quadratic: Dict[Tuple[str, str], float],
                    i1: int, t1: int, k1: int,
                    i2: int, t2: int, k2: int,
                    val: float) -> None:
    '''
    adds a quadratic bias to the QUBO

    :quadratic: quadratic constraints (output variable)
    :i1: unit index source
    :t1: time index source
    :k1: power level index source
    :i2: unit index target
    :t2: time index target
    :k2: power level index target
    :value: weight of the bias
    '''
    index: Tuple[str, str] = (self.p[i1][t1][k1].name, self.p[i2][t2][k2].name)
    if not quadratic.get(index):
      quadratic[index] = val
    else:
      debug_msg('Quadratic constraint overwritten')

  def quadratic_startup_shutdown(self, quadratic: Dict[Tuple[str, str], float], y_s: float) -> None:
    '''
    sets the quadratic biases for the startup costs for the QUBO

    :quadratic: quadratic constraints (output variable)
    '''
    for i in range(self.ucp.parameters.num_plants):
      AU: float = self.ucp.plants[i].AU
      AD: float = self.ucp.plants[i].AD

      for t in range(1, self.ucp.parameters.num_loads):
        for k in range(1, len(self.P[i])):
          self.add_quadratic(quadratic, i, t-1, 0, i, t, k, AU * y_s)
          self.add_quadratic(quadratic, i, t-1, k, i, t, 0, AD * y_s)

  def quadratic_demand(self, quadratic: Dict[Tuple[str, str], float], y_d: float) -> None:
    '''
    sets the quadratic biases for the demand for the QUBO

    :quadratic: quadratic constraints (output variable)
    '''
    for j in range(self.ucp.parameters.num_plants):
      for i in range(j):
        for l in range(len(self.P[j])):
          for k in range(len(self.P[i])):
            value: float = self.P[j][l] * self.P[i][k]
            for t in range(self.ucp.parameters.num_loads):
              self.add_quadratic(quadratic, i, t, k, j, t, l, value * y_d)

  def quadratic_discretized(self, quadratic: Dict[Tuple[str, str], float], y_d: float) -> None:
    '''
    sets the quadratic biases for making sure only one power level is active per unit and time

    :quadratic: quadratic constraints (output variable)
    '''
    for i in range(self.ucp.parameters.num_plants):
      for t in range(self.ucp.parameters.num_loads):
        for l in range(len(self.P[i])):
          for k in range(l):
            self.add_quadratic(quadratic, i, t, k, i, t, l, y_d)

  def get_quadratic(self, y_s: float, y_d: float, y_p: float) -> Dict[Tuple[str, str], float]:
    '''
    generates the quadratic biases for the QUBO
    '''
    quadratic: Dict[Tuple[str, str], float] = {}

    self.quadratic_startup_shutdown(quadratic, y_s)
    self.quadratic_demand(quadratic, y_d)
    self.quadratic_discretized(quadratic, y_p)

    return quadratic

  def __init__(self, ucp, y_c: float = 1, y_s: float = 1, y_d: float = 1, y_p: float = 1, max_h: float = 10) -> None:
    '''
    builds a QUBO from an UCP using Qiskit

    :ucp: UCP instance
    :y_c: factor of objective function
    :y_s: factor of startup and shutdown cost
    :y_d: factor of demand constraints
    :y_p: factor of constraints making sure only one power level is active per unit and time
    :max_h: maximum difference of non-zero power levels, default: 10
    '''
    self.model = QuadraticProgram()
    self.ucp = ucp

    self.discretizise_plants(max_h)
    self.init_variables()

    quadratic: Dict[Tuple[str, str], float] = self.get_quadratic(y_s, y_d, y_p)
    linear: Dict[str, float] = self.get_linear(y_c, y_s, y_d, y_p)
    constant: float = self.get_constant(y_p)
    self.model.minimize(constant, linear, quadratic)

  def get_variables_from_result(self, result: OptimizationResult, u: List[List[bool]], p: List[List[float]]) -> None:
    '''
    computes the UCP variables from a QUBO solution

    :result: QUBO solution
    :u: commitment of units (output variable)
    :p: power output of units (output variable)
    '''
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
            debug_msg('Warning: {} possible power levels for plant {} detected'.format(num_indices, i))

        p[i].append(value)
        u[i].append((bool) (p[i][t] > 0))

  def optimize(self, solver, adjust: bool = True) -> UCPSolution:
    '''
    optimizes the QUBO using a specified sampler

    :solver: solver used to optimize the QUBO
    :adjust: whether the result should be adjusted to meet power demand at all times
    '''
    result: OptimizationResult = solver.solve(self.model)

    u: List[List[bool]] = []
    p: List[List[float]] = []

    self.get_variables_from_result(result, u, p)

    time: float = -1
    solution: UCPSolution = UCPSolution(self.ucp, time, True, self.ucp.calculate_o(u, p), u, p)

    if adjust:
      solution.adjust_variables()

    return solution

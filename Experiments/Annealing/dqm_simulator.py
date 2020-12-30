#!/bin/python3.8


import sys
from typing import List
from dimod import DiscreteQuadraticModel
from dimod.sampleset import SampleSet
import numpy as np # type: ignore


class DQMSimulator(object):
  dqm: DiscreteQuadraticModel
  v: List[int] = []
  c: List[int] = []

  def __init__(self) -> None:
    pass


  def initialize_variables(self) -> None:
    for i in range(len(self.dqm.variables)):
      self.v.append(0)
      self.c.append(len(self.dqm.get_linear(self.dqm.variables[i])))

    print(self.c)


  def possible_v(self):
    self.v[0] = -1

    while True:
      add: bool = True

      for i in range(len(self.v)):
        if add:
          if self.v[i] < self.c[i] - 1:
            self.v[i] += 1
            add = False

          else:
            self.v[i] = 0
            add = True

      if add:
        break

      yield self.v

  def compute_o(self, v: List[int]) -> float:
    o: float = 0

    for i in range(len(self.dqm.variables)):
      linear_bias: np.ndarray = self.dqm.get_linear(self.dqm.variables[i])
      o += linear_bias[v[i]]

    for j in range(len(self.dqm.variables)):
      for i in range(j):
        try:
          quadratic_bias: np.ndarray = self.dqm.get_quadratic(
            self.dqm.variables[i],
            self.dqm.variables[j]
          )
          o += quadratic_bias[v[i]][v[j]]

        except:
          pass

    return o


  def brute_force_solution(self) -> None:
    min_o: float = sys.float_info.max
    optimal_v: List[int] = self.v.copy()

    for v in self.possible_v():
      o = self.compute_o(v)
      if o < min_o:
        min_o = o
        optimal_v = v.copy()

    self.v = optimal_v.copy()


  def sample(self, dqm: DiscreteQuadraticModel) -> SampleSet:
    self.dqm = dqm

    self.initialize_variables()
    self.brute_force_solution()

    # TODO: return a sample set
    print(self.v)

#!/bin/python3.8


import math
from typing import Any, List
from dimod import DiscreteQuadraticModel # type: ignore

from Data.build_ucp import build_ucp
from UCP.unit_commitment_problem import ExperimentParameters, UCP


class UCP_DQM(object):
  model: DiscreteQuadraticModel
  p: List[List[Any]] # variables of model

  P: List[List[float]] # discretizised power levels

  def discretizise_plants(self, ucp: UCP, max_h: float = 10) -> None:
    self.P = []

    for plant in ucp.plants:
      spectrum: float = plant.Pmax - plant.Pmin
      n: int = math.ceil(math.log(spectrum / max_h + 2, 2))
      h: float = spectrum / (2 ** n - 2)

      P_i: List[float] = [0]
      for k in range(2 ** n - 1):
        P_i.append(plant.Pmin + k * h)

      self.P.append(P_i)

  def init_variables(self, ucp: UCP) -> None:
    self.p = []

    for i in range(ucp.parameters.num_plants):
      p_i: List[Any] = []
      var_size: int = len(self.P[i])

      for t in range(ucp.parameters.num_loads):
        p_i.append(self.model.add_variable(var_size))

      self.p.append(p_i)


  def __init__(self, ucp: UCP) -> None:
      self.model = DiscreteQuadraticModel()

      self.discretizise_plants(ucp)
      self.init_variables(ucp)

      print(self.model.variables.stop)


if __name__ == "__main__":
  dqm = UCP_DQM(build_ucp(ExperimentParameters(2, 4)))

#!/bin/python3.8


import math
from typing import List
from dimod import DiscreteQuadraticModel # type: ignore

from Data.build_ucp import build_ucp
from UCP.unit_commitment_problem import ExperimentParameters, UCP


class UCP_DQM(object):
  model: DiscreteQuadraticModel
  P: List[List[float]] # discretizised power levels

  def discretizise_plants(self, ucp: UCP, max_h: float = 10) -> None:
    self.P = []

    for plant in ucp.plants:
      spectrum: float = plant.Pmax - plant.Pmin
      n: int = math.ceil(math.log(spectrum / max_h + 2, 2))
      h: float = spectrum / (2 ** n - 2)

      P: List[float] = [0]
      for i in range(2 ** n - 1):
        P.append(plant.Pmin + i * h)

      self.P.append(P)



  def __init__(self, ucp: UCP) -> None:
      self.model = DiscreteQuadraticModel()

      self.discretizise_plants(ucp)



if __name__ == "__main__":
  dqm = UCP_DQM(build_ucp(ExperimentParameters(2, 4)))

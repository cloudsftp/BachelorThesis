#!/bin/python3.8

from typing import Sized
from pyomo.core.base.PyomoModel import ConcreteModel # type: ignore
from pyomo.core.base.var import Var, VarList # type: ignore
from pyomo.environ import NonNegativeReals, Boolean # type: ignore

from UCP.unit_commitment_problem import CombustionPlant, UCP, UCP_Solution

def create_variable_list(type, initialize: float, x: int, y: int) -> Var:
  return Var(range(x), range(y), domain=type, initialize=initialize)


class UCP_MINLP(object):
  model: ConcreteModel

  def __init__(self, ucp: UCP) -> None:
    ''' Build self.model from UCP '''
    self.model = ConcreteModel()

    I: int = len(ucp.plants)
    T: int = len(ucp.loads)

    self.model.u = create_variable_list(Boolean, 1, I, T)
    self.model.p = create_variable_list(NonNegativeReals, 1, I, T)


  def optimize(self) -> UCP_Solution:
    ''' Optimize self.model and return the solution '''
    pass


if __name__ == "__main__":
  ucp = UCP([1, 2, 1], [
    CombustionPlant(1, 2, 3, 1, 2),
    CombustionPlant(0, 1, 1, 2, 3)
  ])

  minlp = UCP_MINLP(ucp)
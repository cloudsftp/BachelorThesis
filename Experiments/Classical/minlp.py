#!/bin/python3.8

from pyomo.core.base.PyomoModel import ConcreteModel # type: ignore
from pyomo.core.base.objective import Objective # type: ignore
from pyomo.core.base.set import RangeSet # type: ignore
from pyomo.core.base.var import Var, VarList # type: ignore
from pyomo.environ import NonNegativeReals, Boolean # type: ignore

from UCP.unit_commitment_problem import CombustionPlant, UCP, UCP_Solution

def create_variable_list(type, initialize: float, X: RangeSet, Y: RangeSet) -> Var:
  return Var(X, Y, domain=type, initialize=initialize)


class UCP_MINLP(object):
  model: ConcreteModel

  def instanciate_variables(self) -> None:
    self.model.u = create_variable_list(Boolean, 1, self.model.I, self.model.T)
    self.model.p = create_variable_list(NonNegativeReals, 1, self.model.I, self.model.T)

  def build_objective(self, ucp: UCP) -> None:
    def objective_function(model: ConcreteModel) -> float:
      return sum(
        sum(
          model.u[(i, t)] * (
            ucp.plants[i].A +
            ucp.plants[i].B * model.p[(i, t)] +
            ucp.plants[i].C * model.p[(i, t)] ** 2
          ) for t in self.model.T
        ) for i in self.model.I
      )

    self.model.o = Objective(rule=objective_function)

  def __init__(self, ucp: UCP) -> None:
    ''' Build self.model from UCP '''
    self.model = ConcreteModel()

    self.model.I = RangeSet(0, len(ucp.plants) - 1)
    self.model.T = RangeSet(0, len(ucp.loads) - 1)

    self.instanciate_variables()
    self.build_objective(ucp)

  def optimize(self) -> UCP_Solution:
    ''' Optimize self.model and return the solution '''
    pass


if __name__ == "__main__":
  ucp = UCP([1, 2, 1], [
    CombustionPlant(1, 2, 3, 1, 2),
    CombustionPlant(0, 1, 1, 2, 3)
  ])

  minlp = UCP_MINLP(ucp)
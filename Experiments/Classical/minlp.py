#!/bin/python3.8

from pyomo.core.base.PyomoModel import ConcreteModel # type: ignore
from pyomo.core.base.constraint import Constraint # type: ignore
from pyomo.core.base.objective import Objective # type: ignore
from pyomo.core.base.set import RangeSet # type: ignore
from pyomo.core.base.var import Var # type: ignore
from pyomo.core.expr.logical_expr import inequality # type: ignore
from pyomo.environ import NonNegativeReals, Boolean # type: ignore
from pyomo.opt import SolverFactory # type: ignore

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

  def build_load_constraints(self, ucp: UCP) -> None:
    def load_constraint_rule(model, t):
      return ucp.loads[t] <= sum(model.u[(i, t)] * model.p[(i, t)] for i in model.I)

    self.model.l_constr = Constraint(self.model.T, rule=load_constraint_rule)

  def build_power_constraints(self, ucp: UCP) -> None:
    def power_constraint_rule(model, i, t) -> bool:
      return inequality(ucp.plants[i].Pmin, model.p[(i, t)], ucp.plants[i].Pmax)

    self.model.p_constr = Constraint(self.model.I, self.model.T, rule=power_constraint_rule)

  def __init__(self, ucp: UCP) -> None:
    ''' Build self.model from UCP '''
    self.model = ConcreteModel()

    self.model.I = range(len(ucp.plants))
    self.model.T = range(len(ucp.loads))

    self.instanciate_variables()
    self.build_objective(ucp)
    self.build_load_constraints(ucp)
    self.build_power_constraints(ucp)

  def optimize(self) -> UCP_Solution:
    ''' Optimize self.model and return the solution '''
    with SolverFactory("couenne") as solver:
      results = solver.solve(self.model)
      print('time: {} seconds -----------------'
        .format(results.solver.time))
      self.model.display()

      return UCP_Solution(self.ucp) # TODO return a solution


if __name__ == "__main__":
  ucp = UCP([x for x in range(6)], [
    CombustionPlant(2, 2, 3, 1, 24),
    CombustionPlant(9, 1, 1, 1, 24)
  ])

  minlp = UCP_MINLP(ucp)
  minlp.optimize()
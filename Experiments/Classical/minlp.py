#!/bin/python3.8

from dataclasses import asdict
from typing import List
from pyomo.core.base.PyomoModel import ConcreteModel # type: ignore
from pyomo.core.base.constraint import Constraint # type: ignore
from pyomo.core.base.expression import Expression # type: ignore
from pyomo.core.base.objective import Objective # type: ignore
from pyomo.core.base.var import Var # type: ignore
from pyomo.core.base.plugin import TransformationFactory # type: ignore
from pyomo.core.expr.logical_expr import inequality # type: ignore
from pyomo.gdp import Disjunct, Disjunction # type: ignore
from pyomo.environ import NonNegativeReals, Boolean # type: ignore
from pyomo.opt import SolverFactory # type: ignore
from pyomo.opt.results.solver import TerminationCondition # type: ignore

from UCP.unit_commitment_problem import CombustionPlant, ExperimentParameters, UCP, UCP_Solution


class UCP_MINLP(object):
  model: ConcreteModel

  def instanciate_variables(self) -> None:
    self.model.u = Var(self.model.I, self.model.T, domain=Boolean, initialize=0)
    self.model.p = Var(self.model.I, self.model.T, domain=NonNegativeReals, initialize=0)
    self.model.startup_shutdown_cost = Var(self.model.I, self.model.T, domain=NonNegativeReals, initialize=0, bounds=(0, 1000))

  def build_startup_shutdown_disjunctions(self):
    self.model.shutdown_disjunct = Disjunct(self.model.I, self.model.T)
    self.model.on_disjunct = Disjunct(self.model.I, self.model.T)
    self.model.off_disjunct = Disjunct(self.model.I, self.model.T)
    self.model.startup_disjunct = Disjunct(self.model.I, self.model.T)

    plants: List[CombustionPlant] = self.ucp.plants
    for i in self.model.I:
      for t in self.model.T:
        self.model.shutdown_disjunct[i, t].l = Constraint(expr=self.model.startup_shutdown_cost[i, t] == plants[i].AD)
        self.model.shutdown_disjunct[i, t].c = Constraint(expr=self.model.u[i, t] == 0)

        self.model.on_disjunct[i, t].l = Constraint(expr=self.model.startup_shutdown_cost[i, t] == 0)
        self.model.on_disjunct[i, t].c = Constraint(expr=self.model.u[i, t] == 1)

        self.model.startup_disjunct[i, t].l = Constraint(expr=self.model.startup_shutdown_cost[i, t] == plants[i].AU)
        self.model.startup_disjunct[i, t].c = Constraint(expr=self.model.u[i, t] == 1)

        self.model.off_disjunct[i, t].l = Constraint(expr=self.model.startup_shutdown_cost[i, t] == 0)
        self.model.off_disjunct[i, t].c = Constraint(expr=self.model.u[i, t] == 0)

        if t > 0:
          self.model.shutdown_disjunct[i, t].p = Constraint(expr=self.model.u[i, t-1] == 1)
          self.model.on_disjunct[i, t].p = Constraint(expr=self.model.u[i, t-1] == 1)
          self.model.startup_disjunct[i, t].p = Constraint(expr=self.model.u[i, t-1] == 0)
          self.model.off_disjunct[i, t].p = Constraint(expr=self.model.u[i, t-1] == 0)

    def disjunction_rule(model: ConcreteModel, i: int, t: int) -> Expression:
      if t > 0:
        return [
          model.shutdown_disjunct[i, t], model.on_disjunct[i, t],
          model.startup_disjunct[i, t], model.off_disjunct[i, t]
        ]
      else:
        if plants[i].initially_on:
          return [model.shutdown_disjunct[i, t], model.on_disjunct[i, t]]
        else:
          return [model.startup_disjunct[i, t], model.off_disjunct[i, t]]

    self.model.startup_shutdown_disjunction = Disjunction(self.model.I, self.model.T, rule=disjunction_rule)


  def build_objective(self) -> None:
    def objective_function(model: ConcreteModel) -> Expression:
      plants: List[CombustionPlant] = self.ucp.plants

      return sum(
        sum(
          model.u[(i, t)] * (
            plants[i].A +
            plants[i].B * model.p[i, t] +
            plants[i].C * model.p[i, t] ** 2
          ) + (
            model.startup_shutdown_cost[i, t]
          ) for t in model.T
        ) for i in model.I
      )

    self.model.o = Objective(rule=objective_function)

  def build_load_constraints(self) -> None:
    def load_constraint_rule(model: ConcreteModel, t: int) -> Expression:
      return self.ucp.loads[t] == sum(model.u[(i, t)] * model.p[(i, t)] for i in model.I)

    self.model.l_constr = Constraint(self.model.T, rule=load_constraint_rule)

  def build_power_constraints(self) -> None:
    def power_constraint_rule(model: ConcreteModel, i: int, t: int) -> Expression:
      return inequality(
        self.ucp.plants[i].Pmin,
        model.p[(i, t)],
        self.ucp.plants[i].Pmax
      )

    self.model.p_constr = Constraint(self.model.I, self.model.T, rule=power_constraint_rule)

  def __init__(self, ucp: UCP, parameters: ExperimentParameters) -> None:
    ''' Build self.model from UCP '''
    self.ucp: UCP = ucp
    self.parameters: ExperimentParameters = parameters
    self.model: ConcreteModel = ConcreteModel()

    self.model.I = range(len(ucp.plants))
    self.model.T = range(len(ucp.loads))

    self.instanciate_variables()
    self.build_startup_shutdown_disjunctions()
    self.build_objective()
    self.build_load_constraints()
    self.build_power_constraints()

    TransformationFactory('gdp.bigm').apply_to(self.model)

  def to_ucp_solution(self, results) -> UCP_Solution:
    time: float = results.solver.time
    optimal: bool = results.solver.termination_condition == TerminationCondition.optimal

    o: float = self.model.o()
    u: List[List[bool]] = [[self.model.u[(i, t)].value == 1 for t in self.model.T]
                                                            for i in self.model.I]

    p: List[List[float]] = [[self.model.p[(i, t)].value if u[i][t]
                                                        else 0
                                                        for t in self.model.T]
                                                        for i in self.model.I]

    return UCP_Solution(self.parameters, self.ucp, time, optimal, o, u, p)

  def optimize(self, solver_command: str = 'couenne') -> UCP_Solution:
    ''' Optimize self.model and return the solution '''
    with SolverFactory(solver_command) as solver:
      results = solver.solve(self.model)
      return self.to_ucp_solution(results)

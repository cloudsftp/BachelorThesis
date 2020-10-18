#!/bin/python3.8

from pyomo.core.base.PyomoModel import ConcreteModel
from pyomo.core.base.constraint import Constraint
from pyomo.core.base.objective import Objective
from pyomo.core.base.var import Var
from pyomo.environ import *
from pyomo.opt import SolverFactory

def create_model():
  model = ConcreteModel()

  model.x = Var()
  model.o = Objective(expr=model.x)
  model.c = Constraint(expr=model.x >= 1)

  model.x.set_value(2)

  return model

if __name__ == "__main__":
  with SolverFactory("couenne") as opt:
    model = create_model()
    opt.options.linear_solver = "mumps"
    results = opt.solve(model, load_solutions=False)
    if results.solver.termination_condition != TerminationCondition.optimal:
            raise RuntimeError('Solver did not report optimality:\n%s'
                               % (results.solver))
    model.solutions.load_from(results)
    print("Objective: %s" % (model.o()))

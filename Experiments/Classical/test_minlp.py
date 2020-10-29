#!/bin/python3.8

from pyomo.core.base.PyomoModel import ConcreteModel # type: ignore
from pyomo.core.base.constraint import Constraint # type: ignore
from pyomo.core.base.objective import Objective # type: ignore
from pyomo.core.base.var import Var # type: ignore
from pyomo.core.expr.logical_expr import inequality # type: ignore
from pyomo.environ import NonNegativeReals, Boolean # type: ignore
from pyomo.opt import SolverFactory # type: ignore
from pyomo.opt.results.solver import TerminationCondition # type: ignore

def create_model() -> ConcreteModel:
  model = ConcreteModel()

  model.p1 = Var(domain=NonNegativeReals, initialize=100)
  model.u1 = Var(domain=Boolean, initialize=1)
  model.p2 = Var(domain=NonNegativeReals, initialize=100)
  model.u2 = Var(domain=Boolean, initialize=1)

  f1 = model.u1 * (200 + 10 * model.p1 + model.p1 ** 2)
  f2 = model.u2 * (100 + 5 * model.p2 + 5 * model.p2 ** 2)

  model.o = Objective(expr=f1 + f2)

  model.pc1 = Constraint(expr=inequality(70, model.p1, 200))
  model.pc2 = Constraint(expr=inequality(10, model.p2, 80))

  model.l = Constraint(expr=100 <= model.u1 * model.p1 + model.u2 * model.p2)

  return model

if __name__ == "__main__":
  with SolverFactory("couenne") as opt:
    model = create_model()
    results = opt.solve(model, load_solutions=False)
    if results.solver.termination_condition != TerminationCondition.optimal:
            raise RuntimeError('Solver did not report optimality:\n%s'
                               % (results.solver))
    model.solutions.load_from(results)

    print('time: {}\nobjective: {}\n'.format(results.solver.time, model.o()))
    for v in model.component_data_objects(ctype=Var):
      print('{}: {}'.format(v, v.value))
#!/bin/python3.8

import numpy as np
import ipopt

class opt_obj(object):
  def __init__(self) -> None:
    pass
  
  def objective(self, x):
    return x[0] * x[3] * np.sum(x[0:3]) + x[2]

  def gradient(self, x):
    return np.array([
      x[0] * x[3] + x[3] * np.sum(x[0:3]),
      x[0] * x[3],
      x[0] * x[3] + 1.0,
      x[0] * np.sum(x[0:3])
    ])

  def constraints(self, x):
    return np.array((np.prod(x), np.dot(x, x)))

  def jacobian(self, x):
    return np.concatenate((np.prod(x) / x, 2*x))


if __name__ == "__main__":
  x0 = [1.0, 5.0, 5.0, 1.0]

  lb = [1.0, 1.0, 1.0, 1.0]
  ub = [5.0, 5.0, 5.0, 5.0]

  cl = [25.0, 40.0]
  cu = [2.0e19, 40.0]

  nlp = ipopt.problem(
    n=len(x0),
    m=len(cl),
    problem_obj=opt_obj(),
    lb=lb,
    ub=ub,
    cl=cl,
    cu=cu
  )

  x, info = nlp.solve(x0)

  print(x)

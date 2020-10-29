#!/bin/python3.8

from pyomo.core.base.PyomoModel import ConcreteModel # type: ignore

from UCP.unit_commitment_problem import UCP, UCP_Solution


class UCP_MINLP(object):
  model: ConcreteModel

  def __init__(self, ucp: UCP) -> None:
    ''' Build self.model from ucp '''
    pass

  def optimize(self) -> UCP_Solution:
    ''' Optimize self.model  and return the solution '''
    pass


if __name__ == "__main__":
  pass

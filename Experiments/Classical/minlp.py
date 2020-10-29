#!/bin/python3.8

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from Experiments.UCP.unit_commitment_problem import UCP, UCP_Solution

from pyomo.core.base.PyomoModel import ConcreteModel


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

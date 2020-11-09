#!/bin/python3.8


import unittest
from Classical.minlp import UCP_MINLP

from UCP.unit_commitment_problem import CombustionPlant, UCP, UCP_Solution


class TestUCP(unittest.TestCase):
  def test_ucp_objective(self):
    assert(False) # TODO: test basic case (only objective)

  def test_start_up(self):
    ucp = UCP([1, 1, 4], [
      CombustionPlant(0, 10, 5, 1, 50, 0, 0),
      CombustionPlant(0, 20, 1, 1, 50, 1000, 0)
    ])

    minlp = UCP_MINLP(ucp)
    solution: UCP_Solution = minlp.optimize() # TODO: use pyomo solver
    assert(not solution.u[1][2])
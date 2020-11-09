#!/bin/python3.8


import unittest

from Classical.minlp import UCP_MINLP

from UCP.unit_commitment_problem import CombustionPlant, UCP, UCP_Solution


class TestUCP(unittest.TestCase):
  @staticmethod
  def optimize(ucp: UCP) -> UCP_Solution:
    minlp: UCP_MINLP = UCP_MINLP(ucp)
    return minlp.optimize() # TODO: use pyomo optimizer

  def test_ucp_no_load(self):
    load = [0, 0, 0, 0, 0]
    plant = CombustionPlant(1, 1, 1, 0, 1000, 0, 0)
    ucp = UCP(load, [plant])

    solution = TestUCP.optimize(ucp)

    assert(solution.o == 0)
    for t in range(len(load)):
      assert(not solution.u[0][t])

  def test_start_up(self):
    load = [1, 1, 4]
    plants = [
      CombustionPlant(0, 10, 5, 1, 50, 500, 0),
      CombustionPlant(0, 20, 1, 1, 50, 1000, 0)
    ]
    ucp = UCP(load, plants)

    solution = TestUCP.optimize(ucp)
    
    for t in range(len(load)):
      assert(not solution.u[0][t])
      assert(solution.u[1][t])

  def test_start_up_initial(self): # TODO: adjust test conditions
    load = [1, 1, 4]
    plants = [
      CombustionPlant(0, 10, 5, 1, 50, 500, 0, initially_on=True),
      CombustionPlant(0, 20, 1, 1, 50, 1000, 0)
    ]
    ucp = UCP(load, plants)

    solution = TestUCP.optimize(ucp)
    
    for t in range(len(load)):
      assert(solution.u[0][t])
      assert(not solution.u[1][t])
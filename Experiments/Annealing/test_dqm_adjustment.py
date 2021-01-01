#!/bin/python3.8


from typing import List
import unittest
from Annealing.dqm import UCP_DQM
from Annealing.dqm_simulator import DQMSimulator

from UCP.unit_commitment_problem import CombustionPlant, ExperimentParameters, UCP, UCP_Solution


class TestDQMAdjust(unittest.TestCase):

  def assertFloatCustomEqual(self, actual: float, expected: float) -> None:
    self.assertAlmostEqual(actual, expected, delta=0.00001)

  def assertFloatArrayCustomEqual(self, actual: List[float], expected: List[float]) -> None:
    self.assertEqual(len(actual), len(expected))

    for i in range(len(actual)):
      self.assertFloatCustomEqual(actual[i], expected[i])

  def assertFloat2DimArrayCustomEqual(self, actual: List[List[float]], expected: List[List[float]]) -> None:
    self.assertEqual(len(actual), len(expected))

    for i in range(len(actual)):
      self.assertFloatArrayCustomEqual(expected[i], actual[i])

  def power_levels(self, ucp_solution: UCP_Solution, p: List[List[float]]):
    self.assertFloat2DimArrayCustomEqual(ucp_solution.p, p)


  def test_uniform_adjustment(self):
    ucp: UCP = UCP(
      ExperimentParameters(1, 2),
      [30],
      [
        CombustionPlant(0, 1, 0, 10, 30, 0, 0),
        CombustionPlant(0, 1, 0, 10, 30, 0, 0)
      ]
    )

    dqm: UCP_DQM = UCP_DQM(ucp)
    sol_unadjusted: UCP_Solution = dqm.optimize(DQMSimulator(), adjust=False)
    self.power_levels(sol_unadjusted, [[10], [10]])

    dqm = UCP_DQM(ucp)
    sol_adjusted: UCP_Solution = dqm.optimize(DQMSimulator(), adjust=True)
    self.power_levels(sol_adjusted, [[15], [15]])

  def test_dont_adjust_off_plants(self):
    ucp: UCP = UCP(
      ExperimentParameters(1, 2),
      [10],
      [
        CombustionPlant(0, 1, 0, 10, 30, 0, 0),
        CombustionPlant(0, 1, 0, 10, 30, 0, 0)
      ]
    )

    dqm: UCP_DQM = UCP_DQM(ucp)
    sol_unadjusted: UCP_Solution = dqm.optimize(DQMSimulator(), adjust=False)
    self.power_levels(sol_unadjusted, [[0], [0]])

    dqm = UCP_DQM(ucp)
    sol_adjusted: UCP_Solution = dqm.optimize(DQMSimulator(), adjust=True)
    self.power_levels(sol_adjusted, [[0], [0]])

  def test_adjust_dont_violate_pmax_single(self):
    ucp: UCP = UCP(
      ExperimentParameters(1, 2),
      [80],
      [
        CombustionPlant(0, 1, 0, 10, 30, 0, 0),
        CombustionPlant(0, 1, 0, 10, 70, 0, 0)
      ]
    )

    dqm: UCP_DQM = UCP_DQM(ucp)
    sol_unadjusted: UCP_Solution = dqm.optimize(DQMSimulator(), adjust=False)
    self.power_levels(sol_unadjusted, [[30], [40]])

    dqm = UCP_DQM(ucp)
    sol_adjusted: UCP_Solution = dqm.optimize(DQMSimulator(), adjust=True)
    self.power_levels(sol_adjusted, [[30], [50]])

  def test_adjust_dont_violate_pmax_all(self):
    ucp: UCP = UCP(
      ExperimentParameters(1, 2),
      [80],
      [
        CombustionPlant(0, 1, 0, 10, 30, 0, 0),
        CombustionPlant(0, 1, 0, 10, 30, 0, 0)
      ]
    )

    dqm: UCP_DQM = UCP_DQM(ucp)
    sol_unadjusted: UCP_Solution = dqm.optimize(DQMSimulator(), adjust=False)
    self.power_levels(sol_unadjusted, [[30], [30]])

    dqm = UCP_DQM(ucp)
    sol_adjusted: UCP_Solution = dqm.optimize(DQMSimulator(), adjust=True)
    self.power_levels(sol_adjusted, [[30], [30]])

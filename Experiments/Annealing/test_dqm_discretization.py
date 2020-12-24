#!/bin/python3.8

from typing import List
import unittest

from UCP.unit_commitment_problem import CombustionPlant, ExperimentParameters, UCP
from Annealing.dqm import UCP_DQM

class TestDQMDiscretization(unittest.TestCase):

  def assertFloatCustomEqual(self, actual: float, expected: float) -> None:
    self.assertAlmostEqual(actual, expected, delta=0.00001)

  def assertFloatArrayCustomEqual(self, actual: List[float], expected: List[float]) -> None:
    self.assertEqual(len(actual), len(expected))

    for i in range(len(actual)):
      self.assertFloatCustomEqual(actual[i], expected[i])

  def discretize_plant(self, Pmin: float, Pmax: float, expected_P: List[float]) -> None:
    ucp = UCP(ExperimentParameters(1, 1), [1], [
      CombustionPlant(1, 1, 1, Pmin, Pmax, 0, 0)
    ])

    dqm: UCP_DQM = UCP_DQM(ucp)

    self.assertFloatArrayCustomEqual(dqm.P[0], expected_P)

  def test_2(self):
    self.discretize_plant(10, 28, [0, 10, 19, 28])
    self.discretize_plant(10, 30, [10 * x for x in range(4)])

  def test_3(self):
    self.discretize_plant(10, 64, [0, 10, 19, 28, 37, 46, 55, 64])
    self.discretize_plant(10, 70, [10 * x for x in range(8)])

  def test_4(self):
    self.discretize_plant(10, 136, [0, 10, 19, 28, 37, 46, 55, 64, 73, 82, 91, 100, 109, 118, 127, 136])
    self.discretize_plant(10, 150, [10 * x for x in range(16)])

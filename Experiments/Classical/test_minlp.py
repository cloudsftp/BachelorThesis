#!/bin/python3.8


from typing import List
import unittest

from Classical.minlp import UCP_MINLP

from UCP.unit_commitment_problem import CombustionPlant, UCP, UCP_Solution


class TestUCP(unittest.TestCase):
  @staticmethod
  def optimize(ucp: UCP) -> UCP_Solution:
    minlp: UCP_MINLP = UCP_MINLP(ucp)
    return minlp.optimize() # TODO: use pyomo optimizer

  def assertFloatCustomEqual(self, actual: float, expected: float) -> None:
    self.assertAlmostEqual(actual, expected, delta=0.01)

  def assertFloatArrayCustomEqual(self, actual: List[float], expected: List[float]) -> None:
    self.assertEqual(len(actual), len(expected))

    for i in range(len(actual)):
      self.assertFloatCustomEqual(actual[i], expected[i])

  def assertFloat2DimArrayCustomEqual(self, actual: List[List[float]], expected: List[List[float]]) -> None:
    self.assertEqual(len(actual), len(expected))

    for i in range(len(actual)):
      self.assertFloatArrayCustomEqual(expected[i], actual[i])

  def assert_solution(self, solution: UCP_Solution, \
                      u: List[List[bool]] = None, p: List[List[float]] = None, o: float = None) -> None:

    if u:
      self.assertEqual(solution.u, u)

    if p:
      self.assertFloat2DimArrayCustomEqual(solution.p, p)

    if o or o == 0:
      self.assertFloatCustomEqual(solution.o, o)

  def plants(self, load: List[float], plants: List[CombustionPlant], \
                  u: List[List[bool]] = None, p: List[List[float]] = None, o: float = None) -> None:

    ucp: UCP = UCP(load, plants)
    solution: UCP_Solution = TestUCP.optimize(ucp)
    self.assert_solution(solution, u, p, o)

  def single_plant(self, load: List[float], plant: CombustionPlant, \
                       u: List[bool] = None, p: List[float] = None, o: float = None) -> None:

    self.plants(load, [plant],\
       u=[u] if u else None, p=[p] if p else None, o=o if not o == None else None)

  def test_no_load(self):
    self.single_plant(
      [0, 0, 0, 0, 0],
      CombustionPlant(1, 1, 1, 0, 1000, 0, 0),
      u=[False for _ in range(5)],
      o=0
      )

  def test_only_load(self):
    self.single_plant(
      [10, 20, 10, 100],
      CombustionPlant(100, 10, 0.1, 0, 1000, 0, 0),
      u=[True for _ in range(4)],
      o=2860
    )

  def test_power_constraint(self):
    self.single_plant(
      [10], CombustionPlant(0, 1, 0, 10, 1000, 0, 0),
      u=[True], p=[10], o=10
    )

  def test_startup_cost(self):
    self.single_plant(
      [0, 10], CombustionPlant(0, 1, 0, 10, 1000, 5, 0),
      u=[False, True], p=[0, 10], o=15
    )
    self.single_plant(
      [10], CombustionPlant(0, 1, 0, 10, 1000, 5, 0),
      u=[True], p=[10], o=15
    )

  def test_no_startup_cost_when_initially_on(self):
    self.single_plant(
      [0, 10], CombustionPlant(0, 1, 0, 10, 1000, 15, 0, initially_on=True),
      u=[True, True], p=[10, 10], o=20
    )

  def test_shutdown_cost(self):
    self.single_plant(
      [10, 0], CombustionPlant(0, 1, 0, 10, 1000, 0, 5),
      u=[True, False], p=[10, 0], o=15
    )

  def test_dont_shut_down_if_too_expensive(self):
    self.single_plant(
      [10, 0], CombustionPlant(0, 1, 0, 10, 1000, 0, 15),
      u=[True, True], p=[10, 10], o=20
    )

  def test_two_plants_only_load(self):
    self.plants(
      [10, 20],
      [
        CombustionPlant(1, 1, 0, 0, 1000, 0, 0),
        CombustionPlant(1, 2, 0, 0, 1000, 0, 0)
      ],
      u=[[True, True], [False, False]],
      p=[[10, 20], [0, 0]],
      o=32
    )
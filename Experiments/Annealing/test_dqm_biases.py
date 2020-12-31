#!/bin/python3.8

from typing import List, Union

import numpy as np # type: ignore
from numpy.testing import assert_array_equal # type: ignore
import unittest

from UCP.unit_commitment_problem import CombustionPlant, ExperimentParameters, UCP
from Annealing.dqm import UCP_DQM

class TestDQMBiases(unittest.TestCase):

  def linear_biases(self, dqm: UCP_DQM, i: int, t: int, biases: List[float]) -> None:
    assert_array_equal(dqm.model.get_linear(dqm.p[i][t]), np.array(biases))

  def quadratic_biases(self, dqm: UCP_DQM, i0: int, t0: int, i1: int, t1: int, biases: Union[List[List[float]], np.ndarray]) -> None:
    assert_array_equal(dqm.model.get_quadratic(dqm.p[i0][t0], dqm.p[i1][t1], array=True), np.array(biases))

  def no_quadratic_biases(self, dqm: UCP_DQM, i0: int, t0: int, i1: int, t1: int) -> None:
    with self.assertRaises(ValueError) as context:
      dqm.model.get_quadratic(dqm.p[i0][t0], dqm.p[i1][t1])

    self.assertTrue('there is no interaction between given variables' in context.exception.args)

  ucp_instance_1: UCP = UCP( # This instance is unsolvable
    ExperimentParameters(3, 3),
    [1, 2, 1],
    [
      CombustionPlant(1, 0.5, 1, 10, 30, 1, 2),
      CombustionPlant(2, 1, 2, 10, 30, 2, 1),
      CombustionPlant(3, 2, 3, 20, 80, 0, 0)
    ]
  )

  def test_linear_1(self):
    dqm: UCP_DQM = UCP_DQM(self.ucp_instance_1)

    self.linear_biases(dqm, 0, 0, [6, 203, 798, 1793])
    self.linear_biases(dqm, 0, 1, [6, 192, 777, 1762])
    self.linear_biases(dqm, 0, 2, [6, 202, 797, 1792])

    self.linear_biases(dqm, 1, 0, [6, 310, 1210, 2710])
    self.linear_biases(dqm, 1, 1, [6, 298, 1188, 2678])
    self.linear_biases(dqm, 1, 2, [6, 308, 1208, 2708])

    self.linear_biases(dqm, 2, 0, [6, 1629, 3639, 6449, 10059, 14469, 19679, 25689])
    self.linear_biases(dqm, 2, 1, [6, 1609, 3609, 6409, 10009, 14409, 19609, 25609])
    self.linear_biases(dqm, 2, 2, [6, 1629, 3639, 6449, 10059, 14469, 19679, 25689])

  def test_quadratic_start_1(self):
    dqm: UCP_DQM = UCP_DQM(self.ucp_instance_1)

    S_0: List[List[float]] = [[0, 1, 1, 1],
                              [2, 0, 0, 0],
                              [2, 0, 0, 0],
                              [2, 0, 0, 0]]

    self.quadratic_biases(dqm, 0, 0, 0, 1, S_0)
    self.quadratic_biases(dqm, 0, 1, 0, 2, S_0)

    S_1: List[List[float]] = [[0, 2, 2, 2],
                              [1, 0, 0, 0],
                              [1, 0, 0, 0],
                              [1, 0, 0, 0]]

    self.quadratic_biases(dqm, 1, 0, 1, 1, S_1)
    self.quadratic_biases(dqm, 1, 1, 1, 2, S_1)

    S_2: np.ndarray = np.zeros((8, 8))
    self.quadratic_biases(dqm, 2, 0, 2, 1, S_2)
    self.quadratic_biases(dqm, 2, 1, 2, 2, S_2)

  def test_quadratic_demand_1(self):
    dqm: UCP_DQM = UCP_DQM(self.ucp_instance_1)

    P_0x1: List[List[float]] = [[0,   0,   0,   0],
                                [0, 100, 200, 300],
                                [0, 200, 400, 600],
                                [0, 300, 600, 900]]

    self.quadratic_biases(dqm, 0, 0, 1, 0, P_0x1)
    self.quadratic_biases(dqm, 0, 1, 1, 1, P_0x1)
    self.quadratic_biases(dqm, 0, 2, 1, 2, P_0x1)

    P_0x2: List[List[float]] = [[0,   0,   0,    0,    0,    0,    0,    0],
                                [0, 200, 300,  400,  500,  600,  700,  800],
                                [0, 400, 600,  800, 1000, 1200, 1400, 1600],
                                [0, 600, 900, 1200, 1500, 1800, 2100, 2400]]

    self.quadratic_biases(dqm, 0, 0, 2, 0, P_0x2)
    self.quadratic_biases(dqm, 0, 1, 2, 1, P_0x2)
    self.quadratic_biases(dqm, 0, 2, 2, 2, P_0x2)

    P_1x2: List[List[float]] = P_0x2
    self.quadratic_biases(dqm, 1, 0, 2, 0, P_1x2)
    self.quadratic_biases(dqm, 1, 1, 2, 1, P_1x2)
    self.quadratic_biases(dqm, 1, 2, 2, 2, P_1x2)

  def test_quadratic_zeros_1(self):
    dqm: UCP_DQM = UCP_DQM(self.ucp_instance_1)

    for i0 in range(3):
      for i1 in range(3):
        for t0 in range(3):
          for t1 in range(3):
            if i0 != i1 and t0 != t1:
              self.no_quadratic_biases(dqm, i0, t0, i1, t1)

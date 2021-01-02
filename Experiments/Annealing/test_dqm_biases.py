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


  ucp_instance_2: UCP = UCP(
    ExperimentParameters(2, 2),
    [30, 50],
    [
      CombustionPlant(0, 1, 0, 10, 30, 10, 20),
      CombustionPlant(0, 1, 0, 10, 30, 10, 20, initially_on=True)
    ]
  )

  def test_linear_2_all_1(self):
    dqm: UCP_DQM = UCP_DQM(self.ucp_instance_2)

    self.linear_biases(dqm, 0, 0, [3400, 3220, 3230, 3440])
    self.linear_biases(dqm, 1, 0, [3420, 3210, 3220, 3430])

    linear_biases_t_1: List[float] = [3400, 3010, 2820, 2830]
    self.linear_biases(dqm, 0, 1, linear_biases_t_1)
    self.linear_biases(dqm, 1, 1, linear_biases_t_1)

  def test_linear_2_cost_2(self):
    dqm: UCP_DQM = UCP_DQM(self.ucp_instance_2, y_c=2)

    self.linear_biases(dqm, 0, 0, [3400, 3230, 3250, 3470])
    self.linear_biases(dqm, 1, 0, [3420, 3220, 3240, 3460])

    linear_biases_t_1: List[float] = [3400, 3020, 2840, 2860]
    self.linear_biases(dqm, 0, 1, linear_biases_t_1)
    self.linear_biases(dqm, 1, 1, linear_biases_t_1)

  def test_linear_2_demand_2(self):
    dqm: UCP_DQM = UCP_DQM(self.ucp_instance_2, y_d=2)

    self.linear_biases(dqm, 0, 0, [6800, 6420, 6430, 6840])
    self.linear_biases(dqm, 1, 0, [6820, 6410, 6420, 6830])

    linear_biases_t_1: List[float] = [6800, 6010, 5620, 5630]
    self.linear_biases(dqm, 0, 1, linear_biases_t_1)
    self.linear_biases(dqm, 1, 1, linear_biases_t_1)

  def test_linear_2_startup_2(self):
    dqm: UCP_DQM = UCP_DQM(self.ucp_instance_2, y_s=2)

    self.linear_biases(dqm, 0, 0, [3400, 3230, 3240, 3450])
    self.linear_biases(dqm, 1, 0, [3440, 3210, 3220, 3430])

    linear_biases_t_1: List[float] = [3400, 3010, 2820, 2830]
    self.linear_biases(dqm, 0, 1, linear_biases_t_1)
    self.linear_biases(dqm, 1, 1, linear_biases_t_1)

  def test_quadratic_startup_2_1(self):
    dqm: UCP_DQM = UCP_DQM(self.ucp_instance_2)

    S: List[List[float]] = [[ 0, 10, 10, 10],
                            [20,  0,  0,  0],
                            [20,  0,  0,  0],
                            [20,  0,  0,  0]]

    for i in range(2):
      self.quadratic_biases(dqm, i, 0, i, 1, S)

  def test_quadratic_startup_2_2(self):
    dqm: UCP_DQM = UCP_DQM(self.ucp_instance_2, y_s=2)

    S: List[List[float]] = [[ 0, 20, 20, 20],
                            [40,  0,  0,  0],
                            [40,  0,  0,  0],
                            [40,  0,  0,  0]]

    for i in range(2):
      self.quadratic_biases(dqm, i, 0, i, 1, S)

  def test_quadratic_demand_2_1(self):
    dqm: UCP_DQM = UCP_DQM(self.ucp_instance_2)

    for t in range(2):
      self.quadratic_biases(dqm, 0, t, 1, t, [[0,   0,   0,   0],
                                              [0, 100, 200, 300],
                                              [0, 200, 400, 600],
                                              [0, 300, 600, 900]])

  def test_quadratic_zeros_2(self):
    dqm: UCP_DQM = UCP_DQM(self.ucp_instance_2)

    for i0 in range(2):
      for i1 in range(2):
        for t0 in range(2):
          for t1 in range(2):
            if i0 != i1 and t0 != t1:
              self.no_quadratic_biases(dqm, i0, t0, i1, t1)

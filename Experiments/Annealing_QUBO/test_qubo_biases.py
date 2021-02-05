#!/bin/python3.8

from typing import List, Union

import numpy as np # type: ignore
import unittest

from numpy.testing._private.utils import assert_equal # type: ignore

from UCP.unit_commitment_problem import CombustionPlant, ExperimentParameters, UCP
from Annealing_QUBO.qubo import UCP_QUBO

class TestQUBOBiases(unittest.TestCase):

  def linear_biases(self, qubo: UCP_QUBO, i: int, t: int, biases: List[float]) -> None:
    for k, bias in enumerate(biases):
      m: int = qubo.m[i, t, k]
      assert_equal(qubo.model[m, m], bias, '{}, {}, {}'.format(i, t, k))

  def quadratic_biases(self, qubo: UCP_QUBO, i0: int, t0: int, i1: int, t1: int, biases: Union[List[List[float]], np.ndarray]) -> None:
    for k0 in range(len(biases)):
      bias_list: Union[List[float], np.ndarray] = biases[k0]
      for k1 in range(len(bias_list)):
        m0: int = qubo.m[i0, t0, k0]
        m1: int = qubo.m[i1, t1, k1]

        assert_equal(qubo.model.get((m0, m1), 0), bias_list[k1])

  def no_quadratic_biases(self, qubo: UCP_QUBO, i0: int, t0: int, i1: int, t1: int) -> None:
    for k0 in range(len(qubo.P[i0])):
      for k1 in range(len(qubo.P[i1])):
        m0: int = qubo.m[i0, t0, k0]
        m1: int = qubo.m[i1, t1, k1]

        assert_equal(qubo.model.get((m0, m1), 0), 0)

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
    qubo: UCP_QUBO = UCP_QUBO(self.ucp_instance_1)

    self.linear_biases(qubo, 0, 0, [1, 198, 793, 1788])
    self.linear_biases(qubo, 0, 1, [1, 187, 772, 1757])
    self.linear_biases(qubo, 0, 2, [1, 197, 792, 1787])

    self.linear_biases(qubo, 1, 0, [1, 305, 1205, 2705])
    self.linear_biases(qubo, 1, 1, [1, 293, 1183, 2673])
    self.linear_biases(qubo, 1, 2, [1, 303, 1203, 2703])

    self.linear_biases(qubo, 2, 0, [1, 1624, 3634, 6444, 10054, 14464, 19674, 25684])
    self.linear_biases(qubo, 2, 1, [1, 1604, 3604, 6404, 10004, 14404, 19604, 25604])
    self.linear_biases(qubo, 2, 2, [1, 1624, 3634, 6444, 10054, 14464, 19674, 25684])

  def test_quadratic_start_1(self):
    qubo: UCP_QUBO = UCP_QUBO(self.ucp_instance_1)

    S_0: List[List[float]] = [[0, 1, 1, 1],
                              [2, 0, 0, 0],
                              [2, 0, 0, 0],
                              [2, 0, 0, 0]]

    self.quadratic_biases(qubo, 0, 0, 0, 1, S_0)
    self.quadratic_biases(qubo, 0, 1, 0, 2, S_0)

    S_1: List[List[float]] = [[0, 2, 2, 2],
                              [1, 0, 0, 0],
                              [1, 0, 0, 0],
                              [1, 0, 0, 0]]

    self.quadratic_biases(qubo, 1, 0, 1, 1, S_1)
    self.quadratic_biases(qubo, 1, 1, 1, 2, S_1)

    S_2: np.ndarray = np.zeros((8, 8))
    self.quadratic_biases(qubo, 2, 0, 2, 1, S_2)
    self.quadratic_biases(qubo, 2, 1, 2, 2, S_2)

  def test_quadratic_demand_1(self):
    qubo: UCP_QUBO = UCP_QUBO(self.ucp_instance_1)

    P_0x1: List[List[float]] = [[0,   0,   0,   0],
                                [0, 100, 200, 300],
                                [0, 200, 400, 600],
                                [0, 300, 600, 900]]

    self.quadratic_biases(qubo, 0, 0, 1, 0, P_0x1)
    self.quadratic_biases(qubo, 0, 1, 1, 1, P_0x1)
    self.quadratic_biases(qubo, 0, 2, 1, 2, P_0x1)

    P_0x2: List[List[float]] = [[0,   0,   0,    0,    0,    0,    0,    0],
                                [0, 200, 300,  400,  500,  600,  700,  800],
                                [0, 400, 600,  800, 1000, 1200, 1400, 1600],
                                [0, 600, 900, 1200, 1500, 1800, 2100, 2400]]

    self.quadratic_biases(qubo, 0, 0, 2, 0, P_0x2)
    self.quadratic_biases(qubo, 0, 1, 2, 1, P_0x2)
    self.quadratic_biases(qubo, 0, 2, 2, 2, P_0x2)

    P_1x2: List[List[float]] = P_0x2
    self.quadratic_biases(qubo, 1, 0, 2, 0, P_1x2)
    self.quadratic_biases(qubo, 1, 1, 2, 1, P_1x2)
    self.quadratic_biases(qubo, 1, 2, 2, 2, P_1x2)

  def test_quadratic_zeros_1(self):
    qubo: UCP_QUBO = UCP_QUBO(self.ucp_instance_1)

    for i0 in range(3):
      for i1 in range(3):
        for t0 in range(3):
          for t1 in range(3):
            if i0 != i1 and t0 != t1:
              self.no_quadratic_biases(qubo, i0, t0, i1, t1)


  ucp_instance_2: UCP = UCP(
    ExperimentParameters(2, 2),
    [30, 50],
    [
      CombustionPlant(0, 1, 0, 10, 30, 10, 20),
      CombustionPlant(0, 1, 0, 10, 30, 10, 20, initially_on=True)
    ]
  )

  def test_linear_2_all_1(self):
    qubo: UCP_QUBO = UCP_QUBO(self.ucp_instance_2)

    self.linear_biases(qubo, 0, 0, [1, -179, -169, 41])
    self.linear_biases(qubo, 1, 0, [21, -189, -179, 31])

    linear_biases_t_1: List[float] = [1, -389, -579, -569]
    self.linear_biases(qubo, 0, 1, linear_biases_t_1)
    self.linear_biases(qubo, 1, 1, linear_biases_t_1)

  def test_linear_2_cost_2(self):
    qubo: UCP_QUBO = UCP_QUBO(self.ucp_instance_2, y_c=2)

    self.linear_biases(qubo, 0, 0, [1, -169, -149, 71])
    self.linear_biases(qubo, 1, 0, [21, -179, -159, 61])

    linear_biases_t_1: List[float] = [1, -379, -559, -539]
    self.linear_biases(qubo, 0, 1, linear_biases_t_1)
    self.linear_biases(qubo, 1, 1, linear_biases_t_1)

  def test_linear_2_demand_2(self):
    qubo: UCP_QUBO = UCP_QUBO(self.ucp_instance_2, y_d=2)

    self.linear_biases(qubo, 0, 0, [1, -379, -369, 41])
    self.linear_biases(qubo, 1, 0, [21, -389, -379, 31])

    linear_biases_t_1: List[float] = [1, -789, -1179, -1169]
    self.linear_biases(qubo, 0, 1, linear_biases_t_1)
    self.linear_biases(qubo, 1, 1, linear_biases_t_1)

  def test_linear_2_startup_2(self):
    qubo: UCP_QUBO = UCP_QUBO(self.ucp_instance_2, y_s=2)

    self.linear_biases(qubo, 0, 0, [1, -169, -159, 51])
    self.linear_biases(qubo, 1, 0, [41, -189, -179, 31])

    linear_biases_t_1: List[float] = [1, -389, -579, -569]
    self.linear_biases(qubo, 0, 1, linear_biases_t_1)
    self.linear_biases(qubo, 1, 1, linear_biases_t_1)

  def test_linear_2_power_2(self):
    qubo: UCP_QUBO = UCP_QUBO(self.ucp_instance_2, y_p=2)

    self.linear_biases(qubo, 0, 0, [2, -178, -168, 42])
    self.linear_biases(qubo, 1, 0, [22, -188, -178, 32])

    linear_biases_t_1: List[float] = [2, -388, -578, -568]
    self.linear_biases(qubo, 0, 1, linear_biases_t_1)
    self.linear_biases(qubo, 1, 1, linear_biases_t_1)

  def test_quadratic_startup_2_1(self):
    qubo: UCP_QUBO = UCP_QUBO(self.ucp_instance_2)

    S: List[List[float]] = [[ 0, 10, 10, 10],
                            [20,  0,  0,  0],
                            [20,  0,  0,  0],
                            [20,  0,  0,  0]]

    for i in range(2):
      self.quadratic_biases(qubo, i, 0, i, 1, S)

  def test_quadratic_startup_2_2(self):
    qubo: UCP_QUBO = UCP_QUBO(self.ucp_instance_2, y_s=2)

    S: List[List[float]] = [[ 0, 20, 20, 20],
                            [40,  0,  0,  0],
                            [40,  0,  0,  0],
                            [40,  0,  0,  0]]

    for i in range(2):
      self.quadratic_biases(qubo, i, 0, i, 1, S)

  def test_quadratic_demand_2_1(self):
    qubo: UCP_QUBO = UCP_QUBO(self.ucp_instance_2)

    for t in range(2):
      self.quadratic_biases(qubo, 0, t, 1, t, [[0,   0,   0,   0],
                                              [0, 100, 200, 300],
                                              [0, 200, 400, 600],
                                              [0, 300, 600, 900]])

  def test_quadratic_power_2(self):
    qubo: UCP_QUBO = UCP_QUBO(self.ucp_instance_2)

    for i in range(2):
      for t in range(2):
        for l in range(4):
          for k in range(l):
            m0: int = qubo.m[i, t, k]
            m1: int = qubo.m[i, t, l]

            assert_equal(qubo.model[m0, m1], 1)

  def test_quadratic_zeros_2(self):
    qubo: UCP_QUBO = UCP_QUBO(self.ucp_instance_2)

    for i0 in range(2):
      for i1 in range(2):
        for t0 in range(2):
          for t1 in range(2):
            if i0 != i1 and t0 != t1:
              self.no_quadratic_biases(qubo, i0, t0, i1, t1)

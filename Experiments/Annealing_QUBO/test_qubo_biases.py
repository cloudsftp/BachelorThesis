#!/bin/python
# version 3.8 required

from typing import List, Union
import numpy as np # type: ignore
import unittest
from numpy.testing._private.utils import assert_equal # type: ignore

from UCP.unit_commitment_problem import CombustionPlant, ExperimentParameters, UCP
from Annealing_QUBO.qubo import UCP_QUBO

class TestQUBOBiases(unittest.TestCase):
  '''
  tests the generation of QUBOs using different UCPs
  '''

  def linear_biases(self, qubo: UCP_QUBO, i: int, t: int, biases: List[float]) -> None:
    for k, bias in enumerate(biases):
      m: int = qubo.m[i, t, k]
      assert_equal(qubo.model.get((m, m), 0), bias, '{}, {}, {}'.format(i, t, k))

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

    self.linear_biases(qubo, 0, 0, [0, 197, 792, 1787])
    self.linear_biases(qubo, 0, 1, [0, 186, 771, 1756])
    self.linear_biases(qubo, 0, 2, [0, 196, 791, 1786])

    self.linear_biases(qubo, 1, 0, [0, 304, 1204, 2704])
    self.linear_biases(qubo, 1, 1, [0, 292, 1182, 2672])
    self.linear_biases(qubo, 1, 2, [0, 302, 1202, 2702])

    self.linear_biases(qubo, 2, 0, [0, 1623, 3633, 6443, 10053, 14463, 19673, 25683])
    self.linear_biases(qubo, 2, 1, [0, 1603, 3603, 6403, 10003, 14403, 19603, 25603])
    self.linear_biases(qubo, 2, 2, [0, 1623, 3633, 6443, 10053, 14463, 19673, 25683])

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

    self.linear_biases(qubo, 0, 0, [0, -180, -170, 40])
    self.linear_biases(qubo, 1, 0, [20, -190, -180, 30])

    linear_biases_t_1: List[float] = [0, -390, -580, -570]
    self.linear_biases(qubo, 0, 1, linear_biases_t_1)
    self.linear_biases(qubo, 1, 1, linear_biases_t_1)

  def test_linear_2_cost_2(self):
    qubo: UCP_QUBO = UCP_QUBO(self.ucp_instance_2, y_c=2)

    self.linear_biases(qubo, 0, 0, [0, -170, -150, 70])
    self.linear_biases(qubo, 1, 0, [20, -180, -160, 60])

    linear_biases_t_1: List[float] = [0, -380, -560, -540]
    self.linear_biases(qubo, 0, 1, linear_biases_t_1)
    self.linear_biases(qubo, 1, 1, linear_biases_t_1)

  def test_linear_2_demand_2(self):
    qubo: UCP_QUBO = UCP_QUBO(self.ucp_instance_2, y_d=2)

    self.linear_biases(qubo, 0, 0, [0, -380, -370, 40])
    self.linear_biases(qubo, 1, 0, [20, -390, -380, 30])

    linear_biases_t_1: List[float] = [0, -790, -1180, -1170]
    self.linear_biases(qubo, 0, 1, linear_biases_t_1)
    self.linear_biases(qubo, 1, 1, linear_biases_t_1)

  def test_linear_2_startup_2(self):
    qubo: UCP_QUBO = UCP_QUBO(self.ucp_instance_2, y_s=2)

    self.linear_biases(qubo, 0, 0, [0, -170, -160, 50])
    self.linear_biases(qubo, 1, 0, [40, -190, -180, 30])

    linear_biases_t_1: List[float] = [0, -390, -580, -570]
    self.linear_biases(qubo, 0, 1, linear_biases_t_1)
    self.linear_biases(qubo, 1, 1, linear_biases_t_1)

  def test_linear_2_power_2(self):
    qubo: UCP_QUBO = UCP_QUBO(self.ucp_instance_2, y_p=2)

    self.linear_biases(qubo, 0, 0, [0, -180, -170, 40])
    self.linear_biases(qubo, 1, 0, [20, -190, -180, 30])

    linear_biases_t_1: List[float] = [0, -390, -580, -570]
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

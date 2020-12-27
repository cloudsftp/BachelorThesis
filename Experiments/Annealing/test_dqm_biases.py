#!/bin/python3.8

from typing import List

import numpy as np
from numpy.testing import assert_array_equal # type: ignore
import unittest

from UCP.unit_commitment_problem import CombustionPlant, ExperimentParameters, UCP
from Annealing.dqm import UCP_DQM

class TestDQMBiases(unittest.TestCase):

  def linear_biases(self, dqm: UCP_DQM, i: int, t: int, biases: List[float]) -> None:
    assert_array_equal(dqm.model.get_linear(dqm.p[i][t]), np.array(biases))


  ucp_instance_0: UCP = UCP(
    ExperimentParameters(3, 3),
    [1, 2, 1],
    [
      CombustionPlant(1, 0.5, 1, 10, 30, 1, 2),
      CombustionPlant(2, 1, 2, 10, 30, 2, 1),
      CombustionPlant(3, 2, 3, 20, 80, 0, 0)
    ]
  )

  def testdummy(self):
    dqm: UCP_DQM = UCP_DQM(self.ucp_instance_0)

    self.linear_biases(dqm, 0, 0, [0, 196, 791, 1786])
    self.linear_biases(dqm, 0, 1, [0, 186, 771, 1756])
    self.linear_biases(dqm, 0, 2, [0, 196, 791, 1786])

    self.linear_biases(dqm, 1, 0, [0, 302, 1202, 2702])
    self.linear_biases(dqm, 1, 1, [0, 292, 1182, 2672])
    self.linear_biases(dqm, 1, 2, [0, 302, 1202, 2702])

    self.linear_biases(dqm, 2, 0, [0, 1623, 3633, 6443, 10053, 14463, 19673, 25683])
    self.linear_biases(dqm, 2, 1, [0, 1603, 3603, 6403, 10003, 14403, 19603, 25603])
    self.linear_biases(dqm, 2, 2, [0, 1623, 3633, 6443, 10053, 14463, 19673, 25683])

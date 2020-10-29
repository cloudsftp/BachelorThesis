#!/bin/python3.8

import json
import os
from dataclasses import asdict
import unittest

from unit_commitment_problem import CombustionPlant, UCP


class TestUCP(unittest.TestCase):
  ucp = UCP([1, 2, 3], [
    CombustionPlant(1, 1, 1, 0, 100),
    CombustionPlant(2, 2, 2, 0, 200),
  ])

  ucp_dict = asdict(ucp)

  test_file_name = 'test_ucp.json'

  def test_save(self):
    self.ucp.save_to(self.test_file_name)

    assert(os.path.isfile(self.test_file_name))

    with open(self.test_file_name, 'r') as file:
      stored_dict = json.load(file)
      assert(stored_dict == self.ucp_dict)
    
    os.remove(self.test_file_name)

  def test_load(self):
    with open(self.test_file_name, 'w') as file:
      json.dump(self.ucp_dict, file)

    ucp = UCP.load_from(self.test_file_name)

    assert(asdict(ucp) == self.ucp_dict)
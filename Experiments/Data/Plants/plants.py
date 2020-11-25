#!/bin/python3.8

import os
import json
from dataclasses import dataclass
from typing import Any, Dict, List

from UCP.unit_commitment_problem import CombustionPlant


@dataclass
class Plants(object):
  meta: Dict[str, Any]
  plants: List[CombustionPlant]
  path: str = os.path.join('Data', 'Plants')

  @staticmethod
  def read_from_json(file_name):
    with open(os.path.join(Plants.path, file_name), 'r') as file:
      raw_data: Dict[str, Any] = json.load(file)

      meta: Dict[str, any] = raw_data['meta']

      raw_plants: List[Dict[str, Any]] = raw_data['plants']
      plants: List[CombustionPlant] = []
      for raw_plant in raw_plants:
        raw_plant.pop('source', None)
        plants.append(CombustionPlant(**raw_plant))

      return Plants(meta, plants)
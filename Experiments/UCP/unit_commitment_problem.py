#/bin/python3.8

from dataclasses import dataclass, field, asdict
import json
from typing import List

@dataclass
class CombustionPlant(object):
  A: float
  B: float
  C: float
  Pmin: float
  Pmax: float
  

@dataclass
class UCP(object):
  loads: List[float]
  plants: List[CombustionPlant] = field(default_factory=list)

  def save_to(self, filename) -> None:
    with open(filename, 'w') as file:
      json.dump(asdict(self), file, ensure_ascii=False, indent=4)

  def load_from(filename):
    with open(filename, 'r') as file:
      instance_dict: dict = json.load(file)

      loads: List[int] = instance_dict['loads']

      plants_dict_list: List[dict] = instance_dict['plants']
      plants: List[CombustionPlant] = []

      for plants_dict in plants_dict_list:
        A: float = plants_dict['A']
        B: float = plants_dict['B']
        C: float = plants_dict['C']
        Pmin: float = plants_dict['Pmin']
        Pmax: float = plants_dict['Pmax']

        plants.append(CombustionPlant(A, B, C, Pmin, Pmax))

      return UCP(loads, plants)

@dataclass
class UCP_Solution(object):
  ucp: UCP
  time: float
  optimal: bool
  o: float
  u: List[List[bool]]
  p: List[List[float]]
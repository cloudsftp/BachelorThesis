#/bin/python3.8

from dataclasses import dataclass, field, asdict
import json
from typing import List

from Util.json_file_handler import write_dataclass_to, read_dataclass_from

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

  def save_to(self, file_name) -> None:
    write_dataclass_to(self, file_name)

  def load_from(file_name):
    return read_dataclass_from(file_name, UCP)

@dataclass
class UCP_Solution(object):
  ucp: UCP
  time: float
  optimal: bool
  o: float
  u: List[List[bool]]
  p: List[List[float]]
#/bin/python3.8

import os
from dataclasses import dataclass, field, asdict
from typing import List

from Util.json_file_handler import write_dataclass_to, read_dataclass_from

@dataclass
class CombustionPlant(object):
  A: float
  B: float
  C: float
  Pmin: float
  Pmax: float
  AU: float
  AD: float
  initially_on: bool = False
  type: str = 'None'


@dataclass
class UCP(object):
  loads: List[float]
  plants: List[CombustionPlant] = field(default_factory=list)

  def save_to(self, file_name) -> None:
    write_dataclass_to(self, file_name)

  @staticmethod
  def load_from(file_name):
    return read_dataclass_from(file_name, UCP)


@dataclass
class ExperimentParameters(object):
  num_loads: int
  num_plants: int
  offset_loads: int = 0

  def to_file_name(self, prefix: str) -> str:
    return '{}_{:03}_{:03}.json' \
      .format(prefix, self.num_loads, self.num_plants)

  @staticmethod
  def from_file_name(file_name: str):
    file_name = os.path.basename(file_name)
    file_name = file_name.split('.')[0]

    file_name_parts: List[str] = file_name.split('_')
    num_loads: int = int(file_name_parts[1])
    num_plants: int = int(file_name_parts[2])

    return ExperimentParameters(num_loads, num_plants)


@dataclass
class UCP_Solution(object):
  parameters: ExperimentParameters
  ucp: UCP
  time: float
  optimal: bool
  o: float
  u: List[List[bool]]
  p: List[List[float]]

  def save_to(self, file_name) -> None:
    write_dataclass_to(self, file_name)

  @staticmethod
  def load_from(file_name):
    return read_dataclass_from(file_name, UCP_Solution)

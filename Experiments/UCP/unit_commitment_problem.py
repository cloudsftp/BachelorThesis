#/bin/python3.8

import os
from dataclasses import dataclass, field
import functools
from typing import List

from Util.json_file_handler import write_dataclass_to, read_dataclass_from
from Util.logging import debug_msg_time, debug_msg


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
  parameters: ExperimentParameters
  loads: List[float]
  plants: List[CombustionPlant] = field(default_factory=list)

  def save_to(self, file_name) -> None:
    write_dataclass_to(self, file_name)

  @staticmethod
  def load_from(file_name):
    return read_dataclass_from(file_name, UCP)

  def calculate_o(self, u: List[List[bool]], p: List[List[float]]) -> float:
    o: float = 0

    for i in range(self.parameters.num_plants):
      plant: CombustionPlant = self.plants[i]
      for t in range(self.parameters.num_loads):
        if u[i][t]:
          o += plant.A + plant.B * p[i][t] + plant.C * (p[i][t] ** 2)

        if t > 0 and u[i][t] and not u[i][t-1]:
          o += plant.AU
        elif t > 0 and not u[i][t] and u[i][t-1]:
          o += plant.AD

    return o


@dataclass
class UCPSolution(object):
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
    return read_dataclass_from(file_name, UCPSolution)


  def check_validity(self) -> None:
    debug_msg_time('Start Checking Validity of Solution\n')

    quality: float = 0

    for t in range(self.ucp.parameters.num_loads):
      combined_output: float = 0

      for i in range(self.ucp.parameters.num_plants):
        p: float = self.p[i][t]
        Pmin: float = self.ucp.plants[i].Pmin
        Pmax: float = self.ucp.plants[i].Pmax

        if not Pmin <= p <= Pmax and p != 0:
          quality += p - Pmin if p < Pmin else Pmax - p
          debug_msg('p {:3d}, {:3d}:\t{:4.2f} <= {:4.2f} <= {:4.2f}'.format(i, t, Pmin, p, Pmax))

        combined_output += p

      l = self.ucp.loads[t]
      if l > combined_output:
        quality += combined_output - l
        debug_msg('sum p {:3d}:\t{:4.2f} <= {:4.2f} - off {:4.2f}'.format(t, l, combined_output, combined_output - l))

    debug_msg('Quality:\t{:12.2f}'.format(quality))

  def adjust_variables(self) -> None:
    for t in range(self.ucp.parameters.num_loads):
      adjust: List[bool] = [self.u[i][t] for i in range(self.ucp.parameters.num_plants)]
      delta: float = self.ucp.loads[t] - sum([self.p[i][t] for i in range(self.ucp.parameters.num_plants)])

      while True:
        if delta == 0 or not functools.reduce(lambda a,b: a or b, adjust):
          break

        adjustment: float = delta / sum([1 if b else 0 for b in adjust])
        delta = 0

        for i in range(self.ucp.parameters.num_plants):
          if adjust[i]:
            self.p[i][t] += adjustment
            Pmax: float = self.ucp.plants[i].Pmax
            Pmin: float = self.ucp.plants[i].Pmin

            if self.p[i][t] > Pmax:
              delta += self.p[i][t] - Pmax
              self.p[i][t] = Pmax
              adjust[i] = False

            elif self.p[i][t] < Pmin:
              delta += self.p[i][t] - Pmin
              self.p[i][t] = Pmin
              adjust[i] = False

    self.o = self.ucp.calculate_o(self.u, self.p)

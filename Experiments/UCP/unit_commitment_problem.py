#/bin/python3.8

from dataclasses import dataclass, field
from typing import List

@dataclass
class CombustionPlant(object):
  A: float
  B: float
  C: float
  

@dataclass
class UCP(object):
  load: float
  plants: List[CombustionPlant] = field(default_factory=list)


if __name__ == "__main__":
  pass
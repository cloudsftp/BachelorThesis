#!/bin/python3.8

import json
from dataclasses import asdict
from typing import Any, Dict

# NOTE: Functions only work on/with dataclasses
#       static type checking is not supported

def write_dataclass_to(data: Any, file_name: str) -> None:
  with open(file_name, 'w') as file:
    json.dump(asdict(data), file, ensure_ascii=False, indent=4)

def read_dataclass_from(file_name: str, Dataclass) -> Any:
  data: Dict = {}

  with open(file_name, 'r') as file:
    data = json.load(file)

  return Dataclass(**data)
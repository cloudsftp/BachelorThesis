#!/bin/python
# version 3.8 required

import json
from dataclasses import asdict
from typing import Any, Dict

# NOTE: Functions only work on/with dataclasses
#       static type checking is not supported

def write_dataclass_to(data: Any, file_name: str) -> None:
  '''
  writes a dataclass to a file

  :data: data to write
  :file_name: file to write to
  '''
  with open(file_name, 'w') as file:
    json.dump(asdict(data), file, ensure_ascii=False, indent=4)

def convert_dict_to_datclass(dict: Dict, Dataclass) -> Any:
  '''
  converts a dictinionary to a dataclass

  :dict: data to convert
  :Dataclass: type of dataclass
  '''
  for key in dict:
    if isinstance(dict[key], Dict) and not Dataclass.__annotations__[key] == dict:
      dict[key] = convert_dict_to_datclass(dict[key], Dataclass.__annotations__[key])

  return Dataclass(**dict)

def read_dataclass_from(file_name: str, Dataclass) -> Any:
  '''
  reads a dataclass from a file

  :file_name: file to read from
  :Dataclass: type of dataclass
  '''
  data: Dict = {}

  with open(file_name, 'r') as file:
    data = json.load(file)

  return convert_dict_to_datclass(data, Dataclass)

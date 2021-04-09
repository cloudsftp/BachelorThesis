#!/bin/python
# version 3.8 required

import json
from dataclasses import asdict
from typing import Any, Dict

# NOTE: Functions only work on/with dataclasses
#       static type checking is not supported

'''
writes a dataclass to a file
'''
def write_dataclass_to(data: Any, file_name: str) -> None:
  with open(file_name, 'w') as file:
    json.dump(asdict(data), file, ensure_ascii=False, indent=4)


'''
converts a disctinionary to a dataclass of the specified type
'''
def convert_dict_to_datclass(dict: Dict, Dataclass) -> Any:
  for key in dict:
    if isinstance(dict[key], Dict) and not Dataclass.__annotations__[key] == dict:
      dict[key] = convert_dict_to_datclass(dict[key], Dataclass.__annotations__[key])

  return Dataclass(**dict)

'''
reads a dataclass of the specified type from a file
'''
def read_dataclass_from(file_name: str, Dataclass) -> Any:
  data: Dict = {}

  with open(file_name, 'r') as file:
    data = json.load(file)

  return convert_dict_to_datclass(data, Dataclass)

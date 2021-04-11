#!/bin/python
# version 3.8 required

import logging
from datetime import datetime
from typing import Any


def get_time() -> str:
  '''
  returns a string of the current time
  '''
  return datetime.now().strftime('%m.%d %H:%M:%S')

def debug_msg(msg: Any) -> None:
  '''
  prints a debugging message

  :msg: message to print
  '''
  logging.getLogger().debug(msg)
  print(msg)

def debug_msg_time(msg: Any) -> None:
  '''
  prints a debugging message including the current time

  :msg: message to print
  '''
  debug_msg('[ {} ] . {}'.format(get_time(), msg))

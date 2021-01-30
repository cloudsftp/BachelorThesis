#!/bin/python3.8

import logging
from datetime import datetime

def get_time() -> str:
  return datetime.now().strftime('%m.%d %H:%M:%S')

def debug_msg(msg: str) -> None:
  logging.getLogger().debug(msg)
  print(msg)

def debug_msg_time(msg: str) -> None:
  debug_msg('[ {} ] . {}'.format(get_time(), msg))

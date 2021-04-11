#!/bin/python
# version 3.8 required

import os
import numpy as np # type: ignore
import pandas as pd # type: ignore
from datetime import timedelta


class DemandData:
  '''
  holds demand data
  '''
  path: str = os.path.join('Data', 'DemandData')

  def __init__(self, data: pd.DataFrame=None, period: timedelta=None, interval_minutes: int=10) -> None:
    '''
    initializes the data object

    :data: demand data, default: None
    :timedelta: time resolution of data, default: None
    '''
    if isinstance(data, pd.DataFrame):
      # if data is passed, use it as demand data
      self.data = data

    elif isinstance(period, timedelta):
      # else initialize demand data with zeros
      period_minutes: float = period.days * 1440 + period.seconds / 60
      num_data_points: int = int (period_minutes / interval_minutes)

      self.data = pd.DataFrame(
        data=np.zeros([num_data_points, 1]),
        columns=['power_kW'],
        dtype=float
      )

  def to_csv(self, file_name: str) -> None:
    '''
    saves the demand data to a file

    :file_name: file to write to
    '''
    self.data.to_csv(os.path.join(self.path, file_name))

  @staticmethod
  def read_from_csv(file_name: str):
    '''
    loads demand data from a file

    :file_name: file to read from
    '''
    data: pd.DataFrame = pd.read_csv(os.path.join(DemandData.path, file_name), index_col=0)
    return DemandData(data=data)

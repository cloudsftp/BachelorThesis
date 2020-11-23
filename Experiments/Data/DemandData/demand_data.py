#!/bin/python3.8

import numpy as np # type: ignore
import pandas as pd # type: ignore
from datetime import timedelta

class DemandData:
  path: str= 'Data/DemandData/'

  def __init__(self, data: pd.DataFrame=None, period: timedelta=None, interval_minutes: int=10) -> None:
    if period == None:
      self.data = data

    else:
      period_minutes: float = period.days * 1440 + period.seconds / 60
      num_data_points: int = int (period_minutes / interval_minutes)

      self.data = pd.DataFrame(
        data=np.zeros([num_data_points, 1]),
        columns=['power_kW'],
        dtype=float
      )

  def to_csv(self, name: str) -> None:
    self.data.to_csv(self.path + name)

  def read_from_csv(name: str):
    data: pd.DataFrame = pd.read_csv(DemandData.path + name, index_col=0)
    return DemandData(data=data)
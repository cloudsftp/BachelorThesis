#!/bin/python3.8

import numpy as np # type: ignore
import pandas as pd # type: ignore
from datetime import timedelta

class DemandData:
  path: str= 'Data/DemandData/'

  def __init__(self, period: timedelta=None, data: pd.DataFrame=None, interval_minutes: int=10) -> None:
    if timedelta == None:
      self.data = data

    else:
      period_minutes: float = period.days * 1440 + period.seconds / 60
      num_data_points: int = int (period_minutes / interval_minutes)

      self.data = pd.DataFrame(
        np.array([[0, 0] for _ in range(num_data_points)]),
        index=[interval_minutes * i for i in range(num_data_points)],
        columns=['power_kW', 'num_cons'],
        dtype=float
      )

  def to_csv(self, name: str) -> None:
    self.data.to_csv(self.path + name)

  def read_from_csv(name: str):
    data: pd.DataFrame = pd.read_csv(DemandData.path + name, index_col=0)
    period: timedelta = timedelta(minutes=int(data.index[-1] - data.index[0]))
    return DemandData(period, data=data)
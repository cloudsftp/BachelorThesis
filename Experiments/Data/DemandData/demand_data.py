#!/bin/python3.8

import numpy as np # type: ignore
import pandas as pd # type: ignore
from datetime import datetime, timedelta

class DemandData:
  def __init__(self, start: datetime, end: datetime, interval_minutes=10) -> None:
    self.interval_minutes: float = interval_minutes

    period: timedelta = end - start
    period_minutes: float = period.days * 1440 + period.seconds / 60
    num_data_points: int = int (period_minutes / interval_minutes)

    self.data = pd.DataFrame(
      np.array([[0, 0, 0] for _ in range(num_data_points)]),
      index=[timedelta(minutes=interval_minutes) * i for i in range(num_data_points)],
      columns=['power_kW', 'num_cons', 'num_prod'],
      dtype=float
    )

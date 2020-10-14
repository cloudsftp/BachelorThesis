#!/bin/python3.8

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class DemandData:
  def __init__(self, start: datetime, end: datetime, interval_minutes=10) -> None:
    self.startdate = start
    self.enddate = end
    self.interval_minutes = interval_minutes

    period = end - start
    period_minutes = period.days * 1440 + period.seconds / 60
    num_data_points = int (period_minutes / interval_minutes)

    self.data = pd.DataFrame(
      np.array([[0, 0, 0] for _ in range(num_data_points)]),
      index=[timedelta(minutes=interval_minutes) * i for i in range(num_data_points)],
      columns=['power_kW', 'num_cons', 'num_prod'],
      dtype=float
    )

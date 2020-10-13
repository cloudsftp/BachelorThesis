import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class DemandData:
  def __init__(self, start: datetime, end: datetime, period_minutes=10) -> None:
    self.startdate = start
    self.enddate = end
    self.period_minutes = period_minutes

    interval = end - start
    interval_minutes = interval.days * 1440 + interval.seconds / 60
    num_data_points = int (interval_minutes / period_minutes)

    self.data = pd.DataFrame(
      np.array([[0, 0, 0] for _ in range(num_data_points)]),
      index=[timedelta(minutes=period_minutes) * i for i in range(num_data_points)],
      columns=['kw', 'num_cons', 'num_prod'],
      dtype=float
    )

import json

from pandas.core.indexes import interval
import numpy as np
import pandas as pd
from datetime import date, datetime, timedelta

class EV_Data(object):
  unimportant_keys = ['clusterID', 'siteID', 'spaceID', 'stationID', 'timezone', 'userID', 'userInputs']
  date_keys = ['connectionTime', 'disconnectTime', 'doneChargingTime']

  dateformat ='%a, %d %b %Y %H:%M:%S %Z'

  def __init__(self, data_file_name) -> None:
    self.read_data(data_file_name)

  def read_data(self, data_file_name) -> None:
    with open(data_file_name, 'r') as file:
      raw_data = json.load(file)

    self.items = raw_data['_items']

  def remove_unnescessary_info(self) -> None:
    for item in self.items:
      for key in self.unimportant_keys:
        item.pop(key, None)

  def parse_dates(self) -> None:
    for item in self.items:
      for key in self.date_keys:
        datestr = item[key]

        if datestr:
          date = datetime.strptime(datestr, self.dateformat)
          item[key] = date

  def specify_load(self) -> None:
    for item in self.items:
      if item['doneChargingTime'] is None:
        item['doneChargingTime'] = item['disconnectTime']
        
      chargingTime : timedelta = item['doneChargingTime'] - item['connectionTime']
      kwH : float = item['kWhDelivered']
      hours = chargingTime.total_seconds() / 3600
      kw = kwH * hours

      item['hours'] = hours
      item['kw'] = kw

  def get_load_of_timeframe(self, start: datetime, end : datetime, period_minutes = 10) -> pd.DataFrame:
    interval = end - start
    interval_minutes = interval.days * 1440 + interval.seconds / 60
    num_data_points = int (interval_minutes / period_minutes)

    df = pd.DataFrame(
      np.array([[0, 0, 0, 0] for x in range(num_data_points)]),
      index=[start + timedelta(minutes=period_minutes) * x for x in range(num_data_points)],
      columns=['timestamp', 'kw', 'num_cons', 'num_prod'],
      dtype=float
    )
    
    # above : in datatype for load data
    # todo : fill dataframe

    return df

  def get_current_data(self):
    return self.items


if __name__ == "__main__":
  data_file_name = "ACN_caltech_2020-10.json"
  ev_data = EV_Data(data_file_name)

  ev_data.remove_unnescessary_info()
  ev_data.parse_dates()
  ev_data.specify_load()

  data = ev_data.get_current_data()

  load_df = ev_data.get_load_of_timeframe(datetime(2020, 1, 1, 0, 0), datetime(2020, 1, 2, 0, 0))
  print(load_df)
import json
from typing import List
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from Experiments.Data.demand_data import DemandData

class ACN_DataItem(object):
  start: datetime
  end: datetime
  kWh: float
  period_hours: float
  kw: float

class ACN_Data(object):
  date_keys = ['connectionTime', 'disconnectTime', 'doneChargingTime']
  dateformat ='%a, %d %b %Y %H:%M:%S %Z'

  def __init__(self, data_file_name) -> None:
    self.read_data(data_file_name)
    self.items: list[ACN_DataItem] = []

  def read_data(self, data_file_name) -> None:
    with open(data_file_name, 'r') as file:
      raw_data = json.load(file)

    self.raw_items = raw_data['_items']

  def parse_dates(self) -> None:
    for item in self.raw_items:
      for key in self.date_keys:
        datestr = item[key]

        if datestr:
          date = datetime.strptime(datestr, self.dateformat)
          item[key] = date

  def convert_items(self) -> None:
    for raw_item in self.raw_items:
      item = ACN_DataItem()
      item.start = raw_item['connectionTime']

      if raw_item['doneChargingTime'] is None:
        item.end = raw_item['disconnectTime']
      else:
        item.end = raw_item['doneChargingTime']

      item.kWh = raw_item['kWhDelivered']

      self.items.append(item)

  def specify_load(self) -> None:
    for item in self.items:
      charging_period = item.end - item.start
      item.period_hours = charging_period.total_seconds() / 3600
      item.kw = item.kWh * item.period_hours

  def process_data(self) -> None:
    self.parse_dates()
    self.convert_items()
    self.specify_load()

  def get_load_of_timeframe(self, start: datetime, end: datetime, interval_minutes=10) -> pd.DataFrame:
    demand_data = DemandData(start, end, interval_minutes)
    
    # todo : fill dataframe
    df = demand_data.data

    for i in range(df.shape[0]):
      current_delta = timedelta(minutes=interval_minutes) * i
      current_moment = start + current_delta

      for item in self.items:
        if current_moment >= item.start and current_moment < item.end:
          df.loc[[current_delta], ['kw']] += item.kw
          df.loc[[current_delta], ['num_cons']] += 1

    return demand_data.data


if __name__ == "__main__":
  data_file_name = "ACN_caltech_2020-10.json"
  ev_data = ACN_Data(data_file_name)
  ev_data.process_data()

  load_df = ev_data.get_load_of_timeframe(datetime(2020, 1, 1, 0, 0), datetime(2020, 1, 9, 0, 0))
  print(load_df.max())
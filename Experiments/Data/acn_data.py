#!/bin/python3.8

import json
import pandas as pd # type: ignore
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List

from Data.demand_data import DemandData

@dataclass
class ACN_DataItem(object):
  start: datetime
  end: datetime
  work_kWh: float = 0
  period_hours: float = 0
  power_kW: float = 0

class ACN_Data(object):
  date_keys = ['connectionTime', 'disconnectTime', 'doneChargingTime']
  dateformat ='%a, %d %b %Y %H:%M:%S %Z'

  def __init__(self, data_file_name) -> None:
    self.read_data(data_file_name)
    self.items: List[ACN_DataItem] = []

  def read_data(self, data_file_name) -> None:
    with open(data_file_name, 'r') as file:
      raw_data: Dict = json.load(file)

    self.raw_items = raw_data['_items']

  def parse_dates(self) -> None:
    for item in self.raw_items:
      for key in self.date_keys:
        datestr: str = item[key]

        if datestr:
          date: datetime = datetime.strptime(datestr, self.dateformat)
          item[key] = date

  def convert_items(self) -> None:
    for raw_item in self.raw_items:
      end: datetime

      if raw_item['doneChargingTime'] is None:
        end = raw_item['disconnectTime']
      else:
        end = raw_item['doneChargingTime']

      self.items.append(ACN_DataItem(raw_item['connectionTime'], end, work_kWh=raw_item['kWhDelivered']))

  def specify_load(self) -> None:
    for item in self.items:
      charging_period: timedelta = item.end - item.start
      item.period_hours = charging_period.total_seconds() / 3600
      item.power_kW = item.work_kWh * item.period_hours

  def process_data(self) -> None:
    self.parse_dates()
    self.convert_items()
    self.specify_load()

  def get_load_of_timeframe(self, start: datetime, end: datetime, interval_minutes=10) -> pd.DataFrame:
    demand_data: DemandData = DemandData(start, end, interval_minutes)
    
    df: pd.DataFrame = demand_data.data

    for i in range(df.shape[0]):
      current_delta: timedelta = timedelta(minutes=interval_minutes) * i
      current_moment: datetime = start + current_delta

      for item in self.items:
        if current_moment >= item.start and current_moment < item.end:
          df.loc[[current_delta], ['power_kW']] += item.power_kW
          df.loc[[current_delta], ['num_cons']] += 1

    return demand_data.data


if __name__ == "__main__":
  data_file_name = "Data/ACN_caltech_2020-10.json"
  ev_data: ACN_Data = ACN_Data(data_file_name)
  ev_data.process_data()

  load_df: pd.DataFrame = ev_data.get_load_of_timeframe(datetime(2020, 1, 1, 0, 0), datetime(2020, 1, 9, 0, 0))
  print(load_df.max())
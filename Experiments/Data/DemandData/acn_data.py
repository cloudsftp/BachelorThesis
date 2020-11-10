#!/bin/python3.8

import pandas as pd # type: ignore
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Any, Dict, List

from Util.json_file_handler import read_dataclass_from
from Data.DemandData.demand_data import DemandData


@dataclass
class ACN_Root(object):
  _meta: Dict
  _items: List[Dict[str, Any]]

@dataclass
class ACN_DataItem(object):
  start: datetime
  disconnectTime: datetime
  work_kWh: float = 0
  period_hours: float = 0
  power_kW: float = 0

class ACN_DataConverter(object):
  @staticmethod
  def date(date_str: str) -> datetime:
    dateformat ='%a, %d %b %Y %H:%M:%S %Z'
    return datetime.strptime(date_str, dateformat)

  items: List[ACN_DataItem] = []

  def __init__(self, data_file_name) -> None:
    acn_root: ACN_Root = read_dataclass_from(data_file_name, ACN_Root)
    self.acn_loading_sessions: List[Dict] = acn_root._items

  def convert_items(self) -> None:
    for loading_session in self.acn_loading_sessions:
      connectionTime: datetime = ACN_DataConverter.date(loading_session['connectionTime'])

      disconnectTime: datetime
      if loading_session.get('doneChargingTime'):
        disconnectTime = ACN_DataConverter.date(loading_session['doneChargingTime'])
      else:
        disconnectTime = ACN_DataConverter.date(loading_session['disconnectTime'])

      self.items.append(ACN_DataItem(connectionTime, disconnectTime, work_kWh=loading_session['kWhDelivered']))

  def specify_load(self) -> None:
    for item in self.items:
      charging_period: timedelta = item.disconnectTime - item.start
      item.period_hours = charging_period.total_seconds() / 3600
      item.power_kW = item.work_kWh * item.period_hours

  def process_data(self) -> None:
    self.convert_items()
    self.specify_load()

  def get_load_of_timeframe(self, connectionTime: datetime, disconnectTime: datetime, interval_minutes=10) -> pd.DataFrame:
    demand_data: DemandData = DemandData(connectionTime, disconnectTime, interval_minutes)
    
    df: pd.DataFrame = demand_data.data

    for i in range(df.shape[0]):
      current_delta: timedelta = timedelta(minutes=interval_minutes) * i
      current_moment: datetime = connectionTime + current_delta

      for item in self.items:
        if current_moment >= item.start and current_moment < item.disconnectTime:
          df.loc[[current_delta], ['power_kW']] += item.power_kW
          df.loc[[current_delta], ['num_cons']] += 1

    return demand_data.data


if __name__ == "__main__":
  data_file_name = "Data/DemandData/ACN_caltech_2020-10.json"
  ev_data: ACN_DataConverter = ACN_DataConverter(data_file_name)
  ev_data.process_data()

  load_df: pd.DataFrame = ev_data.get_load_of_timeframe(datetime(2020, 1, 1, 0, 0), datetime(2020, 1, 9, 0, 0))
  print(load_df.max())
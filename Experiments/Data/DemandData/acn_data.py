#!/bin/python3.8

import pandas as pd # type: ignore
from datetime import date, datetime, timedelta
from dataclasses import dataclass
from typing import Any, Dict, List

from Util.json_file_handler import read_dataclass_from
from Data.DemandData.demand_data import DemandData


@dataclass
class ACN_Root(object):
  '''
  represents ACN data object
  '''
  _meta: Dict
  _items: List[Dict[str, Any]]

@dataclass
class ACN_DataItem(object):
  '''
  represents one data item of the ACN data
  '''
  start: datetime
  disconnectTime: datetime
  work_kWh: float = 0
  period_hours: float = 0
  power_kW: float = 0

class ACN_DataConverter(object):
  '''
  handles the conversion of the ACN data to a DemandData object
  '''
  items: List[ACN_DataItem] = []

  @staticmethod
  def date(date_str: str) -> datetime:
    '''
    parses a date

    :date_str: string representation of a date
    '''
    dateformat ='%a, %d %b %Y %H:%M:%S %Z'
    return datetime.strptime(date_str, dateformat)

  def __init__(self, data_file_name) -> None:
    '''
    initializes the converter

    :data_file_name: file to read data from
    '''
    acn_root: ACN_Root = read_dataclass_from(data_file_name, ACN_Root)
    self.acn_loading_sessions: List[Dict] = acn_root._items

  def convert_items(self) -> None:
    '''
    converts raw ACN data to ACN_DataItems
    '''
    for loading_session in self.acn_loading_sessions:
      connectionTime: datetime = ACN_DataConverter.date(loading_session['connectionTime'])

      disconnectTime: datetime
      if loading_session.get('doneChargingTime'):
        disconnectTime = ACN_DataConverter.date(loading_session['doneChargingTime'])
      else:
        disconnectTime = ACN_DataConverter.date(loading_session['disconnectTime'])

      self.items.append(ACN_DataItem(connectionTime, disconnectTime, work_kWh=loading_session['kWhDelivered']))

  def specify_load(self) -> None:
    '''
    computes the power demand of every data item based on the charging time and total energy
    '''
    for item in self.items:
      charging_period: timedelta = item.disconnectTime - item.start
      item.period_hours = charging_period.total_seconds() / 3600
      item.power_kW = item.work_kWh * item.period_hours

  def process_data(self) -> None:
    self.convert_items()
    self.specify_load()

  def get_load_of_timeframe(self, start: datetime, end: datetime, interval_minutes: int=10) -> pd.DataFrame:
    '''
    compute the power demand of a specific time period

    :start: start date
    :end: end date
    :interval_minutes: time resolution of the data, default: 10 (minutes)
    '''
    demand_data: DemandData = DemandData(period=end - start, interval_minutes=interval_minutes)

    df: pd.DataFrame = demand_data.data

    for i in range(df.shape[0]):
      current_delta: int = interval_minutes * i
      current_moment: datetime = start + timedelta(minutes=current_delta)

      for item in self.items:
        if current_moment >= item.start and current_moment < item.disconnectTime:
          df.loc[i, 'power_kW'] += item.power_kW

    return df

  def get_load_of_one_day(self, start: datetime) -> pd.DataFrame:
    '''
    compute the power demand of one day
    '''
    one_day: timedelta = timedelta(1)
    return self.get_load_of_timeframe(start, start + one_day)

def get_average_day() -> DemandData:
  '''
  compute the average day of power demand
  '''
  data_file_name = "Data/DemandData/ACN_caltech_2020-10.json"
  ev_data: ACN_DataConverter = ACN_DataConverter(data_file_name)
  ev_data.process_data()

  dates: Dict[int, int] = { # The key is the month, the entry is the last day of the month
    1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 30, 9: 30
  }

  load_df: pd.DataFrame = ev_data.get_load_of_one_day(datetime(2020, 1, 1, 0, 0)) # this day has no power demand
  num_of_days = 0
  load_df_day: pd.DataFrame

  for month in dates:
    for day in range(1, dates[month]):
      load_df_day = ev_data.get_load_of_one_day(datetime(2020, month, day, 0, 0))
      load_df = load_df.add(load_df_day, fill_value=0)
      num_of_days += 1

  load_df /= num_of_days
  return DemandData(data=load_df)

if __name__ == "__main__":
  average_demand: DemandData = get_average_day()
  print(average_demand.data)
  average_demand.to_csv('acn_data.csv')

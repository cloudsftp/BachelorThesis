#!/bin/python
# version 3.8 required

import os
from typing import List
import numpy as np # type: ignore
import pandas as pd # type: ignore
from Data.DemandData.demand_data import DemandData


path_to_data: str = 'Data/DemandData/OfficeData/'
num_data_items: int = 24 * 6

def read_file(file_name: str) -> DemandData:
  '''
  reads data from a file

  :file_name: file to read from
  '''
  device_day_load_df: pd.DataFrame = pd.read_csv(file_name)
  device_day_load_df = device_day_load_df.drop(columns=['timestamp', 'deviceMac'])

  # convert to kW
  device_day_load_df = device_day_load_df.rename(columns={'watt': 'power_kW'})
  device_day_load_df /= 1000

  # convert to 10 minute time resolution
  ten_seconds_in_ten_minutes: int = 60
  device_day_load_df = device_day_load_df.groupby(device_day_load_df.index // ten_seconds_in_ten_minutes).sum() / ten_seconds_in_ten_minutes

  return device_day_load_df


def read_device(device: str) -> pd.DataFrame:
  '''
  reads data of one device

  :device: name of device
  '''
  print('Reading {}...'.format(device))

  path_to_device: str = os.path.join(path_to_data, device)
  file_names: List[str] = os.listdir(path_to_device)

  device_load_df: pd.DataFrame = pd.DataFrame(data=np.zeros([num_data_items, 1]), columns=['power_kW'])
  num_days: int = 0

  for file_name in file_names:
    device_day_load_df: pd.DataFrame = read_file(os.path.join(path_to_device, file_name))
    device_load_df = device_load_df.add(device_day_load_df, fill_value=0)
    num_days += 1

  device_load_df /= num_days

  return device_load_df

def read_all() -> pd.DataFrame:
  '''
  reads data of all devices
  '''
  devices: List[str] = os.listdir(path_to_data)

  load_df: pd.DataFrame = pd.DataFrame(data=np.zeros([num_data_items, 1]), columns=['power_kW'])

  for device in devices:
    device_load_df: pd.DataFrame = read_device(device)
    load_df = load_df.add(device_load_df, fill_value=0)

  return DemandData(data=load_df)

if __name__ == "__main__":
  demand: DemandData = read_all()
  demand.to_csv('office_data.csv')

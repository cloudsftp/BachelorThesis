#!/bin/python3.8


import pandas as pd

from Data.DemandData.demand_data import DemandData # type: ignore


def read_file(name: str) -> DemandData:
  df: pd.DataFrame = pd.read_csv(name)
  df = df.drop(columns=['timestamp', 'deviceMac'])
  df = df.rename(columns={'watt': 'power_kW'})
  df /= 1000

  ten_seconds_in_ten_minutes: int = 60
  df = df.groupby(df.index // ten_seconds_in_ten_minutes).sum()

  return df


def read_all():
  df: pd.DataFrame = read_file('Data/DemandData/OfficeData/CoffeeMaker/2016-02-03.csv')
  print(df)

if __name__ == "__main__":
  read_all()
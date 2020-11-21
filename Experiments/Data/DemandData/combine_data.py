#!/bin/python3.8

from Data.DemandData.demand_data import DemandData


if __name__ == "__main__":
  acn_data: DemandData = DemandData.read_from_csv('acn_data.csv')
  print(acn_data.data)
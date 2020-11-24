#!/bin/python3.8


import dataclasses
from typing import List
from Data.DemandData.demand_data import DemandData
from Data.Plants.plants import Plants
from UCP.unit_commitment_problem import UCP


demand_file_file: str = 'combined_data.csv'
plants_file_name: str = 'thermal_power_coefficients.json'


if __name__ == "__main__":
  demand_data: DemandData = DemandData.read_from_csv(demand_file_file)
  loads: List[float] = demand_data.data['power_kW'].to_list()

  plants_data: Plants = Plants.read_from_json(plants_file_name)
  plants = plants_data.plants

  ucp: UCP = UCP(loads, plants)
  print(ucp)
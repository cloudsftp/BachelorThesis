#!/bin/python3.8


from dataclasses import dataclass
import random
from typing import List
from Data.DemandData.demand_data import DemandData
from Data.Plants.plants import Plants
from UCP.unit_commitment_problem import CombustionPlant, UCP, ExperimentParameters


demand_file_file: str = 'combined_data.csv'
plants_file_name: str = 'thermal_power_coefficients.json'

def select_loads(loads: List[float], num_loads: int, offset_loads: int) -> List[float]:
  # make sure indices of selected loads are inside list
  num_loads = min(num_loads, len(loads) - offset_loads)
  return loads[offset_loads : offset_loads + num_loads]

def scale_loads(loads: List[float], available_plants: List[CombustionPlant], num_plants: int) -> List[float]:
  '''
  this function scales the loads such that the maximum load is at 100% of the maximum output
  of num_plants of the plant with the lowest maximum output
  '''
  load_max = max(loads)
  Pmax_min = min(plant.Pmax for plant in available_plants)

  # this factor determines, how the loads have to scale with the number of plants
  # it depends on the data
  load_factor: float = Pmax_min / load_max
  return list(map(lambda x: x * load_factor * num_plants, loads))

def select_plants(available_plants: List[CombustionPlant], num_plants: int) -> List[CombustionPlant]:
  # initialize pseudo random number generator to get reproducable results
  random.seed(1)
  def random_plant() -> CombustionPlant:
    rand: int = int(random.random() * len(available_plants))
    return available_plants[rand]

  plants: List[CombustionPlant] = []
  for _ in range(num_plants):
    plants.append(random_plant())

  return plants


def build_ucp(parameters: ExperimentParameters) -> UCP:
  demand_data: DemandData = DemandData.read_from_csv(demand_file_file)
  loads: List[float] = demand_data.data['power_kW'].to_list()

  plants_data: Plants = Plants.read_from_json(plants_file_name)
  available_plants: List[CombustionPlant] = plants_data.plants

  loads = select_loads(loads, parameters.num_loads, parameters.offset_loads)
  loads = scale_loads(loads, available_plants, parameters.num_plants)

  plants: List[CombustionPlant] = select_plants(available_plants, parameters.num_plants)

  return UCP(parameters, loads, plants)

#!/bin/python3.8


import random
from typing import List

from numpy.lib.function_base import copy
from Data.DemandData.demand_data import DemandData
from Data.Plants.plants import Plants
from UCP.unit_commitment_problem import CombustionPlant, UCP, ExperimentParameters


demand_file_file: str = 'combined_data.csv'
plants_file_name: str = 'thermal_power_plant_data.json'

def select_loads(loads: List[float], num_loads: int, offset_loads: int) -> List[float]:
  # make sure indices of selected loads are inside list
  result: List[float] = []

  result += loads[offset_loads:]
  if len(result) > num_loads:
    result = result[:num_loads]
  elif len(result) < num_loads:
    loads_factor: int = (int) ((num_loads - len(result)) / len(loads))
    result += loads_factor * loads

    remainder: int = num_loads - len(result)
    result += loads[:remainder]

  return result

def select_plants(available_plants: List[CombustionPlant], num_plants: int) -> List[CombustionPlant]:
  # initialize pseudo random number generator to get reproducable results
  random.seed(1)
  def random_plant() -> CombustionPlant:
    rand: int = int(random.random() * len(available_plants))
    return available_plants[rand]

  plants: List[CombustionPlant] = available_plants * int(num_plants / len(available_plants))
  for _ in range(num_plants - len(plants)):
    plants.append(random_plant())

  return plants

def scale_loads(loads: List[float], plants: List[CombustionPlant], num_plants: int) -> List[float]:
  '''
  this function scales the loads such that the maximum load is at 100% of the maximum output
  of num_plants of the plant with the lowest maximum output
  '''
  load_max = max(loads)
  Pmax_avg = sum(plant.Pmax for plant in plants) / len(plants)

  # this factor determines, how the loads have to scale with the number of plants
  # it depends on the data
  load_factor: float = Pmax_avg / load_max
  return list(map(lambda x: x * load_factor * num_plants * 0.5, loads))


def build_ucp(parameters: ExperimentParameters) -> UCP:
  demand_data: DemandData = DemandData.read_from_csv(demand_file_file)
  loads: List[float] = demand_data.data['power_kW'].to_list()

  plants_data: Plants = Plants.read_from_json(plants_file_name)
  available_plants: List[CombustionPlant] = plants_data.plants

  loads = select_loads(loads, parameters.num_loads, parameters.offset_loads)
  plants: List[CombustionPlant] = select_plants(available_plants, parameters.num_plants)
  loads = scale_loads(loads, plants, parameters.num_plants)

  return UCP(parameters, loads, plants)

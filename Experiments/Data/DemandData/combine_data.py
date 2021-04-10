#!/bin/python
# version 3.8 required

import matplotlib.pyplot as plt # type: ignore
import pandas as pd # type: ignore
from Data.DemandData.demand_data import DemandData


if __name__ == "__main__":
  '''
  loads the demand data from ACN and the office and combines them 1 : 1000
  '''
  acn_demand: DemandData = DemandData.read_from_csv('acn_data.csv')
  office_demand: DemandData = DemandData.read_from_csv('office_data.csv')

  acn_data: pd.DataFrame = acn_demand.data
  office_data: pd.DataFrame = office_demand.data

  combined_data: pd.DataFrame = acn_data.add(office_data * 1000)

  combined_data.plot()
  plt.show()

  combined_demand: DemandData = DemandData(data=combined_data)
  combined_demand.to_csv('combined_data.csv')

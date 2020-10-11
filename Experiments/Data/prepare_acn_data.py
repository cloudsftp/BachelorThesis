import json

data_file_name = "ACN_caltech_2020-10.json"

def read_data(file_name):
  with open(file_name, 'r') as file:
    data = json.load(file)

  return data


def get_items(data):
  return data['_items']


if __name__ == "__main__":
  data = read_data(data_file_name)
  data = get_items(data)
# json_loader.py

import json

# Load and parse the JSON data
def load_json(file_path):
    with open(file_path, "r") as json_file:
        data = json.load(json_file)
    return data
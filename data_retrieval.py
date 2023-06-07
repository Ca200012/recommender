import json
import glob

def read_json_file(filename):
    with open(filename, 'r', encoding='utf8') as f:
        data = json.load(f)
    return data

def get_data():
    # Use a glob pattern to get all json files
    files = glob.glob('resources/original/styles/*.json')

    # Initialize an empty list to store the dictionaries
    data = []

    # Loop through the first 10000 files and append their data to the list
    for file in files[:20000]:
        data.append(read_json_file(file))

    return data
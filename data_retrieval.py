import json
import glob

def read_json_file(filename):
    with open(filename, 'r', encoding='utf8') as f:
        data = json.load(f)
    return data

def get_data():
    files = glob.glob('resources/original/styles/*.json')

    data = []

    for file in files:
        data.append(read_json_file(file))

    return data
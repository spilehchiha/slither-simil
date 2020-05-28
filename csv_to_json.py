import csv
import json
import ast

csv_input_file_path = "../../../issues-dataset/issues_dataset - Sheet1.csv"

def csv_to_json(file_path): 
    with open (file_path, 'r') as input_file:
        csv_data = list()
        for row in csv.DictReader(input_file):
            csv_data.append(row)
    input_file.close()
    return ast.literal_eval(json.dumps(csv_data))


if __name__ == "__main__": 
    json_object = csv_to_json(csv_input_file_path)
    with open('./vul_dataset.json', 'w') as f:
        json.dump(json_object, f)
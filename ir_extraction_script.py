import csv
import json
import ast
import subprocess
import re

csv_input_file_path = "./issues_dataset - Sheet1.csv"

search_term = input("Enter a function name with the pattern below: \n Functoin [file_name.function_name]:\n")

def csv_to_json(file_path): 
    with open (file_path, 'r') as input_file:
        csv_data = list()
        for row in csv.DictReader(input_file):
            csv_data.append(row)
    input_file.close()
    return ast.literal_eval(json.dumps(csv_data))

def json_search_and_extraction(file_path, name):
    json_object = csv_to_json(file_path)
    json_element = [obj for obj in json_object if obj['func']==name][0]
    return "../smart-contract-clients/contracts_audited/" + json_element['project_id'] + '/' + json_element['func_origin_contract']

def run_slither(slithir_output_path):
    slithir_output = open(slithir_output_path, 'w')
    subprocess.call(["slither", "--json", "-", "--print", "slithir", json_search_and_extraction(csv_input_file_path, search_term)], stdout=slithir_output)
    slithir_output.close()

def load_slithir_data(slithir_output_path):
    run_slither(slithir_output_path)
    with open(slithir_output_path, 'r') as slithir_output:
        json_data = json.load(slithir_output)
    return json_data['results']['printers'][0]['description']

def slithir_search_and_extraction(slithir_output_path):
    regex_pattern = "\\n\\t" + re.escape(search_term) + "\\n\\t\\t(.*?)\\n\\tFunction"
    string = load_slithir_data(slithir_output_path)
    return re.search(regex_pattern, string, flags=re.DOTALL).group(1)

if __name__ == "__main__":
    output = slithir_search_and_extraction('./slithir.json')
    print (output)
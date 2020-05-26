import csv
import json
import ast
#import subprocess
import re
from slither import Slither
from slither.printers.all_printers import PrinterSlithIR
        
csv_input_file_path = "../../../issues-dataset/issues_dataset - Sheet1.csv"

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
    return "../" + json_element['project_id'] + '/' + json_element['func_origin_contract']

def run_slither(slithir_output_path):
    slithir_output = open(slithir_output_path, 'w')    
    # Init slither
    slither = Slither(json_search_and_extraction(csv_input_file_path, search_term))
    slither.register_printer(PrinterSlithIR)
    slithir_output.write(json.dumps(slither.run_printers()))
    slithir_output.close()

def load_slithir_data(slithir_output_path):
    run_slither(slithir_output_path)
    with open(slithir_output_path, 'r') as slithir_output:
        json_data = json.load(slithir_output)
    return json_data[0]['description']

def slithir_search_and_extraction(slithir_output_path):
    regex_pattern = "\\n\\t" + re.escape(search_term) + "(.*?)\\n\\tFunction" 
    return re.search(regex_pattern, load_slithir_data(slithir_output_path), flags=re.DOTALL).group(1)

if __name__ == "__main__":
    output = slithir_search_and_extraction('./slithir.json')
    print (output)
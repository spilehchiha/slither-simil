import csv
from slither import Slither
        
csv_input_file_path = "../../../issues-dataset/issues_dataset - Sheet1.csv"

search_term = input("Enter a function name with the pattern below: \n Functoin [file_name.function_name]:\n")

def csv_to_json(file_path): 
    with open (file_path, 'r') as input_file:
        csv_data = list()
        for row in csv.DictReader(input_file):
            csv_data.append(row)
    input_file.close()
    return csv_data

def json_search_and_extraction(file_path, name):
    csv_object = csv_to_json(file_path)
    for row in csv_object:
        if search_term == row['func']:
            return row['func_origin_contract']

def run_slither(slithir_output_path): 
    # Init slither
    slither = Slither(json_search_and_extraction(csv_input_file_path, search_term))
    
    # Extracts the function name without the 'Function' keyword from the user input
    function_name = search_term.split(r" ")[1]

    for function in slither.functions:
        if function.canonical_name == function_name:
            for node in function.nodes:
                if node.expression:
                    print('\t\tExpression: {}'.format(node.expression))
                    print('\t\tIRs:')
                    for ir in node.irs:
                        print('\t\t\t{}'.format(ir))

if __name__ == "__main__":
    run_slither('./slithir.json')
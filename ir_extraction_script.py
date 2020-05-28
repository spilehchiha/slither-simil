import json
from slither import Slither

input_dataset = './vul_dataset.json'
search_term = input("Enter a function name with the pattern below: \n Functoin [contract_name.function_name]:\n")

def json_search_and_extraction(file_path, name):
    with open(file_path, 'r') as f:
        json_object = json.load(f)
    for row in json_object:
        if search_term == row['func']:
            return row['func_origin_contract']

def run_slither(slithir_output_path): 
    # Init slither
    slither = Slither(json_search_and_extraction(input_dataset, search_term))
    
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
import json
from slither import Slither

input_dataset = './vul_dataset.json'

def json_search_and_extraction(file_path):
    array = list()
    with open(file_path, 'r') as f:
        json_object = json.load(f)
    for row in json_object:
        array.append(row['func_origin_contract'])
    return array

def run_slither(slithir_output_path): 
    data = json_search_and_extraction(input_dataset)
    # Init slither
    for contract_file_name in data:
        slither = Slither(contract_file_name)
        for function in slither.functions:
                for node in function.nodes:
                    if node.expression:
                        print('\t\tExpression: {}'.format(node.expression))
                        print('\t\tIRs:')
                        for ir in node.irs:
                            print('\t\t\t{}'.format(ir))

if __name__ == "__main__": 
    run_slither('./slithir.json')
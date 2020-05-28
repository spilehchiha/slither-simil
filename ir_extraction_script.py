import json
from slither import Slither

input_dataset = './vul_dataset.json'

def load_json(file_path):
    with open(file_path, 'r') as f:
        json_object = json.load(f)
    return json_object

def run_slither(slithir_output_path): 
    data = load_json(input_dataset)
    
    for element in data:
        # Init slither
        slither = Slither(element['func_origin_contract'])
        for contract in slither.contracts:
                for function in contract.functions:
                    if function.canonical_name == element['func']:
                        if function.contract_declarer == contract:
                            print('Contract: {}\t\tVulnerability: {}'.format(element['func'].split('.')[0], element['vulnerability_type']))
                            print('''Function: {}\t\t\t\tSeverity: {}\n'''.format(function.name, element['severity']))
                            for node in function.nodes:
                                if node.expression:
                                    print('\t\tExpression: {}'.format(node.expression))
                                    print('\t\tIRs:')
                                    for ir in node.irs:
                                        print('\t\t\t{}'.format(ir))
                            print('\n\n')

if __name__ == "__main__": 
    run_slither('./slithir.json')
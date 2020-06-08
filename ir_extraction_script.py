import json
from slither import Slither
import os

input_dataset = 'golem/vul_dataset.json'

def load_json(file_path):
    with open(file_path, 'r') as f:
        json_object = json.load(f)
    return json_object

def encode_function(): 
    data = load_json(input_dataset)
    
    for datum in data:

        for cfilename in eval(datum['func_origin_contract_file_name']):
            #cfilename = datum['func_origin_contract_file_name']
            funcname = eval(datum['func'])[eval(datum['func_origin_contract_file_name']).index(cfilename)]
            # Init slither
            os.chdir(os.getcwd() + os.sep + datum['project_id'])
            try:
                slither = Slither(cfilename)
                os.chdir('..')
            except:
                #simil_logger.error("Compilation failed for %s using %s", cfilename, kwargs['solc'])
                print("Slither Compilation Unsuccessful!" + "\t" + datum['finding_id'] + '\t' + datum['func_origin_contract_file_name'])
                os.chdir('..')

            # Iterate over all the contracts
            for contract in slither.contracts:

                # Iterate over all the functions
                for function in contract.functions_declared:

                    if function.canonical_name == funcname:

                        if function.contract_declarer == contract:
                            print('Contract: {}\t\t\t\tVulnerability: {}'.format(funcname.split('.')[0], datum['vulnerability_type']))
                            print('''Function: {}\t\t\t\tSeverity: {}\n'''.format(function.name, datum['severity']))
  

                            if function.nodes == [] or function.is_constructor_variables:
                                continue

                            # Iterate over the nodes of the function
                            for node in function.nodes:
                                # Print the Solidity expression of the nodes
                                # And the SlithIR operations
                                if node.expression:
                                    print('\t\tExpression: {}'.format(node.expression))
                                    print('\t\tIRs:')
                                    for ir in node.irs:
                                        print('\t\t\t{}'.format(ir))
                                        #print(ir);print("\n\n");#r[x].append(encode_ir(ir))

if __name__ == "__main__": 
    encode_function()
import logging
import os
import subprocess
import pickle

import csv
import json
import ast

from slither import Slither

extract_logger = logging.getLogger("Slither-extract")
compiler_logger = logging.getLogger("CryticCompile")
compiler_logger.setLevel(logging.CRITICAL)
slither_logger = logging.getLogger("Slither")
slither_logger.setLevel(logging.CRITICAL)

def csv_to_json(csvfilepath):
    with open (csvfilepath, 'r') as csvfile:
        csvdata = []
        for row in csv.DictReader(csvfile):
            csvdata.append(row)
    csvfile.close()
    return ast.literal_eval(json.dumps(csvdata))

def encode_function(input_csv, client_list, **kwargs): 
    r = dict()
    jsondata = csv_to_json(input_csv)
    if 'all' in client_list: client_list = ['golem', 'nomisma', 'paxos', 'ampleforth', 'origin-protocol']
    else:
        jsondata = [datum for datum in jsondata if datum['project_id'] in client_list]
    
    prev_proj_id = ''
    for datum in jsondata:
        for cfilename in eval(datum['func_origin_contract_file_name']):
            funcname = eval(datum['func'])[eval(datum['func_origin_contract_file_name']).index(cfilename)]
            if (datum['project_id'] != prev_proj_id): print('processing %s contracts' % datum['project_id'])
            prev_proj_id = datum['project_id']
            # Init slither
            if datum['project_id'] == 'golem':
                subprocess.run(["solc", "use", "0.4.23"], stdout=subprocess.DEVNULL)
                os.chdir(os.getcwd() + os.sep + datum['project_id'])
                try:
                    slither = Slither(cfilename)
                    os.chdir('..')
                except:
                    extract_logger.error("Compilation failed for %s", cfilename)
                    os.chdir('..')
                    continue
            
            elif datum['project_id'] == 'nomisma':
                subprocess.run(["solc", "use", "0.4.24"], stdout=subprocess.DEVNULL)
                os.chdir(os.getcwd() + os.sep + datum['project_id'] + os.sep + 'BankProtcol')
                try:
                    slither = Slither('.')
                    os.chdir('../..')
                except:
                    extract_logger.error("Compilation failed for %s", cfilename)
                    os.chdir('../..')
                    continue

            elif datum['project_id'] == 'paxos':
                subprocess.run(["solc", "use", "0.4.24"], stdout=subprocess.DEVNULL)
                os.chdir(os.getcwd() + os.sep + datum['project_id'])
                try:
                    slither = Slither(cfilename)
                    os.chdir('..')
                except:
                    extract_logger.error("Compilation failed for %s", cfilename)
                    os.chdir('..')
                    continue
            
            elif datum['project_id'] == 'ampleforth':
                subprocess.run(["solc", "use", "0.4.24"], stdout=subprocess.DEVNULL)
                os.chdir(os.getcwd() + os.sep + datum['project_id'] + os.sep +'market-oracle')
                try:
                    slither = Slither('.')
                    os.chdir('../..')
                except:
                    extract_logger.error("Compilation failed for %s", cfilename)
                    os.chdir('../..')
                    continue

            elif datum['project_id'] == 'origin-protocol':
                subprocess.run(["solc", "use", "0.4.24"], stdout=subprocess.DEVNULL)
                os.chdir(os.getcwd() + os.sep + datum['project_id'] + os.sep + 'origin-contracts')
                try:
                    slither = Slither('contracts/marketplace/v00/Marketplace.sol')
                    os.chdir('../..')
                except:
                    extract_logger.error("Compilation failed for %s", cfilename)
                    os.chdir('../..')
                    continue
            
            else:
                continue  

            """
            elif datum['project_id'] == 'livepeer':
                subprocess.run(["solc", "use", "0.4.24"], stdout=subprocess.DEVNULL)
                os.chdir(os.getcwd() + os.sep + datum['project_id'] + os.sep + 'contracts')
                try:
                    slither = Slither('bonding/')
                    os.chdir('../..')
                except:
                    extract_logger.error("Compilation failed for %s", cfilename)
                    os.chdir('../..')
                    continue
            """

            # Iterate over all the contracts
            for contract in slither.contracts:

                # Iterate over all the functions
                for function in contract.functions_declared:

                    if function.canonical_name == funcname:

                        if function.contract_declarer == contract:

                            if function.nodes == [] or function.is_constructor_variables:
                                continue

                            x = (datum['project_id'],cfilename,contract.name,function.name)
                            r[x] = []

                            # Iterate over the nodes of the function
                            for node in function.nodes:
                                if node.expression:
                                    for ir in node.irs:
                                        r[x].append(ir)

    with open('slithIR', 'wb') as f:
        pickle.dump(r, f)

if __name__ == "__main__": 
    input_csv = str(input('Enter the issues_dataset.csv path first:\n'))
    try: 
        client_list = [] 
        print('Enter a list of client project_ids separated by carrier return; Type all to process all existing contracts. when finished, press Ctrl-C:\n')
        while True: 
            client_list.append(str(input()))
    except: 
        print('\n')
        encode_function(input_csv, client_list)
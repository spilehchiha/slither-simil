import logging
import os
import subprocess

import csv
import json
import ast

from slither import Slither
from slither.core.declarations import Structure, Enum, SolidityVariableComposed, SolidityVariable, Function
from slither.core.solidity_types import ElementaryType, ArrayType, MappingType, UserDefinedType
from slither.core.variables.local_variable import LocalVariable
from slither.core.variables.local_variable_init_from_tuple import LocalVariableInitFromTuple
from slither.core.variables.state_variable import StateVariable
from slither.slithir.operations import Assignment, Index, Member, Length, Balance, Binary, \
    Unary, Condition, NewArray, NewStructure, NewContract, NewElementaryType, \
    SolidityCall, Push, Delete, EventCall, LibraryCall, InternalDynamicCall, \
    HighLevelCall, LowLevelCall, TypeConversion, Return, Transfer, Send, Unpack, InitArray, InternalCall
from slither.slithir.variables import TemporaryVariable, TupleVariable, Constant, ReferenceVariable

extract_logger = logging.getLogger("Slither-extract")
compiler_logger = logging.getLogger("CryticCompile")
compiler_logger.setLevel(logging.CRITICAL)
slither_logger = logging.getLogger("Slither")
slither_logger.setLevel(logging.CRITICAL)


def ntype(_type):
    if isinstance(_type, ElementaryType):
        _type = str(_type)
    elif isinstance(_type, ArrayType):
        if isinstance(_type.type, ElementaryType):
            _type = str(_type)
        else:
            _type = "user_defined_array"
    elif isinstance(_type, Structure):
        _type = str(_type)
    elif isinstance(_type, Enum):
        _type = str(_type)
    elif isinstance(_type, MappingType):
        _type = str(_type)
    elif isinstance(_type, UserDefinedType):
        _type = "user_defined_type"  # TODO: this could be Contract, Enum or Struct
    else:
        _type = str(_type)

    _type = _type.replace(" memory","")
    _type = _type.replace(" storage ref","")

    if "struct" in _type:
        return "struct"
    elif "enum" in _type:
        return "enum"
    elif "tuple" in _type:
        return "tuple"
    elif "contract" in _type:
        return "contract"
    elif "mapping" in _type:
        return "mapping"
    else:
        return _type.replace(" ","_")

def encode_ir(ir):
    # operations
    if isinstance(ir, Assignment):
        return '({}):=({})'.format(encode_ir(ir.lvalue), encode_ir(ir.rvalue))
    if isinstance(ir, Index):
        return 'index({})'.format(ntype(ir._type)) 
    if isinstance(ir, Member):
        return 'member' #.format(ntype(ir._type))
    if isinstance(ir, Length):
        return 'length'
    if isinstance(ir, Balance):
        return 'balance'
    if isinstance(ir, Binary):
        return 'binary({})'.format(ir.type_str)
    if isinstance(ir, Unary):
        return 'unary({})'.format(ir.type_str) 
    if isinstance(ir, Condition):
        return 'condition({})'.format(encode_ir(ir.value))
    if isinstance(ir, NewStructure):
        return 'new_structure'
    if isinstance(ir, NewContract):
        return 'new_contract'
    if isinstance(ir, NewArray):
        return 'new_array({})'.format(ntype(ir._array_type)) 
    if isinstance(ir, NewElementaryType):
        return 'new_elementary({})'.format(ntype(ir._type)) 
    if isinstance(ir, Push):
        return 'push({},{})'.format(encode_ir(ir.value), encode_ir(ir.lvalue))
    if isinstance(ir, Delete):
        return 'delete({},{})'.format(encode_ir(ir.lvalue), encode_ir(ir.variable))
    if isinstance(ir, SolidityCall):
        return 'solidity_call({})'.format(ir.function.full_name)
    if isinstance(ir, InternalCall):
        return 'internal_call({})'.format(ntype(ir._type_call)) 
    if isinstance(ir, EventCall): # is this useful?
        return 'event'
    if isinstance(ir, LibraryCall):
        return 'library_call'
    if isinstance(ir, InternalDynamicCall):
        return 'internal_dynamic_call'
    if isinstance(ir, HighLevelCall): # TODO: improve
        return 'high_level_call'
    if isinstance(ir, LowLevelCall): # TODO: improve
        return 'low_level_call'
    if isinstance(ir, TypeConversion):
        return 'type_conversion({})'.format(ntype(ir.type))
    if isinstance(ir, Return): # this can be improved using values
        return 'return' #.format(ntype(ir.type))
    if isinstance(ir, Transfer):
        return 'transfer({})'.format(encode_ir(ir.call_value))
    if isinstance(ir, Send):
        return 'send({})'.format(encode_ir(ir.call_value))
    if isinstance(ir, Unpack): # TODO: improve
        return 'unpack'
    if isinstance(ir, InitArray): # TODO: improve
        return 'init_array'
    if isinstance(ir, Function): # TODO: investigate this
        return 'function_solc'

    # variables
    if isinstance(ir, Constant):
        return 'constant({})'.format(ntype(ir._type))
    if isinstance(ir, SolidityVariableComposed):
        return 'solidity_variable_composed({})'.format(ir.name)
    if isinstance(ir, SolidityVariable):
        return 'solidity_variable{}'.format(ir.name)
    if isinstance(ir, TemporaryVariable):
        return 'temporary_variable'
    if isinstance(ir, ReferenceVariable):
        return 'reference({})'.format(ntype(ir._type)) 
    if isinstance(ir, LocalVariable):
        return 'local_solc_variable({})'.format(ir._location) 
    if isinstance(ir, StateVariable):
        return 'state_solc_variable({})'.format(ntype(ir._type))
    if isinstance(ir, LocalVariableInitFromTuple):
        return 'local_variable_init_tuple'
    if isinstance(ir, TupleVariable):
        return 'tuple_variable'

    # default
    else:
        extract_logger.error(type(ir),"is missing encoding!")
        return ''

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
                                        r[x].append(encode_ir(ir))
                                        
    w = csv.writer(open("output.csv", "w+"))
    for key, val in r.items():
        w.writerow([key, val])
    return r

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
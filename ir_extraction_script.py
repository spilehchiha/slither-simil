import logging
import csv
import json
import ast
import subprocess
import os

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
from crytic_compile import compile_all

extract_logger = logging.getLogger("Slither-extract")
compiler_logger = logging.getLogger("CryticCompile")
slither_logger = logging.getLogger("Slither")

compiler_logger.setLevel(logging.CRITICAL)
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
        if str(ir.function) == 'transfer':
            return 'high_level_call_transfer'
        else:
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
        return 'temporary_variable({})'.format(ntype(ir._type))
    if isinstance(ir, ReferenceVariable):
        return 'reference({})'.format(ntype(ir._type)) 
    if isinstance(ir, LocalVariable):
        return 'local_solc_variable({}, {})'.format(ir._location, ir._type) 
    if isinstance(ir, StateVariable):
        return 'state_solc_variable({})'.format(ntype(ir._type))
    if isinstance(ir, LocalVariableInitFromTuple):
        return 'local_variable_init_tuple({})'.format(ntype(ir._type))
    if isinstance(ir, TupleVariable):
        return 'tuple_variable{})'.format(ntype(ir._type))
    # default
    else:
        extract_logger.error(type(ir),"is missing encoding!")
        return ''

def csv_to_json(csv_file_path):
    with open (csv_file_path, 'r') as csv_file:
        csv_data = list()
        for row in csv.DictReader(csv_file):
            csv_data.append(row)
    csv_file.close()
    return ast.literal_eval(json.dumps(csv_data))

def encode_function(input_csv, client_list, **kwargs):
    function_dict = dict()
    input_json = csv_to_json(input_csv)
    if 'all' in client_list: # Checks whether the user has typed 'all' as input or not.
        client_list = ['golem', 
                        'nomisma', 
                        'paxos', 
                        'ampleforth', 
                        'origin-protocol',
                        'uma',
                        'vbm',
                        'celo',
                        'ocean-protocol']
    else:
        input_json = [datum for datum in input_json if datum['project_id'] in client_list]
    
    previous_project_id = ''
    flag = False
    for datum in input_json:
        
        for cfilename in eval(datum['func_origin_contract_file_name']):            
            funcname = eval(datum['func'])[eval(datum['func_origin_contract_file_name']).index(cfilename)]
            
            if (datum['project_id'] != previous_project_id):
                flag = True
                print('processing %s contracts' % datum['project_id'])           
            
            # Init slither
            if datum['project_id'] == 'golem':
                if flag == True:
                    compilation = compile_all(os.getcwd() + '/golem/g.zip')
                else:
                    pass
            
            elif datum['project_id'] == 'paxos':
                if flag == True:
                    compilation = compile_all(os.getcwd() + '/paxos/contracts/p.zip')
                else:
                    pass
            
            elif datum['project_id'] == 'ampleforth':
                if flag == True:
                    compilation_am = compile_all(os.getcwd() + '/ampleforth/market-oracle/am.zip')
                    compilation2_au = compile_all(os.getcwd() + '/ampleforth/uFragments/au.zip')
                    compilation = compilation_am + compilation2_au
                else:
                    pass
            
            elif datum['project_id'] == 'nomisma':
                if flag == True:
                    compilation_bp = compile_all(os.getcwd() + '/nomisma/BankProtcol/bp.zip')
                    compilation_e = compile_all(os.getcwd() + '/nomisma/EthereumSmartContracts/e.zip')
                    compilation = compilation_bp + compilation_e
                else:
                    pass
            
            elif datum['project_id'] == 'origin-protocol':
                if flag == True:
                    compilation = compile_all(os.getcwd() + '/origin-contracts/contracts/o.zip')
                else:
                    pass
            
            elif datum['project_id'] == 'uma':
                if flag == True:
                    compilation = compile_all(os.getcwd() + '/uma/u.zip')
                else:
                    pass
            
            elif datum['project_id'] == 'celo':
                if flag == True:
                    compilation = compile_all(os.getcwd() + '/celo/c.zip')
                else:
                    pass
            
            elif datum['project_id'] == 'vbm':
                if flag == True:
                    compilation = compile_all(os.getcwd() + '/vbm/src/securevote/v.zip')
                else:
                    pass
            
            elif datum['project_id'] == 'ocean-protocol':
                if flag == True:
                    compilation = compile_all(os.getcwd() + '/ocean-protocol/o.zip')
                else:
                    pass
            
            previous_project_id = datum['project_id'] 
            
            # Iterate over all of the contracts
            for c in compilation:
                slither = Slither(c)
                for contract in slither.contracts:
                    if str(contract.contract_kind) != 'library':
                        # Iterate over all of the functions
                        for function in contract.functions_declared:
                            if function.canonical_name == funcname:
                                if function.contract_declarer == contract:
                                    if function.nodes == [] or function.is_constructor_variables:
                                        continue
                                    x = (datum['project_id'], cfilename, contract.name, function.name)
                                    function_dict[x] = []
                                    
                                    # Iterate over the nodes of the function
                                    for node in function.nodes:
                                        if node.expression:
                                            for ir in node.irs:
                                                if hasattr(ir, 'destination') and ir.destination == 'SafeMath':
                                                    function_dict[x].append(encode_ir(ir) + '_SafeMath_' + str(ir.function))
                                                else:
                                                    function_dict[x].append(encode_ir(ir))
    
    w = csv.writer(open("output.csv", "w+"))
    for key, val in function_dict.items():
        w.writerow([key, val])
    return function_dict


if __name__ == "__main__":
    input_csv = str(input("Enter the path for the csv file named issues_dataset.csv first:\n"))
    try:
        client_list = list()
        print("""Enter a list of client project_ids separated by carrier return:\n(Type 'all' to process all existing clients. when finished typing, press Ctrl-C.)""")
        while True:
            client_list.append(str(input()))
    except:
        print("\tDone!")
        encode_function(input_csv, client_list)

# -*- coding: utf-8 -*-
"""
Created on Wed Jul 14 16:50:44 2021

@author: I2R
"""

from discharging_init import Process_input
from vlcc_gen import Generate_plan 
from vlcc_check import Check_plans
import numpy as np
from valveSequence import Constants, ValveFilters, ValveOperations, ValveSequencing, ValveConversion, \
    ValveFiltersDischarge, ValveOperationsDischarge, ValveSequencingDischarge, getManifoldUsed
# import json

# import pickle
#import dill as pickle

def gen_sequence1(data: dict) -> dict:
    
    if not data['vessel']:
        return {'message': 'Vessel details not available!!'}
    
    out = discharging(data)
    
    return out


def discharging(data: dict) -> dict:
    out = {}
    
    params = Process_input(data)
    params.prepare_data()
    params.write_ampl(IIS = False)
    
    # input("Press Enter to continue...")
    
    
    gen_output = Generate_plan(params)
    gen_output.run(num_plans=1)
    
    # with open('result.pickle', 'wb') as fp_:
    #     pickle.dump(gen_output, fp_)  
    
    # with open('result.pickle', 'rb') as fp_:
    #     gen_output = pickle.load(fp_)
    
    
    # ## check and modify plans    
    plan_check = Check_plans(params, reballast = True)
    plan_check._check_plans(gen_output)
    
      
    ## gen json  
    out = gen_output.gen_json3({}, plan_check.stability_values)

    # Valve
    disableValves = False
    if disableValves:
        print('Valve section currently disabled.')
        return out
    elif params.error:
       print('Error while processing input. Skipping valve module.')
       return out
    elif len(gen_output.plans.get('ship_status', [])) == 0:
        print('Infeasible Solution. Skipping valve module.')
        return out
    elif params.vessel_id == 2:
        print('Valves module not ready for Atlantic Pioneer')
        return out
    else:

        # Cargo Valves
        manifold = getManifoldUsed(out)
        constants = Constants()
        valve_sequence = ValveSequencingDischarge(out, constants, data)
        df_merged_final_grouped, eductor = valve_sequence.df_final_merged_operations(out)
        valve_filter = ValveFiltersDischarge(constants)
        valve_operation = ValveOperationsDischarge(valve_filter, constants, eductor, manifold, data)
        valve_dict_final = valve_sequence.generate_sequence(valve_operation, df_merged_final_grouped)

        # Ballast Valves
        vfilter = ValveFilters(constants)
        voperation = ValveOperations(vfilter, data, constants)
        valve_time = ValveSequencing(out, voperation, "discharging", constants)
        # Conversion
        valve_conversion = ValveConversion(out, constants)
        valve_conversion.convertValves(valve_dict_final, 'cargoValves')
        if hasattr(valve_time, 'ballast_valves'):
            valve_conversion.convertValves(valve_time.ballast_valves, 'ballastValves')
        return valve_conversion.json
    
    return out


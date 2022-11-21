# -*- coding: utf-8 -*-
"""
Created on Sun Dec  6 12:24:27 2020

@author: I2R
"""
import json
#import requests
#from requests.exceptions import HTTPError

from vlcc_init import Process_input
from vlcc_check import Check_plans
from vlcc_rotation import Check_rotations
from vlcc_gen import Generate_plan 
from vlcc_multi_gen import Multiple_plans 



from discharge_init import Process_input1

# import pickle

def gen_allocation(data):
    out = []
            
    if not data['vessel']:
        return {'message': 'Vessel details not available!!'}
    
    if data.get('loadablePlanPortWiseDetails', []):
        out = manual_mode(data)        
    elif data['module'] in ['LOADABLE']:
        print ('Auto Mode LOADABLE --------------------------------------------')
        out = auto_mode(data)
    else:
        print ('DISCHARGE Mode --------------------------------------------')
        out = discharge_mode(data)
    
    return out

def discharge_mode(data):
    out = []
    
    input_param = Process_input1(data)
    input_param.prepare_dat_file()
    input_param.write_dat_file()
    
    # collect plan from AMPL
    gen_output = Generate_plan(input_param)
    gen_output.run(num_plans=1)
    
    # with open('result.pickle', 'wb') as fp_:
    #     pickle.dump(gen_output, fp_)  
    
    # with open('result.pickle', 'rb') as fp_:
    #     gen_output = pickle.load(fp_)
    
    ## check and modify plans    
    plan_check = Check_plans(input_param, reballast = True)
    plan_check._check_plans(gen_output)
    
      
    ## gen json  
    out = gen_output.gen_json2({}, plan_check.stability_values)
    
    return out

def manual_mode(data):
    if not data.get('ballastEdited', False):
        print('Manual Mode LOADABLE -------------------------------------------')
    else:
        print('Full Manual Mode LOADABLE -------------------------------------------')
    
    out = []
    
    # data = get_plan(data)
    
    input_param = Process_input(data)
    input_param.prepare_dat_file()
    input_param.write_dat_file()
    
    # collect plan from AMPL
    gen_output = Generate_plan(input_param)
    gen_output.run(num_plans=1)
    
    ## check and modify plans    
    plan_check = Check_plans(input_param, reballast = True)
    plan_check._check_plans(gen_output)
     
    # gen json  
    out = gen_output.gen_json({}, plan_check.stability_values)
    
    
    return out

# get the loading and ballast operations


def auto_mode(data):
    out = []
    ## process input and gen dat for AMPL
    input_param = Process_input(data)
    input_param.prepare_dat_file()
    input_param.write_dat_file()
    
    input_param.gen_distinct_plan = True
    
    # collect plan from AMPL or ORTOOLS
    outputs = Multiple_plans(data, input_param)
    outputs.run()
    
    # print(outputs.plans.get('cargo_tank',[]))
    # with open('outputs.json', 'w') as f_:  
    #    json.dump(outputs.plans, f_)
    
    ## check and modify plans    
#    plan_check = Check_plans(input_param)
#    plan_check._check_plans(outputs.plans.get('ship_status',[]), outputs.plans.get('cargo_tank',[]))
    
    # with open('result.pickle', 'wb') as handle:
    #     pickle.dump((data, input_param, outputs.plans), handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    
    

    
    # ## check cargo rotation
    cargo_rotate = Check_rotations(data, input_param)
    cargo_rotate._check_plans(outputs.plans, outputs.permute_list, outputs.permute_list1)
    
    # # # ## gen json  
    out = outputs.gen_json(cargo_rotate.constraints, outputs.plans['stability'])
    ## out = outputs.gen_json({str(k_):[] for k_ in range(0,len(outputs.plans.get('ship_status',[])))}, plan_check.stability_values)
    
        
    
    return out
    
def loadicator(data, limits):
    
    out = {"processId": data["processId"], "loadicatorResults":{}}
    # print(limits)
    
    # print(limits['limits']['feedback'], limits['limits']['sfbm'])
    
    if type(data.get("loadicatorPatternDetail",None)) is dict:
        
        # Manual or fully Manual
        
        out["loadicatorResults"]["loadablePatternId"] = data['loadicatorPatternDetail']['loadablePatternId']
        out["loadicatorResults"]['loadicatorResultDetails'] = []
        
        results_ =  data['loadicatorPatternDetail']
        fail_SF_, fail_BM_ = False, False
        last_depart_ = len(results_['ldTrim'])
        
        for n_, (u_, v_) in enumerate(zip(results_['ldTrim'],results_['ldStrength'])):
            assert u_['portId'] == v_['portId']
            info_ = {}
            info_['portId'] = int(u_['portId'])
            info_['synopticalId'] = int(u_['synopticalId'])
            info_['operationId'] = int(limits['limits']['operationId'][str(u_['portRotationId'])])
            info_["calculatedDraftFwdPlanned"] = u_["foreDraftValue"]
            info_["calculatedDraftMidPlanned"] = u_["meanDraftValue"]
            info_["calculatedDraftAftPlanned"] = u_["aftDraftValue"]
            info_["calculatedTrimPlanned"] = u_["trimValue"]
            info_["blindSector"] = None
            info_["list"] = str(u_["heelValue"])
            info_['airDraft'] = u_['airDraftValue']
            info_['deflection'] = u_.get("deflection", None) 
            
            info_["SF"] = v_["shearingForcePersentValue"]
            info_['BM'] = v_["bendingMomentPersentValue"]
            
            
            info_['errorDetails'] = []
            if u_["errorDetails"] not in [""]:
                info_['errorDetails'].append(u_["errorDetails"])
            if v_["errorDetails"] not in [""]:
                info_['errorDetails'].append(v_["errorDetails"])
            
            
            if info_['deflection'] in [None, ""]:
                sag_ = 0.
            else:
                sag_ = float(u_.get('deflection', 0.))/4000
            
            mid_ship_draft_ = float(u_["meanDraftValue"]) + sag_
            info_['judgement'] = []
            
            if data['module'] in ['LOADABLE']:
                
                # trim
                if (0 <= n_ < last_depart_-1): # and (info_['operationId'] in [1,2]):
                    if (float(u_["trimValue"]) < limits['limits']['trimLimit'][0]) or (float(u_["trimValue"]) > limits['limits']['upperTrimLimit'][str(n_)]):
                        info_['judgement'].append('Port ' + str( u_['portId']) +': Failed trim check ('+ "{:.2f}".format(float(u_["trimValue"])) +'m)!')
                        print('Port ' + str( u_['portId']) +': Failed trim check ('+ "{:.2f}".format(float(u_["trimValue"])) +'m)!')
                   
                        
                # list
                if u_["heelValue"] not in [None and ""]:
                    if (float(u_["heelValue"]) < limits['limits']['listLimit'][0]) or (float(u_["heelValue"]) > limits['limits']['listLimit'][1]):
                        info_['judgement'].append('Port ' + str( u_['portId']) +': Failed list check ('+ "{:.1f}".format(float(u_["heelValue"])) +')!')
                        print('Port ' + str( u_['portId']) +': Failed list check ('+ "{:.1f}".format(float(u_["heelValue"])) +')!')
            
            elif data['module'] in ['DISCHARGE']:
                
                    # trim
                if abs(float(u_["trimValue"])) > 0.1:
                    info_['judgement'].append('Port ' + str( u_['portId']) +': Failed trim check ('+ "{:.2f}".format(float(u_["trimValue"])) +'m)!')
                    print('Port ' + str( u_['portId']) +': Failed trim check ('+ "{:.2f}".format(float(u_["trimValue"])) +'m)!')
                    
                # list
                if u_["heelValue"] not in [None and ""] and abs(float(u_["heelValue"])) >= 0.1:
                    info_['judgement'].append('Port ' + str( u_['portId']) +': Failed list check ('+ "{:.1f}".format(float(u_["heelValue"])) +')!')
                    print('Port ' + str( u_['portId']) +': Failed list check ('+ "{:.1f}".format(float(u_["heelValue"])) +')!')
 
                
            
            
            # max permissible draft
            max_draft_ = max([float(u_["foreDraftValue"]), float(u_["aftDraftValue"])]) 
            if limits['limits']['draft'][str(info_['portId'])] < max_draft_:
                info_['judgement'].append('Port ' + str( u_['portId']) +': Failed max permissible draft check ('+ "{:.2f}".format(max_draft_) +'m)!')
                print('Port ' + str( u_['portId']) +': Failed max permissible draft check ('+ "{:.2f}".format(max_draft_) +'m)!')
            # loadline 
            if limits['limits']['draft']['loadline'] < max_draft_:
                info_['judgement'].append('Port ' + str( u_['portId']) +': Failed loadline check ('+ "{:.2f}".format(max_draft_) +'m)!')
                print('Port ' + str( u_['portId']) +': Failed loadline check ('+ "{:.2f}".format(max_draft_) +'m)!')
            # airDraft
            if limits['limits']['airDraft'][str(info_['portId'])] < float(info_['airDraft']):
                info_['judgement'].append('Port ' + str( u_['portId']) +': Failed airdraft check ('+ "{:.2f}".format(float(info_['airDraft'])) +'m)!')
                print('Port ' + str( u_['portId']) +': Failed airdraft check ('+ "{:.2f}".format(float(info_['airDraft'])) +'m)!')
            
            # SF
            not_dep_last_port_ = True
            if data['module'] in ['LOADABLE']:
                l_ = limits['limits']['SFLimit']
                not_dep_last_port_ = (0 <= n_ < last_depart_-1)
            elif data['module'] in ['DISCHARGE']:
                l_ = 100
            
            if not_dep_last_port_ and abs(float(v_["shearingForcePersentValue"])) > l_:
                info_['judgement'].append('Port ' + str( u_['portId']) +': Failed SF check ('+ "{:.0f}".format(float(v_["shearingForcePersentValue"])) +')!')
                print('Port ' + str( u_['portId']) +': Failed SF check ('+ "{:.0f}".format(float(v_["shearingForcePersentValue"])) +')!')
                # fail_SF_  = True
            # BM
            not_dep_last_port_ = True
            if data['module'] in ['LOADABLE']:
                l_ = limits['limits']['BMLimit']
                not_dep_last_port_ = (0 <= n_ < last_depart_-1)
            elif data['module'] in ['DISCHARGE']:
                l_ = 100
                
            if not_dep_last_port_ and abs(float(v_["bendingMomentPersentValue"])) > l_:
                info_['judgement'].append('Port ' + str( u_['portId']) +': Failed BM check ('+ "{:.0f}".format(float(v_["bendingMomentPersentValue"])) +')!')
                print('Port ' + str( u_['portId']) +': Failed BM check ('+ "{:.0f}".format(float(v_["bendingMomentPersentValue"])) +')!')
                # fail_BM_ = True
            
            
            out["loadicatorResults"]['loadicatorResultDetails'].append(info_)
            
        rerun_ = True if fail_BM_ or fail_SF_ else False
            
    elif type(data["loadicatorPatternDetails"]) is list:
        # auto mode
        out = {"processId": data["processId"], "loadicatorResultsPatternWise":[]}
        
        # print(len(data['loadicatorPatternDetails']))
        
        fail_BMSF_ = 0
        
        for p__, p_ in enumerate(data['loadicatorPatternDetails']): # number of plans
            print('case:',p__)
            out_ = {"loadablePatternId":p_["loadablePatternId"], 'loadicatorResultDetails':[]}
            
            fail_SF_, fail_BM_ = False, False
            last_depart_ = len(p_['ldTrim']) - 1
            # print('last_depart_', last_depart_)
            for n_, (u_, v_) in enumerate(zip(p_['ldTrim'],p_['ldStrength'])):
                # print(n_)
                assert u_['portId'] == v_['portId']
                info_ = {}
                info_['portId'] = int(u_['portId'])
                info_['synopticalId'] = int(u_.get('synopticalId',""))
                info_['operationId'] = int(limits['limits']['operationId'][str(u_['portRotationId'])])
                
                info_["calculatedDraftFwdPlanned"] = u_["foreDraftValue"]
                info_["calculatedDraftMidPlanned"] = u_["meanDraftValue"]
                info_["calculatedDraftAftPlanned"] = u_["aftDraftValue"]
                info_["calculatedTrimPlanned"] = u_["trimValue"]
                info_["blindSector"] = None
                info_["list"] = str(u_["heelValue"])
                info_['airDraft'] = u_['airDraftValue']
                info_['deflection'] = u_.get('deflection', None)
                
                info_["SF"] = v_["shearingForcePersentValue"]
                info_['BM'] = v_["bendingMomentPersentValue"]
                
                info_['errorDetails'] = []
                if u_["errorDetails"] not in [""]:
                    info_['errorDetails'].append(u_["errorDetails"])
                if v_["errorDetails"] not in [""]:
                    info_['errorDetails'].append(v_["errorDetails"])
            
                
                if info_['deflection'] in [None, ""]:
                    sag_ = 0.
                else:
                    sag_ = float(u_.get('deflection', 0.))/4000
                
                
                mid_ship_draft_ = float(u_["meanDraftValue"]) + sag_
                info_['judgement'] = []
                
                if data['module'] in ['LOADABLE']:
                
                    # trim
                    if (0 <= n_ < last_depart_-1): # and (info_['operationId'] in [1,2]):
                        if (float(u_["trimValue"]) < limits['limits']['trimLimit'][0]) or (float(u_["trimValue"]) > limits['limits']['upperTrimLimit'][str(n_)]):
                            info_['judgement'].append('Port ' + str( u_['portId']) +': Failed trim check ('+ "{:.2f}".format(float(u_["trimValue"])) +'m)!')
                            print('Port ' + str( u_['portId']) +': Failed trim check ('+ "{:.2f}".format(float(u_["trimValue"])) +'m)!')
                        
                    # list
                    if (0 <= n_ < last_depart_-1) and u_["heelValue"] not in [None and ""]:
                        if (float(u_["heelValue"]) < limits['limits']['listLimit'][0]) or (float(u_["heelValue"]) > limits['limits']['listLimit'][1]):
                            info_['judgement'].append('Port ' + str( u_['portId']) +': Failed list check ('+ "{:.1f}".format(float(u_["heelValue"])) +')!')
                            print('Port ' + str( u_['portId']) +': Failed list check ('+ "{:.1f}".format(float(u_["heelValue"])) +')!')
                
                elif data['module'] in ['DISCHARGE']:
                    
                        # trim
                    if (0 < n_ <= last_depart_):
                        if (float(u_["trimValue"]) < -0.1) or (float(u_["trimValue"]) > limits['limits']['upperTrimLimit'][str(n_)]):
                        
                            info_['judgement'].append('Port ' + str( u_['portId']) +': Failed trim check ('+ "{:.2f}".format(float(u_["trimValue"])) +'m)!')
                            print('Port ' + str( u_['portId']) +': Failed trim check ('+ "{:.2f}".format(float(u_["trimValue"])) +'m)!')
                        
                    # list
                    if u_["heelValue"] not in [None and ""] and abs(float(u_["heelValue"])) >= 0.1:
                        info_['judgement'].append('Port ' + str( u_['portId']) +': Failed list check ('+ "{:.1f}".format(float(u_["heelValue"])) +')!')
                        print('Port ' + str( u_['portId']) +': Failed list check ('+ "{:.1f}".format(float(u_["heelValue"])) +')!')
                  
                    
   
                # max permissible draft
                max_draft_ = max([float(u_["foreDraftValue"]), float(u_["aftDraftValue"])]) 
                if limits['limits']['draft'][str(info_['portId'])] < max_draft_:
                    info_['judgement'].append('Port ' + str( u_['portId']) +': Failed max permissible draft check ('+ "{:.2f}".format(max_draft_) +'m)!')
                    print('Port ' + str( u_['portId']) +': Failed max permissible draft check ('+ "{:.2f}".format(max_draft_) +'m)!')
                    print(mid_ship_draft_, info_['deflection'], u_["meanDraftValue"])
                # loadline 
                if limits['limits']['draft']['loadline'] < max_draft_:
                    info_['judgement'].append('Port ' + str( u_['portId']) +': Failed loadline check ('+ "{:.2f}".format(max_draft_) +'m)!')
                    print('Port ' + str( u_['portId']) +': Failed loadline check ('+ "{:.2f}".format(max_draft_) +'m)!')
                # airDraft
                if limits['limits']['airDraft'][str(info_['portId'])] < float(info_['airDraft']):
                    info_['judgement'].append('Port ' + str( u_['portId']) +': Failed airdraft check ('+ "{:.2f}".format(float(info_['airDraft'])) +'m)!')
                    print('Port ' + str( u_['portId']) +': Failed airdraft check ('+ "{:.2f}".format(float(info_['airDraft'])) +'m)!')
                
                # SF
                not_dep_last_port_ = True
                if data['module'] in ['LOADABLE']:
                    l_ = limits['limits']['SFLimit']
                    not_dep_last_port_ = (0 <= n_ < last_depart_-1)
                elif data['module'] in ['DISCHARGE']:
                    l_ = 100
                    
                if not_dep_last_port_ and abs(float(v_["shearingForcePersentValue"])) > l_:
                    info_['judgement'].append('Port ' + str( u_['portId']) +': Failed SF check ('+ "{:.0f}".format(float(v_["shearingForcePersentValue"])) +')!')
                    print('Port ' + str( u_['portId']) +': Failed SF check ('+ "{:.0f}".format(float(v_["shearingForcePersentValue"])) +')!')
                    fail_SF_ = True
                
                # BM
                not_dep_last_port_ = True
                if data['module'] in ['LOADABLE']:
                    l_ = limits['limits']['BMLimit']
                    not_dep_last_port_ = (0 <= n_ < last_depart_-1)
                elif data['module'] in ['DISCHARGE']:
                    l_ = 100
                    
                if not_dep_last_port_ and abs(float(v_["bendingMomentPersentValue"])) > l_:
                    info_['judgement'].append('Port ' + str( u_['portId']) +': Failed BM check ('+ "{:.0f}".format(float(v_["bendingMomentPersentValue"])) +')!')
                    print('Port ' + str( u_['portId']) +': Failed BM check ('+ "{:.0f}".format(float(v_["bendingMomentPersentValue"])) +')!')
                    fail_BM_ = True
                
                out_["loadicatorResultDetails"].append(info_)
            
            out['loadicatorResultsPatternWise'].append(out_)
            if fail_SF_ and fail_BM_:
                fail_BMSF_ += 1
                
            
        rerun_ = True if fail_BMSF_ == len(data['loadicatorPatternDetails']) else False
            
    else:
        print('Unknown type!!')
            
        
    # print(fail_BMSF_)
    # rerun_ = True
    if not rerun_:    
        ## feedback loop
        out['feedbackLoop'] = False
        out['feedbackLoopCount'] = limits['limits'].get('feedback', {}).get('feedbackLoopCount', 0)
        out['sfbmFac'] = limits['limits'].get('sfbm', 0.95)
        
        # print('do')
    elif data.get('module', None) in ['LOADABLE']:
        print('Rerun!!')
        out['feedbackLoop'] = True
        out['feedbackLoopCount'] = limits['limits']['feedback']['feedbackLoopCount'] + 1
        out['sfbmFac'] = limits['limits'].get('sfbm', 0.95) - 0.05
    ## 
    
    
    return out
#    print(out)

if __name__ == "__main__":
    
    data = {}
    with open('loadableStudy1.json') as json_file: 
        data['loadable'] = json.load(json_file) 
    with open('vessel.json') as json_file: 
        data['vessel'] = json.load(json_file) 
        
    message = gen_allocation(data)

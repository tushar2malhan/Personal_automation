# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 12:05:21 2020

@author: I2R
"""

from copy import deepcopy

class Port:
    def __init__(self, inputs):
        ports_info_ = {}
        ports_info_['bunkering'], ports_info_['normalOp'] = {},{}
        ## remove bunkering operation if loading/discharging are done at the same port
        # port_operation_ = {}

        ports_info_['ignorePortRotationId'], ports_info_['ignorePortRotationId1'] = {}, {}
        ports_info_['new_arrival_plan'] = {}
        ports_info_['past_plans'] = []
        ports_info_['past_plans1'] = []
        
        if inputs.module in ['DISCHARGE'] and inputs.discharge_json["existingDischargePlanDetails"]:
            # print("Ignore ports")
            
            plans_ = inputs.discharge_json["existingDischargePlanDetails"]['existingDischargePatternDetails']['dischargePlanDetails'][0]['dischargePlanPortWiseDetails']
            for p_ in inputs.discharge_json["existingDischargePlanDetails"]['dischargingPlans']:
                if p_['actual']:
                    pre_id_ = p_['portRotationId']
                    new_id_ = inputs.discharge_json["existingDischargePlanDetails"]['portRotationMappings'][str(pre_id_)]['portRotationId']
                    ports_info_['ignorePortRotationId'][new_id_] = pre_id_
                    ports_info_['ignorePortRotationId1'][pre_id_] = new_id_
                    ports_info_['new_arrival_plan'] = p_['actual']['departure']['planDetails']
                    ports_info_['past_plans'].append({str(new_id_): deepcopy(p_['actual'])})
                    
                    plan_ = next(item for item in plans_ if item.get("portRotationId")  == pre_id_)
                    plan1_ = deepcopy(plan_)
                    
                    # arr cargo
                    act1_ = p_['actual']['arrival']['planDetails']['stowageDetails']
                    for k__, k_ in enumerate(plan_['arrivalCondition']['dischargePlanStowageDetails']):
                        tankId_ = k_['tankId']
                        info_ = next(item for item in act1_ if item.get("tankId")  == tankId_)
                        
                        plan1_['arrivalCondition']['dischargePlanStowageDetails'][k__]['actualQuantityMT'] = str(info_['quantity'])
                        plan1_['arrivalCondition']['dischargePlanStowageDetails'][k__]['actualQuantityM3'] = str(info_['quantityM3'])
                        plan1_['arrivalCondition']['dischargePlanStowageDetails'][k__]['actualAPI'] = str(info_['api'])
                        plan1_['arrivalCondition']['dischargePlanStowageDetails'][k__]['actualTemperature'] = str(info_['temperature'])
                        plan1_['arrivalCondition']['dischargePlanStowageDetails'][k__]['actualUllage'] = str(info_['ullage'])
                        
                    # arr ballast    
                    act1_ = p_['actual']['arrival']['planDetails']['ballastDetails']
                    for k__, k_ in enumerate(plan_['arrivalCondition']['dischargePlanBallastDetails']):
                        tankId_ = k_['tankId']
                        info_ = next(item for item in act1_ if item.get("tankId")  == tankId_)
                        
                        plan1_['arrivalCondition']['dischargePlanBallastDetails'][k__]['actualQuantityMT'] = str(info_['quantity'])
                        plan1_['arrivalCondition']['dischargePlanBallastDetails'][k__]['actualQuantityM3'] = str(info_['observedM3'])
                        # plan1_['arrivalCondition']['dischargePlanBallastDetails'][k__]['actualAPI'] = str(info_['api'])
                        # plan1_['arrivalCondition']['dischargePlanBallastDetails'][k__]['actualTemperature'] = str(info_['temperature'])
                        plan1_['arrivalCondition']['dischargePlanBallastDetails'][k__]['actualSounding'] = str(info_['sounding'])
                       
                        
                    # dep cargo    
                    act2_ = p_['actual']['departure']['planDetails']['stowageDetails']
                    for k__, k_ in enumerate(plan_['departureCondition']['dischargePlanStowageDetails']):
                        tankId_ = k_['tankId']
                        info_ = next(item for item in act2_ if item.get("tankId")  == tankId_)
                        
                        plan1_['departureCondition']['dischargePlanStowageDetails'][k__]['actualQuantityMT'] = str(info_['quantity'])
                        plan1_['departureCondition']['dischargePlanStowageDetails'][k__]['actualQuantityM3'] = str(info_['quantityM3'])
                        plan1_['departureCondition']['dischargePlanStowageDetails'][k__]['actualAPI'] = str(info_['api'])
                        plan1_['departureCondition']['dischargePlanStowageDetails'][k__]['actualTemperature'] = str(info_['temperature'])
                        plan1_['departureCondition']['dischargePlanStowageDetails'][k__]['actualUllage'] = str(info_['ullage'])
                    
                    # dep cargo    
                    act2_ = p_['actual']['departure']['planDetails']['ballastDetails']
                    for k__, k_ in enumerate(plan_['departureCondition']['dischargePlanBallastDetails']):
                        tankId_ = k_['tankId']
                        info_ = next(item for item in act2_ if item.get("tankId")  == tankId_)
                        
                        plan1_['departureCondition']['dischargePlanBallastDetails'][k__]['actualQuantityMT'] = str(info_['quantity'])
                        plan1_['departureCondition']['dischargePlanBallastDetails'][k__]['actualQuantityM3'] = str(info_['observedM3'])
                        # plan1_['departureCondition']['dischargePlanBallastDetails'][k__]['actualAPI'] = str(info_['api'])
                        # plan1_['departureCondition']['dischargePlanBallastDetails'][k__]['actualTemperature'] = str(info_['temperature'])
                        plan1_['departureCondition']['dischargePlanBallastDetails'][k__]['actualSounding'] = str(info_['sounding'])
                       
                        
                    ports_info_['past_plans1'].append({str(new_id_):plan1_})
            
            print("Ignore ports", ports_info_['ignorePortRotationId'])
            # for k_, v_ in inputs.discharge_json["existingDischargePlanDetails"]['portRotationMappings'].items():
            #     ports_info_['ignorePortRotationId'][v_['portRotationId']] = int(k_)
        for p__, p_ in enumerate(inputs.port_json['portRotation']):
            # if p_['portId'] not in port_operation_.keys():
            #     port_operation_[p_['portId']] = [p_['operationId']]
            # else:
            #     port_operation_[p_['portId']].append(p_['operationId'])
                
            if p_['id'] not in ports_info_['ignorePortRotationId']:    
            	if p_['operationId'] not in [1,2]:
                	ports_info_['bunkering'][p__] = p_
            	else:
                	ports_info_['normalOp'][p__] = p_['portId']
                
        print('bunkering:', list(ports_info_['bunkering'].keys()))
                
        
        port_details_ = {}
        for p__, p_ in enumerate(inputs.port_json['portDetails']):
            port_details_[p_['id']] = {'densitySeaWater':p_['densitySeaWater'],
                                       'code': p_['code'], 'tideHeight': float(p_["tideHeight"]) if p_.get("tideHeight",None) not in [None, ""] else 0.,
                                       'seaWaterTemperature':p_.get('seaWaterTemperature', 0.),
                                       'ambientTemperature':p_.get('ambientTemperature', 0.)}

        # for k_, v_ in port_operation_.items():
        #     if len(v_) > 1:
        #         oper_ = [l_  for l_ in v_ if l_ in [1,2]]
        #         port_operation_[k_] = oper_
                
        # print('port_operation:', port_operation_)     
        ## assume either loading or discharging but not both
        port_rotation_, order_ = [], 1
        ports_info_['ignore_port'] = {}
        for p__, p_ in enumerate(inputs.port_json['portRotation']):
            # if p_['operationId'] in [3,4]:
            #     print(p_)
            if p_['id'] not in ports_info_['ignorePortRotationId']:
                port_rotation_.append(p_)
                port_rotation_[order_-1]['portOrder'] = order_
                order_ += 1
            else:
                detail_ = port_details_[p_['portId']]
                ports_info_['ignore_port'][p_['id']] = (p_['portId'], detail_['code'])

            
        if inputs.module in ['LOADABLE']:
            last_loading_port_ = max([p_['portOrder'] for p_ in port_rotation_ if p_["operationId"] in [1,3,4]])
        else:
            last_loading_port_ = 0
        
        
        ports_info_['portRotation'] = {}
        ports_info_['portOrder'], ports_info_['idPortOrder'] = {}, {}
        ports_info_['portOrderId'] = {}
        ports_info_['firstPortBunker'] = False
        
        ports_info_['lastLoadingPort'] = last_loading_port_
        
        ports_info_['seawaterDensity'] = {}
        ports_info_['tide'] = {}
        ports_info_['portRotationId'] = {}
        ports_info_['portRotationId1'] = {}
        
        ports_info_['cargoSeq'] = {}
        ports_info_['maxEmptyTanks'] = {}
        ports_info_['cowType'] = {}
        ports_info_['cowAllowed'] = {}

           
        last_port_ = last_loading_port_ + 1 if inputs.module == 'LOADABLE' else len(port_rotation_) + 1
        for p__, p_ in enumerate(port_rotation_): #inputs.port_json['portRotation']):
            if p_['portOrder'] <= last_port_:
                # print(p_['portId'])
                detail_ = port_details_[p_['portId']]
                
                densitySeaWater_ = detail_.get('densitySeaWater', 1.025)
                if densitySeaWater_ in [None, ""]:
                    densitySeaWater_ = 1.025
                    
                code_ = detail_['code'] + str(p__)
                portId_ = int(str(p_['portId'])+str(p__))
                
                ports_info_['cowAllowed'][str(portId_)] = p_.get('cow', False)
                ports_info_['seawaterDensity'][str(portId_)] = float(densitySeaWater_)
                ports_info_['tide'][str(portId_)] = float(detail_['tideHeight'])
                ports_info_['portRotationId'][str(p_['id'])] = portId_
                ports_info_['portRotationId1'][str(portId_)] = p_['id']
                    
                ports_info_['portRotation'][code_] = {}
                ports_info_['portRotation'][code_]['order'] = p_['portOrder']
                ports_info_['portRotation'][code_]['maxDraft'] = float(p_['maxDraft'])
                ports_info_['portRotation'][code_]['portId'] = portId_
                ports_info_['portRotation'][code_]['seawaterDensity'] = float(p_['seaWaterDensity']) if p_['seaWaterDensity'] not in ["",None] else 1.025
                ports_info_['portRotation'][code_]['portRotationId'] = p_['id']
                
                if inputs.module in ['DISCHARGE']:
                    ports_info_['portRotation'][code_]['cowAllowed']  = p_.get('cow', True)
                    ports_info_['portRotation'][code_]['freshCrudeOil']  = p_.get('freshCrudeOil', False)
                    ports_info_['portRotation'][code_]['freshCrudeOilTime']  = p_.get('freshCrudeOilTime', 0)
                    ports_info_['portRotation'][code_]['freshCrudeOilQuantity']  = p_.get('freshCrudeOilQuantity', 0)

                # if inputs.module == 'LOADABLE':
                #     ports_info_['portRotation'][code_]['maxDraft'] = p_['maxDraft'] - float(inputs.draftsag)/400
                
                ports_info_['portOrder'][str(p_['portOrder'])] = code_
                ports_info_['idPortOrder'][str(portId_)] = str(p_['portOrder']) # id:order
                ports_info_['portOrderId'][str(p_['portOrder'])] = str(portId_) # order:id
                
                ports_info_['portRotation'][code_]['operationId'] = p_['operationId']
                ports_info_['portRotation'][code_]['maxAirDraft'] = float(p_["maxAirDraft"]) if p_.get("maxAirDraft",None) not in [None, ""] else 200
                ports_info_['portRotation'][code_]['tideHeight'] = detail_['tideHeight']
                
                ports_info_['portRotation'][code_]['ambientTemperature'] = detail_['ambientTemperature']
                ports_info_['portRotation'][code_]['seaWaterTemperature'] = detail_['seaWaterTemperature']
                
                if p_['portOrder'] == 1 and p_['operationId'] not in [1, 2]:
                    ports_info_['firstPortBunker'] = True
                    
                if p_['portOrder'] == 2 and p_['operationId'] not in [1] and ports_info_['firstPortBunker']:
                    ports_info_['firstPortBunker'] = True
                    # inputs.error['Port Operation Error'] = ['One of the first two ports must be a loading port!!']
                    
                # if inputs.module == 'DISCHARGE':
                #     ports_info_['cargoSeq'][str(portId_)] = ['P'+str(pp_["cargoNominationId"]) for pp_ in p_['cargosToBeDischarged']]
                #     ports_info_['maxEmptyTanks'][str(portId_)] = {'P'+str(pp_["cargoNominationId"]): pp_['emptyMaxNumberOfTanks'] for pp_ in p_['cargosToBeDischarged']}
                ports_info_['lastDraft'] = p_['maxDraft']
                ports_info_['draftRestrictive']  = float(p_['maxDraft']) <= 19.8
                
            ## berth info
            
            if p__ == 10:
                inputs.error['Port Rotation Error'] = ['10 ports rotation not tested yet!!']
                
        
        ports_info_['numPort'] = len(ports_info_['portRotation'])
        # for k_, v_ in ports_info_['cowType'].items():
        #     if v_ not in [0,1]:
        #         if 'Cow Type Error' not in inputs.error.keys():
        #             inputs.error['Cow Type Error'] = ['Manual COW at port  ' + str(k_[:-1]) + ' not supported yet!!']
        #         else:
        #             inputs.error['Cow Type Error'].append('Manual COW at port  ' + str(k_[:-1]) + ' not supported yet!!')
        
#        print(ports_info_['portOrder'])
        # arrival and departure ports for ballast synchronize
        # ports_info_['ballastList'] = [2*i_-1 for i_ in range(1,last_loading_port_+1)] 
        # ports_info_['deBallastList'] = []
        # ports_info_['finalBallastPort'] = []
        ports_info_['operationId'] = {str(v_['portId']): str(v_['operationId']) for k_,v_ in ports_info_['portRotation'].items() }
        ports_info_['maxDraft'] = {str(v_['portId']): v_['maxDraft'] for k_,v_ in ports_info_['portRotation'].items() }
        ports_info_['maxAirDraft'] = {str(v_['portId']): v_['maxAirDraft'] for k_,v_ in ports_info_['portRotation'].items()}
        ports_info_['ambientTemperature'] = {str(v_['order']): float(v_['ambientTemperature']) for k_,v_ in ports_info_['portRotation'].items()}
        
        # print(ports_info_)
        
                    
        self.info = ports_info_     
        
      #   if inputs.module == 'LOADABLE':
    		# # error checking -----------------------------------------------------
      #       discharge_port_ = False
      #       for a_, (k_, v_) in enumerate(ports_info_['portOrder'].items()):
      #           oper_ = ports_info_['portRotation'][v_]['operationId']
                
      #           if oper_ in ['2',2]:
      #               discharge_port_ = True
                    
      #           if oper_ in ['2',2] and int(k_) < ports_info_['lastLoadingPort']:
      #               if 'Port Rotation Error' not in inputs.error.keys():
      #                   inputs.error['Port Rotation Error'] = ['Discharging before loading!!']
      #               else:
      #                   inputs.error['Port Rotation Error'].append('Discharging before loading!!')
                    
      #       if not discharge_port_:
      #           if 'Port Rotation Error' not in inputs.error.keys():
      #               inputs.error['Port Rotation Error'] = ['Discharging port not present!!']
      #           else:
      #               inputs.error['Port Rotation Error'].append('Discharging port not present!!')
                    
      #       for k_, v_ in ports_info_['maxDraft'].items():
      #           if v_ in [None]:
      #               port_ =  ports_info_['portOrder'][ports_info_['idPortOrder'][k_]]
      #               if 'Max Draft Error' not in inputs.error.keys():
      #                   inputs.error['Max Draft Error'] = ['Max Draft Error at '+ port_ +'!!']
      #               else:
      #                   inputs.error['Max Draft Error'].append('Max Draft Error at '+ port_ +'!!')
                        
      #       port_order_ = list(ports_info_['portOrder'].keys())
      #       for p__ in range(1,ports_info_['numPort']+1):
      #           if str(p__)  not in  port_order_:
      #               # print(v_)
      #               if 'Port Order Error' not in inputs.error.keys():
      #                   inputs.error['Port Order Error'] = ['Port order ' + str(p__) + ' is missing!!']
      #               else:
      #                   inputs.error['Port Order Error'].append('Port order ' + str(p__) + ' is missing!!')
                    
            
            
        
 
 
            
            
            
            
        
        
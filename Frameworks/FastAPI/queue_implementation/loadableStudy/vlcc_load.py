# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 10:59:03 2020

@author: I2R
"""
DEC_PLACE = 3
import numpy as np
import itertools
from math import ceil
from datetime import datetime

class Loadable:
    def __init__(self, inputs):
        
        self.commingled_ratio = 0.6
        
        cargos_info_ = {}
        cargos_info_['parcel'] = {}
        cargos_info_['sg'] = []
        cargos_info_['maxPriority'] = 0
        cargos_info_['priority'] = {i_:[] for i_ in range(10)}
        cargos_info_['condensateCargo'] = []
        cargos_info_['hrvpCargo'] = []
        cargos_info_['backLoadingCargo'] = []
        
        data_ = inputs.loadable_json['cargoNomination'] if inputs.module == 'LOADABLE' else inputs.discharge_json['cargoNomination']
        
        # operations_ = {}
        
        cargoNominationId_, dscargoNominationId_ = {}, {}
        if inputs.module in ['DISCHARGE']:
            for c__, c_ in enumerate(inputs.discharge_json['cargoOperation']):
                if 'P' + str(c_['dscargoNominationId']) not in cargoNominationId_:
                    cargoNominationId_['P' + str(c_['dscargoNominationId'])] = 'P' + str(c_['cargoNominationId']) 
                    dscargoNominationId_['P' + str(c_['cargoNominationId'])] = 'P' + str(c_['dscargoNominationId']) 
                    
                if c_.get('operationId',2) in [1]:
                    cargos_info_['backLoadingCargo'].append('P' + str(c_['dscargoNominationId']))

            cargos_info_['cargoNominationId'] = cargoNominationId_
            cargos_info_['dscargoNominationId'] = dscargoNominationId_
            
                    
            
        
        
        for c__, c_ in enumerate(data_):
#            print(c_)
            cargo_id_ = 'P' + str(c_['id'])
            
            cargos_info_['parcel'][cargo_id_] = {}
#            cargos_info_['parcel'][cargo_id_]['cargoName'] = c_['cargoname']
            cargos_info_['parcel'][cargo_id_]['cargoId']   = c_['cargoId']
            cargos_info_['parcel'][cargo_id_]['minMaxTol'] = [c_['minTolerance'], c_['maxTolerance']]
            cargos_info_['parcel'][cargo_id_]['priority']  = c_['priority']
            # cargos_info_['parcel'][cargo_id_]['temperature']  = c_['temperature']
            cargos_info_['parcel'][cargo_id_]['color']  = c_['color']
            cargos_info_['parcel'][cargo_id_]['api']  = c_['api']
            cargos_info_['parcel'][cargo_id_]['abbreviation']  = c_['abbreviation']
            cargos_info_['parcel'][cargo_id_]['loadingTemperature']  = c_['temperature']
            cargos_info_['parcel'][cargo_id_]['cargoNominationId'] = cargoNominationId_.get(cargo_id_, None)
            
            if c_['api'] > 90:
                message_ = 'API > 90 for cargo ' + c_['abbreviation'] + '!!'
                if 'API Error' not in inputs.error.keys():
                    inputs.error['API Error'] = [message_]
                else:
                    inputs.error['API Error'].append(message_)
            
            if inputs.module in ['LOADABLE']:
            
                ## temperature, correction factor
                first_loading_port_ = 100
                for o__, o_ in enumerate(inputs.loadable_json['cargoOperation']):
                    if c_['id'] == o_['cargoNominationId']:
                        
                        port_id_ = str(inputs.port.info['portRotationId'][str(o_['portRotationId'])])
                        port_order_ = int(inputs.port.info['idPortOrder'][port_id_])
                        first_loading_port_ = min(first_loading_port_, port_order_)
                        
                ambient_ = []
                for k_, v_ in inputs.port.info['ambientTemperature'].items():
                    if first_loading_port_ <= int(k_):
                        ambient_.append(round(float(v_)*1.8+32,2))
                        
                    
                temp_F_, api_ = c_['temperature'], c_['api']
                temp_F_ = max(temp_F_, inputs.air_temperature, max(ambient_))
            
            else:
                temp_F_, api_ = c_['temperature'], c_['api']
                
            sg_ = self._cal_density(api_,temp_F_)
            
            cargos_info_['parcel'][cargo_id_]['temperature'] = temp_F_
#            print(sg_, c_['sg'])
            
            cargos_info_['parcel'][cargo_id_]['SG']  = sg_
            cargos_info_['parcel'][cargo_id_]['maxtempSG']  = sg_
            cargos_info_['parcel'][cargo_id_]['mintempSG']  = sg_
            
            cargos_info_['parcel'][cargo_id_]['condensateCargo']  = c_.get('isCondensateCargo', False)
            cargos_info_['parcel'][cargo_id_]['hrvpCargo']  = c_.get('isHrvpCargo', False)
            
            # cargos_info_['parcel'][cargo_id_]['condensateCargo'] = True
            # if cargos_info_['parcel'][cargo_id_]['condensateCargo']:
            #     inputs.error['Cargo Error'] = ['Condensate cargo not supported yet!! Cargo history not available!!']
                
            if c_.get('isCondensateCargo',False):
                cargos_info_['condensateCargo'].append(cargo_id_)

            
            # cargos_info_['parcel'][cargo_id_]['hrvpCargo'] = True
            cargos_info_['parcel'][cargo_id_]['banTank'] = []
            if cargos_info_['parcel'][cargo_id_]['hrvpCargo'] and inputs.config['loadableConfig']:
                cargos_info_['parcel'][cargo_id_]['banTank'] += inputs.config['loadableConfig'].get('hrvpCargoBanTank', [])
                
            
            
            cargos_info_['sg'].append(sg_)
            cargos_info_['maxPriority'] = max(cargos_info_['maxPriority'], c_['priority'])
            cargos_info_['priority'][c_['priority']].append(cargo_id_)
       
        self.info = cargos_info_ 
        
        
    def _create_operations(self,inputs):
        
        cargos_info_ = {}
        cargos_info_['cargoPort'] = {k_:[] for k_,v_ in inputs.port.info['idPortOrder'].items()}
        cargos_info_['cargoRotation'] = {}
        cargos_info_['rotationCheck'] = []
        
        for o__, o_ in enumerate(inputs.loadable_json['cargoOperation']):
            
            # portId_ = str(o_['portId'])+'1' if inputs.module in ['LOADABLE'] else str(o_['portId'])+'2'
            portId_ = str(inputs.port.info['portRotationId'][str(o_['portRotationId'])])
            
            cargos_info_['cargoPort'][portId_].append('P'+str(o_['cargoNominationId']))
            if len(cargos_info_['cargoPort'][portId_]) > 1:
                if not inputs.cargo_rotation:
                #     cargos_info_['cargoRotation'][str(o_['portId'])] = inputs.cargo_rotation
                # else:
                    cargos_info_['cargoRotation'][portId_] = cargos_info_['cargoPort'][portId_]
                    
        if inputs.cargo_rotation:
            cargos_info_['cargoRotation'] = inputs.cargo_rotation
                
        len_virtual_ports_ = len(inputs.port.info['portOrder'])*2 # without cargo rotation
        
        # order -> virtual order (only departure)
        virtual_port_ = {}
        arr_dep_virtual_port_ = {}
        max_virtual_port_ = 0
        virtual_arr_dep_ = {}
        rotation_virtual_, rotation_cargo_, rotation_portOrder_ = [], [], []
        
        print('cargo rotation:', cargos_info_['cargoRotation'])
        
        if len(cargos_info_['cargoRotation']) >= 1:
            print('cargo rotation required')
            rotation_portId_ = []
            for k_ in range(1,inputs.port.info['numPort']+1):
                portId_ = inputs.port.info['portOrderId'][str(k_)]
                if portId_ in cargos_info_['cargoRotation']:
                    rotation_portId_.append(portId_)
                    
            for r__, r_ in enumerate(rotation_portId_):
                rotation_portOrder_.append(inputs.port.info['idPortOrder'][r_])
                rotation_cargo_.append(cargos_info_['cargoRotation'][r_])
                rotation_len_ = len(rotation_cargo_)
            
                # store current rotation
                cargos_info_['rotationCheck'].append(rotation_cargo_[r__])
                len_virtual_ports_ += rotation_len_-1
            
            k__, i__, v_ = 0, 0, 0
            for k_ in range(1,inputs.port.info['numPort']+1):
                if str(k_) in  rotation_portOrder_:
                    
                    arr_dep_virtual_port_[str(k_)+'A'] = str(v_)
                    virtual_arr_dep_[str(v_)] = str(k_)+'A'
                    virtual_port_[str(k_)] = {}
                    rotation_virtual__ = []
                    for c__, c_ in enumerate(rotation_cargo_[i__]):
                        v_ += 1
                        virtual_port_[str(k_)][c_] = str(v_)
                        rotation_virtual__.append(v_)
                    k__ = c__
                    i__ += 1
                    
                    rotation_virtual_.append(rotation_virtual__)
                    arr_dep_virtual_port_[str(k_)+'D'] = str(v_)
                    virtual_arr_dep_[str(v_)] = str(k_)+'D'
                    max_virtual_port_ = v_ if v_ > max_virtual_port_ else max_virtual_port_
                    
                else:
                    # v_ = 2*int(k_)-1 + k__
                    virtual_port_[str(k_)] = str(v_+1)
                    arr_dep_virtual_port_[str(k_)+'A'] = str(v_)
                    arr_dep_virtual_port_[str(k_)+'D'] = str(v_+1)
                    
                    virtual_arr_dep_[str(v_)] = str(k_)+'A'
                    virtual_arr_dep_[str(v_+1)] = str(k_)+'D'
                    
                    v_ += 1
                    max_virtual_port_ = v_ if v_ > max_virtual_port_ else max_virtual_port_
                    
                v_ += 1
                    
        else:
            print('cargo rotation not required or ignored')
            # order -> virtual order (only departure)
            virtual_port_ = {str(k_):str(2*int(k_)-1) for k_ in inputs.port.info['portOrderId']}
            # rotation_cargo_ = {}
            
            for k_ in range(1,inputs.port.info['numPort']+1):
                v_ = 2*int(k_)-1
                arr_dep_virtual_port_[str(k_)+'A'] = str(v_-1)
                arr_dep_virtual_port_[str(k_)+'D'] = str(v_)
                
                virtual_arr_dep_[str(v_-1)] = str(k_)+'A'
                virtual_arr_dep_[str(v_)] = str(k_)+'D'
                
                max_virtual_port_ = v_ if v_ > max_virtual_port_ else max_virtual_port_
                
        last_arr_ = '1A'
        for k_ in range(max_virtual_port_+1):
            arr_dep_ = virtual_arr_dep_.get(str(k_),'11NK')
            if arr_dep_ == '11NK':
                virtual_arr_dep_[str(k_)] = str(last_arr_[:-1])+'D'
                
            last_arr_ = arr_dep_ if arr_dep_[-1] == 'A' else last_arr_
            
        print(virtual_port_)    
        cargos_info_['virtualPort'] = virtual_port_
        cargos_info_['arrDepVirtualPort'] = arr_dep_virtual_port_
        cargos_info_['virtualArrDepPort'] = virtual_arr_dep_
        cargos_info_['lastVirtualPort'] = max_virtual_port_
        cargos_info_['rotationVirtual'] = rotation_virtual_ # rotation virtual port
        cargos_info_['rotationCargo']   = rotation_cargo_ # rotation virtual port
        
        # sea water density
        cargos_info_['seawaterDensity'] = {}
        for k_, v_ in cargos_info_['virtualArrDepPort'].items():
            port_name_ = inputs.port.info['portOrder'][v_[:-1]]
            cargos_info_['seawaterDensity'][k_] = inputs.port.info['portRotation'][port_name_]['seawaterDensity']
            
            
        # cargos_info_ = {}
        
        # cargos_info_['commingleCargo'] = {}
        self._set_commingle_info(inputs, cargos_info_)
            
        cargos_info_['operation'] = {k_:{}  for k_,v_ in self.info['parcel'].items()}
        cargos_info_['toLoad'] = {k_:0 for k_,v_ in self.info['parcel'].items()}
        cargos_info_['toLoadIntend']    = {k_:0 for k_,v_ in self.info['parcel'].items()}
        cargos_info_['toLoadMin'] = {k_:0 for k_,v_ in self.info['parcel'].items()}
        
        cargos_info_['toLoadPort'] = np.zeros(int(virtual_port_[str(inputs.port.info['numPort'])])+1) # exact ports to virtual ports
        cargos_info_['toLoadMinPort'] = np.zeros(int(virtual_port_[str(inputs.port.info['numPort'])])+1) # exact ports to virtual ports
        cargos_info_['cargoOrder'] = {str(p_):[] for p_ in range(1,max_virtual_port_+1)}
        for o__, o_ in enumerate(inputs.loadable_json['cargoOperation']):
            parcel_ = 'P'+str(o_['cargoNominationId'])
            qty__ = round(float(o_['quantity']),1) #if o_['operationId'] == 1 else -o_['quantity'] 
            
            # portId_ = str(o_['portId'])+'1' if inputs.module in ['LOADABLE'] else str(o_['portId'])+'2' 
            portId_ = str(inputs.port.info['portRotationId'][str(o_['portRotationId'])])
            order_ = inputs.port.info['idPortOrder'][portId_]
            # max qty
            qty_ = qty__ * (1+ 0.01*self.info['parcel'][parcel_]['minMaxTol'][1])
            # min qty
            qty_min_ = qty__ *(1 + 0.01*self.info['parcel'][parcel_]['minMaxTol'][0])
            
            
            cargos_info_['toLoad']['P'+str(o_['cargoNominationId'])] += qty_        # max
            cargos_info_['toLoadIntend']['P'+str(o_['cargoNominationId'])] += qty__ # original
            cargos_info_['toLoadMin']['P'+str(o_['cargoNominationId'])] += qty_min_ # min
            
            if type(virtual_port_[str(order_)]) == dict:
                virtual_order_ = virtual_port_[str(order_)][parcel_]
            else:
                virtual_order_ = virtual_port_[str(order_)]
            
            cargos_info_['toLoadPort'][int(virtual_order_)] += qty_
            cargos_info_['toLoadMinPort'][int(virtual_order_)] += qty_min_
            cargos_info_['operation'][parcel_][virtual_order_] = qty_
            
            if qty_ > 0:
                cargos_info_['cargoOrder'][virtual_order_].append(parcel_)
                
            
            ## single loading port for each cargo set the discharging qty 
            ## no discharge info
            last_discharge_port_ = virtual_port_[str(inputs.port.info['numPort'])]
            if last_discharge_port_ not in cargos_info_['operation'][parcel_]:
                cargos_info_['operation'][parcel_][last_discharge_port_] = -qty_
            else:
                cargos_info_['operation'][parcel_][last_discharge_port_] += -qty_
                
            cargos_info_['toLoadPort'][int(last_discharge_port_)] += -qty_
            cargos_info_['toLoadMinPort'][int(last_discharge_port_)] += -qty_min_
            
            
            
        cargos_info_['toLoadPort1'] = {a__:a_ for a__, a_ in enumerate(cargos_info_['toLoadPort']) if a_ > 0} 
        cargos_info_['toLoadPort'] = np.cumsum(cargos_info_['toLoadPort'])
        cargos_info_['toLoadMinPort'] = np.cumsum(cargos_info_['toLoadMinPort'])
        
        cargos_info_['numParcel'] = len(self.info['parcel'])
        
        cargo_order_ = [v_ for k_,v_ in  cargos_info_['cargoOrder'].items()]
        cargo_order_ = list(itertools.chain.from_iterable(cargo_order_))
        cargos_info_['cargoOrder'] = {c_:c__+1 for c__,c_ in enumerate(cargo_order_)}
        
        
        # for k_, v_ in self.info['parcel'].items():
        #     loading_order_ = cargo_order_.index(k_) + 1
        #     self.info['parcel'][k_]['loadingOrder'] = loading_order_
        
        # cargos_info_['cargoRotation'] = {}
        # for p__, p_ in enumerate(inputs.port.info['ballastList']):
        #     cargos_ = [k_ for k_,v_ in cargos_info_['operation'].items() if v_.get(str(p_),0.) > 0.]
        #     if len(cargos_) > 1:
        #         # print(p_, cargos_)
        #         port_order_ = round(0.5*p_+0.51) # convert virtual port to exact port
        #         cargos_info_['cargoRotation'][str(port_order_)] = cargos_
            
        cargos_info_['manualOperation'] = {}
        for k_, v_ in inputs.loadable_json['loadingPlan'].items():
            order_ = k_
            for k__, v__ in v_.items():
                parcel_ = v__[0]['parcel']
                if parcel_ not in cargos_info_['manualOperation'].keys():
                    cargos_info_['manualOperation'][parcel_] = {}
                    
                qty_ = float(v__[0]['wt']) 
                tank_ = k__
                    
                if order_ not in cargos_info_['manualOperation'][parcel_].keys():
                    cargos_info_['manualOperation'][parcel_][order_] = [{'qty':qty_, 'tank':tank_}]
                else:
                    cargos_info_['manualOperation'][parcel_][order_].append({'qty':qty_, 'tank':tank_})
            
        cargos_info_['preloadOperation'] = {}
        
        cargos_info_['ballastOperation'] = {}
        cargos_info_['fixedBallastPort'] = []
        
        if inputs.mode in ['Auto']:
            for k_, v_ in inputs.loadable_json['ballastPlan'].items():
                order_ = k_
                cargos_info_['fixedBallastPort'].append(order_)
                for k__, v__ in v_.items():
                    tank_ = k__
                    qty_ = float(v__[0]['wt']) 
                    
                    if tank_ not in cargos_info_['ballastOperation'].keys():
                        cargos_info_['ballastOperation'][tank_] = [{'qty':qty_, 'order':order_}]
                    else:
                        cargos_info_['ballastOperation'][tank_].append({'qty':qty_, 'order':order_})
                        
            cargos_info_['zeroListPorts'] = []
            # if inputs.port.info['firstPortBunker']:
            #    cargos_info_['zeroListPorts'] = ['1', '2']
                # initial_ballast_ = {'LFPT':4800, 'WB1P':9000, 'WB1S':9000, 'WB2P':9000, 'WB2S':9000,
                #  'WB3P':9000, 'WB3S':9000, 'WB4P':8900, 'WB4S':8900, 'WB5P':7600, 'WB5S':7600} ## config
                
                # if inputs.config['loadableConfig'].get('initBallastTanksAmt',[]):
                #     ratio_ = inputs.config['loadableConfig']['initBallastTanksAmt']['amt']
                #     initial_ballast_ = {}
                #     for t_ in inputs.config['loadableConfig']['initBallastTanksAmt']['tanks']:
                #         if t_[-1] in ["W"]:
                #             t1_, t2_ = 'WB'+t_[0]+'P', 'WB'+t_[0]+'S'
                #             initial_ballast_[t1_] = round(self.info['ballastTanks'][t1_]['capacityCubm']*ratio_*1.025,2)
                #             initial_ballast_[t2_] = round(self.info['ballastTanks'][t2_]['capacityCubm']*ratio_*1.025,2)
                            
                #         else:
                #             initial_ballast_[t_] = round(self.info['ballastTanks'][t_]['capacityCubm']*ratio_*1.025,2)
                # else:
                #     initial_ballast_ = inputs.config['initial_ballast']
                
                # initial_ballast_ = inputs.config['initial_ballast']
                
                # for k_ in ['1', '2']:
                #     if k_ not in cargos_info_['fixedBallastPort']:
                #         order_ = k_
                #         cargos_info_['fixedBallastPort'].append(order_)
                #         for k__, v__ in initial_ballast_.items():
                #             tank_ = k__
                #             qty_ = v__ 
                            
                #             if tank_ not in cargos_info_['ballastOperation'].keys():
                #                 cargos_info_['ballastOperation'][tank_] = [{'qty':qty_, 'order':order_}]
                #             else:
                #                 cargos_info_['ballastOperation'][tank_].append({'qty':qty_, 'order':order_})
                        
                    
                    
                
                
            
        # if len(cargos_info_['fixedBallastPort']) > 0:
        #     # fixed ballast:
        #     cargos_info_['stablePorts'] = [str(i_)  for i_ in range(1,cargos_info_['lastVirtualPort']) if str(i_) not in  cargos_info_['fixedBallastPort']]    
        
        self.info = {**self.info, **cargos_info_}     
        
        ## infeasible check
        min_cargo_ = sum([v_ for k_, v_ in cargos_info_['toLoadMin'].items()])
        if float(inputs.cargoweight) < min_cargo_- 0.1:
            inputs.error['Min Tolerance Error'] = ['Min cargo tolerance is more than loadable quantity!!']
        
    def _set_commingle_info(self, inputs, cargos_info_):
        
        cargos_info_['commingleCargo'] = {}
        for c__, c_ in enumerate(inputs.loadable_json['commingleCargo']):
            # print('Commingle cargo!!')
            c1_ = 'P'+str(c_['cargoNomination1Id'])
            c2_ = 'P'+str(c_['cargoNomination2Id'])
            
            cargos_info_['commingleCargo']['parcel1'] = c1_
            cargos_info_['commingleCargo']['parcel2'] = c2_
            t1_, t2_ = self.info['parcel'][c1_]['temperature'], self.info['parcel'][c2_]['temperature']
            
            api1_ = self.info['parcel'][c1_]['api']
            api2_ = self.info['parcel'][c2_]['api']
              
            if str(c_['purposeXid']) == str(1):
                print('Commingle cargo in auto mode!!')
                # expected_ratio_ = 0.6
                if inputs.commingle_temperature in [None]:
                    cargos_info_['commingleCargo']['temperature'] = min(t1_,t2_) + abs(t1_-t2_)*self.commingled_ratio
                else:
                    cargos_info_['commingleCargo']['temperature'] = inputs.commingle_temperature
                    
                if t1_ > t2_:
                    cargos_info_['commingleCargo']['ratio1'] = self.commingled_ratio
                    cargos_info_['commingleCargo']['ratio2'] = 1-self.commingled_ratio
                    
                else:
                    cargos_info_['commingleCargo']['ratio2'] = self.commingled_ratio
                    cargos_info_['commingleCargo']['ratio1'] = 1-self.commingled_ratio
                    
                print('approx commingle temperature:', cargos_info_['commingleCargo']['temperature'])
                print('approx ratio:', c1_, c2_, cargos_info_['commingleCargo']['ratio1'], cargos_info_['commingleCargo']['ratio2'])
                
            else:
                print('Commingle cargo in manual mode!!')
                # inputs.error.append('Commingle cargo in manual mode not supported yet!!')
                # return
                
                wt1_ = float(c_['quantity'])*float(c_['cargo1Percentage'])*0.01
                wt2_ = float(c_['quantity'])*float(c_['cargo2Percentage'])*0.01
                
                cargos_info_['commingleCargo']['temperature'] = (wt1_*t1_ + wt2_*t2_)/(wt1_ + wt2_)
                print('approx commingle temperature:', cargos_info_['commingleCargo']['temperature'])
                cargos_info_['commingleCargo']['tank'] = [d_ for d_ in c_['tankIds'].split(',')]
                cargos_info_['commingleCargo']['wt1'] = wt1_
                cargos_info_['commingleCargo']['wt2'] = wt2_
                
            cargos_info_['commingleCargo']['SG1'] = self._cal_density(api1_, cargos_info_['commingleCargo']['temperature'])
            cargos_info_['commingleCargo']['SG2'] = self._cal_density(api2_, cargos_info_['commingleCargo']['temperature'])
            
            cargos_info_['commingleCargo']['api1'] = self.info['parcel'][c1_]['api']
            cargos_info_['commingleCargo']['api2'] = self.info['parcel'][c2_]['api']
            
            cargos_info_['commingleCargo']['t1'] = self.info['parcel'][c1_]['temperature']
            cargos_info_['commingleCargo']['t2'] = self.info['parcel'][c2_]['temperature']
            cargos_info_['commingleCargo']['priority'] = str(c_['priority'])
            cargos_info_['commingleCargo']['mode'] = str(c_['purposeXid'])
            
            cargos_info_['commingleCargo']['slopOnly'] = c_.get('isSlopOnly',False)
            cargos_info_['commingleCargo']['colorCode'] = c_.get('commingleColour', None)
    
    
    
    def _create_man_operations(self, inputs):
        
        cargos_info_ = {}
        cargos_info_['cargoPort'] = {k_:[] for k_,v_ in inputs.port.info['idPortOrder'].items()}
        cargos_info_['cargoLastLoad'] = {k_:[] for k_,v_ in self.info['parcel'].items()}
        # cargos_info_['cargoRotation'] = {}
        # cargos_info_['rotationCheck'] = []
        
        for o__, o_ in enumerate(inputs.loadable_json['cargoOperation']):
            
            # port_ = str(o_['portId']) + '1'
            port_ = str(inputs.port.info['portRotationId'][str(o_['portRotationId'])])
            
            cargos_info_['cargoLastLoad']['P'+str(o_['cargoNominationId'])].append(inputs.port.info['idPortOrder'][port_])
            cargos_info_['cargoPort'][port_].append('P'+str(o_['cargoNominationId']))
            
            # if len(cargos_info_['cargoPort'][str(o_['portId'])]) > 1:
            #     if inputs.cargo_rotation:
            #         cargos_info_['cargoRotation'][str(o_['portId'])] = inputs.cargo_rotation
            #     else:
            #         cargos_info_['cargoRotation'][str(o_['portId'])] = cargos_info_['cargoPort'][str(o_['portId'])]
                
        len_virtual_ports_ = len(inputs.port.info['portOrder'])*2 # without cargo rotation
        cargos_info_['virtualArrDepPort'], cargos_info_['arrDepVirtualPort']  = {},{}
        for l_ in range(int(len_virtual_ports_/2)):
            virtual_port_ = 2*(l_)
            cargos_info_['virtualArrDepPort'][str(virtual_port_)] = str(l_+1)+'A'
            cargos_info_['virtualArrDepPort'][str(virtual_port_+1)] = str(l_+1)+'D'
            
            cargos_info_['arrDepVirtualPort'][str(l_+1)+'A'] = str(virtual_port_)
            cargos_info_['arrDepVirtualPort'][str(l_+1)+'D'] = str(virtual_port_+1)
            
        
        # sea water density ---------------------------------------------------------------------
        cargos_info_['seawaterDensity'] = {}
        for k_, v_ in cargos_info_['virtualArrDepPort'].items():
            port_name_ = inputs.port.info['portOrder'][v_[:-1]]
            cargos_info_['seawaterDensity'][k_] = inputs.port.info['portRotation'][port_name_]['seawaterDensity']
            
            
        # cargos_info_ = {}
        
        cargos_info_['commingleCargo'] = {}
        for c__, c_ in enumerate(inputs.loadable_json['commingleCargo']):
            # print('Commingle cargo!!')
            c1_ = 'P'+str(c_['cargoNomination1Id'])
            c2_ = 'P'+str(c_['cargoNomination2Id'])
            
            cargos_info_['commingleCargo']['parcel1'] = c1_
            cargos_info_['commingleCargo']['parcel2'] = c2_
            t1_, t2_ = self.info['parcel'][c1_]['temperature'], self.info['parcel'][c2_]['temperature']
            
            api1_ = self.info['parcel'][c1_]['api']
            api2_ = self.info['parcel'][c2_]['api']
            
            wt1_, wt2_ = 0. , 0. 
            for p_ in inputs.loadable_json['planDetails']:
                if p_['arrivalCondition']['loadablePlanCommingleDetails']:
                    wt1_ = float(p_['arrivalCondition']['loadablePlanCommingleDetails'][0]['cargo1QuantityMT'])
                    wt2_ = float(p_['arrivalCondition']['loadablePlanCommingleDetails'][0]['cargo2QuantityMT'])
                    cargos_info_['commingleCargo']['temperature'] = (wt1_*t1_ + wt2_*t2_)/(wt1_ + wt2_)
                    cargos_info_['commingleCargo']['wt1'] = wt1_
                    cargos_info_['commingleCargo']['wt2'] = wt2_
                    
                    
            if wt1_ == 0 or wt2_ == 0:
                print("No commingle found in plan!!")
                cargos_info_['commingleCargo']['temperature'] = min(t1_,t2_) + abs(t1_-t2_)*self.commingled_ratio
                
                    # print(p_)
            
            cargos_info_['commingleCargo']['SG1'] = self._cal_density(api1_, cargos_info_['commingleCargo']['temperature'])
            cargos_info_['commingleCargo']['SG2'] = self._cal_density(api2_, cargos_info_['commingleCargo']['temperature'])
            
            cargos_info_['commingleCargo']['api1'] = self.info['parcel'][c1_]['api']
            cargos_info_['commingleCargo']['api2'] = self.info['parcel'][c2_]['api']
            
            cargos_info_['commingleCargo']['t1'] = self.info['parcel'][c1_]['temperature']
            cargos_info_['commingleCargo']['t2'] = self.info['parcel'][c2_]['temperature']
            cargos_info_['commingleCargo']['priority'] = str(c_['priority'])
            cargos_info_['commingleCargo']['mode'] = str(c_['purposeXid'])
            
            cargos_info_['commingleCargo']['slopOnly'] = c_.get('isSlopOnly',False)
            cargos_info_['commingleCargo']['colorCode'] = c_.get('commingleColour', None)
                
        
        cargos_info_['operation'] = {k_:{}  for k_,v_ in self.info['parcel'].items()}
        cargos_info_['toLoad'] = {k_:0 for k_,v_ in self.info['parcel'].items()}
        cargos_info_['toLoadIntend']    = {k_:0 for k_,v_ in self.info['parcel'].items()}
        cargos_info_['toLoadMin'] = {k_:0 for k_,v_ in self.info['parcel'].items()}
        
        max_virtual_port_ = len(cargos_info_['virtualArrDepPort'])
        cargos_info_['lastVirtualPort'] = max_virtual_port_-1
        cargos_info_['toLoadPort'] = np.zeros(max_virtual_port_) # exact ports to virtual ports
        cargos_info_['toLoadMinPort'] = np.zeros(max_virtual_port_) # exact ports to virtual ports
        cargos_info_['cargoOrder'] = {str(p_):[] for p_ in range(1,max_virtual_port_)}
        for o__, o_ in enumerate(inputs.loadable_json['cargoOperation']):
            parcel_ = 'P'+str(o_['cargoNominationId'])
            qty__ = float(o_['quantity']) #if o_['operationId'] == 1 else -o_['quantity'] 
            
            # port_ = str(o_['portId']) + '1'
            port_ = str(inputs.port.info['portRotationId'][str(o_['portRotationId'])])
            order_ = inputs.port.info['idPortOrder'][port_]
            # max qty
            qty_ = qty__ * (1+ 0.01*self.info['parcel'][parcel_]['minMaxTol'][1])
            # min qty
            qty_min_ = qty__ *(1 + 0.01*self.info['parcel'][parcel_]['minMaxTol'][0])
            
            cargos_info_['toLoad']['P'+str(o_['cargoNominationId'])] += qty_
            cargos_info_['toLoadIntend']['P'+str(o_['cargoNominationId'])] += qty__
            cargos_info_['toLoadMin']['P'+str(o_['cargoNominationId'])] += qty_min_
            
            virtual_order_ = 2*(int(order_)-1) + 1
            # if type(virtual_port_[str(order_)]) == dict:
            #     virtual_order_ = virtual_port_[str(order_)][parcel_]
            # else:
            #     virtual_order_ = virtual_port_[str(order_)]
            
            cargos_info_['toLoadPort'][int(virtual_order_)] += qty_
            cargos_info_['toLoadMinPort'][int(virtual_order_)] += qty_min_
            cargos_info_['operation'][parcel_][virtual_order_] = qty_
            
            if qty_ > 0:
                cargos_info_['cargoOrder'][str(virtual_order_)].append(parcel_)
                
            
            ## single loading port for each cargo set the discharging qty 
            ## no discharge info
            last_discharge_port_ = max_virtual_port_-1
            if last_discharge_port_ not in cargos_info_['operation'][parcel_]:
                cargos_info_['operation'][parcel_][last_discharge_port_] = -qty_
            else:
                cargos_info_['operation'][parcel_][last_discharge_port_] += -qty_
                
            cargos_info_['toLoadPort'][int(last_discharge_port_)] += -qty_
            cargos_info_['toLoadMinPort'][int(last_discharge_port_)] += -qty_min_
            
            
        cargos_info_['toLoadPort1'] = {a__:a_ for a__, a_ in enumerate(cargos_info_['toLoadPort']) if a_ > 0} 
        cargos_info_['toLoadPort'] = np.cumsum(cargos_info_['toLoadPort'])
        cargos_info_['toLoadMinPort'] = np.cumsum(cargos_info_['toLoadMinPort'])
        cargos_info_['numParcel'] = len(self.info['parcel'])
        
        cargo_order_ = [v_ for k_,v_ in  cargos_info_['cargoOrder'].items()]
        cargo_order_ = list(itertools.chain.from_iterable(cargo_order_))
        cargos_info_['cargoOrder'] = {c_:c__+1 for c__,c_ in enumerate(cargo_order_)}
        
        
        # for k_, v_ in self.info['parcel'].items():
        #     loading_order_ = cargo_order_.index(k_) + 1
        #     self.info['parcel'][k_]['loadingOrder'] = loading_order_
        
        # cargos_info_['cargoRotation'] = {}
        # for p__, p_ in enumerate(inputs.port.info['ballastList']):
        #     cargos_ = [k_ for k_,v_ in cargos_info_['operation'].items() if v_.get(str(p_),0.) > 0.]
        #     if len(cargos_) > 1:
        #         # print(p_, cargos_)
        #         port_order_ = round(0.5*p_+0.51) # convert virtual port to exact port
        #         cargos_info_['cargoRotation'][str(port_order_)] = cargos_
        
        self._get_plan(inputs, cargos_info_)
            
        cargos_info_['manualOperation'] = {}
        for k_, v_ in inputs.loadable_json['loadingPlan'].items():
            order_ = cargos_info_['arrDepVirtualPort'][k_]
            for v__ in v_:
                parcel_ = v__['parcel']
                if parcel_ not in cargos_info_['manualOperation'].keys():
                    cargos_info_['manualOperation'][parcel_] = {}
                    
                qty_ = float(v__['wt']) 
                tank_ = v__['tankId']
                    
                if order_ not in cargos_info_['manualOperation'][parcel_].keys():
                    cargos_info_['manualOperation'][parcel_][order_] = [{'qty':qty_, 'tankId':tank_}]
                else:
                    cargos_info_['manualOperation'][parcel_][order_].append({'qty':qty_, 'tankId':tank_})
            
        cargos_info_['preloadOperation'] = {}
        
        cargos_info_['ballastOperation'] = {}
        if inputs.mode in ['FullManual']: 
            for k_, v_ in inputs.loadable_json['ballastPlan'].items():
                order_ = cargos_info_['arrDepVirtualPort'][k_]
                cargos_info_['ballastOperation'][order_] = v_
        
        cargos_info_['fixedBallastPort'] = []
        # for k_, v_ in inputs.loadable_json['ballastPlan'].items():
        #     order_ = cargos_info_['arrDepVirtualPort'][k_]
        #     cargos_info_['fixedBallastPort'].append(order_)
        #     for v__ in v_:
        #         tank_ = v__['tank']
        #         qty_ = float(v__['wt']) 
                
        #         if tank_ not in cargos_info_['ballastOperation'].keys():
        #             cargos_info_['ballastOperation'][tank_] = [{'qty':qty_, 'order':order_}]
        #         else:
        #             cargos_info_['ballastOperation'][tank_].append({'qty':qty_, 'order':order_})
            
        cargos_info_['zeroListPorts'] = []
        # if inputs.port.info['firstPortBunker']:
        #     cargos_info_['zeroListPorts'] = ['1', '2']
            
        if len(cargos_info_['fixedBallastPort']) > 0:
            # fixed ballast:
            cargos_info_['stablePorts'] = [str(i_)  for i_ in range(1,cargos_info_['lastVirtualPort']) if str(i_) not in  cargos_info_['fixedBallastPort']]    
        
        self.info = {**self.info, **cargos_info_}     
             
  
    
    def _create_discharge_operations(self, inputs):
        
        cargos_info_ = {}
        cargos_info_['cargoPort'] = {k_:{} for k_,v_ in inputs.port.info['idPortOrder'].items()}
        cargos_info_['cargoPortEmpty'] = {k_:{} for k_,v_ in inputs.port.info['idPortOrder'].items()}
        cargos_info_['blDischAmtPort'] = {k_:{} for k_,v_ in inputs.port.info['idPortOrder'].items()}
        cargos_info_['cargoRotation'] = {}
        cargos_info_['blFigure'] = {}
        
        for o__, o_ in enumerate(inputs.discharge_json['cargoNomination']):
            if o_['quantity'] not in [None]:
                cargos_info_['blFigure']['P'+str(o_['id'])] = float(o_['quantity'])
            else:
                cargos_info_['blFigure']['P'+str(o_['id'])] = float(1.0)
            
            
        ## get preloaded/ship figure
        cargos_info_['preloadOperation'] = {}
        cargos_info_['preload'] = {}
        cargos_info_['isLoadedOnTop'], cargos_info_['isSlopTank'] = {}, {}
        cargos_info_['lastLoadingPort'] = {}
        cargos_info_['minAmount'] = {}
        cargos_info_['inSlop'] = {c_:[]  for c_ in cargos_info_['blFigure']}
        cargos_info_['preCargoNominationId'] = {}
        
        arrival_plan_ = inputs.discharge_json['arrivalPlan']['loadablePlanStowageDetails']
        if inputs.discharge_json["existingDischargePlanDetails"]: 
            # new port
            arrival_plan_ = inputs.port.info['new_arrival_plan']['stowageDetails']
            for k_, v_ in inputs.discharge_json["existingDischargePlanDetails"]['cargoNominationMappings'].items():
                cargos_info_['preCargoNominationId']['P'+str(k_)] = 'P'+str(v_['dsCargoNominationId'])
                # previous cargoNominationId -> current dsCargoNominationId

        for d__, d_  in enumerate(arrival_plan_):
            wt_ = d_['quantity']
            if wt_ not in [None] and float(wt_) > 0:
                wt_ = float(wt_)
                
                if cargos_info_['preCargoNominationId']:
                    pp_ = 'P' + str(d_['cargoNominationId']) # previous cargoNomination
                    parcel_ =  cargos_info_['preCargoNominationId'][pp_] # current dsCargoNomination
                else:
                    parcel_ = self.info['dscargoNominationId']['P' + str(d_['cargoNominationId'])]

                tank_ = d_['tankId']
                cargos_info_['isLoadedOnTop'][tank_] = d_.get('isLoadedOnTop', False)
                cargos_info_['isSlopTank'][tank_] = d_.get('isSlopTank', False)
                
                ## need to convert to tankName later
                if parcel_ not in cargos_info_['preloadOperation']:
                    cargos_info_['preloadOperation'][parcel_] = {}
                    cargos_info_['minAmount'][parcel_] = 100000
                    cargos_info_['preload'][parcel_]  = 0
                    
                cargos_info_['preloadOperation'][parcel_][tank_] = round(wt_,1)
                cargos_info_['preload'][parcel_]  += round(wt_,1)
                
                if cargos_info_['minAmount'][parcel_] > wt_:
                    cargos_info_['minAmount'][parcel_] = round(wt_,1)
                    
        arrival_plan_ = inputs.discharge_json['arrivalPlan']['loadableQuantityCommingleCargoDetails']
        if inputs.discharge_json["existingDischargePlanDetails"]:
            arrival_plan_ = [] # new port
            
        for d__, d_  in enumerate(inputs.discharge_json['arrivalPlan']['loadableQuantityCommingleCargoDetails']):
            wt_ = float(d_['quantity'])
            if wt_ > 0:
                parcel_ = self.info['dscargoNominationId']['PNone']
                tank_ = d_['tankId']
                
                cargos_info_['isLoadedOnTop'][tank_] = d_.get('isLoadedOnTop', False)
                cargos_info_['isSlopTank'][tank_] = d_.get('isSlopTank', False)
                
                ## need to convert to tankName later
                if parcel_ not in cargos_info_['preloadOperation']:
                    cargos_info_['preloadOperation'][parcel_] = {}
                    cargos_info_['preload'][parcel_]  = 0
                    
                cargos_info_['preloadOperation'][parcel_][tank_] = round(wt_,1)
                cargos_info_['preload'][parcel_]  += round(wt_,1)
            
        cargos_info_['partialDischarge'] = {c_:[]  for c_ in cargos_info_['blFigure']}
        # 1 balance 2 manual 3 remaining/entire
        for o__, o_ in enumerate(inputs.discharge_json['cargoOperation']):
            # cargos_info_['cargoLastLoad']['P'+str(o_['cargoNominationId'])].append(inputs.port.info['idPortOrder'][str(o_['portId'])])
            
            # if o_['dischargingMode'] not in [2]:
            #     inputs.error['Discharging Mode Error'] = ['Only manual mode is supported now!!']
            #     return
            
            if o_['dischargingMode']  in [2] and float(o_['quantity']) == 0.:
                pass
            else:
                # port_ = str(o_['portId']) + '2'
                
                if str(o_['portRotationId']) in inputs.port.info['portRotationId']:
                    port_ = str(inputs.port.info['portRotationId'][str(o_['portRotationId'])])
                    
                    # seq_ = o_['sequenceNo']
                    
                    if o_['operationId'] == 2:
                        cargos_info_['partialDischarge']['P'+str(o_['dscargoNominationId'])].append((port_, o_['sequenceNo']))
                    
                    if o_['sequenceNo'] not in cargos_info_['cargoPort'][port_].keys():
                        cargos_info_['cargoPort'][port_][o_['sequenceNo']] = ['P'+str(o_['dscargoNominationId'])]
                    else:
                        cargos_info_['cargoPort'][port_][o_['sequenceNo']].append('P'+str(o_['dscargoNominationId']))
        
                    if port_ not in cargos_info_['cargoPortEmpty']:
                        cargos_info_['cargoPortEmpty'][port_] = {'P'+str(o_['dscargoNominationId']):o_['emptyMaxNoOfTanks']}
                        
                        if o_.get("operationId",2) in [2]:
                            cargos_info_['blDischAmtPort'][port_] = {'P'+str(o_['dscargoNominationId']): float(o_['quantity'])}
                        else:
                            cargos_info_['blDischAmtPort'][port_] = {'P'+str(o_['dscargoNominationId']): -float(o_['quantity'])}
                        
                    else:
                        cargos_info_['cargoPortEmpty'][port_]['P'+str(o_['dscargoNominationId'])] = o_['emptyMaxNoOfTanks']
                        if o_.get("operationId",2) in [2]:
                            cargos_info_['blDischAmtPort'][port_]['P'+str(o_['dscargoNominationId'])] = float(o_['quantity'])
                        else:
                            cargos_info_['blDischAmtPort'][port_]['P'+str(o_['dscargoNominationId'])] = -float(o_['quantity'])

        cargos_info_['partialDischarge1'] = {}           
        for k_, v_ in cargos_info_['partialDischarge'].items():
            cargos_info_['partialDischarge1'][k_] = True if len(v_) > 1 else False
                
        if inputs.cargo_rotation:
            # input cargo_rotation
            cargos_info_['cargoRotation'] = inputs.cargo_rotation
        else:
            cargos_info_['cargoRotation'] = cargos_info_['cargoPort']
            
        
        len_virtual_ports_ = len(inputs.port.info['portOrder'])*2 # without cargo rotation
        
        
        cargos_info_['virtualArrDepPort'], cargos_info_['arrDepVirtualPort']  = {},{}
        virtual_port_, virtual_port1_ = {}, {}
        arr_dep_virtual_port_ = {}
        max_virtual_port_ = 0
        virtual_arr_dep_ = {}
        rotation_virtual_, rotation_cargo_, rotation_portOrder_ = [], [], []
        # emtpy_tank_ = {}
        
        
        print('cargo rotation:', cargos_info_['cargoRotation'])
        
        if len(cargos_info_['cargoRotation']) >= 1:
            print('cargo rotation required')
            
            rotation_portId_ = []
            for k_ in range(1,inputs.port.info['numPort']+1):
                portId_ = inputs.port.info['portOrderId'][str(k_)]
                if portId_ in cargos_info_['cargoRotation']:
                    rotation_portId_.append(portId_)
                    
            for r__, r_ in enumerate(rotation_portId_):
                rotation_portOrder_.append(inputs.port.info['idPortOrder'][r_])
                rotation_cargo_.append(cargos_info_['cargoRotation'][r_])
                rotation_len_ = len(rotation_cargo_)
            
                # store current rotation
                # cargos_info_['rotationCheck'].append(rotation_cargo_[r__])
                len_virtual_ports_ += rotation_len_-1
            
            k__, i__, v_ = 0, 0, 0
            for k_ in range(1,inputs.port.info['numPort']+1):
                if str(k_) in  rotation_portOrder_:
                    
                    arr_dep_virtual_port_[str(k_)+'A'] = str(v_)
                    virtual_arr_dep_[str(v_)] = str(k_)+'A'
                    virtual_port_[str(k_)] = {}
                    rotation_virtual__ = []
                    for a_, b_ in rotation_cargo_[i__].items():
                        v_ += 1
                        for c_ in b_:
                            virtual_port_[str(k_)][c_] = str(v_)
                            
                            if str(v_) not in virtual_port1_:
                                virtual_port1_[str(v_)] = [c_]
                            else:
                                virtual_port1_[str(v_)].append(c_)
                                
                            
                            
                            if v_ not in rotation_virtual__:
                                rotation_virtual__.append(v_)
                    # k__ = c__
                    if len(rotation_cargo_[i__]) == 0:
                        v_ += 1
 
                    i__ += 1
                    
                    rotation_virtual_.append(rotation_virtual__)
                    arr_dep_virtual_port_[str(k_)+'D'] = str(v_)
                    virtual_arr_dep_[str(v_)] = str(k_)+'D'
                    max_virtual_port_ = v_ if v_ > max_virtual_port_ else max_virtual_port_
                    
                else:
                    exit()
                    # v_ = 2*int(k_)-1 + k__
                    # virtual_port_[str(k_)] = str(v_+1)
                    
                    # # if str(v_) not in virtual_port1_:
                    # #     virtual_port1_[str(v_)] = [c_]
                    # # else:
                    # #     virtual_port1_[str(v_)].append(c_)
                                
                    
                    
                    # arr_dep_virtual_port_[str(k_)+'A'] = str(v_)
                    # arr_dep_virtual_port_[str(k_)+'D'] = str(v_+1)
                    
                    # virtual_arr_dep_[str(v_)] = str(k_)+'A'
                    # virtual_arr_dep_[str(v_+1)] = str(k_)+'D'
                    
                    # v_ += 1
                    # max_virtual_port_ = v_ if v_ > max_virtual_port_ else max_virtual_port_
                    
                v_ += 1
                
            last_arr_ = '1A'
            for k_ in range(max_virtual_port_+1):
                arr_dep_ = virtual_arr_dep_.get(str(k_),'11NK')
                if arr_dep_ == '11NK':
                    virtual_arr_dep_[str(k_)] = str(last_arr_[:-1])+'D'
                    
                last_arr_ = arr_dep_ if arr_dep_[-1] == 'A' else last_arr_
                
            print(virtual_port_)    
            cargos_info_['virtualPort'] = virtual_port_
            cargos_info_['virtualPort1'] = virtual_port1_
            
            cargos_info_['arrDepVirtualPort'] = arr_dep_virtual_port_
            cargos_info_['virtualArrDepPort'] = virtual_arr_dep_
            cargos_info_['lastVirtualPort'] = max_virtual_port_
            cargos_info_['rotationVirtual'] = rotation_virtual_ # rotation virtual port
            # cargos_info_['rotationCargo']   = rotation_cargo_ # rotation virtual port
            cargos_info_['emptyTank'] = []
            for k_, v_ in cargos_info_['cargoPortEmpty'].items():
                order_ = inputs.port.info['idPortOrder'][k_]
                for k__, v__ in v_.items():
                    if v__ in [True]:
                        cargos_info_['emptyTank'].append((k__, virtual_port_[order_][k__]))
                        
            print('opt empty tank:', cargos_info_['emptyTank'])
            
            
        else:
            exit()
        
        cargos_info_['partialDischarge2'] = {} # to virtual port
        for k_, v_ in cargos_info_['partialDischarge'].items():
            cargos_info_['partialDischarge2'][k_] = []
            for l_ in v_:
                portOrder_ = inputs.port.info['idPortOrder'][l_[0]]
                cargos_info_['partialDischarge2'][k_].append(virtual_port_[portOrder_][k_])

        for k_, v_ in cargos_info_['partialDischarge2'].items():
            cargos_info_['partialDischarge2'][k_] = sorted(v_)
            
        
        # sea water density ---------------------------------------------------------------------
        cargos_info_['seawaterDensity'] = {}
        for k_, v_ in cargos_info_['virtualArrDepPort'].items():
            port_name_ = inputs.port.info['portOrder'][v_[:-1]]
            cargos_info_['seawaterDensity'][k_] = inputs.port.info['portRotation'][port_name_]['seawaterDensity']
                
       
        cargos_info_['operation'] = {k_:{}  for k_,v_ in self.info['parcel'].items()}
        cargos_info_['toDischarge'] = {k_:0 for k_,v_ in self.info['parcel'].items()}
        cargos_info_['mode'] = {k_:{} for k_,v_ in self.info['parcel'].items()}
        
        
        
        cargos_info_['lastVirtualPort'] = max_virtual_port_# departure of last discharge port included
        cargos_info_['toDischargePort'] = np.zeros(max_virtual_port_+1) # exact ports to virtual ports
        cargos_info_['toDischargePort2'] = []
        
        
        # assume discharging only port
        #
        for o__, o_ in enumerate(inputs.discharge_json['cargoOperation']):
            if o_['dischargingMode']  in [2] and float(o_['quantity']) == 0.:
                pass
            else:
                if str(o_['portRotationId']) in inputs.port.info['portRotationId']:
                    parcel_ = 'P'+str(o_['dscargoNominationId'])
                    qty_ = float(o_['quantity']) # bl figure
                    ship_fig_ = cargos_info_['preload'].get(parcel_, 0.0)
                    if ship_fig_ == 0.0:
                        print('backloading Cargo')
                    else:
                        qty_ = min(1.0,qty_/cargos_info_['blFigure'][parcel_])*ship_fig_
                    
                    # port_ = str(o_['portId']) + '2'
                    port_ = str(inputs.port.info['portRotationId'][str(o_['portRotationId'])])
                    order_ = inputs.port.info['idPortOrder'][port_]
                    
                    if o_.get('operationId',2) in [1]:
                        qty_ = -qty_
                        
                    print(parcel_, round(qty_,1), o_.get('operationId',2), o_['portId'], "mode:", o_['dischargingMode'])
                    cargos_info_['toDischarge'][parcel_] += round(qty_,1)
                    
                    if virtual_port_.get(str(order_), {}):
                        virtual_order_ = virtual_port_[str(order_)][parcel_]
                    else:
                        virtual_order_ = 2*(int(order_)-1) + 1
                   
                    if virtual_order_ not in  cargos_info_['toDischargePort2']:
                        cargos_info_['toDischargePort2'].append(int(virtual_order_))
                    cargos_info_['toDischargePort'][int(virtual_order_)] -= ceil(qty_ *10)/10 #round(qty_,1)
                    cargos_info_['operation'][parcel_][virtual_order_] = -ceil(qty_ *10)/10 #round(qty_,1)
                    if o_['dischargingMode'] not in [1] and qty_ > 0:
                        cargos_info_['mode'][parcel_][virtual_order_] = 2
                    else:
                        cargos_info_['mode'][parcel_][virtual_order_] = o_['dischargingMode']
            
        cargos_info_['numParcel'] = len(self.info['parcel'])
        cargos_info_['toDischargePort1'] = {a__: round(a_,1) for a__, a_ in enumerate(cargos_info_['toDischargePort']) if a_ < 0} 
        cargos_info_['toDischargePort'] = np.cumsum(cargos_info_['toDischargePort'])
        
        cargos_info_['manualOperation'] = {}
        
        cargos_info_['ballastOperation'] = {}
        cargos_info_['initialBallast'] = {}

        arrival_ballast_ = inputs.discharge_json['arrivalPlan']['loadablePlanBallastDetails']
        if inputs.discharge_json["existingDischargePlanDetails"]:
            arrival_ballast_ = inputs.port.info['new_arrival_plan']['ballastDetails']

        for d__, d_  in enumerate(arrival_ballast_):
            wt_ = float(d_['quantity'])
            tank_ = d_['tankId']
            cargos_info_['initialBallast'][tank_] = wt_
        
        
        
        self.info = {**self.info, **cargos_info_}         
        
    
    def _cal_density(self, api, temperature_F):
        
        # temperature = ((temperature_F - 32)*5/9*100+0.5)/100
        # temperature = (temperature_F - 32)/1.8
        # # temp_F_ = round(temperature*1.8+32,1)
        
        # if 10 <= api < 18.4:
        #     density15c = 141500/(api+131.5) - 0.55
        # elif 18.4 <= api < 31.9:
        #     density15c = 141500/(api+131.5) - 0.505
        # elif 31.9 <= api < 45.3:
        #     density15c = 141500/(api+131.5) - 0.44
        # elif 45.3 <= api < 57.6:
        #     density15c = 141500/(api+131.5) - 0.27
        # elif 57.6 <= api < 80.6:
        #     density15c = 141500/(api+131.5) - 0.16
        # elif 80.6 <= api < 85:
        #     density15c = 141500/(api+131.5) - 0.1
        # else:
        #     density15c = None
            
        # density_15C_ = density15c/1000
            
        # # density_15C_ = 141.5/(api+0.08775+131.5)
            
        # vcf_ = np.exp(-(613.97231/(density_15C_*1000)**2)*(temperature-15.0)*(1.0+(0.8*(613.97231/(density_15C_*1000)**2)*(temperature-15.0))))
        
        # # density@15C in air == density_15C_-0.0011
        # density = (density_15C_-0.0011)*vcf_  # 
        
        
        ## https://www.myseatime.com/blog/detail/cargo-calculations-on-tankers-astm-tables
    
        a60 = 341.0957/(141360.198/(api+131.5))**2
        dt = temperature_F-60
        vcf_ = np.exp(-a60*dt*(1+0.8*a60*dt))
        t13_ = (535.1911/(api+131.5)-0.0046189)*0.42/10
        density = t13_*vcf_*6.2898
        
    
        return round(density,6)
    
    def _get_plan(self,inputs, cargos_info):
        
        onboard_json = inputs.vessel_json['onBoard']
        # onboard_json = [{"id": 29632,"portId": 1,"tankId": 25580,
        #                  "cargoId": None,
        #                  "volume": "100",
        #                  "plannedArrivalWeight": "100.0000"
        #                  }]
        
        onBoard = {}
        for o__, o_ in enumerate(onboard_json):
            tank_ = o_['tankId']
            # port_order_ = '1A'
            
            # print(o_)
            wt_ = float(o_['plannedArrivalWeight']) if o_['plannedArrivalWeight'] not in [None] else 0.
            vol1_ = float(o_['volume']) if o_['volume'] not in [None] else 0.
            if wt_ > 0. and vol1_ > 0.:
                onBoard[tank_] = wt_
                
                 
        loading_plan_, ballast_plan_ = {},{}
        
        plan_ = []
        
        for k_, v_ in inputs.port.info['portRotationId'].items():
            
            info_ = []
            for q__, q_ in enumerate(inputs.loadable_json['planDetails']):
                if k_ == str(q_['portRotationId']):
                    info_.append(q_)
                    
            plan_.append(info_[0])
        
        tank_cargo_ = {}
        for p__, p_ in enumerate(plan_):
            port_ = str(p__+1) # for each port
            # print(port_)
            # arrival and departure 
            arr_port_ = port_ + 'A'
            dep_port_ = port_ + 'D'
            # print(arr_port_,dep_port_)
            loading_plan_[dep_port_] = []
            ballast_plan_[arr_port_] = []
            ballast_plan_[dep_port_] = []
            
            # only ballast
            arr_ballast_ = p_['arrivalCondition']['loadablePlanBallastDetails']
            # both ballast and cargo
            dep_ballast = p_['departureCondition']['loadablePlanBallastDetails'] if p__+1 <= inputs.port.info['lastLoadingPort'] else []
            dep_cargo__  = p_['departureCondition']['loadablePlanStowageDetails'] if p__+1 <= inputs.port.info['lastLoadingPort'] else []
            dep_commingle_ =  p_['departureCondition'].get('loadablePlanCommingleDetails',[]) if p__+1 <= inputs.port.info['lastLoadingPort'] else []
            
            
            dep_cargo_ = [d_ for d_ in dep_cargo__ if float(d_['quantityMT']) > 0.]
            
            for l__, l_ in enumerate(arr_ballast_):
                tankId_ = l_['tankId']
                info_ = {}
                info_['wt'] = float(l_['quantityMT'])
                info_['tankId'] = tankId_
                ballast_plan_[arr_port_].append(info_)
                
                
            for l__, l_ in enumerate(dep_ballast):
                tankId_ = l_['tankId']
                info_ = {}
                info_['wt'] = float(l_['quantityMT'])
                info_['tankId'] = tankId_
                ballast_plan_[dep_port_].append(info_)
                
            
            for l__, l_ in enumerate(dep_commingle_):
                # print(l_)
                tankId_ = l_['tankId']
                if tankId_ not in tank_cargo_:
                    tank_cargo_[tankId_] = []
                
                for c_ in range(2):
                    # parcel_ = 'P'+str(l_['cargoNomination'+ str(c_+1)+'Id'])
                    parcel_ = 'P'+str(l_['cargo'+ str(c_+1)+'NominationId'])
                    info_ = {}
                    info_['parcel'] = parcel_
                    info_['wt'] = float(l_['cargo'+str(c_+1)+'QuantityMT'])
                    info_['tankId'] = tankId_
                    info_['port'] = dep_port_
                    onboard_ = onBoard.get(tankId_,0.)
                    
                    if len(tank_cargo_[tankId_]) == 0:
                        tank_cargo_[tankId_].append(info_)
                        loading_plan_[dep_port_].append(info_)
                        
                    elif len([tc_ for tc_ in tank_cargo_[tankId_] if tc_['parcel'] == parcel_]) == 0:
                        tank_cargo_[tankId_].append(info_)
                        loading_plan_[dep_port_].append(info_)
                        
                    else:
                        total_wt_ = sum([0.]+[i_['wt']  for i_ in tank_cargo_[tankId_] if i_['parcel'] == parcel_])
                        add_wt_ = info_['wt'] -  total_wt_ - onboard_
                        if add_wt_ > 0:
                            print('add wt', tankId_)
                            info_['wt'] = round(add_wt_,3)
                            tank_cargo_[tankId_].append(info_)
                            loading_plan_[dep_port_].append(info_)
                            
                        elif add_wt_ < 0:
                            print('reduce wt', tankId_)
                            if int(p__+1) > int(max(cargos_info['cargoLastLoad'][parcel_])) :
                                last_port_ = max(cargos_info['cargoLastLoad'][parcel_])
                            else:
                                cargos_info['cargoLastLoad'][parcel_].sort()
                                last_port_ = cargos_info['cargoLastLoad'][parcel_][-2]
                                
                            pre_wt_ = [i_['wt']  for i_ in tank_cargo_[tankId_] if i_['parcel'] == parcel_ and i_['port'] == last_port_ +'D']
                            new_load_ = pre_wt_[0] + add_wt_
                            if new_load_ > 0:
                                info1_ = {'parcel':parcel_, 'wt':pre_wt_[0], 'tankId':tankId_, 'port':last_port_ +'D'}
                                loading_plan_[last_port_+'D'].remove(info1_)
                                tank_cargo_[tankId_].remove(info1_)
                                
                                info1_['wt'] = new_load_
                                loading_plan_[last_port_+'D'].append(info1_)
                                tank_cargo_[tankId_].append(info1_)
                            else:
                                inputs.error.append('Error in adjusting manual allocation!!')
                            
                    
                            
            
            for l__, l_ in enumerate(dep_cargo_):
                # parcel_ = l_['parcelId']
                tankId_ = l_['tankId']
                if tankId_ not in tank_cargo_:
                    tank_cargo_[tankId_] = []
                    
                parcel_ = 'P'+str(l_['cargoNominationId'])
                
                if str(l_['cargoNominationId']) not in ['']:
                    info_ = {}
                    info_['parcel'] = 'P'+ str(l_['cargoNominationId'])
                    info_['wt'] = float(l_['quantityMT'])
                    info_['tankId'] = tankId_
                    info_['port'] = dep_port_
                    onboard_ = onBoard.get(tankId_,0.)
                    
                    if onboard_ > 0:
                        print(tankId_,onboard_)
                    
                    # print(info_,l_)
                    if len(tank_cargo_[tankId_]) == 0:
                        info_['wt'] -= onboard_                        
                        tank_cargo_[tankId_].append(info_)
                        loading_plan_[dep_port_].append(info_)
                        
                    else:
                        # print('repeat cargo_tank')
                        # without onboard
                        total_wt_ = sum([0.]+[i_['wt']  for i_ in tank_cargo_[tankId_] if i_['parcel'] == parcel_])
                        add_wt_ = info_['wt'] -  total_wt_ - onboard_
                        if add_wt_ > 0:
                            # print('add wt', tankId_)
                            # info_['wt'] = round(add_wt_,3)
                            # tank_cargo_[tankId_].append(info_)
                            # loading_plan_[dep_port_].append(info_)
                            
                            ## one loading port only
                            last_port_ = str(int(info_['port'][:-1])-1)
                            pre_wt_ = [i_['wt']  for i_ in tank_cargo_[tankId_] if i_['parcel'] == parcel_ and i_['port'] == last_port_ +'D']
                            new_load_ = pre_wt_[0] + add_wt_
                            if new_load_ > 0:
                                info1_ = {'parcel':parcel_, 'wt':pre_wt_[0], 'tankId':tankId_, 'port':last_port_ +'D'}
                                loading_plan_[last_port_+'D'].remove(info1_)
                                tank_cargo_[tankId_].remove(info1_)
                                
                                info1_['wt'] = new_load_
                                loading_plan_[last_port_+'D'].append(info1_)
                                tank_cargo_[tankId_].append(info1_)
                            else:
                                inputs.error.append('Error in adjusting manual allocation!!')
                            
                            
                        elif add_wt_ < 0:
                            # print('reduce wt', tankId_)
                            if int(p__+1) > int(max(cargos_info['cargoLastLoad'][parcel_])) :
                                last_port_ = max(cargos_info['cargoLastLoad'][parcel_])
                            else:
                                cargos_info['cargoLastLoad'][parcel_].sort()
                                last_port_ = cargos_info['cargoLastLoad'][parcel_][-2]
                                
                            pre_wt_ = [i_['wt']  for i_ in tank_cargo_[tankId_] if i_['parcel'] == parcel_ and i_['port'] == last_port_ +'D']
                            new_load_ = pre_wt_[0] + add_wt_
                            if new_load_ > 0:
                                info1_ = {'parcel':parcel_, 'wt':pre_wt_[0], 'tankId':tankId_, 'port':last_port_ +'D'}
                                loading_plan_[last_port_+'D'].remove(info1_)
                                tank_cargo_[tankId_].remove(info1_)
                                
                                info1_['wt'] = new_load_
                                loading_plan_[last_port_+'D'].append(info1_)
                                tank_cargo_[tankId_].append(info1_)
                            else:
                                inputs.error.append('Error in adjusting manual allocation!!')
                            
                    
                # if l_ not in tank_cargo_[]
             
        inputs.loadable_json['loadingPlan'] = loading_plan_
        inputs.loadable_json['ballastPlan'] = ballast_plan_
    
    
        # return loading_plan_,  ballast_plan_
    def _get_COW(self,inputs):
        
        cow_history_ = inputs.discharge_json['cowHistory']
        
        # if cow_history_ not in [None]:
        #     dateList_ = [l_["voyageEndDate"] for l_ in cow_history_]
        #     tanks_ = [inputs.vessel.info['tankId'][l_["tankId"]] for l_ in cow_history_]
        #     ind_ = sorted(range(len(dateList_)), key = dateList_.__getitem__)
        
        # else:
        #     dateList_,tanks_,ind_ = [], [], []
        
        
        self.info['toCow'] = ['3C']
        available_tanks_ = ['1', '1C', '2', '2C', '3', '4', '4C', '5', '5C'] + inputs.vessel.info['slopTank']
        
        # for i_ in range(len(ind_)):
        #     t_ = tanks_[ind_[i_]]
        #     if t_[-1] in ['C'] or t_ in inputs.vessel.info['slopTank']:
        #         pass
        #     else:
        #         t_ = t_[0]
        #     if t_ in available_tanks_:    
        #         available_tanks_.remove(t_)
            
        # print(available_tanks_)
        percent_ = inputs.discharge_json.get('cowDetails', {}).get('percentage', 100)
        mode_ = inputs.discharge_json.get('cowDetails', {}).get('type', -1)
        
        if percent_ not in [100] and mode_ == 1:
            inputs.error['Cow Error'] = ['Less than 100% COW not tested yet!!']
        
        if mode_ == 1:
            ## auto mode
            num_ = 1
            while num_ <= 16:
                t_ = available_tanks_.pop(0)
                if t_[-1] in ['C'] or t_ in inputs.vessel.info['slopTank']:
                    t_ = [t_]
                    num_ += 1
                else:
                    t_ = [t_+'P', t_+'S']
                    num_ += 2
                    
                self.info['toCow'] += t_
        elif mode_ == 2:
            tanks_ = inputs.discharge_json.get('cowDetails', {}).get('tanks', "")
            
            for t_ in tanks_.split(','):
                if t_ not in self.info['toCow'] + [""]:
                    self.info['toCow'].append(t_)
                    
            
            
        print('toCow: ',self.info['toCow'])
                
            
        
        
        
        
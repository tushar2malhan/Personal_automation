# -*- coding: utf-8 -*-
"""
Created on Thu Jul 15 10:48:53 2021

@author: I2R
"""
import pandas as pd
import numpy as np
from copy import deepcopy


## virtual ports
# DENSITY = {'DSWP':1.0, 'DWP':1.0, 'FWS':1.0, 'DSWS':1.0,
#            'FO2P':0.98, 'FO2S':0.98, 'FO1P':0.98, 'FO1S':0.98, 'BFOSV':0.98, 'FOST':0.98, 'FOSV':0.98,
#            'DO1S':0.88,  'DO2S':0.88, 'DOSV1':0.88, 'DOSV2':0.88}

# INDEX = ['Time','SLS', 'SLP', '5W', '5C', '4W', '4C', '2W', '2C','1W','1C','3W','3C']
# INDEX1 = ['LFPT', 'WB1P', 'WB1S', 'WB2P', 'WB2S', 'WB3P', 'WB3S', 'WB4P', 'WB4S', 'WB5P', 'WB5S', 'AWBP', 'AWBS', 'APT']
# OPEN_TANKS = ['3C', '2C', '4C', '5C', '1C', '3W', '4W', '2W', '5W', '1W' ]
# OPEN_TANKS = ['1C', '1W', '2C', '2W', '3C','3W', '4C', '4W', '5C', '5W' , 'SLP', 'SLS']
OPEN_TANKS = ['1C', '1W', '2C', '2W', '3C','3W', '4C', '4W', '5C', '5W' ]



#1C, 1W, 2C, 2W, 3C, 3W, 4C, 4W, 5C and 5W
DEC_PLACE = 10

# TIME_EDUCTING = 60*3
        
class LoadingOperations(object):
    # 
    def __init__(self, data):
        
        self.error = {}
        
        self.first_loading_port = data.first_loading_port
        self.ballast_color, self.rob_color = {}, {}
        self.vessel = data.vessel
        self.initial_delay = data.initial_delay
        self.time_interval1 = data.loading_info_json['loadingStages']['stageDuration']*60 # in 60*4 min
        # self.time_interval1 = 2*60 # in 60*4 min
        
        self.num_stage_interval = data.loading_info_json['loadingStages']['stageOffset']
        self.time_interval = {}
        
        self.config = data.config
        self.eduction_pump, self.ballast_pump = [], []
        self.manifold_port = True
        print('time interval:', self.time_interval1)
        
        
        manifolds_, bottomLines_ =  [], []
        for d__, d_ in enumerate(data.loading_info_json['loadingMachinesInUses']):
            if d_['machineName'][:3] in ['Man']:
                manifolds_.append(int(d_['machineName'][-1]))
                if d_['tankTypeName'] not in ['Port']:
                    self.manifold_port = True
        
            elif d_['machineName'][:3] in ['Bot']:
                bottomLines_.append(int(d_['machineName'][-1]))
            elif d_['machineName'][:15] in ['Ballast Eductor']:
                self.eduction_pump.append(d_['machineName'])
            elif d_['machineName'][:2] in ['BP']:
                self.ballast_pump.append(d_['machineName'])
                
            
            
                
        # pump in use

        if len(manifolds_) == 0:
            manifolds_ = [2,3]
            
        if len(bottomLines_) == 0:
            bottomLines_ = [2,3]
            
        
        self.load_param = {'Manifolds':manifolds_,
                     'centreTank':[],
                     'wingTank': [],
                     'slopTank': [],
                     'BottomLines': bottomLines_
                    }
        
        shoreLoadingRate_ = data.loading_info_json['loadingRates'].get('shoreLoadingRate',1e6)
        shoreLoadingRate_ = shoreLoadingRate_ if shoreLoadingRate_ not in [None] else 1e6
        
        loading_rate_ = min(data.loading_info_json['loadingRates'].get('maxLoadingRate', 7000), shoreLoadingRate_)
        # loading_rate_ = 5000
        self.max_loading_rate = loading_rate_
        print('loading rate (max):', loading_rate_)
        min_loading_rate_ = data.loading_info_json['loadingRates']['minLoadingRate']
        min_loading_rate_ = min_loading_rate_ if min_loading_rate_ not in [None, ""] else 1000.
        print('loading rate (min):', min_loading_rate_)
        
        self.max_ballast_rate = data.loading_info_json['loadingRates'].get('maxDeBallastingRate',7000.)*1.025
        # self.max_ballast_rate = 7000.
        print('max ballast:', round(self.max_ballast_rate,2))
        
        self.staggering_param = {'maxShoreRate': loading_rate_, ####  11129
                                 'minLoadingRate': min_loading_rate_,
                                 'wingTank': 2*self.vessel.info['loadingRate6']['WingTankBranchLine'], # 7900
                                 'centerTank': self.vessel.info['loadingRate6']['CentreTankBranchLine'], #5790,
                                 'slopTank': self.vessel.info['loadingRate6']['SlopTankBranchLine'], #3435,
                                 'toppingSeq':[]}
        
        seawater_density_ =  data.port_json['portDetails'][0]['seawaterDensity']
        if seawater_density_ not in [None, ""]:
            self.seawater_density = float(data.port_json['portDetails'][0]['seawaterDensity'])
        else:
            self.seawater_density = 1.025
        
        self.preloaded_cargos, self.to_load_cargos = [], []
        self.commingle_loading, self.commingle_preloaded = False, False
        
         
        cargo_info_ = {}
        
        # get CargoId
        cargo_info_['cargoId'] = {'P'+str(l_['cargoNominationId']): l_['cargoId']  for l_ in data.loading_info_json["loadableQuantityCargoDetails"]}
        
        # initial and final ROB
        self._get_rob(data.vessel_json['onHand'], cargo_info_)
                
        cargo_info_['cargoTanksUsed'], cargo_info_['ballastTanksUsed'] = [], []
        # initial Ballast, final Ballast
        cargo_info_['ballast'] = []
        self._get_ballast(data.loadable_json['planDetails']['arrivalCondition']['loadablePlanBallastDetails'], cargo_info_)
        self._get_ballast(data.loadable_json['planDetails']['departureCondition']['loadablePlanBallastDetails'], cargo_info_)
        self._get_eduction(cargo_info_)
        
        deballastAmt_ = 0
        for t_ in cargo_info_['tankToDeballast']:
            ini_ = cargo_info_['ballast'][0].get(t_,[{}])[0].get('quantityM3', 0)
            fin_ = cargo_info_['ballast'][1].get(t_,[{}])[0].get('quantityM3', 0)
            deballastAmt_ += (ini_-fin_)
            
        cargo_info_['deballastAmt'] = round(deballastAmt_,2)
        tank_ = [t_ for t_ in cargo_info_['tankToDeballast'] if t_[0] == 'W' ]
        # self.num_pump = 1 if (len(cargo_info_['tankToBallast']) + len(cargo_info_['tankToDeballast']) <= 4) else 2
        self.num_pump = 1 if (len(tank_) <= 4) else 2
        print('num ballast pump:', self.num_pump)
        
        
        
        # for d_ in data.loadable_json['planDetails']['departureCondition']['loadablePlanBallastDetails']:
        #     type_, tank_, wt_ = 'Ballast', d_['tankId'], d_['quantityMT']
        #     tankName_ = data.vessel.info['tankId'][tank_]
        #     if wt_ not in [None, 0.]:
        #         cargo_info_['finalBallast'][(type_,tankName_)] = wt_
            
        # cargo_info_['loading_order'] = ['P'+str(d_['cargoNominationId']) for d_ in data.loading_info_json['loadingSequences']['loadingDelays'] if d_['cargoNominationId'] not in [0]]
        
        # for the whole voyage
        # cargo_info_['loading_order1'] = {'P'+str(d_['cargoNominationId']): d_['loadingOrder']  for d_ in data.loading_info_json['loadableQuantityCargoDetails']}
        cargo_info_['loading_order1'], order_ = {}, 1
        cargo_info_['timing_delay2'] = {}
        cargo_info_['loading_rate'] = {}
        for d_ in data.loading_info_json['loadingSequences']['loadingDelays']:
            if d_['cargoNominationId'] in [0]:
                pass
            else:
                cargo_ = 'P'+str(d_['cargoNominationId'])
                cargo_info_['loading_order1'][cargo_] = order_
                cargo_info_['timing_delay2'][order_] = d_['duration'] # dict for each cargo
                cargo_info_['loading_rate'][cargo_] = d_.get('loadingRate', 5000)
                order_ += 1
                        
        # cargo_info_['timing_delay1'] = [0 for d_ in range(len(cargo_info_['loading_order1']))]
        # # cumsum  60: initial delay, 120: cargo 1, 180: cargo 2
        # # cargo_info_['timing_delay1'] = [180, 180]
        # for d_ in data.loading_info_json['loadingSequences']['loadingDelays']:
        #     if d_['cargoNominationId'] in [0]:
        #         cargo_info_['timing_delay1'][0] +=  d_['duration']
        #     else:
        #         o_ = cargo_info_['loading_order1']['P'+str(d_['cargoNominationId'])]-1
        #         cargo_info_['timing_delay1'][o_] += d_['duration']
                
        # cargo_info_['loading_order1'] = {'P17338': 1, 'P17339': 2}               
            
        
        # add plans -------------------------------------------------------------------------
        cargo_info_['cargo_plans'] = []
        cargo_info_['cargo_tank'] = {}
        cargo_info_['density'], cargo_info_['api'], cargo_info_['temperature'] = {}, {}, {}
        cargo_info_['colorCode'], cargo_info_['abbreviation'] = {}, {}
        cargo_info_['commingle'] = {}
        
        # initial plan
        self._get_plan(data.loadable_json['planDetails']['arrivalCondition']['loadablePlanStowageDetails'],
                       cargo_info_, data.loading_info_json['loadableQuantityCargoDetails'], 
                       commingleDetails = data.loadable_json['planDetails']['arrivalCondition']['loadablePlanCommingleDetails'],
                       initial = True)
        
        
        cargo_info_['pre_cargo'] = [k_ for k_,v_ in cargo_info_['cargo_tank'].items()]
        cargo_info_['loading_order'] = [-1 for d_ in range(len(cargo_info_['loading_order1']))]
        # cargo_info_['timing_delay'] = [-1 for d_ in range(len(cargo_info_['loading_order1']))]
        for k_, v_ in cargo_info_['loading_order1'].items():
            if k_ not in cargo_info_['pre_cargo']:
                cargo_info_['loading_order'][v_-1] = k_
                # cargo_info_['timing_delay'][v_-1] = cargo_info_['timing_delay1'][v_-1]
        
        # remove -1; info only for current loading in this port
        # cargo_info_['loading_order'] = ['P17338', 'P17339']
        # cargo_info_['timing_delay'] = cargo_info_['timing_delay1']
        cargo_info_['loading_order'] = [d_ for d_ in cargo_info_['loading_order'] if d_ not in [-1]]
        # cargo_info_['timing_delay'] = [d_ for d_ in cargo_info_['timing_delay'] if d_ not in [-1]]
        
       
        # cargo_info_['loading_order'] = ['A','B','C','D']
        for o__,o_ in enumerate(cargo_info_['loading_order'][:-1]):
            
            not_cargo_ = cargo_info_['loading_order'][o__+1:]
            # print(not_cargo_)
            self._get_plan(data.loadable_json['planDetails']['departureCondition']['loadablePlanStowageDetails'],
                       cargo_info_, data.loading_info_json['loadableQuantityCargoDetails'], 
                       commingleDetails = data.loadable_json['planDetails']['departureCondition']['loadablePlanCommingleDetails'],
                       initial = False, not_cargo = not_cargo_)
                    
            
        # final plan 
        self._get_plan(data.loadable_json['planDetails']['departureCondition']['loadablePlanStowageDetails'],
                       cargo_info_, data.loading_info_json['loadableQuantityCargoDetails'], 
                       commingleDetails = data.loadable_json['planDetails']['departureCondition']['loadablePlanCommingleDetails'],
                       initial = False)
        
        cargo_info_['fillingRatio'] = {}
        for o_ in range(1,6):
           
            if cargo_info_['cargo_plans'][-1].get(str(o_)+'P', []):
                wt1_ = cargo_info_['cargo_plans'][-1][str(o_)+'P'][0]['quantityMT']
                wt2_ = cargo_info_['cargo_plans'][-1][str(o_)+'S'][0]['quantityMT']
            
                cargo_info_['fillingRatio'][str(o_)+'W'] = wt1_/wt2_
            
        print('fillingRatio:', cargo_info_['fillingRatio'])
        cargo_info_['loading_amt'] = {'tot': 0.}
        for c_ in cargo_info_['loading_order']:
            cargo_info_['loading_amt'][c_] = 0.
            for k_, v_ in cargo_info_['cargo_plans'][-1].items():
                if len(v_) == 2:
                    if v_[0]['cargo'] == c_:
                        cargo_info_['loading_amt'][c_] += v_[0]['quantityM3']
                        cargo_info_['loading_amt']['tot'] += v_[0]['quantityM3']
                    elif v_[1]['cargo'] == c_:
                        cargo_info_['loading_amt'][c_] += v_[1]['quantityM3']
                        cargo_info_['loading_amt']['tot'] += v_[1]['quantityM3']
                    
                else:
                    if v_[0]['cargo'] == c_:
                        cargo_info_['loading_amt'][c_] += v_[0]['quantityM3']
                        cargo_info_['loading_amt']['tot'] += v_[0]['quantityM3']
        
        
        init_time_ = 0 if not self.first_loading_port else 2
        ballast_time_ = deballastAmt_/self.num_pump/3500
        eduction_time_ = 2 if cargo_info_['eduction'] else 0
        topping_time_ = 2
        tot_time_ = init_time_ + ballast_time_ + eduction_time_ + topping_time_
        avail_rate_ = cargo_info_['loading_amt']['tot']/tot_time_
        
        # print(init_time_, round(ballast_time_), eduction_time_, topping_time_ )
        print("avail_rate:", round(avail_rate_,2), init_time_, round(ballast_time_), eduction_time_, topping_time_)
       
        self.info = cargo_info_
        
        # print('total wt_', total_wt_)
        # data.error['Input Error'] = ['Error']
    
    def _get_rob(self, onhand, cargo_info_):
        
        DENSITY = self.config['rob_density']
        
        plan_i_, plan_f_ = {}, {}
        for o__,o_ in enumerate(onhand):
            # print(o_['tankName'])
            tankName_ = o_['tankName']
            
            tcg_data_ = self.vessel.info['tankTCG']['tcg'][tankName_] # tcg_data
            lcg_data_ = self.vessel.info['tankLCG']['lcg'][tankName_] # lcg_data
            color_ = o_.get('colorCode', None)
            
            self.rob_color[tankName_] = color_
                
            if o_['arrivalQuantity'] > 0:
                
                wt_ =  o_['arrivalQuantity']
                vol_ = float(wt_)/DENSITY[tankName_]
                
                tcg_ = np.interp(vol_, tcg_data_['vol'], tcg_data_['tcg'])
                lcg_ = np.interp(vol_, lcg_data_['vol'], lcg_data_['lcg'])
                
                tank_ = self.vessel.info['tankName'][tankName_]
                
                plan_i_[tankName_] =  [{'quantityMT': float(wt_), 
                                'quantityM3': vol_,
                                'tankId':tank_,
                                'tcg':tcg_, 'lcg':lcg_, 'colorCode':color_}]
                
                
            if o_['departureQuantity'] > 0:
                wt_ =  o_['departureQuantity']
                vol_ = float(o_['departureQuantity'])/DENSITY[tankName_]
                
                tcg_ = np.interp(vol_, tcg_data_['vol'], tcg_data_['tcg'])
                lcg_ = np.interp(vol_, lcg_data_['vol'], lcg_data_['lcg'])
                
                tank_ = self.vessel.info['tankName'][tankName_]
                
                plan_f_[tankName_] =  [{'quantityMT': float(wt_), 
                                'quantityM3': vol_,
                                'tankId':tank_,
                                'tcg':tcg_, 'lcg':lcg_, 'colorCode':color_}]
                
        cargo_info_['ROB'] = [plan_i_, plan_f_]
    
    def _get_eduction(self, cargo_info_):

        cargo_info_['tankToBallast'] = []
        cargo_info_['tankToDeballast'] = []
        cargo_info_['eduction'] = []
        
        for k_, v_ in cargo_info_['ballast'][0].items():
            initial_ = v_[0]['quantityMT']
            final_ = cargo_info_['ballast'][1].get(k_, [{'quantityMT':0.}])[0]['quantityMT']
            # print(initial_,  final_, k_)
            if initial_ - final_ > 0. and k_ not in cargo_info_['tankToDeballast']:
                # print('tankToDeballast', initial_,  final_, k_)
                cargo_info_['tankToDeballast'].append(k_)
                if final_ == 0.:
                    cargo_info_['eduction'].append(k_)
                    
            elif initial_ - final_ < 0. and k_ not in cargo_info_['tankToBallast']:
                # print('tankToBallast', initial_,  final_, k_)
                cargo_info_['tankToBallast'].append(k_)
                
        for k_, v_ in cargo_info_['ballast'][1].items():
            final_ = v_[0]['quantityMT']
            initial_ = cargo_info_['ballast'][0].get(k_, [{'quantityMT':0.}])[0]['quantityMT']
            # print(initial_,  final_, k_)
            if initial_ - final_ > 0. and k_ not in cargo_info_['tankToDeballast']:
                # print('tankToDeballast', initial_,  final_, k_)
                cargo_info_['tankToDeballast'].append(k_)
            elif initial_ - final_ < 0. and k_ not in cargo_info_['tankToBallast']:
                # print('tankToBallast', initial_,  final_, k_)
                cargo_info_['tankToBallast'].append(k_)
                
                
        cargo_info_['numEductionTanks'] = sum([1 for e_ in cargo_info_['eduction']  if e_ not in ['FPT', 'LFPT'] ])
        print('tankToBallast: ', cargo_info_['tankToBallast'])
        print('tankToDeballast: ', cargo_info_['tankToDeballast'])
        print('eduction: ', cargo_info_['eduction'], cargo_info_['numEductionTanks'])
        
        if cargo_info_['numEductionTanks'] > 0:
            self.time_eduction = int(60 + 12*cargo_info_['numEductionTanks'])
        else:
            self.time_eduction = 0
        # self.time_eduction = 0
        print('eduction duration: ', self.time_eduction)
        
        
                
        
    
    
    def _get_ballast(self, ballast, cargo_info_):
        
        density_ = 1.025 #  ballast density
        # density_ = self.seawater_density
        plan_ = {}
        for d_ in ballast:
            tank_, wt_ = d_['tankId'], d_['quantityMT']
            tankName_ = self.vessel.info['tankId'][tank_]
            color_ = d_.get('colorCode', None)
            self.default_ballast_color = color_       
            
            if tankName_ not in cargo_info_['ballastTanksUsed'] and tankName_ not in self.vessel.info['banBallast']:
                cargo_info_['ballastTanksUsed'].append(tankName_)
                # print(tankName_)
                
            
            self.ballast_color[tankName_] = color_
            
            if wt_ not in [None, '0', 'null']:
               vol_ = float(wt_)/density_
               
               tcg_data_ = self.vessel.info['tankTCG']['tcg'][tankName_] # tcg_data
               lcg_data_ = self.vessel.info['tankLCG']['lcg'][tankName_] # lcg_data
                
               tcg_ = np.interp(vol_, tcg_data_['vol'], tcg_data_['tcg'])
               lcg_ = np.interp(vol_, lcg_data_['vol'], lcg_data_['lcg'])
                
               tank_ = self.vessel.info['tankName'][tankName_]
               
                
               plan_[tankName_] =  [{'quantityMT': float(wt_), 
                                     'quantityM3': vol_,
                                'tankId':tank_,
                                'tcg':tcg_, 'lcg':lcg_,'density':density_, 'colorCode':color_}]
        
        cargo_info_['ballast'].append(plan_)
                
                
                
        
    def _get_plan(self, stowageDetails, cargo_info_, cargoDetails, commingleDetails = [], initial = True, not_cargo = []):
        
        plan_ = {}
        for d_ in stowageDetails:
            
            
            if not d_.get('cargoNominationId', None):
                continue
            elif 'P'+str(d_['cargoNominationId']) in not_cargo:
                continue
            
            self._get_plan1(d_["cargoNominationId"], d_["tankId"], d_["quantityMT"], 
                            d_.get('cargoId',None), d_.get('colorCode',None), d_.get('abbreviation',None),
                            plan_, cargo_info_, cargoDetails, initial)
            
        for d_ in commingleDetails:
            
            if initial:
                self.commingle_preloaded = True 
            else:
                self.commingle_loading = True
            
            self._get_plan2(d_, plan_, cargo_info_, cargoDetails, initial, not_cargo)
            
                
        cargo_info_['cargo_plans'].append(plan_)
        
    def _get_plan1(self, cargoNominationId, tankId, quantityMT, cargoId, color, abbrev, plan_, cargo_info_, cargoDetails, initial):
        
        cargo_, tank_, wt_ = 'P'+str(cargoNominationId), tankId, quantityMT
            
        if cargo_ not in cargo_info_['density']:
            i_ = [j_ for j_ in cargoDetails if j_["cargoNominationId"] == cargoNominationId][0]
            cargo_info_['density'][cargo_] = self._cal_density(float(i_['estimatedAPI']),float(i_['estimatedTemp']))
            cargo_info_['api'][cargo_] = float(i_['estimatedAPI'])
            cargo_info_['temperature'][cargo_] = float(i_['estimatedTemp'])
            # cargo_info_['cargoId'][cargo_] = cargoId
            cargo_info_['colorCode'][cargo_] = color
            cargo_info_['abbreviation'][cargo_] = abbrev
            
        
        tankName_ = self.vessel.info['tankId'][tank_]
        if tankName_ not in cargo_info_['cargoTanksUsed']:
            cargo_info_['cargoTanksUsed'].append(tankName_)
    
        
        vol_ = float(wt_)/cargo_info_['density'][cargo_]
        
        tcg_ = 0.
        if tankName_ in self.vessel.info['tankTCG']['tcg']:
            tcg_ = np.interp(vol_, self.vessel.info['tankTCG']['tcg'][tankName_]['vol'],
                                   self.vessel.info['tankTCG']['tcg'][tankName_]['tcg'])
        
        lcg_ = 0.
        if tankName_ in self.vessel.info['tankLCG']['lcg']:
            lcg_ = np.interp(vol_, self.vessel.info['tankLCG']['lcg'][tankName_]['vol'],
                                  self.vessel.info['tankLCG']['lcg'][tankName_]['lcg'])
            
        tankId_ = self.vessel.info['tankName'][tankName_]     
        try:
            corrLevel_ = self.vessel.info['ullage'][str(tankId_)](vol_).tolist()
        except:
            print(tankName_, vol_, ': correctLevel not available!!')
            corrLevel_ = 0.
            
        info_ = {'quantityMT': float(wt_), 'cargo':cargo_, 
                            'quantityM3': vol_,
                            'SG':cargo_info_['density'][cargo_],
                            'tankId':tank_,
                            'api':cargo_info_['api'][cargo_],
                            'temperature':cargo_info_['temperature'][cargo_],
                            'tcg':tcg_, 'lcg':lcg_, 'corrUallage':corrLevel_,
                            'cargoId':cargo_info_['cargoId'][cargo_], 
                            'colorCode':cargo_info_['colorCode'][cargo_], 
                            'abbreviation':cargo_info_['abbreviation'][cargo_] 
                            }
        
        if tankName_ not in plan_.keys():
            plan_[tankName_] = [info_]
        else:
            plan_[tankName_].append(info_)
            
        
        if tankName_[-1] == 'C' or tankName_ in self.vessel.info['slopTank']: #['SLS', 'SLP']:
            tank1_ = tankName_ 
        else:
            tank1_ = tankName_[:-1] + 'W'
            
        
        if cargo_ not in cargo_info_['cargo_tank']:
            cargo_info_['cargo_tank'][cargo_] = [tank1_]
        elif tank1_ not in cargo_info_['cargo_tank'][cargo_]:
            cargo_info_['cargo_tank'][cargo_].append(tank1_)
            
        if initial and cargo_ not in self.preloaded_cargos :
            self.preloaded_cargos.append(cargo_)
        elif (cargo_ not in self.to_load_cargos) and (cargo_ not in self.preloaded_cargos):
            self.to_load_cargos.append(cargo_)
        
    def _get_plan2(self, d_, plan_, cargo_info_, cargoDetails, initial, not_cargo):
        
        cargo1_, cargo2_ = 'P'+str(d_['cargo1NominationId']), 'P'+str(d_['cargo2NominationId'])
        
        if cargo1_ not in not_cargo:
            # load cargo 1
            cargoId_ = cargo_info_['cargoId'][cargo1_]
            self._get_plan1(d_["cargo1NominationId"], d_["tankId"], d_["cargo1QuantityMT"],
                            cargoId_, d_.get('colorCode',None), d_.get('abbreviation',None),
                            plan_, cargo_info_, cargoDetails, initial)
        
        if cargo2_ not in not_cargo:
            # load cargo 2
            cargoId_ = cargo_info_['cargoId'][cargo2_]
            self._get_plan1(d_["cargo2NominationId"], d_["tankId"], d_["cargo2QuantityMT"],
                            cargoId_, d_.get('colorCode',None), d_.get('abbreviation',None),
                            plan_, cargo_info_, cargoDetails, initial)
            
            
        if cargo1_ not in not_cargo and cargo2_ not in not_cargo:
            # update commingle
            print(cargo1_, cargo2_, 'commingle')
            cargo_info_['commingle'] = {k_:v_  for k_, v_ in d_.items() if k_ in ['tankId', 'cargo1QuantityMT', 'cargo2QuantityMT', 'cargo1NominationId', 'cargo2NominationId']}
            
            api__ = [cargo_info_['api'][cargo1_], cargo_info_['api'][cargo2_]]
            wt__ = [float(cargo_info_['commingle']['cargo1QuantityMT']), float(cargo_info_['commingle']['cargo2QuantityMT'])]
            temp__ = [cargo_info_['temperature'][cargo1_], cargo_info_['temperature'][cargo2_]]
            api_, temp_ = self._get_commingleAPI(api__, wt__, temp__)
            
            density_ = self._cal_density(round(api_,2), round(temp_,1))
            cargo_info_['commingle']['density'] = density_
            cargo_info_['commingle']['tankName'] = self.vessel.info['tankId'][cargo_info_['commingle']['tankId']]
            cargo_info_['commingle']['parcel1'] = 'P'+str(cargo_info_['commingle']['cargo1NominationId'])
            cargo_info_['commingle']['parcel2'] = 'P'+str(cargo_info_['commingle']['cargo2NominationId'])
            cargo_info_['commingle']['t1'] = cargo_info_['temperature'][cargo1_]
            cargo_info_['commingle']['t2'] = cargo_info_['temperature'][cargo2_]
            cargo_info_['commingle']['api1'] = cargo_info_['api'][cargo1_]
            cargo_info_['commingle']['api2'] = cargo_info_['api'][cargo2_]
            cargo_info_['commingle']['colorCode'] = d_.get('colorCode', None)
            cargo_info_['commingle']['abbreviation'] = d_.get('abbreviation', None)
            
            
        
        
    def _get_commingleAPI(self, api, weight, temp):
        weight_api_ , weight_temp_ = 0., 0.
        
        sg60_ = [141.5/(a_+131.5) for a_ in api]
        t13_ = [(535.1911/(a_+131.5)-0.0046189)*0.042 for a_ in api]
        vol_bbls_60_ = [w_/t_ for (w_,t_) in zip(weight,t13_)]
        
        weight_sg60_ = sum([v_*s_ for (v_,s_) in zip(vol_bbls_60_,sg60_)])/sum(vol_bbls_60_)
        weight_api_ = 141.5/weight_sg60_ - 131.5
        
        weight_temp_ = sum([v_*s_ for (v_,s_) in zip(vol_bbls_60_,temp)])/sum(vol_bbls_60_)
        
        return weight_api_, weight_temp_
        
    def _gen_topping(self):
        
        INDEX = self.config["gantt_chart_index"]
        
        self.seq = {}
        # self.seq['cargo'] =[]
        start_time_ = 0 # local start
        
        for p__, p_ in enumerate(self.info['cargo_plans'][:-1]):
            
            # gravity_ = self.first_loading_port and p__ == 0 and (self.max_loading_rate < 15000)
            
            # gravity_ = False
            first_loading_cargo_ = self.first_loading_port and p__ == 0 
            
            print('first_loading_cargo', first_loading_cargo_)

            df_ = pd.DataFrame(index=INDEX)
            
            df_['Initial'] = None
            df_['Initial']['Time'] = 0
            
            stages_ = {"initialCondition":(df_['Initial']['Time'], df_['Initial']['Time'])}
            
            cargo_to_load_ = self.info['loading_order'][p__]
            
            self.seq[cargo_to_load_] = {}
            self.seq[cargo_to_load_]['exactTime'] = {}
            self.seq[cargo_to_load_]['loadingRate'] = {}
            
            self.seq[cargo_to_load_]['exactTime']['Initial'] = df_['Initial']['Time']
            
            print(p__, cargo_to_load_,'cargo topping')
            # for each cargo volume
            for k_, v_ in p_.items(): #self.info['plans'][p__+1].items():
                # set time 0
                tank_ = k_
                if tank_[-1] == 'C' or tank_ in self.vessel.info['slopTank']: #['SLS', 'SLP']:
                    if len(v_) == 1:
                        df_['Initial'][tank_] = (v_[0]['cargo'], v_[0]['quantityM3'])
                    elif len(v_) == 2:
                        df_['Initial'][tank_] = (v_[0]['cargo'], v_[0]['quantityM3'], v_[1]['cargo'], v_[1]['quantityM3'])
                else:
                    tank_ = tank_[:-1] +'W'
                    if df_['Initial'][tank_] == None:
                        df_['Initial'][tank_] = (v_[0]['cargo'], v_[0]['quantityM3'])
                    else:
                        df_['Initial'][tank_] = (v_[0]['cargo'], v_[0]['quantityM3'] + df_['Initial'][tank_][-1])
                        
                        
            empty_ = []
            for t_ in self.info['cargo_tank'][cargo_to_load_]:
                if df_['Initial'][t_] in [None]:
                    empty_.append(True)
                else:
                    empty_.append(False)
                    
            self.commingle_loading1 = True if False in empty_ else False # at cargo level
                        
            # open first tank ---------------------------------
            preload_one_tank_ = False
            OPEN_TANKS_ = OPEN_TANKS + self.vessel.info['slopTank']
            first_tank__ = [t_ for t_ in OPEN_TANKS_ if t_ in self.info['cargo_tank'][cargo_to_load_]] ### fixed
            first_tank_, t_ = False, 0
            while not first_tank_:
                tank_ = first_tank__[t_]
                if df_['Initial'][tank_] in [None]: # incase the tank is preloaded
                    first_tank_ = tank_
                    break
                elif t_+1 == len(first_tank__):
                    print('all tanks are preloaded')
                    first_tank_ = tank_
                    preload_one_tank_ = True
                    break
                t_ += 1
                
            # first_tank_ = first_tank__[0]
            print('preload_one_tank_', preload_one_tank_)
            
            self.seq[cargo_to_load_]['firstTank'] = first_tank_     
            # copy self.load_param
            load_param = deepcopy(self.load_param)
                
            if first_tank_[-1] in ['C']:
                load_param['centreTank'].append(first_tank_)
            elif first_tank_ in self.vessel.info['slopTank']: #['SLS','SLP']:
                load_param['slopTank'].append(first_tank_)
            else:
                load_param['wingTank'].append(first_tank_)
                    
            loading_rate_ = self._cal_max_rate(load_param)
            
            print('initial rate: ', loading_rate_, first_tank_) # m3/hr
            self.seq[cargo_to_load_]['initialRate'] = loading_rate_     
            
            # Open one tank 
            df_['Open'] =  df_['Initial']  
            df_['Open']['Time'] = 5
            initial_stage_ = df_['Open']['Time']
            stages_['openSingleTank'] = (df_['Initial']['Time'], df_['Open']['Time'])
            
            self.seq[cargo_to_load_]['exactTime']['Open'] = df_['Open']['Time']

            # Initial rate - fill first tank -------------------------------------------
            df_['InitialRate'] =  df_['Initial']
            df_['InitialRate']['Time'] = 15
            
            initial_rate_stage_ = df_['InitialRate']['Time']
            
            if preload_one_tank_:
                df_['InitialRate'][first_tank_] += (cargo_to_load_, loading_rate_/6) # P111, vol
            else:
                df_['InitialRate'][first_tank_] = (cargo_to_load_, loading_rate_/6) # P111, vol
            
            stages_['initialRate'] = (df_['Open']['Time'], df_['InitialRate']['Time'])
            
            self.seq[cargo_to_load_]['exactTime']['InitialRate'] = df_['InitialRate']['Time']
            
            time_diff_ = initial_rate_stage_ - initial_stage_
            self.seq[cargo_to_load_]['loadingRate']['InitialRatePerTank']  = self._cal_rate('Open', 'InitialRate', df_, time_diff_, [first_tank_], cargo_to_load_)
            self.seq[cargo_to_load_]['loadingRate']['InitialRatePerTank']['time'] = [initial_stage_, initial_rate_stage_]

            # open all empty tanks ----------------------------------------------------
            df_['OpenAll'] =  df_['Initial']
            df_['OpenAll']['Time'] = 20 # end time
            open_all_stage_ = df_['OpenAll']['Time']
            
            stages_['openAllTanks'] = (df_['InitialRate']['Time'], df_['OpenAll']['Time'])
            
            total_tank_ = 0
            for t_ in self.info['cargo_tank'][cargo_to_load_]:
                if t_ == self.info['commingle'].get('tankName', None) and self.commingle_loading1:
                    continue # not counting commingle tank unless numTanktoLoad = 1
                
                if 'W' not in t_:
                    total_tank_ += 1
                else:
                    total_tank_ += 2
                    
            if preload_one_tank_:
                total_tank_ = 1 # only one tank                
            
            cargo_loaded_ = loading_rate_/4
            cargo_loaded_per_tank_ = cargo_loaded_/total_tank_
            # should have used same ullage but used uniform volume instead
            
            time_diff_ = open_all_stage_ - initial_rate_stage_
            
            if preload_one_tank_:
                
                df_['OpenAll'][first_tank_] += (cargo_to_load_, cargo_loaded_per_tank_)
                self.seq[cargo_to_load_]['loadingRate']['openAllTanksPerTank']  = self._cal_rate('InitialRate','OpenAll', df_, time_diff_, [first_tank_], cargo_to_load_)
                
            else:
                            
                for t_ in self.info['cargo_tank'][cargo_to_load_]:
                    
                    if t_ == self.info['commingle'].get('tankName', None) and self.commingle_loading1:
                        continue # not counting commingle tank
                    
                    if t_[-1] == 'C' or t_ in self.vessel.info['slopTank']: #['SLS','SLP']:
                        df_['OpenAll'][t_] = (cargo_to_load_, cargo_loaded_per_tank_)
                    else:
                        df_['OpenAll'][t_] = (cargo_to_load_, 2*cargo_loaded_per_tank_)

                self.seq[cargo_to_load_]['loadingRate']['openAllTanksPerTank']  = self._cal_rate('InitialRate','OpenAll', df_, time_diff_, self.info['cargo_tank'][cargo_to_load_], cargo_to_load_)
            
            self.seq[cargo_to_load_]['loadingRate']['openAllTanksPerTank']['time'] = [initial_rate_stage_, open_all_stage_]
            
            # increase to max rate ----------------------------------------------------------------
            df_['IncMax'] =  df_['Initial']
            df_['IncMax']['Time'] = 30 # end time
            inc_to_max_stage_  = df_['IncMax']['Time']
            self.seq[cargo_to_load_]['exactTime']['IncMax'] = df_['IncMax']['Time']

            load_param = deepcopy(self.load_param)
            for t_ in self.info['cargo_tank'][cargo_to_load_]:
                
                if t_[-1] in ['C']:
                    load_param['centreTank'].append(t_)
                elif t_ in self.vessel.info['slopTank']: #['SLS','SLP']:
                    load_param['slopTank'].append(t_)
                else:
                    load_param['wingTank'].append(t_)
                    
            loading_rate__ = self._cal_max_rate(load_param, required_rate = 6)
            
            
            # max_loading_rate_ = min(loading_rate__, self.staggering_param['maxShoreRate'])
            max_loading_rate_ = min(loading_rate__, self.info['loading_rate'][cargo_to_load_])

            # max_loading_rate_ = 5000
            print('max loading rate:', max_loading_rate_)
            cargo_loaded_ = loading_rate_*5/60 + max_loading_rate_*5/60
            cargo_loaded_per_tank_ = cargo_loaded_/total_tank_
            
            stages_['increaseToMaxRate'] = (df_['OpenAll']['Time'], df_['IncMax']['Time'])
            
            df_inc_max_ = pd.DataFrame(index=INDEX[1:])
            df_inc_max_['IncMax'] = 0.
            
            time_diff_ = inc_to_max_stage_- open_all_stage_ 

            if preload_one_tank_:
                
                df_['IncMax'][first_tank_] += (cargo_to_load_, cargo_loaded_per_tank_)
                df_inc_max_['IncMax'][first_tank_] = cargo_loaded_per_tank_
                self.seq[cargo_to_load_]['loadingRate']['IncMaxPerTank']  = self._cal_rate('OpenAll','IncMax', df_, time_diff_, [first_tank_], cargo_to_load_)

            else:
            
                for t_ in self.info['cargo_tank'][cargo_to_load_]:
                    if t_ == self.info['commingle'].get('tankName', None) and self.commingle_loading1:
                        continue # not counting commingle tank
                    
                    if t_[-1] == 'C' or t_ in self.vessel.info['slopTank']: #['SLS','SLP']:
                        df_['IncMax'][t_] = (cargo_to_load_, cargo_loaded_per_tank_)
                        df_inc_max_['IncMax'][t_] = cargo_loaded_per_tank_
                    else:
                        df_['IncMax'][t_] = (cargo_to_load_, 2*cargo_loaded_per_tank_)
                        df_inc_max_['IncMax'][t_] = 2*cargo_loaded_per_tank_
                        
                self.seq[cargo_to_load_]['loadingRate']['IncMaxPerTank']  = self._cal_rate('OpenAll','IncMax', df_, time_diff_, self.info['cargo_tank'][cargo_to_load_], cargo_to_load_)
            
            self.seq[cargo_to_load_]['loadingRate']['IncMaxPerTank']['time'] = [open_all_stage_, inc_to_max_stage_]

            ## backward calculation ------------------------------------------------------------------------
            # staggering rate  ## fixed
            # param_ = {'maxShoreRate': 11129, 
            #          'wingTank': 7900,
            #          'centerTank': 5790,
            #          'slopTank': 3435,
            #          'toppingSeq':[]}
            
            param_ = deepcopy(self.staggering_param)
            param_['maxShoreRate'] = max_loading_rate_
            
            self.seq[cargo_to_load_]['maxShoreRate'] = max_loading_rate_ #param_['maxShoreRate']
            
            for t_ in INDEX:
                if t_ in self.info['cargo_tank'][cargo_to_load_]:
                    param_['toppingSeq'].append([t_])
                        
            staggering_rate_ = self._cal_staggering_rate(param_)
            
            
            self.seq[cargo_to_load_]['staggerRate'] = deepcopy(staggering_rate_) 
            
            num_staggering_ = len(staggering_rate_.columns)
            
            staggering_rate_['TotalVol'] = None
            # staggering_rate_['TotalWeight'] = None
            
            for k_, v_ in self.info['cargo_plans'][p__+1].items():
                # print(k_, v_)
                
                if len(v_) == 1:
                    fill_tank_ = True if  v_[0]['cargo'] == cargo_to_load_ else False
                elif len(v_) == 2:
                    fill_tank_ = True if  v_[0]['cargo'] == cargo_to_load_ or  v_[1]['cargo'] == cargo_to_load_ else False
                    
                if fill_tank_:
                    # print(k_)
                    if k_[-1] == 'C' or k_ in self.vessel.info['slopTank']: #['SLS', 'SLP']:
                        if k_ == self.info['commingle'].get('tankName', None) and self.commingle_loading1:
                            print(k_, 'use own density instead')
                            # only consider loading of new cargo .... 
                            # cargo1 : own density
                            # cargo2 (now to add): own density
                            wt_ = [v__['quantityMT'] for v__ in v_ if v__['cargo'] == cargo_to_load_][0]
                            vol_ =  wt_/self.info['density'][cargo_to_load_]
                            staggering_rate_['TotalVol'][k_] = round(vol_,2)
                        else:
                            staggering_rate_['TotalVol'][k_] = v_[0]['quantityM3']
                        # staggering_rate_['TotalWeight'][k_[1]] = staggering_rate_['TotalVol'][k_[1]]*self.info['density'][cargo_to_load_]
                        
                    else:
                        tank1_ = k_[:-1] + 'P'
                        tank2_ = k_[:-1] + 'S'
                        tank_ = k_[:-1] + 'W'
                        staggering_rate_['TotalVol'][tank_]  = self.info['cargo_plans'][p__+1][tank1_][0]['quantityM3'] + self.info['cargo_plans'][p__+1][tank2_][0]['quantityM3'] 
                        
                        
            # amt filled during topping         
            staggering_rate_['AmtFilled'] = None
            for t_ in self.info['cargo_tank'][cargo_to_load_]:
                rate_ = staggering_rate_.loc[t_].to_list()[:-2]
                len_rate_ = len(rate_) - rate_.count(None)
                vol_ = np.array(rate_[:len_rate_]).sum()/4 # fixed 15 min per stage
                staggering_rate_['AmtFilled'][t_] = vol_ #round(vol_,10)
            
            # amt in tank before topping starts    
            staggering_rate_['AmtBefTop'] =  staggering_rate_['TotalVol'] -  staggering_rate_['AmtFilled']
            
            commingle_start_ = None
            if self.commingle_loading1:
                commingle_tank_ = self.info['commingle']['tankName']
                
                if preload_one_tank_:
                    ratio_ = 0
                else:
                    initial_vol_ = df_['Initial'][commingle_tank_][1] # stick to the original density and not commingle density
                    capacity_ = self.vessel.info['cargoTanks'][commingle_tank_]['capacityCubm']
                    ratio_ = initial_vol_/capacity_ 
                
                add_vol_ = staggering_rate_['AmtBefTop'][commingle_tank_]
                
                total_vol1_ = staggering_rate_['AmtBefTop'].sum() - df_inc_max_['IncMax'].sum()
                total_vol2_ = total_vol1_ - add_vol_ # - commingle vol
                
                if preload_one_tank_:
                    first_half_ = 0
                    commingle_start_ = int(5)
                
                else:
                    first_half_ = ratio_*total_vol2_/param_['maxShoreRate']*60 # min
                    commingle_start_ = int(first_half_ + 30)
                
                
                second_half_ = ((1-ratio_)*total_vol2_ + add_vol_)/param_['maxShoreRate']*60 
                time_taken_ = first_half_ + second_half_
                
                
                
                staggering_rate_['LoadingRateM3Min1'] = ratio_*(staggering_rate_['AmtBefTop'] - df_inc_max_['IncMax'])/max(0.0001,first_half_)
                staggering_rate_['LoadingRateM3Min1'][commingle_tank_] = np.nan
                
                staggering_rate_['LoadingRateM3Min2'] = (1-ratio_)*(staggering_rate_['AmtBefTop'] - df_inc_max_['IncMax'])/second_half_
                staggering_rate_['LoadingRateM3Min2'][commingle_tank_] = add_vol_/second_half_
                
                print('comminglePartition:', round(first_half_), round(second_half_))
                
            else:
                time_taken_ =  (staggering_rate_['AmtBefTop'].sum() - df_inc_max_['IncMax'].sum())/param_['maxShoreRate']*60 # min
                staggering_rate_['LoadingRateM3Min'] = (staggering_rate_['AmtBefTop'] - df_inc_max_['IncMax'])/time_taken_
            
            topping_start_ = time_taken_ + 30
            
            time_interval_ = self.time_interval1 ## fixed
            num_stages_ = 0
            self.time_interval[cargo_to_load_] = time_interval_
            
            df1_ = df_.copy()
            
            # self.num_stage_interval = 2
            
            while num_stages_ < self.num_stage_interval and time_interval_ >= 60 :
            
                # self.time_interval = time_interval_
                time_, stage_ = time_interval_, 1
                time_incmax_ = df_['IncMax']['Time']
                
                ballast_ = [(0, 'Initial')]
                ballast_stop_, before_topping_ = [], 'MaxLoading' + str(stage_)
                ballast_init_ = [] # for first 2 hr no deballasting 
                single_max_stage_ = True
                stage1_ = 'IncMax'
                while (time_ < topping_start_):
                    single_max_stage_ = False
                    # print(time_)
                    ss_ = 'MaxLoading' + str(stage_)
                    df_[ss_] = df_['IncMax']
                    df_[ss_]['Time'] = int(time_)
                    before_topping_ = ss_
                    ballast_.append((int(time_),ss_))
                    
                    self.seq[cargo_to_load_]['exactTime'][ss_] = time_
                    # first two hrs no deballasting 
                    if int(time_) <= 120 and first_loading_cargo_:
                        ballast_init_.append((int(time_),ss_))
                        
                    for t_ in self.info['cargo_tank'][cargo_to_load_]:
                        if self.commingle_loading1:
                            
                            vol0_ = df_['IncMax'][t_][1] 
                            vol2_ = 0.
                            
                            if time_ <= first_half_ + 30:
                                vol1_ = (time_-time_incmax_)*staggering_rate_['LoadingRateM3Min1'][t_]
                               
                            else:
                                vol0_ = df_['IncMax'][t_][1] 
                                vol1_ = first_half_* staggering_rate_['LoadingRateM3Min1'][t_]
                                vol2_ = (time_ - first_half_ - 30) * staggering_rate_['LoadingRateM3Min2'][t_]
                                
                            if t_ == self.info['commingle']['tankName']:
                                preloaded_ = df_[ss_][t_][:2]
                                df_[ss_][t_] = preloaded_ + (cargo_to_load_, vol2_)
                                
                            else:
                                df_[ss_][t_] = (cargo_to_load_, vol0_ + vol1_ + vol2_)
                        
                        else:
                            df_[ss_][t_] = (cargo_to_load_, df_['IncMax'][t_][1] + (time_-time_incmax_)*staggering_rate_['LoadingRateM3Min'][t_])
                    
                    pre_col_ = self.seq[cargo_to_load_]['exactTime'][stage1_] 
                    col_ = time_
                    
                    time_diff_ = col_ - pre_col_
                    self.seq[cargo_to_load_]['loadingRate'][ss_+'PerTank']  = self._cal_rate(stage1_,ss_, df_, time_diff_, self.info['cargo_tank'][cargo_to_load_], cargo_to_load_)
                    self.seq[cargo_to_load_]['loadingRate'][ss_+'PerTank']['time'] = [pre_col_, col_]
                    self.seq[cargo_to_load_]['exactTime'][ss_] = time_

                    time_ += time_interval_
                    stage_ += 1
                    stage1_ = ss_
                
                num_stages_ = stage_-1
                
                next_time_ = time_ # next interval
                time_ = topping_start_
                ss_ = 'MaxLoading' + str(stage_)
                just_before_topping_ = ss_
                df_[ss_] = df_['IncMax']
                df_[ss_]['Time'] = int(time_)
                self.seq[cargo_to_load_]['exactTime'][ss_] = time_

                for t_ in self.info['cargo_tank'][cargo_to_load_]:
                    if self.commingle_loading1:
                        vol0_ = df_['IncMax'][t_][1] 
                        vol2_ = 0.
                        
                        if time_ <= first_half_ + 30:
                            vol1_ = (time_-time_incmax_)*staggering_rate_['LoadingRateM3Min1'][t_]
                           
                        else:
                            vol0_ = df_['IncMax'][t_][1] 
                            vol1_ = first_half_* staggering_rate_['LoadingRateM3Min1'][t_]
                            vol2_ = (time_ - first_half_ - 30) * staggering_rate_['LoadingRateM3Min2'][t_]
                            
                        if t_ == self.info['commingle']['tankName']:
                            preloaded_ = df_[ss_][t_][:2]
                            df_[ss_][t_] = preloaded_ + (cargo_to_load_, vol2_)
                            
                        else:
                            df_[ss_][t_] = (cargo_to_load_, vol0_ + vol1_ + vol2_)
                    else:
                        df_[ss_][t_] = (cargo_to_load_, df_['IncMax'][t_][1] + (time_-time_incmax_)*staggering_rate_['LoadingRateM3Min'][t_])
                
                pre_col_ = self.seq[cargo_to_load_]['exactTime'][stage1_] 
                col_ = time_
                
                time_diff_ = col_ - pre_col_
                self.seq[cargo_to_load_]['loadingRate'][ss_+'PerTank']  = self._cal_rate(stage1_,ss_, df_, time_diff_, self.info['cargo_tank'][cargo_to_load_], cargo_to_load_)
                self.seq[cargo_to_load_]['loadingRate'][ss_+'PerTank']['time'] = [pre_col_, col_]
                self.seq[cargo_to_load_]['exactTime'][ss_] = time_

                if num_stages_ < self.num_stage_interval:
                    time_interval_ -= 60
                    self.time_interval[cargo_to_load_] = time_interval_
                    print('Reduce stage interval', cargo_to_load_, time_interval_)
                    df_ = df1_
                    
                    if time_interval_ == 0:
                        self.error['Interval Error'] = ["No. of stages requirement cannot be met!!"]
                        return
                
            self.seq[cargo_to_load_]['addTime'] = 0
            if  df_[ss_]['Time'] == df_['MaxLoading'+str(stage_-1)]['Time']:
                print('Add 1 min to last Maxloading stage')
                df_[ss_]['Time'] = int(df_[ss_]['Time'] +1)
                self.seq[cargo_to_load_]['addTime'] = 1 
                
                
            last_loading_max_rate_stage_ = ss_
            stages_['loadingAtMaxRate'] = (df_['IncMax']['Time'], df_[ss_]['Time'])
            
            # last max stage before topping
            # if p__+1 < len(self.info['loading_order'])+1:
            ballast_.append((int(df_[ss_]['Time']),ss_))
            ballast_stop_.append((int(df_[ss_]['Time']),ss_))
                
            
            next_ballast_ = (None,None,10000)  # time; stage; relative to interval
            final_ballast_ = (None, None)
            stage1_ = ss_
            for c_ in range(1,num_staggering_+1):
                # print(c_)
                ss_ = 'Topping' + str(c_)
                df_[ss_] = df_[df_.columns[-1]]
                df_[ss_]['Time'] += 15
                
                self.seq[cargo_to_load_]['exactTime'][ss_] = time_+15*c_
 
                final_ballast_ = (int(df_[ss_]['Time']),ss_)
                
                if abs(df_[ss_]['Time']-next_time_) < next_ballast_[-1]:
                    next_ballast_ = (int(df_[ss_]['Time']),ss_,int(abs(df_[ss_]['Time']-next_time_)))
                    
                
                for t_ in self.info['cargo_tank'][cargo_to_load_]:
                    rate_ = 0 if staggering_rate_[c_][t_] == None else staggering_rate_[c_][t_]
                    vol_ = rate_/4
                   
                    if self.commingle_loading1:
                        if t_ == self.info['commingle']['tankName']:
                            df_[ss_][t_] = (df_[ss_][t_][0], df_[ss_][t_][1], cargo_to_load_, df_[ss_][t_][3] + vol_)
                        else:
                            df_[ss_][t_] = (cargo_to_load_, df_[ss_][t_][1] + vol_)
                            
                    else:
                        df_[ss_][t_] = (cargo_to_load_, df_[ss_][t_][1] + vol_)  

                pre_col_ = self.seq[cargo_to_load_]['exactTime'][stage1_] 
                col_ = self.seq[cargo_to_load_]['exactTime'][ss_]
                
                time_diff_ = col_ - pre_col_
                self.seq[cargo_to_load_]['loadingRate'][ss_+'PerTank']  = self._cal_rate(stage1_,ss_, df_, time_diff_, self.info['cargo_tank'][cargo_to_load_], cargo_to_load_)
                self.seq[cargo_to_load_]['loadingRate'][ss_+'PerTank']['time'] = [pre_col_, col_]
                stage1_ = ss_

            stages_['topping'] = (df_[last_loading_max_rate_stage_]['Time'], df_[ss_]['Time'])
                    
            if next_ballast_ not in [(None,None,10000)]:
                ballast_.append((next_ballast_[0],next_ballast_[1]))    
                if next_ballast_[1] != ss_:
                    ballast_stop_.append((next_ballast_[0],next_ballast_[1]))
                
            if (final_ballast_[0],final_ballast_[1]) not in ballast_:
                ballast_.append((final_ballast_[0],final_ballast_[1]))    
                # ballast_stop_.append((next_ballast_[0],next_ballast_[1]))
                
                
            ## add MaxLoading1 if necessary 
            if single_max_stage_ and  (df_['MaxLoading1']['Time'],'MaxLoading1') not in ballast_:
                ballast_.insert(1, (df_['MaxLoading1']['Time'],'MaxLoading1'))
               
            ballast_limit_ = {} # time for ballast at each interval
            ini_delay_ = 120 # inital delay for first cargo
            for aa_, (bb_,cc_) in enumerate(ballast_):
                if cc_[:3] in ['Max']:
                    time_ = bb_ - ballast_[aa_-1][0]
                    if first_loading_cargo_ and ini_delay_ > 0:
                        if bb_ >= ini_delay_:
                            time_ -= ini_delay_
                            ini_delay_ = 0
                        else:
                            ini_delay_ -= time_
                            time_ = 0
                        
                    
                    ballast_limit_[cc_] = time_
                    # print(ini_delay_)

                    
                    
                
                    
            self.seq[cargo_to_load_]['gantt'] = df_        
            self.seq[cargo_to_load_]['ballast'] = list(ballast_) # need to get ballast for these stages
            self.seq[cargo_to_load_]['toppingStart'] = int(topping_start_) # time when topping starts
            self.seq[cargo_to_load_]['beforeTopping'] = before_topping_ # 2nd last stage before topping
            self.seq[cargo_to_load_]['justBeforeTopping'] = just_before_topping_ # last stage before topping
            self.seq[cargo_to_load_]['stageInterval'] = stages_ # time duration for each stage
            self.seq[cargo_to_load_]['startTime'] = start_time_ # start time without delay
            self.seq[cargo_to_load_]['ballastStop'] = list(ballast_stop_) # no ballasting after  these stage
            self.seq[cargo_to_load_]['lastStage'] = ss_
            if self.commingle_loading1:
                self.seq[cargo_to_load_]['loadingRateM3Min'] = (staggering_rate_['LoadingRateM3Min1'],staggering_rate_['LoadingRateM3Min2'])
            else:
                self.seq[cargo_to_load_]['loadingRateM3Min'] = staggering_rate_['LoadingRateM3Min'] 
            
            self.seq[cargo_to_load_]['timeNeeded'] = df_[ss_]['Time']
            self.seq[cargo_to_load_]['singleMaxStage'] = single_max_stage_
            self.seq[cargo_to_load_]['commingleStart'] = commingle_start_
            self.seq[cargo_to_load_]['ballastLimit'] = ballast_limit_
            self.seq[cargo_to_load_]['ballastInit'] = ballast_init_
            
            self.seq[cargo_to_load_]['stageTime'] = {}
            for (f__,f_) in df_.iteritems():
                self.seq[cargo_to_load_]['stageTime'][f__] = f_['Time'] # local time start from zero
            
                       
            start_time_ += df_[ss_]['Time']
            
            # print(df_.columns.to_list()[5:]) # 'MaxLoading1', 'MaxLoading2', ...

            print(start_time_-df_[ss_]['Time'], start_time_)

    
    def _cal_rate(self, stage1, stage2, df, time_diff_, tanks, cargo):
        
        # time_diff_ = df[stage2]['Time'] - df[stage1]['Time']
        total_vol_change_ = 0
        rate_per_tank_ = {}
        for t_ in tanks:
            # print(t_, df[stage1][t_], df[stage2][t_])
            v1_ = 0.
            if df[stage1][t_] not in [None] and df[stage1][t_][-2] == cargo:
                v1_ = df[stage1][t_][-1]
            v2_ = 0.
            if df[stage2][t_] not in [None] and df[stage2][t_][-2] == cargo:
                v2_ = df[stage2][t_][-1]
                
            if v2_ > 0.:
                vol_change_ = v2_ - v1_
                
                if t_[-1] in ['W']:
                    rate_per_tank_[t_[0]+'P'] = round(vol_change_/2/time_diff_*60,4)
                    rate_per_tank_[t_[0]+'S'] = round(vol_change_/2/time_diff_*60,4)
                else:
                    rate_per_tank_[t_] = round(vol_change_/time_diff_*60,4)
                total_vol_change_ += vol_change_
            
        rate_per_tank_['total'] = round(total_vol_change_/time_diff_*60,4)
        # print(stage1, stage2, time_diff_, vol_change_)
        return rate_per_tank_            

    def _get_ballast_requirements(self, time_left_eduction = 0):
        
        INDEX = self.config["gantt_chart_index"]
        INDEX1 = self.config["gantt_chart_ballast_index"]
        
        
        # main deballast/ballast , eduction finished 1 hrs before topping 
        # eduction take 2 hr
        
        density_ = self.info['density']
        num_port_ = 0
        fixed_ballast_ = []
        same_ballast_ = []
        stages_ = []
        init_ballast_ = []
        delay_ = self.initial_delay
        times_ = []
        self.seq['loadingRate'] = {}
        
        ballastLimit1_ = {}
        for c__, c_ in enumerate(self.info['loading_order']):
            ballastLimit1_[c_] = deepcopy(self.seq[c_]['ballastLimit'])

        for c__, c_ in enumerate(self.info['loading_order']):
            print(c__, 'collecting ballast requirements ....')
            
            # gravity_ = self.first_loading_port and c__ == 0 and (self.max_loading_rate < 15000)
            
            df_ = self.seq[c_]['gantt']
            df_ = df_.append(pd.DataFrame(index=INDEX1))

            # initial
            if c__ == 0: # first cargo to load
                print('1st stage to be fixed; collecting ballast ...')
                fixed_ballast_ = ['Initial1']
                init_ballast_ = ['Initial1']
                for k_, v_ in self.info['ballast'][0].items():
                    df_['Initial'][k_] = v_[0]['quantityMT']
                    
                for p_ in self.seq[c_]['ballastInit']:
                    init_ballast_.append(p_[1]+str(c__+1))
                    for k_, v_ in self.info['ballast'][0].items():
                        df_[p_[1]][k_] = v_[0]['quantityMT']
                    
                
            # topping last cargo topping
            if c__ ==  len(self.info['loading_order']) - 1:
                print('last loading cargo')
                
                # time for educting for last cargo
                # if interval < 2hrs more time might be needed
                time_ = df_[self.seq[c_]['justBeforeTopping']]['Time'] - df_[self.seq[c_]['beforeTopping']]['Time']
                print('Duration of last max loading interval:', time_, self.seq[c_]['justBeforeTopping'])
                if self.info['numEductionTanks']: #self.info['eduction']:
                    if time_ > 0:
                        if time_ < self.time_eduction + time_left_eduction:
                            
                            # self.seq[c_]['ballastLimit'][self.seq[c_]['justBeforeTopping']] = 0
                            ballastLimit1_[c_][self.seq[c_]['justBeforeTopping']] = 0
                            
                            time_interval_ = self.time_interval[c_]
                            time_left_ = time_interval_+time_-self.time_eduction
                            stage_ = self.seq[c_]['beforeTopping']
                            
                            fixed_ballast__ = [stage_]
                            fixed_ballast_.append(stage_+str(c__+1))
                            # self.seq[c_]['ballastLimit'][stage_] = max(0,time_left_)
                            ballastLimit1_[c_][stage_] =  max(0,time_left_-time_left_eduction)
                            
                            while time_left_ <= time_left_eduction:
                                time_left_ += time_interval_
                                if str(int(stage_[10:])-1) in ['0']:
                                    print('Cannot reduce eduction stage!!')
                                    break
                                stage_ = stage_[:10] + str(int(stage_[10:])-1)
                                fixed_ballast__.append(stage_)
                                fixed_ballast_.append(stage_+str(c__+1))
                                print("Move eduction stage", stage_)
                                # self.seq[c_]['ballastLimit'][stage_] = max(0,time_left_)
                                ballastLimit1_[c_][stage_] = max(0,time_left_-time_left_eduction)
                                
                            time_left_  = min(time_left_-time_left_eduction, self.time_interval[c_])
                            print('Eduction needed', stage_+str(c__+1), time_left_, ' given')
                            print('Eduction required', self.time_eduction, time_left_eduction)
                            self.seq[c_]['eduction'] = (time_left_, stage_)
                            
                            # fixed at departure ballast
                            for ss_ in fixed_ballast__:
                                for k_, v_ in self.info['ballast'][-1].items():
                                    df_[ss_][k_] = v_[0]['quantityMT']
                                    
                            
                        else:
                            print('Eduction needed', self.seq[c_]['justBeforeTopping']+str(c__+1), time_-self.time_eduction)
                            self.seq[c_]['eduction'] = (time_-self.time_eduction, self.seq[c_]['justBeforeTopping'])
                            # self.seq[c_]['ballastLimit'][self.seq[c_]['justBeforeTopping']] = time_-self.time_eduction
                            ballastLimit1_[c_][self.seq[c_]['justBeforeTopping']] = time_-self.time_eduction
                            
                    elif time_ == 0:
                        print('Only one maxloading stage')
                        time__ = df_['MaxLoading1']['Time']
                        if time__ > self.time_eduction:
                            print('Fix ballast at MaxLoading1 for educting!!', time__-self.time_eduction)
                            self.seq[c_]['eduction'] = (time__-self.time_eduction, 'MaxLoading1')
                            
                        else:
                            print('No time for eduction!!')
                            self.error['Eduction Error'] = ["No time for eduction!!"]
                            return
                    
                        
                # fixed at departure ballast            
                if self.seq[c_]['justBeforeTopping']+str(c__+1) not in fixed_ballast_:
                    fixed_ballast_.append(self.seq[c_]['justBeforeTopping']+str(c__+1))
                    
                    for k_, v_ in self.info['ballast'][-1].items():
                        df_[self.seq[c_]['justBeforeTopping']][k_] = v_[0]['quantityMT']
                
                
            # get loading info        
            ddf_ = pd.DataFrame(index=INDEX)
            
            if c__ == 0:
                col_ = 'Initial' + str(c__+1)
                ddf_[col_] = df_['Initial']
            
            ddf_ = ddf_.append(pd.DataFrame(index=['Weight']))
            
            for b__,b_ in enumerate(self.seq[c_]['ballast']):
                if b__ > 0:
                    num_port_ += 1
                    stages_.append(b_[1]+str(c__+1))
                    times_.append(self.seq[c_]['stageTime'][b_[1]] + delay_)

                    wt_ = 0
                    col_ = b_[1] + str(c__+1)
                    ddf_[col_] = None
                    ddf_[col_]['Time'] = b_[0] + self.seq[c_]['startTime']
                    pre_col_ = self.seq[c_]['ballast'][b__-1][1]
                    
                    if b_  in self.seq[c_]['ballastStop']:
                        same_ballast_.append(num_port_)
                      
                    for h_, (i_,j_) in enumerate(self.seq[c_]['gantt'][b_[1]].iteritems()): 
                        # print(i_, j_)
                        if i_ not in ['Time'] and j_ not in [None]:
                            # print(i_,j_) # j_ = curr (cargo, vol)
                            
                            pre_ = self.seq[c_]['gantt'][pre_col_][i_]
                            
                            check_ = False
                            if pre_ not in [None]:
                                if pre_[0] == c_:
                                    check_ = True
                                elif len(pre_) == 4 and pre_[2] == c_:
                                    check_ = True
                                
                            
                            #print(pre_, j_)
                            if  pre_ not in [None] and check_:
                                
                                if pre_[0] == c_:
                                    amt_ = j_[1] - pre_[1]
                                    ddf_[col_][i_] = (c_, amt_)
                                    wt_ += round(amt_*density_[c_],10)
                                elif len(pre_) == 4 and pre_[2] == c_:
                                    amt_ = j_[3] - pre_[3]
                                    ddf_[col_][i_] = (c_, amt_)
                                    wt_ += round(amt_*density_[c_],10)
                                
                            elif j_[0] == c_:
                                ddf_[col_][i_] = (c_, j_[1])
                                wt_ += round(j_[1]*density_[c_],10)
                                
                            elif len(j_) > 2 and j_[2] == c_:
                                ddf_[col_][i_] = (c_, j_[3])
                                wt_ += round(j_[3]*density_[c_],10)
                                
                    ddf_[col_]['Weight'] = wt_ # cargo added in this stage 
                    
                    if col_[:-1] == 'MaxDischarging1':
                        time_diff_ = df_[col_[:-1]]['Time'] -  df_['Initial']['Time']
                        print(col_[:-1], time_diff_)
                        pre_time_ = df_['Initial']['Time']
                        
                    else:
                        time_diff_ = df_[col_[:-1]]['Time'] -  df_[pre_col_]['Time']
                        # print(pre_col_, col_[:-1], time_diff_)
                        pre_time_ = self.seq[c_]['exactTime'][pre_col_]
                        
                    cur_time_ = self.seq[c_]['exactTime'][col_[:-1]]
                    # result_ = self.seq[c1_]['info']
                    # self.seq[c1_]['dischargingRate1'][col_+'PerTank'] = self._cal_rate(pre_col_, col_, ddf_, result_)
                        
                    time_diff_ = cur_time_ - pre_time_
                    stage1, stage2 = pre_col_, col_[:-1]
                    total_vol_change_ = 0
                    rate_per_tank_ = {}
                    for t_ in self.info['cargo_tank'][c_]:
                        v1_ = 0 if df_[stage1][t_] in [None] else df_[stage1][t_][-1]
                        v2_ = df_[stage2][t_][-1]
                        vol_change_ = v2_ - v1_
                        
                        if t_[-1] in ['W']:
                            rate_per_tank_[t_[0]+'P'] = round(vol_change_/2/time_diff_*60,4)
                            rate_per_tank_[t_[0]+'S'] = round(vol_change_/2/time_diff_*60,4)
                        else:
                            rate_per_tank_[t_] = round(vol_change_/time_diff_*60,4)
                        total_vol_change_ += vol_change_
                        
                    rate_per_tank_['total'] = round(total_vol_change_/time_diff_*60,4)
                    rate_per_tank_['time'] = [pre_time_, cur_time_]
                    self.seq['loadingRate'][str(num_port_)] = rate_per_tank_
                    
            delay_ += self.info['timing_delay2'][c__+1] + times_[-1]
                    
                          
            self.seq[c_]['loadingInfo'] = ddf_  # cargo in m3
            self.seq[c_]['fixBallast'] = fixed_ballast_
            self.seq[c_]['initBallast'] = init_ballast_
            
            print('fixed ballast: ', fixed_ballast_)
            print('initial ballast: ', init_ballast_)
            
            
            # print(df_.columns)
            
            
            # self.seq[c_]['gantt'] = df_
        
        print('same ballast: ', same_ballast_)
        print('stage: ', stages_)
        
        ballast_limit_, ballast_limit_time_ = {}, {} # max amt of ballast can be removed
        for s__,s_ in enumerate(stages_):
            c_ = self.info['loading_order'][int(s_[-1]) - 1] # less than 10 cargos loading at one port
            if s_[:3] in ['Max']:
                # b_ = round(self.max_ballast_rate * self.seq[c_]['ballastLimit'][s_[:-1]]/60,2) # in MT
                b_ = round(self.max_ballast_rate * ballastLimit1_[c_][s_[:-1]]/60,2) # in MT
                
                ballast_limit_[s__+1] = max(0,b_ - 100)  # in MT 
                # ballast_limit_time_[s__+1] =  self.seq[c_]['ballastLimit'][s_[:-1]]
                ballast_limit_time_[s__+1] =  ballastLimit1_[c_][s_[:-1]]
            
            
        
        self.seq['numPort'] = num_port_
        self.seq['stages'] = stages_
        self.seq['sameBallast'] = same_ballast_
        self.seq['ballastLimitQty'] = ballast_limit_
        self.seq['ballastLimitTime'] = ballast_limit_time_
        self.seq['times'] = times_ # zero start time
        
                    
    def _cal_staggering_rate(self, param, reduce = 1000):
        
        INDEX = self.config["gantt_chart_index"]
    
        stages_ = {}
        for t__, t_ in enumerate(param['toppingSeq']):
            stages_[t__+1] = {}
            for s__, s_ in enumerate(range(t__,t__+20)):
                if s_+1 <= len(param['toppingSeq']):
                    for r_ in param['toppingSeq'][s_]:
                        if r_ in self.vessel.info['slopTank']: #['SLS', 'SLP']:
                            rate_ = param['slopTank']
                        elif r_[-1] == 'C':
                            rate_ = param['centerTank']
                        else:
                            rate_ = param['wingTank']
                        
                        stages_[t__+1][r_] = rate_
        
        df_ = pd.DataFrame(index=INDEX[1:])
        len_stages_ = len(stages_[1])
        
        for k_, v_ in stages_.items():
            total_ = sum([v__ for k__,v__ in v_.items()])
            # print(k_, total_)
            if (len_stages_ - k_) >= 4: # reduce rate 1hr before topping complete
                maxRate_ = min(total_, param['maxShoreRate'])
            else:
                maxRate_ = param['minLoadingRate']
            
            df_[k_] = None
            for k__,v__ in v_.items():
                stages_[k_][k__] = v__/total_*maxRate_
                
                df_[k_][k__] = stages_[k_][k__] 
            
            
        return df_        
               
                
    def _cal_max_rate(self, param, required_rate = 1):
        
        # flow_rate = {'maxLoadingRate': 20500,
        # 'maxRiser': 25625,
        # 'manifolds':         {1: 1140, 6: 6841, 7: 7891, 12:13681},
        # 'dropLines':         {1: 1140, 6: 6841, 7: 7891, 12:13681},
        # 'bottomLines':       {1: 1534, 6: 9205, 7:10739, 12:18409},
        # 'wingTankBranch':    {1:  659, 6: 3950, 7: 3950, 12: 3950},
        # 'centreTankBranch':  {1:  965, 6: 5790, 7: 5790, 12: 5790},
        # 'PVvalveWingTank':   {1: 7050, 6: 7050, 7: 7050, 12: 7050},
        # 'PVvalveCentreTank': {1:12000, 6:12000, 7:12000, 12:12000},
        # 'slopTankBranch':    {1:  573, 6: 3435, 7: 3950, 12: 3950},
        # }
        
        if required_rate == 1:
            flow_rate = self.vessel.info['loadingRate1']
        elif required_rate == 6:
            flow_rate = self.vessel.info['loadingRate6']
        
        max_rate = 1000000
        
        components = {'manifolds':[['Manifolds'], ['Manifolds']],   # param, flow_rate
                      'drop':[['Manifolds'], ['DropLines']], 
                      'bottom':[['BottomLines'],['BottomLines']],
                      'tanks':[['centreTank', 'wingTank','slopTank'], ['CentreTankBranchLine','WingTankBranchLine','SlopTankBranchLine']], 
                      'PVvalves':[['centreTank', 'wingTank','slopTank'], ['PVValveCentreTank','PVValveWingTank','PVValveWingTank']], 
                      'maxVessel':[[''],['maxLoadingRate']],
                      'maxRiser':[[''],['maxRiser']]}
        rate = {}
        # print(param['centreTank'])
        # print(param['wingTank'])
        # print(param['slopTank'])
        
        # min (vessel, riser)
        loading_rate_ = min(self.vessel.info['loadingRateVessel'], self.vessel.info['loadingRateRiser'])

        for k_, v_ in components.items():
            rate_ = 0
            # print(v_)
            for i_, j_ in zip(v_[0], v_[1]):
                # print(i_,j_, param.get(i_,1), flow_rate[j_])
                if j_ in ['maxLoadingRate', 'maxRiser']:
                    # print(i_, j_, flow_rate[j_])
                    rate_ += flow_rate.get(j_, loading_rate_)
                else:
                    # print(i_, j_, parWam[i_], flow_rate[j_])
                    if i_ == 'wingTank':
                        rate_ += len(param[i_])*2 * flow_rate[j_]
                    else:
                        rate_ += len(param[i_]) * flow_rate[j_]
    
            
            rate[k_] = rate_
            if max_rate > rate_:
                max_rate = rate_
            
            # print('>>>', k_, rate_)
            
        # print(rate)
        
        
        return max_rate

                
    def _cal_density(self, api, temperature_F):
        
        ## https://www.myseatime.com/blog/detail/cargo-calculations-on-tankers-astm-tables
    
        a60 = 341.0957/(141360.198/(api+131.5))**2
        dt = temperature_F-60
        vcf_ = np.exp(-a60*dt*(1+0.8*a60*dt))
        t13_ = (535.1911/(api+131.5)-0.0046189)*0.42/10
        density = t13_*vcf_*6.2898
        
    
        return round(density,6)
    
                
                
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
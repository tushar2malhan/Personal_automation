# -*- coding: utf-8 -*-
"""
Created on Thu Oct 14 22:27:05 2021

@author: I2R
"""
import numpy as np
import json
from vlcc_gen import Generate_plan 
from vlcc_check import Check_plans
from copy import deepcopy
import pandas as pd
from scipy.interpolate import interp1d
# from discharge_init import Process_input1

# INITIAL_RATE = 1000
# REDUCED_RATE = 1500

# MAX_RATE = {1: 12000, 2:11129, 3:11553, 4:5829}


#INDEX = ['Time', '1C', '2C', '3C', '4C', '5C', '1P', '1S', '2P', '2S', '3P', '3S', '4P', '4S', '5P', '5S', 'SLP', 'SLS']
INDEX = ['Time', '1C', '2C', '3C', '4C', '5C', '1P', '1S', '2P', '2S', '3P', '3S', '4P', '4S', '5P', '5S']

        

class DischargingOperations(object):
    # 
    def __init__(self, data):
        
        self.error = data.error
        self.ballast_color, self.rob_color = {}, {}
        self.vessel = data.vessel
        self.module = data.module
        self.mode = ""
        self.vessel_id = data.vessel_id
        
        self.time_interval1 = data.discharging_info_json['dischargingStages']['stageDuration']*60 # in 60*4 min
        self.num_stage_interval =  data.discharging_info_json['dischargingStages']['stageOffset']
        
        self.config = data.config
        print('time interval:', self.time_interval1)
        
        self.seawater_density = float(data.port_json['portDetails'].get('seawaterDensity', 1.025))
        self.max_draft = float(data.port_json['portDetails'].get('maxShipDepth', 22))
        
        self.preloaded_cargos = []
        self.commingle_loading, self.commingle_preloaded = False, False
        
        self.time_interval = {}
        
        cargo_info_ = {}
        
        # initial and final ROB: 'ROB', 'depROBweight'
        self._get_rob(data.vessel_json['onHand'], cargo_info_)
        
        cargo_info_['cargoTanksUsed'], cargo_info_['ballastTanksUsed'] = [], []
        # initial Ballast, final Ballast
        cargo_info_['ballast'] = []
        self._get_ballast(data.discharge_json['planDetails']['arrivalCondition']['dischargePlanBallastDetails'], cargo_info_)
        self._get_ballast(data.discharge_json['planDetails']['departureCondition']['dischargePlanBallastDetails'], cargo_info_)
        # 'tankToBallast', 'tankToDeballast', 'eduction'
        self._get_eduction(cargo_info_)
        
        tank_ = [t_ for t_ in cargo_info_['tankToBallast'] if t_[0] == 'W' ]
        # self.num_pump = 1 if (len(cargo_info_['tankToBallast']) + len(cargo_info_['tankToDeballast']) <= 4) else 2
        self.num_pump = 1 if (len(tank_) <= 4) else 2
        print('num ballast pump:', self.num_pump)
        
        self.discharging_rate = {}
        
        cargo_info_['discharging_order1'], cargo_info_['discharging_order2'] = {}, {}
        cargo_info_['discharging_qty1'] = {}
        cargo_info_['slopTankFirst'] = {}
        
        numStages_ = 0
        
        for d_ in data.discharging_info_json['dischargingSequences']['dischargeDelays']:
            if d_['dsCargoNominationId'] in [0]:
                print("*** onboard cargo available")
                pass
            else:
                ## at cargo level                
                cargo_ = 'P'+str(d_['dsCargoNominationId'])
                order_ = d_['sequenceNumber']
                self.discharging_rate[order_] = d_.get('dischargingRate', 7000)
                
                tank_id_ = d_.get('tankId', None)
                if tank_id_ not in [None] and self.vessel.info['tankId'][tank_id_] in self.vessel.info['slopTank']:
                    cargo_info_['slopTankFirst'][cargo_] = (self.vessel.info['tankId'][tank_id_], order_)

                numStages_ = max(numStages_, order_)
                if cargo_ not in cargo_info_['discharging_order1']:
                    cargo_info_['discharging_order1'][cargo_] = [order_]
                    cargo_info_['discharging_qty1'][cargo_] = [d_['quantity']]
                    
                else:
                    cargo_info_['discharging_order1'][cargo_].append(order_)
                    cargo_info_['discharging_qty1'][cargo_].append(d_['quantity'])
                    
                if order_ not in cargo_info_['discharging_order2']:
                    cargo_info_['discharging_order2'][order_] = [cargo_]
                else:
                    cargo_info_['discharging_order2'][order_].append(order_)
                
                
                
        # multiple discharge of single cargo        
        cargo_info_['multiDischarge'] = [k_ for k_, v_ in cargo_info_['discharging_order1'].items() if len(v_) > 1]
        cargo_info_['numStages'] = numStages_
                 
        cargo_info_['timing_delay1'] = [0 for d_ in range(cargo_info_['numStages'])]
                
        # add plans -------------------------------------------------------------------------
        cargo_info_['cargo_plans'] = []
        cargo_info_['cargo_tank'] = {}
        cargo_info_['density'], cargo_info_['api'], cargo_info_['temperature'] = {}, {}, {}
        cargo_info_['cargoId'], cargo_info_['colorCode'], cargo_info_['abbreviation'] = {}, {}, {}
        cargo_info_['commingle'] = {}
        cargo_info_['cargo_pump'] = {}
        
        cargoDetails_ = data.discharging_info_json['dischargeQuantityCargoDetails']
        
        cargo_info_['cargoNominationId'] = {'P'+ str(l_['cargoNominationId']) : 'P'+ str(l_['dsCargoNominationId']) for l_ in cargoDetails_}
        cargo_info_['dsCargoNominationId'] = {'P'+str(l_['dsCargoNominationId']) : 'P'+ str(l_['cargoNominationId']) for l_ in cargoDetails_}
        
        # initial plan
        # 'initCargoWeight', 'initCargoWeight1'
        self._get_plan(data.discharge_json['planDetails']['arrivalCondition']['dischargePlanStowageDetails'],
                       cargo_info_, cargoDetails_, 
                       commingleDetails = data.discharge_json['planDetails']['arrivalCondition']['dischargePlanCommingleDetails'],
                       initial = True)
        
        cargo_info_['pre_cargo'] = [k_ for k_,v_ in cargo_info_['cargo_tank'].items()]
        cargo_info_['discharging_order'] = [[] for d_ in range(cargo_info_['numStages'])]
        cargo_info_['discharging_qty'] = [0 for d_ in range(cargo_info_['numStages'])]
        for (k_, v_), (k1_, v1_) in zip(cargo_info_['discharging_order1'].items(), cargo_info_['discharging_qty1'].items()):
            assert k_ == k1_
            for a_, b_ in zip(v_, v1_):
                cargo_info_['discharging_order'][a_-1].append(k_)
                cargo_info_['discharging_qty'][a_-1] += -b_
                
                
        cargo_info_['tank_cargo'] = {k1_:k_  for k_, v_ in cargo_info_['cargo_tank'].items() for k1_ in v_}
                
        ##        
        # cargo_info_['discharging_order'] = ['P200000178', 'P200000176', 'P200000177']
        # cargo_info_['discharging_order1'] = {'P200000178': [1], 'P200000176': [2], 'P200000177': [3]}
        # cargo_info_['multiDischarge'] = False
        
        cargo_info_['stripping_tanks'] = {d__+1:[]  for d__,d_ in enumerate(cargo_info_['discharging_order'])}
        dep_plan_, dep_tanks_, dep_weight_ = [], [], {}
        for l_ in data.discharge_json['planDetails']['departureCondition']['dischargePlanStowageDetails']:
            wt_ = l_.get('quantityMT', 0.0)
            # print(wt_,l_['tankId'])
            if wt_ not in [None] and float(wt_) > 0:
                dep_plan_.append(l_)
                dep_tanks_.append(self.vessel.info['tankId'][l_['tankId']])
                cargo_ = 'P'+str(l_['cargoNominationId'])
                if cargo_ not in dep_weight_:
                    dep_weight_[cargo_] = float(wt_)
                else:
                    dep_weight_[cargo_] += float(wt_)
                    
        cargo_info_['depCargoWeight1'] = dep_weight_
        
        all_tanks_ = list(self.vessel.info['cargoTanks'].keys())
        empty_tanks_ = set(all_tanks_) - set(dep_tanks_)
        for i_ in data.discharge_json['planDetails']['arrivalCondition']['dischargePlanStowageDetails']:
            tank_ = self.vessel.info['tankId'][i_['tankId']]
            if tank_ in empty_tanks_:
                info_ = dict(i_)
                info_['quantityMT'] = '0.0'
                dep_plan_.append(info_)
                
        # cargo_info_['multiDischarge'] =1
        if not cargo_info_['multiDischarge']:
            cargo_info_['multiDischarge'] = ['None']
        else:
            # self.error['Discharging Error'] = ['Multi discharging not tested!!']
            # return
            pass
            
        
        if not cargo_info_['multiDischarge']:
            print('No multiple discharge for each cargo')
            # cargo_info_['loading_order'] = ['A','B','C','D']
            for o__,o_ in enumerate(cargo_info_['discharging_order'][:-1]):
                
                not_cargo_ = cargo_info_['discharging_order'][o__+1:]
                # print(not_cargo_)
                self._get_plan(dep_plan_,
                            cargo_info_, cargoDetails_, 
                            commingleDetails = data.discharge_json['planDetails']['departureCondition']['dischargePlanCommingleDetails'],
                            initial = False, not_cargo = not_cargo_, strip_info=True)
            
            # final plan     
            self._get_plan(data.discharge_json['planDetails']['departureCondition']['dischargePlanStowageDetails'],
                       cargo_info_, cargoDetails_, 
                       commingleDetails = data.discharge_json['planDetails']['departureCondition']['dischargePlanCommingleDetails'],
                       initial = False, strip_info=True)
            
        else:
            print('multiple_discharge:', cargo_info_['multiDischarge'])
            
            # final plan 
            self._get_plan(data.discharge_json['planDetails']['departureCondition']['dischargePlanStowageDetails'],
                           cargo_info_, cargoDetails_, 
                           commingleDetails = data.discharge_json['planDetails']['departureCondition']['dischargePlanCommingleDetails'],
                           initial = False)
            
            final_plan_ = cargo_info_['cargo_plans'].pop()
            cargo_info_['final_plan'] = final_plan_
            
            cargo_info_['final_cargo_tank'] = {}
            for k_, v_ in final_plan_.items():
                if v_[0]['quantityMT'] > 0:
                    if v_[0]['cargo'] not in cargo_info_['final_cargo_tank']:
                        cargo_info_['final_cargo_tank'][v_[0]['cargo']] = [k_]
                    else:
                        cargo_info_['final_cargo_tank'][v_[0]['cargo']].append(k_)
                        
            cargo_info_['empty_tank'] = {}
            for k_, v_ in cargo_info_['cargo_tank'].items():
                cargo_info_['empty_tank'][k_] = list(set(v_) - set(cargo_info_['final_cargo_tank'].get(k_,[])))
                
            
            cargo_info_['portOpt'] = sum([v_[:-1] for k_, v_ in cargo_info_['discharging_order1'].items() if len(v_) > 1], [])
            self.info = cargo_info_
            self.solver = 'AMPL'
            self._get_plan_ampl()
            self.get_param()
            self.write_ampl(IIS=False, ave_trim = self.ave_trim)
            
            self.module = 'DISCHARGING'
            self.vessel_id  = '1'
            self.discharge_mode = True
            
            gen_output = Generate_plan(self)
            gen_output.IIS = False
            gen_output.run(num_plans=1)
            
            plan_check = Check_plans(self, reballast = True)
            plan_check._check_plans(gen_output)
            
            # # # input("Press Enter to continue...")
    
            
            plan_ = gen_output.plans.get('ship_status',[]) # only non-empty tank
            # plan_ = []
            if len(plan_) == 0:
                self.error['Optimization Error'] = ['No discharge plan generated!!']
                return
            else:
                
                cargo_info_['stability_values'] = plan_check.stability_values[0]
                plan__ = []
                empty_tanks_ = []
                ballast_vol_ = {}
                for k_, v_ in plan_[0].items():
                    
                    ballast_vol__ = 0.    
                    for k1_, v1_ in  v_['ballast'].items():
                        ballast_vol__ += v1_[0].get('vol',0.)
                    ballast_vol_[k_] = ballast_vol__
                    
                    if k_ not in ['0']:
                        info_ = {}
                      
                        cargo_to_discharge1_ = cargo_info_['discharging_order'][int(k_)-1]
                        
                        fill_tank_ = []
                        for k1_, v1_ in  v_['cargo'].items():
                            
                            info_[k1_] = [{'abbreviation': cargo_info_['abbreviation'][v1_[0]['parcel']],
                                          'api': v1_[0]['api'],
                                          'cargo': v1_[0]['parcel'],
                                          'cargoId': cargo_info_['cargoId'][v1_[0]['parcel']],
                                          'colorCode': cargo_info_['colorCode'][v1_[0]['parcel']],
                                          'corrUllage': v1_[0]['corrUllage'],
                                          'lcg': v1_[0]['lcg'],
                                          'quantityMT': v1_[0]['wt'],
                                          'quantityM3': v1_[0]['vol'],
                                          'SG': v1_[0]['SG'],
                                          'tankId': self.vessel.info['tankName'][k1_],
                                          'tcg': v1_[0]['tcg'],
                                          'temperature': v1_[0]['temperature']
                                          }]
                            
                            fill_tank_.append(k1_)
                        
                        cargo_to_discharge_ = [cargo_info_['dsCargoNominationId'][cc_]  for cc_ in cargo_to_discharge1_]
                            
                        empty_ = set(self.vessel.info['cargoTankNames']) - set(fill_tank_)
                        # print(k_, cargo_to_discharge_, empty_)   
                        
                        for t__, t_ in enumerate(empty_):
                            
                            # print(t__, t_)
                            if t_ in cargo_info_['cargo_plans'][0]:
                                info_[t_] =  deepcopy(cargo_info_['cargo_plans'][0][t_])
                                info_[t_][0]['quantityMT'] = 0.
                                info_[t_][0]['quantityM3'] = 0.
                            else:
                                info_[t_] = [{'quantityMT': 0.0, 'quantityM3': 0.0}]
                               
                            # check_ = [c1_ for c1_ in cargo_to_discharge1_ if c1_ in cargo_info_['multiDischarge']]
                            check_ = False
                            if check_:
                                self.error['Optimization Error'] = ['No discharge plan generated!!']
                                return
                            elif t_ not in empty_tanks_ and info_[t_][0]['cargo'] in cargo_to_discharge_:
                                cargo_info_['stripping_tanks'][int(k_)].append(t_)
                                empty_tanks_.append(t_)

                            # if cargo_to_discharge_ == info_[t_][0]['cargo']:
                            #     cc1_ = cargo_info_['cargoNominationId'][cargo_to_discharge_]
                            #     if cc1_ in cargo_info_['multiDischarge']:
                            #         ports_ = cargo_info_['discharging_order1'][cc1_]
                            #         appended_ = [True for a_, b_ in cargo_info_['stripping_tanks'].items() if t_ in b_ and a_ in ports_]
                            #         if True in appended_:
                            #             pass
                            #         else:
                            #             cargo_info_['stripping_tanks'][int(k_)].append(t_)
                                      
                            #     else:
                            #         cargo_info_['stripping_tanks'][int(k_)].append(t_)
                            
                        plan__.append(info_)
                    
            
            ## 
            # with open("plan1.json", "w") as outfile:
            #     json.dump(plan__, outfile)
            
            # with open("plan2.json", "r") as outfile:
            #    plan__ = json.load(outfile)
            # cargo_info_['stripping_tanks'] = {1: [], 2: ['1P', '3P', '3S', '1S'], 3: [], 4: ['2C', '4C']}
            
            # plan_check = Check_plans(self)
            # plan_check._check_plans(gen_output.plans.get('ship_status',[]), gen_output.plans.get('cargo_tank',[]))
            
            cargo_info_['cargo_plans'] += plan__
            
        # cargo_info_['cargo_plans'].append(final_plan_)
        
        cargo_info_['ballast_vol'] = ballast_vol_
        print('strip_tanks:', cargo_info_['stripping_tanks'])
        # self._get_COW_tanks(cargo_info_)
        # print('collect cow_tanks:', cargo_info_['cow_tanks'])
        self.info = cargo_info_
        ## discharging_order1 and discharging_order dsCargoNomination 
        
        
    def _get_COW_tanks(self, cargo_info):
        TANKS_TO_COW = ['3C','1C','2C','4C','5C']
        cargo_info['cow_tanks'] = {1: [], 2: [], 3: [], 4: [], 5:[], 6:[], 7:[], 8:[], 9:[]}
        
        for t_ in TANKS_TO_COW:
            for k_, v_ in cargo_info['stripping_tanks'].items():
                if t_ in v_:
                    cargo_info['cow_tanks'][k_].append(t_)
                    
                    
            
            
            
        
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
                
                
    
        
                
    def _gen_stripping(self, result):
        # INDEX = self.config["gantt_chart_index"]
        
        # MAX_RATE = {1: 12000, 2:11129, 3:11553, 4:5829}
        
        # TIME_SEP = 2
        # TIME_PUMP_WARM = 30
        # TIME_AIR_PURGE = 2 ## if required
        # TIME_INITIAL = TIME_SEP + TIME_PUMP_WARM 
        # TIME_INIT_RATE = 20
        # TIME_INC_RATE = 15 # 15000m3/hr: 45mins 10000-15000m3/hr: 30mins 5000-10000m3/hr: 15mins

        
        ## manually set which tanks to COW at each stage
#        self.info['cow_tanks'] = {1: [], 2: ['1P','3P','1S','3S'], 3: [], 4: [], 5:[], 6:[], 7:[], 8:[]}
        # print('cow tanks', self.info['cow_tanks'])
        self.seq = {}
        
        slopP = [t_ for t_ in self.vessel.info['slopTank'] if t_[-1] == 'P'][0]
        slopS = [t_ for t_ in self.vessel.info['slopTank'] if t_[-1] == 'S'][0]
        start_time_ = 0 # 
        
        INDEX_ = INDEX + [slopP, slopS]
        for p__, p_ in enumerate(self.info['cargo_plans'][:-1]):
            
            self.seq[str(p__+1)] = {}
            self.seq[str(p__+1)]['dischargingRate'] = {}
            result_ = result[p__+1]
            
            df_ = pd.DataFrame(index=INDEX_)
            df_['Initial'] = None
            
            cargo_to_discharge1_ = self.info['discharging_order'][p__]
            cargo_to_discharge_ = [self.info['dsCargoNominationId'][cc_] for cc_ in cargo_to_discharge1_]
            
            self.seq[str(p__+1)]['exactTime'] = {}
            # print(p__+1, cargo_to_discharge_,'cargo discharging')
            
            
            ##--------------------------------------------------------------------
            initial_stage_ = result_['stages_timing']['Initial Rate'][0]
            ddf_ = result_['gantt_chart_volume'].filter([initial_stage_])
            
            # for each cargo volume
            df_['Initial']['Time'] = int(initial_stage_)
            for t_ in ddf_.itertuples():
                cc_ = p_[t_[0]][0].get('cargo', None)
                if cc_:
                    df_['Initial'][t_[0]] = (cc_, t_[1])
                else:
                    df_['Initial'][t_[0]] = None
                    
            stages_ = {"initialCondition":(df_['Initial']['Time'], df_['Initial']['Time'])}
            
            self.seq[str(p__+1)]['exactTime']['Initial'] = initial_stage_
            # initial rate ---------------------------------
            # 20 min
            initial_rate_stage_ = result_['stages_timing']['Initial Rate'][1]
            df_['InitialRate'] =  None
            df_['InitialRate']['Time'] = int(initial_rate_stage_)
            ddf_ = result_['gantt_chart_volume'].filter([initial_rate_stage_])
            for t_ in ddf_.itertuples():
                cc_ = p_[t_[0]][0].get('cargo', None)
                if cc_:
                    df_['InitialRate'][t_[0]] = (cc_, t_[1])
                else:
                    df_['InitialRate'][t_[0]] = None
            
            for t_ in df_['InitialRate'].iteritems():
                if t_[0] in result_['tanksDischarged']:
                    if t_[1][0] not in cargo_to_discharge_:
                        df_['InitialRate'][t_[0]] = (cargo_to_discharge_[0], df_['InitialRate'][t_[0]][1])

            # time_diff_ = df_['InitialRate']['Time'] - df_['Initial']['Time']
            # total_vol_change_ = 0
            # rate_per_tank_ = {}
            # for t_ in result_['tanksDischarged']:
            #     vol_change_ = df_['Initial'][t_][1] - df_['InitialRate'][t_][1]
            #     rate_per_tank_[t_] = vol_change_/time_diff_*60
            #     total_vol_change_ += vol_change_
            time_diff_ = initial_rate_stage_ - initial_stage_
            self.seq[str(p__+1)]['dischargingRate']['InitialRatePerTank']  = self._cal_rate('Initial', 'InitialRate', df_, result_, time_diff_)
            self.seq[str(p__+1)]['dischargingRate']['InitialRatePerTank']['time'] = [initial_stage_, initial_rate_stage_]
                
            # discharging_rate_ = INITIAL_RATE
            # discharging_rate_per_tank_ = discharging_rate_/total_tank_
            # cargo_loaded_per_tank_ = cargo_loaded_/total_tank_
            stages_['initialRate'] = (df_['Initial']['Time'], df_['InitialRate']['Time'])
            self.seq[str(p__+1)]['exactTime']['InitialRate'] = initial_rate_stage_
            
            # self.seq[str(p__+1)]['initialRate'] = total_vol_change_/time_diff_*60
            # self.seq[str(p__+1)]['initialRatePerTank'] = rate_per_tank_
            
            
            # increase to max rate ----------------------------------------------------------------
            inc_to_max_stage_ = result_['stages_timing']['Increase to Max Rate'][1]
            df_['IncMax'] =  None
            df_['IncMax']['Time'] = int(inc_to_max_stage_) # end time
            ddf_ = result_['gantt_chart_volume'].filter([inc_to_max_stage_])
            for t_ in ddf_.itertuples():
                cc_ = p_[t_[0]][0].get('cargo', None)
                if cc_:
                    df_['IncMax'][t_[0]] = (cc_, t_[1])
                else:
                    df_['IncMax'][t_[0]] = None
                    
            for t_ in df_['IncMax'].iteritems():
                if t_[0] in result_['tanksDischarged']:
                    if t_[1][0] not in cargo_to_discharge_:
                        df_['IncMax'][t_[0]] = (cargo_to_discharge_[0], df_['IncMax'][t_[0]][1])
             
            
            stages_['increaseToMaxRate'] = (df_['InitialRate']['Time'], df_['IncMax']['Time'])
            self.seq[str(p__+1)]['exactTime']['IncMax'] = inc_to_max_stage_
           
            
            time_diff_ =  inc_to_max_stage_ -  initial_rate_stage_         
            self.seq[str(p__+1)]['dischargingRate']['IncMaxPerTank']  = self._cal_rate('InitialRate', 'IncMax', df_, result_, time_diff_)
            self.seq[str(p__+1)]['dischargingRate']['IncMaxPerTank']['time'] = [initial_rate_stage_, inc_to_max_stage_]
            
            # max discharging -----------------------------------------------------------------------
            # discharging_rate_ = max_rate_
            i1_, i2_ = result_['stages_timing']['Max Rate Discharging'][0], result_['stages_timing']['Max Rate Discharging'][1]
            stage_ = 1
            ballast_ = [(0, 'Initial')]
            
            time_interval_ = [int(col_) for col_ in result_['gantt_chart_volume'] if i1_ < col_ <= i2_]
            if len(time_interval_) == 1:
                time_interval_ = 60
            else:
                time_interval_ = time_interval_[1]-time_interval_[0]
            # print('time_interval_',time_interval_)
            
            stage1_ = 'IncMax'
            pre_col_ = inc_to_max_stage_
            if time_interval_ < 120:
                print('Time interval less than 2hr')
                ss_ = 'MaxDischarging' + str(stage_)
                col_ = result_['stages_timing']['Increase to Max Rate'][1]
                df_[ss_] =  None
                df_[ss_]['Time'] = int(col_) # end time
                
                ballast_.append((int(col_),ss_))
                ddf_ = result_['gantt_chart_volume'].filter([col_])
                for t_ in ddf_.itertuples():
                    cc_ = p_[t_[0]][0].get('cargo', None)
                    if cc_:
                        df_[ss_][t_[0]] = (cc_, t_[1])
                    else:
                        df_[ss_][t_[0]] = None
                        
                        
                for t_ in df_[ss_].iteritems():
                    if t_[0] in result_['tanksDischarged']:
                        if t_[1][0] not in cargo_to_discharge_:
                            df_[ss_][t_[0]] = (cargo_to_discharge_[0], df_[ss_][t_[0]][1])
                    
                self.seq[str(p__+1)]['dischargingRate'][ss_+'PerTank'] = self.seq[str(p__+1)]['dischargingRate']['IncMaxPerTank'] 
                self.seq[str(p__+1)]['exactTime'][ss_] = col_
                
                stage_ += 1
                stage1_ = ss_
                pre_col_ = col_
                
                self.seq[str(p__+1)]['incMaxAndMaxDischarging'] = True
            else:
                self.seq[str(p__+1)]['incMaxAndMaxDischarging'] = False # incMax == MaxDischarging
                
                
            for col_ in result_['gantt_chart_volume']:
                # print(col_) 
                if i1_ < col_ <= i2_:
                    ss_ = 'MaxDischarging' + str(stage_)
                    df_[ss_] =  None
                    df_[ss_]['Time'] = int(col_) # end time
                    
                    ballast_.append((int(col_),ss_))
                    ddf_ = result_['gantt_chart_volume'].filter([col_])
                    for t_ in ddf_.itertuples():
                        cc_ = p_[t_[0]][0].get('cargo', None)
                        if cc_:
                            df_[ss_][t_[0]] = (cc_, t_[1])
                        else:
                            df_[ss_][t_[0]] = None
                            
                    for t_ in df_[ss_].iteritems():
                        if t_[0] in result_['tanksDischarged']:
                            if t_[1][0] not in cargo_to_discharge_:
                                df_[ss_][t_[0]] = (cargo_to_discharge_[0], df_[ss_][t_[0]][1])

                    time_diff_ = col_ - pre_col_
                    self.seq[str(p__+1)]['dischargingRate'][ss_+'PerTank'] = self._cal_rate(stage1_, ss_, df_, result_, time_diff_)
                    self.seq[str(p__+1)]['dischargingRate'][ss_+'PerTank']['time'] = [pre_col_, col_]
                    self.seq[str(p__+1)]['exactTime'][ss_] = col_
                    stage_ += 1
                    stage1_ = ss_
                    pre_col_ = col_
                    # print(ss_, col_)
            single_max_stage_ = True if stage_ <= 2 else False
            
            ballast1_, time1_ = [], [] # future stage for ballast 
            # remove last MaxDischarging if needed
            if ballast_[-1][0] - ballast_[-2][0] < time_interval_:
                # last_time_ = ballast_[-2][0]
                ballast1_.append(ballast_[-1][1]) 
                time1_.append(ballast_[-1][0])
                ballast_.pop()
                
            # stages_['dischargingAtMaxRate'] = (df_['IncMax']['Time'], df_[ss_]['Time'])
            
            last_discharging_max_rate_stage_ = ss_
            pre_stage_ = int(ss_[14:]) - 1
            if pre_stage_ > 0:
                ss0_ = 'MaxDischarging'+str(pre_stage_)
                if df_[ss_]['Time'] == df_[ss0_]['Time']:
                    print(df_[ss_]['Time'])
                    df_[ss_]['Time'] += 1

            stages_['dischargingAtMaxRate'] = (df_['IncMax']['Time'], df_[ss_]['Time'])
            
            # last max stage before stripping
            # if p__+1 < len(self.info['loading_order'])+1:
            # ballast_.append((int(df_[ss_]['Time']),ss_)) # need to monitor ballast
            # ballast_stop_.append((int(df_[ss_]['Time']),ss_))
            
            # ballast1_, time1_ = [ss_], [int(df_[ss_]['Time'])]
            
            # stripping ------------------------------------------------------------
            # time_ = 1
            stripping_ = False
            if 'Reduced Rate' in  result_['stages_timing']:
                i1_ = result_['stages_timing']['Reduced Rate'][0]
                i2_ = result_['stages_timing']['Reduced Rate'][1]
                
            elif "COW/Stripping" in result_['stages_timing']:
                i1_ = result_['stages_timing']['COW/Stripping'][0]
                i2_ = result_['stages_timing']['COW/Stripping'][1]
                stripping_ = True
                
            if "Slop Discharge" in result_['stages_timing'] and p__+2 != len(self.info['cargo_plans']):
                i2_ = result_['stages_timing']['Slop Discharge'][1]
                
            # print('start-end-stripping:', i1_, i2_) 
            
            stage_ = 1
            pre_col_ = i1_
            for col_ in result_['gantt_chart_volume']:
                # print(col_) 
                if i1_ < col_ <= i2_:
                    ss_ = 'Stripping' + str(stage_)
                    df_[ss_] =  None
                    df_[ss_]['Time'] = int(col_) # end time
                    ddf_ = result_['gantt_chart_volume'].filter([col_])
                    ballast1_.append(ss_)
                    time1_.append(int(col_))
                    for t_ in ddf_.itertuples():
                        cc_ = p_[t_[0]][0].get('cargo', None)
                        if cc_:
                            df_[ss_][t_[0]] = (cc_, t_[1])
                        else:
                            df_[ss_][t_[0]] = None
                            
                    for t_ in df_[ss_].iteritems():
                        if t_[0] in result_['tanksDischarged']:
                            if t_[1][0] not in cargo_to_discharge_:
                                df_[ss_][t_[0]] = (cargo_to_discharge_[0], df_[ss_][t_[0]][1])
                    
                    # print('dischargingRate:', ss_, col_)
                    time_diff_ = col_ - pre_col_
                    ignore_zero_ = True
                    if col_ == result_['stages_timing'].get('Slop Discharge',[0,0])[-1]:
                        # print('Slop Discharge in stage')
                        ignore_zero_ = False
                    self.seq[str(p__+1)]['dischargingRate'][ss_+'PerTank'] = self._cal_rate(stage1_, ss_, df_, result_, time_diff_, ignore_zero= ignore_zero_)
                    self.seq[str(p__+1)]['dischargingRate'][ss_+'PerTank']['time'] = [pre_col_, col_]
                    self.seq[str(p__+1)]['exactTime'][ss_] = col_
                    
                    stage_ += 1
                    stage1_ = ss_
                    pre_col_ = col_
                    # print(ss_, col_)
            stages_['stripping'] = (df_[last_discharging_max_rate_stage_]['Time'], df_[ss_]['Time'])
            
            ## get the ballast monitoring after maxdischarging
            next_time_ = ballast_[-1][0] + time_interval_
            while True:
                nearest_time_ = min(time1_, key=lambda x_:abs(x_-next_time_))
                a_ = time1_.index(nearest_time_)
                b_ = ballast1_[a_]
                if (nearest_time_,b_) not in ballast_:
                    ballast_.append((nearest_time_,b_))
                
                next_time_ += time_interval_
                if next_time_ > time1_[-1]:
                    break
                    
                
            if p__+2 < len(self.info['cargo_plans']) and ss_ != ballast_[-1][1]:
                print('Not Last cargo. Add last stripping stage')
                ballast_.append((df_[ss_]['Time'], ss_))
                
            ballast_limit_ = {}
            for aa_, (bb_,cc_) in enumerate(ballast_):
                if cc_[:3] in ['Max', 'Str']:
                    add_time_ = 0 if cc_ not in ['MaxDischarging1'] else result_['stages_timing']['Initial Rate'][0]
                    time_ = bb_ - ballast_[aa_-1][0] - add_time_
                    ballast_limit_[cc_] = time_
                    # print(cc_,time_)
                    
                    
                    
            last_stripping_ = ss_
            # print(ballast_)
            
            if p__+2 == len(self.info['cargo_plans']):
                # print('last cargo')
                # last_time_ = df_[df_.columns[-1]]['Time']
                df_['Depart'] = None
                
                for k_, v_ in self.info['cargo_plans'][-1].items():
                    df_['Depart'][k_] = (v_[0]['cargo'], round(v_[0]['quantityM3'],2))
                    
                for t_ in df_['Depart'].iteritems():
                    if t_[0] in result_['tanksDischarged']:
                        if t_[1][0] not in cargo_to_discharge_:
                            df_['Depart'][t_[0]] = (cargo_to_discharge_[0], df_['Depart'][t_[0]][1])
                
                ss_ = 'Depart'
                time2_, time3_ = 0, 0
                if 'Dry Check' in result_['stages_timing']:
                    time2_ += (result_['stages_timing']['Dry Check'][1]-result_['stages_timing']['Dry Check'][0])
                    time3_ = max(time3_, result_['stages_timing']['Dry Check'][1])
                    
                if 'Slop Discharge' in result_['stages_timing']:
                    time2_ += (result_['stages_timing']['Slop Discharge'][1]-result_['stages_timing']['Slop Discharge'][0])
                    time3_ = max(time3_, result_['stages_timing']['Slop Discharge'][1])
                    
                    time_diff_ = result_['stages_timing']['Slop Discharge'][1] - result_['stages_timing']['Slop Discharge'][0]
                    
                    self.seq[str(p__+1)]['dischargingRate']['slopDischargePerTank'] = {}
                    total_rate_ = 0
                    info_per_tank_ = {'vol':{}, 'qty':{}, 'ullage':{}, 'dsCargoNominationId':{}}
                    for tank_ in result_['slopDischarge']:
                        a_ = result_['gantt_chart_operation_end'][result_['gantt_chart_operation_end'].index == tank_]
                        b_ = next(k_ for k_, v_ in a_.items() if v_[tank_] == 'Dry Check')
                        vol_ = result_['gantt_chart_volume'][b_][tank_]
                        rate_ = vol_/time_diff_*60
                        total_rate_ += rate_
                        self.seq[str(p__+1)]['dischargingRate']['slopDischargePerTank'][tank_] = rate_
                        
                        
                        vol_ = 0.
                        tankId_ = self.vessel.info['tankName'][tank_]    
                        info_per_tank_['vol'][tankId_] = str(vol_)
                        info_per_tank_['qty'][tankId_] = str(round(self.loadable.info['parcel'][cargo_to_discharge_[0]]['maxtempSG']*vol_,1))
                        pp_ = df_['Depart'][tank_][0]
                        pp_ = self.info['cargoNominationId'][pp_]
                        info_per_tank_['dsCargoNominationId'][tankId_]  = int(pp_[1:])
                        # print(df[stage2][t_][0], t_, df[stage2][t_][1])
                        if vol_ > 0.:
                            corrUllage_ = str(round(self.vessel.info['ullage'][str(tankId_)](vol_).tolist(), 6))
                        else:
                            corrUllage_ = str(self.vessel.info['ullageEmpty'][str(tankId_)])
                                                                     
                        info_per_tank_['ullage'][tankId_] = corrUllage_
            
                        
                        
                    self.seq[str(p__+1)]['dischargingRate']['slopDischargePerTank']['total'] = total_rate_
                    self.seq[str(p__+1)]['dischargingRate']['slopDischargePerTank']['time'] = result_['stages_timing']['Slop Discharge']
                    self.seq[str(p__+1)]['dischargingRate']['slopDischargePerTank']['other'] = info_per_tank_

                if 'Fresh Oil Discharge' in result_['stages_timing']:
                    time2_ += (result_['stages_timing']['Fresh Oil Discharge'][1]-result_['stages_timing']['Fresh Oil Discharge'][0])
                    time3_ = max(time3_, result_['stages_timing']['Fresh Oil Discharge'][1])
                    
                    info_per_tank_ = {'vol':{}, 'qty':{}, 'ullage':{}, 'dsCargoNominationId':{}}
                    
                    time_diff_ = result_['stages_timing']['Fresh Oil Discharge'][1] - result_['stages_timing']['Fresh Oil Discharge'][0]
                    tank_ = result_['freshOilDischarge'][-1]
                    a_ = result_['gantt_chart_operation_end'][result_['gantt_chart_operation_end'].index == tank_]
                    b_ = next(k_ for k_, v_ in a_.items() if v_[tank_] == 'Dry Check')
                    vol_ = result_['gantt_chart_volume'][b_][tank_]
                    rate_ = vol_/time_diff_*60
                    
                    
                    vol_ = 0.
                    tankId_ = self.vessel.info['tankName'][tank_]    
                    info_per_tank_['vol'][tankId_] = str(vol_)
                    info_per_tank_['qty'][tankId_] = str(round(self.loadable.info['parcel'][cargo_to_discharge_[0]]['maxtempSG']*vol_,1))
                    pp_ = df_['Depart'][tank_][0]
                    pp_ = self.info['cargoNominationId'][pp_]
                    info_per_tank_['dsCargoNominationId'][tankId_]  = int(pp_[1:])

                    # print(df[stage2][t_][0], t_, df[stage2][t_][1])
                    if vol_ > 0.:
                        corrUllage_ = str(round(self.vessel.info['ullage'][str(tankId_)](vol_).tolist(), 6))
                    else:
                        corrUllage_ = str(self.vessel.info['ullageEmpty'][str(tankId_)])
                                                                 
                    info_per_tank_['ullage'][tankId_] = corrUllage_
                    
                    self.seq[str(p__+1)]['dischargingRate']['freshOilDischargePerTank'] = {tank_:rate_, 'total':rate_}
                    self.seq[str(p__+1)]['dischargingRate']['freshOilDischargePerTank']['time'] = result_['stages_timing']['Fresh Oil Discharge']
                    self.seq[str(p__+1)]['dischargingRate']['freshOilDischargePerTank']['other'] = info_per_tank_
                    
                if 'Final Stripping' in result_['stages_timing']:
                    time2_ += (result_['stages_timing']['Final Stripping'][1]-result_['stages_timing']['Final Stripping'][0])
                    time3_ = max(time3_, result_['stages_timing']['Final Stripping'][1])
                    
                df_['Depart']['Time'] = int(time3_)
                ballast_limit_['Depart'] = int(time2_)
                ballast_.append((df_['Depart']['Time'], 'Depart'))
                self.seq[str(p__+1)]['exactTime'][ss_] = time3_
            
            
            
            ## cargo pump info
            pump_ = result_['fixedPumpTimes'].to_dict('split')
            pump__ = {}
            for a__, a_ in  enumerate(pump_['index']):
                if 'open' in pump_['data'][a__]:
                    in1_ = [i__ for i__,i_ in enumerate(pump_['data'][a__]) if i_ == 'open']
                    in2_ = [i__ for i__,i_ in enumerate(pump_['data'][a__]) if i_ == 'close']
                    
                    pump__[a_] = []
                    for i_, j_  in zip(in1_, in2_):
                        pump__[a_] += [pump_['columns'][i_], pump_['columns'][j_]]
                    
            # print(pump__)  
            self.seq[str(p__+1)]['pump'] = pump__
            
            ## get strip tanks
            operations_ = ['Strip', 'Full COW', 'Slop Discharge', 'Fresh Oil Discharge', 'Bottom COW', 'Top COW']
            tanks_ = result_['gantt_chart_operation_end'].to_dict('split')
            
            for o_ in operations_:
                tanks__ = {}
                for a__, a_ in  enumerate(tanks_['index']):
                    if o_ in tanks_['data'][a__]:
                        in1_ = tanks_['data'][a__].index(o_)
                        tanks__[a_] = [tanks_['columns'][in1_-1], tanks_['columns'][in1_]]
                        
                # print(o_, tanks__)  
                self.seq[str(p__+1)][o_] = tanks__
            
             
            self.seq[str(p__+1)]['gantt'] = df_        
            self.seq[str(p__+1)]['cargoDischarged'] = cargo_to_discharge_
            self.seq[str(p__+1)]['info'] = result_
            self.seq[str(p__+1)]['ballast'] = list(ballast_) # need to get ballast for these stages
            self.seq[str(p__+1)]['stageInterval'] = stages_ # time duration for each stage
            self.seq[str(p__+1)]['startTime'] = start_time_ # start time without delay
            self.seq[str(p__+1)]['lastStage'] = ss_
            self.seq[str(p__+1)]['timeNeeded'] = df_[ss_]['Time']
            self.seq[str(p__+1)]['singleMaxStage'] = single_max_stage_
            self.seq[str(p__+1)]['ballastLimit'] = ballast_limit_ # time for ballast at each stage
            self.seq[str(p__+1)]['stripping'] = stripping_ # boolean
            
            self.seq[str(p__+1)]['timeInterval'] = time_interval_
            self.seq[str(p__+1)]['lastMaxDischarging'] = last_discharging_max_rate_stage_
            self.seq[str(p__+1)]['lastStripping'] = last_stripping_

            start_time_ += (df_[ss_]['Time']+self.info['timing_delay1'][p__])
            
            print(df_.columns.to_list()[3:]) # 'MaxLoading1', 'MaxLoading2', ...
            print('stage time:', start_time_-df_[ss_]['Time'], start_time_)
            
            change_ballast_ = self.info['ballast_vol'][str(p__+1)] - self.info['ballast_vol'][str(p__)]
            est_vol_rate_ = change_ballast_/df_[ss_]['Time']*60
            self.seq[str(p__+1)]['est_ballast_vol'] = change_ballast_
            print('ballast amt::',change_ballast_, 'ballast rate::', est_vol_rate_)

            
            if est_vol_rate_ > 7000:
                
                if 'Ballast Limit Error' not in self.error.keys():
                    self.error['Ballast Limit Error'] = ['Port ' + str(p__+1) + ' exceeds ballast limit!!']
                else:
                    self.error['Ballast Limit Error'].append('Port ' + str(p__+1) + ' exceeds ballast limit!!')
                
            
    
    def _cal_rate(self, stage1, stage2, df, result, time_diff_, ignore_zero=True):
        
        # time_diff_ = df[stage2]['Time'] - df[stage1]['Time']
        total_vol_change_ = 0
        rate_per_tank_ = {}
        info_per_tank_ = {'vol':{}, 'qty':{}, 'ullage':{}, 'dsCargoNominationId':{}}
        
        for t_ in result['tanksDischarged']:
            if ignore_zero: # for COW/Strip
                if df[stage2][t_][1] > 0:
                    vol_change_ = df[stage1][t_][1] - df[stage2][t_][1]
                    rate_per_tank_[t_] = round(vol_change_/time_diff_*60,4)
                    total_vol_change_ += vol_change_
                else:
                    rate_per_tank_[t_] = round(0.0)
            else:
                vol_change_ = df[stage1][t_][1] - df[stage2][t_][1]
                rate_per_tank_[t_] = round(vol_change_/time_diff_*60,4)
                total_vol_change_ += vol_change_
            
            
            tankId_ = self.vessel.info['tankName'][t_]    
            info_per_tank_['vol'][tankId_] = str(round(df[stage2][t_][1],2))
            info_per_tank_['qty'][tankId_] = str(round(self.loadable.info['parcel'][df[stage2][t_][0]]['maxtempSG']*df[stage2][t_][1],1))
            info_per_tank_['dsCargoNominationId'][tankId_]  = int(self.info['cargoNominationId'][df[stage2][t_][0]][1:])
            
            # print(df[stage2][t_][0], t_, df[stage2][t_][1])
            
            if df[stage2][t_][1] > 0.:
                corrUllage_ = str(round(self.vessel.info['ullage'][str(tankId_)](df[stage2][t_][1]).tolist(), 6))
            else:
                corrUllage_ = str(self.vessel.info['ullageEmpty'][str(tankId_)])
                                                         
            info_per_tank_['ullage'][tankId_] = corrUllage_
                    
        rate_per_tank_['total'] = round(total_vol_change_/time_diff_*60,4)
        rate_per_tank_['other'] = info_per_tank_

        # print(stage1, stage2, time_diff_, vol_change_)
        return rate_per_tank_
    
    

        
    def _get_ballast_requirements(self):
        
        slopP = [t_ for t_ in self.vessel.info['slopTank'] if t_[-1] == 'P'][0]
        slopS = [t_ for t_ in self.vessel.info['slopTank'] if t_[-1] == 'S'][0]
        
        INDEX_ = INDEX + [slopP, slopS] # cargo tank
        # INDEX = self.config["gantt_chart_index"]
        INDEX1 = self.config["gantt_chart_ballast_index"] # ballast tank
        
        self.max_ballast_rate = 7000 ## FIXED
        
        density_ = self.info['density'] # cargo
        num_port_ = 0
        fixed_ballast_ = []
        same_ballast_ = []
        stages_ = []
        delay_ = 0
        times_ = []
        
        self.seq['dischargingRate'] = {}
        for c__,c_ in enumerate(self.info['discharging_order']):
            
            cargo_to_discharge_ = [self.info['dsCargoNominationId'][cc_] for cc_ in c_]
            c1_ = str(c__+1)
            
            # print(c__+1, 'collecting ballast requirements ....')
            df_ = self.seq[c1_]['gantt']
            df_ = df_.append(pd.DataFrame(index=INDEX1))
            
            # initial
            if c__ == 0: # first cargo to load
                # print('1st stage to be fixed; collecting ballast ...')
                fixed_ballast_ = ['Initial1']
                for k_, v_ in self.info['ballast'][0].items():
                    df_['Initial'][k_] = v_[0]['quantityMT']
                
            # stripping last cargo topping
            if c__ ==  len(self.info['discharging_order']) - 1:
                # print('last discharging cargo')
                # # fixed at departure ballast            
                # if self.seq[c1_]['justBeforeTopping']+str(c__+1) not in fixed_ballast_:
                #     fixed_ballast_.append(self.seq[c1_]['justBeforeTopping']+str(c__+1))
                    
                for k_, v_ in self.info['ballast'][-1].items():
                    df_[self.seq[c1_]['lastStage']][k_] = v_[0]['quantityMT']
                
                
            # get loading info        
            ddf_ = pd.DataFrame(index=INDEX_)
            
            if c__ == 0:
                col_ = 'Initial' + str(c__+1)
                ddf_[col_] = df_['Initial']
                
            
            ddf_ = ddf_.append(pd.DataFrame(index=['Weight']))
            
            for b__,b_ in enumerate(self.seq[c1_]['ballast']):
                if b__ > 0:
                    num_port_ += 1
                    stages_.append(b_[1]+str(c__+1))
                    times_.append(df_[b_[1]]['Time'] + self.seq[str(c__+1)]['startTime'])
                    
                    wt_ = 0
                    col_ = b_[1] + str(c__+1)
                    # print(col_)
                    ddf_[col_] = None
                    ddf_[col_]['Time'] = b_[0] + self.seq[c1_]['startTime']
                    pre_col_ = self.seq[c1_]['ballast'][b__-1][1]
                    
                    # if b_  in self.seq[c1_]['ballastStop']:
                    #     same_ballast_.append(num_port_)
                    # print(pre_col_, col_)
                    for h_, (i_,j_) in enumerate(self.seq[c1_]['gantt'][b_[1]].iteritems()): 
                        # print(i_, j_)
                        if i_ not in ['Time'] and j_ not in [None]:
                            # print(i_,j_) # j_ = curr (cargo, vol)
                            
                            pre_ = self.seq[c1_]['gantt'][pre_col_][i_]
                            check_ = False
                            if pre_ not in [None]:
                                if pre_[0] in  cargo_to_discharge_:
                                    check_ = True
                                elif len(pre_) == 4 and pre_[2] in cargo_to_discharge_:
                                    check_ = True
                            # print(pre_, j_)
                            if  pre_ not in [None] and check_:
                                # print(pre_, j_)
                                if pre_[0] in cargo_to_discharge_:
                                    amt_ = j_[1] - pre_[1]
                                    ddf_[col_][i_] = (j_[0], amt_)
                                    wt_ += round(amt_*density_[j_[0]],10)
                                    
                                elif len(pre_) == 4 and pre_[2] in cargo_to_discharge_:
                                    amt_ = j_[3] - pre_[3]
                                    ddf_[col_][i_] = (j_[0], amt_)
                                    wt_ += round(amt_*density_[j_[0]],10)
                                
                            elif j_[0] in cargo_to_discharge_:
                                ddf_[col_][i_] = (j_[0], j_[1])
                                wt_ += round(j_[1]*density_[j_[0]],10)
                                
                            elif len(j_) > 2 and j_[2] in cargo_to_discharge_:
                                ddf_[col_][i_] = (j_[0], j_[3])
                                wt_ += round(j_[3]*density_[j_[0]],10)
                                
                    ddf_[col_]['Weight'] = wt_ # cargo added in this stage       
                    
                    if col_[:-1] == 'MaxDischarging1':
                        time_diff_ = df_[col_[:-1]]['Time'] -  df_['Initial']['Time']
                        # print(col_[:-1], time_diff_)
                        pre_time_ = df_['Initial']['Time']
                        
                    else:
                        time_diff_ = df_[col_[:-1]]['Time'] -  df_[pre_col_]['Time']
                        # print(pre_col_, col_[:-1], time_diff_)
                        pre_time_ = self.seq[c1_]['exactTime'][pre_col_]
                        
                    cur_time_ = self.seq[c1_]['exactTime'][col_[:-1]]
                    # result_ = self.seq[c1_]['info']
                    # self.seq[c1_]['dischargingRate1'][col_+'PerTank'] = self._cal_rate(pre_col_, col_, ddf_, result_)
                        
                    total_vol_change_ = 0
                    rate_per_tank_ = {}
                    for t_ in self.seq[c1_]['info']['tanksDischarged']:
                        vol_change_ = df_[pre_col_][t_][1] - df_[col_[:-1]][t_][1]
                        rate_per_tank_[t_] = round(vol_change_/time_diff_*60,3)
                        total_vol_change_ += vol_change_
                        
                    rate_per_tank_['total'] = round(total_vol_change_/time_diff_*60,3)
                    rate_per_tank_['time'] = [pre_time_, cur_time_]
                    self.seq['dischargingRate'][str(num_port_)] = rate_per_tank_
                    
            # delay_ += self.info['timing_delay2'][c__+1]
              
            self.seq[c1_]['loadingInfo'] = ddf_  # cargo in m3
            self.seq[c1_]['fixBallast'] = fixed_ballast_
            
            print('fixed ballast: ', fixed_ballast_)
            
            # print(df_.columns)
            
            
            # self.seq[c_]['gantt'] = df_
        
        # print('same ballast: ', same_ballast_)
        # print('stage: ', stages_)
        ballast_time_ = {}
        for c_ in range(1,len(self.info['discharging_order'])+1):
            # print(c_)
            tot_time_ = sum(list(self.seq[str(c_)]['ballastLimit'].values()))
            self.seq[str(c_)]['est_ballast_vol_rate']  = self.seq[str(c_)]['est_ballast_vol']/tot_time_*60
            
        
        ballast_limit_ = {}
        est_ballast_ = {}
        amt_left_ = {str(c_): self.seq[str(c_)]['est_ballast_vol'] for c_ in range(1,len(self.info['discharging_order'])+1)}
        for s__,s_ in enumerate(stages_):
            c_ = str(int(s_[-1])) # less than 10 cargos loading at one port 1..9
            
            if s_[:3] in ['Max', 'Str', 'Dep']:
                # print(s_,self.seq[c_]['ballastLimit'][s_[:-1]])
                b_ = round(self.max_ballast_rate * self.seq[c_]['ballastLimit'][s_[:-1]]/60 *1.025,2) # in MT
                ballast_limit_[s__+1] = b_
                b1_ = self.seq[c_]['est_ballast_vol_rate'] * self.seq[c_]['ballastLimit'][s_[:-1]]/60 # in MT
                est_ballast_[s__+1] = round(b1_*1.025,2)
                amt_left_[c_] -= b1_
             
        self.seq['switchStage'] = []
        for s__, s_ in enumerate(stages_):
            if s__ < len(stages_)-1:
                s1_ = s_[-1]
                s2_ = stages_[s__+1][-1]
                if s1_ != s2_:
                    self.seq['switchStage'].append((s__+1, s__+2))
                    
        self.seq['numPort'] = num_port_
        self.seq['stages'] = stages_
        self.seq['sameBallast'] = same_ballast_
        self.seq['ballastLimit'] = ballast_limit_
        self.seq['times'] = times_
        self.seq['est_ballast'] = est_ballast_
        # print(times_)
        port_ = {}
        for ss_, s_ in enumerate(stages_):
            if s_[:3] in ['Str']:
                # print(s_)
                rr_ = 0 if stages_[ss_-1][:3] not in ['Str'] else int(stages_[ss_-1][9:][:-1])
                cc_ = s_[-1]
                for r_ in range(int(s_[9:][:-1]), rr_,-1):
                    # print(r_, 'Stripping'+str(r_)+str(cc_), ss_+1)
                    port_['Stripping'+str(r_)+str(cc_)] = ss_+1
            elif s_[:3] in ['Dep']:
                cc_ = s_[-1]
                s1_ = int(int(self.seq[cc_]['lastStripping'][9:])+1)
                if stages_[ss_-1][:3] in ['Max']:
                    rr_ = 0
                else:
                    rr_ = int(stages_[ss_-1][9:][:-1])
                for r_ in range(s1_-1, rr_,-1):
                    # print(r_, 'Stripping'+str(r_)+str(cc_), ss_+1)
                    port_['Stripping'+str(r_)+str(cc_)] = ss_+1
                
        self.seq['stripToPort'] = port_ # mapping stripping stages to port
        # print(r_)
                
        
            
            
                    
        
        
    def _get_plan_ampl(self):
        
        cargo_info = self.info
        final_plan = self.info['final_plan']
        
        self.limits = {}
        
        self.seawater_density = 1.025 ## self.loading.seawater_density  ##           
        # self.ballast_percent = 0.4 # round(7000/self.loading.staggering_param['maxShoreRate'],3)-0.001  #0.4
        
        
        self.loadable = lambda: None
        setattr(self.loadable, 'info', {})
        self.loadable.info['parcel'] = {c_:{}  for c_ in cargo_info['pre_cargo']}
        self.loadable.info['lastVirtualPort'] = len(cargo_info['discharging_order'])
        for k_, v_ in cargo_info['density'].items():
            self.loadable.info['parcel'][k_]['mintempSG'] = v_
            self.loadable.info['parcel'][k_]['maxtempSG'] = v_
            
        for k_, v_ in cargo_info['api'].items():
            self.loadable.info['parcel'][k_]['api'] = v_
        
        for k_, v_ in cargo_info['temperature'].items():
            self.loadable.info['parcel'][k_]['temperature'] = v_
            
            
        self.loadable.info['operation'], self.loadable.info['toLoadPort1'] = {},{}
        self.loadable.info['toLoad'] = {}
        self.loadable.info['toLoadCargoTank'] = {}
        self.loadable.info['manualOperation'] = {} # cargo tank port amount
        self.loadable.info['preloadOperation0'] = {} # initial cargo tank port amount
        self.loadable.info['preloadOperation'] = {} # port 1 to ... cargo tank port amount
        self.loadable.info['preload'] = {} # port 1 to ... cargo tank port amount
        self.loadable.info['inSlop'] = {}
        
        self.loadable.info['ballastOperation'] = {t_:{}  for t_ in self.vessel.info['ballastTanks'] if t_ not in self.vessel.info['banBallast']} # tank port amount
        self.loadable.info['fixedBallastPort'] = []
        self.trim_upper, self.trim_lower  = {}, {}
        
        port_ = 0
        # density_ = cargo_info['density']
        
        # preloaded cargo
        #first_cargo_ = self.loading.info['loading_order'][0]
        wt_ = 0
        initial_plan_ = cargo_info['cargo_plans'][0]
        for k_, v_ in initial_plan_.items():
            # print(k_, v_)
            cargo_ = v_[0]['cargo']
            if cargo_ not in [None] and v_[0]['quantityMT'] > 0.:
                if cargo_ not in self.loadable.info['preloadOperation0']:
                    self.loadable.info['preloadOperation0'][cargo_] = {}
                    self.loadable.info['preload'][cargo_] = 0.
                    self.loadable.info['inSlop'][cargo_] = []
                    
                
                self.loadable.info['preloadOperation0'][cargo_][k_] = v_[0]['quantityMT']
                wt_ += v_[0]['quantityMT']
                self.loadable.info['preload'][cargo_] = round(self.loadable.info['preload'][cargo_]+v_[0]['quantityMT'],1)
                
                tank_ = self.vessel.info['tankId'][v_[0]['tankId']]
                if tank_ in self.vessel.info['slopTank']:
                    self.loadable.info['inSlop'][cargo_].append(tank_)
                    
                
                if len(v_) > 1: # for commingle??
                    cargo_ = v_[1]['cargo']
                    if cargo_ not in self.loadable.info['preloadOperation0']:
                        self.loadable.info['preloadOperation0'][cargo_] = {}
                    
                    self.loadable.info['preloadOperation0'][cargo_][k_] = v_[1]['quantityMT']
                    wt_ += v_[1]['quantityMT']
                
        # self.loadable.info['stages'], self.loadable.info['stageTimes'] = {}, {}
        self.loadable.info['toLoadPort'] = {0:round(wt_,1)} ## total in port
        
        port_ = 1
        target_wt_ = {k_: round(v_ - cargo_info['depCargoWeight1'].get(k_,0.),1) for k_, v_ in cargo_info['initCargoWeight1'].items()}
        for c__, c_ in enumerate(cargo_info['discharging_order']):
            
            # last_cargo_ = True if c__+1 == len(self.loading.info['loading_order']) else False
            strip_ = False
            wt1_ = 0
            for d__, d_ in enumerate(c_): # for each cargo
                cargo_ = cargo_info['dsCargoNominationId'][d_]
                wt_ = 0.
                if cargo_ not in  self.loadable.info['operation'].keys():
                    self.loadable.info['operation'][cargo_] = {}
                    self.loadable.info['toLoad'][cargo_] = 0.0
                    self.loadable.info['preloadOperation'][cargo_] = {t_:{}  for t_ in self.vessel.info['cargoTanks']}
                    self.loadable.info['toLoadCargoTank'][cargo_] = {} #{t_:0.  for t_ in self.vessel.info['cargoTanks']}
                
                if d_ not in cargo_info['multiDischarge']:
                    # single discharge stage for this cargo
                    for k_, v_ in  final_plan.items():
                        if v_[0]['cargo'] == cargo_:
                            wt__ = round(v_[0]['quantityMT'] - initial_plan_[k_][0]['quantityMT'],1)
                            self.loadable.info['toLoadCargoTank'][cargo_][k_] = wt__
                            wt_ += wt__
                            wt1_ += wt__
                            
                            if v_[0]['quantityMT'] == 0.:
                                strip_ = True
                                # print(cargo_,self.vessel.info['tankId'][v_[0]['tankId']], 'empty!!')
                                
                            if wt__ < 0:
                                # print(cargo_,self.vessel.info['tankId'][v_[0]['tankId']], wt__)
                                self.loadable.info['preloadOperation'][cargo_][k_][port_] = wt__
                                self.loadable.info['toLoad'][cargo_] += wt__
                            
                            
                        elif len(v_) == 2 and v_[1]['cargo'] == cargo_:
                            exit()
                            ##
                            self.loadable.info['toLoadCargoTank'][cargo_][k_] = v_[1]['quantityMT']
                else:
                    wt_ = cargo_info['discharging_qty'][c__]
                    self.loadable.info['toLoad'][cargo_] += wt_
                    strip_ = None
                    if cargo_info['slopTankFirst'].get(cargo_info['cargoNominationId'][cargo_], None):
                        if cargo_info['slopTankFirst'][cargo_info['cargoNominationId'][cargo_]][-1] == c__+1:
                            print('slopTankFirst::', cargo_, c__+1)
                            strip_ = False
                    
                    wt1_ += wt_
                
                
                wt2_ = round(wt_,1)
                wt3_ = target_wt_[cargo_] + wt2_
                if wt3_ > 1:
                    self.loadable.info['operation'][cargo_][port_] = wt2_
                    target_wt_[cargo_] = wt3_
                    print(port_, target_wt_[cargo_], wt2_)
                else:
                    self.loadable.info['operation'][cargo_][port_] = round(wt2_-wt3_,1)
            
                
            # if strip_ == False:
            #     self.trim_lower[str(port_)] = 0.5
            #     self.trim_upper[str(port_)] = 4.0
            # elif strip_ == True: # true
            #     self.trim_lower[str(port_)] = 4.0
            #     self.trim_upper[str(port_)] = 5.0
            # else:
            #     print('Inter discharging stage')
            # toLoadTank_ = {t_:0.  for t_ in self.vessel.info['cargoTanks']}
            
            
            self.loadable.info['toLoadPort'][port_] = max(0., round(wt1_ + self.loadable.info['toLoadPort'][port_-1],1))  ## accumulated at each port
            self.loadable.info['toLoadPort1'][port_] = wt1_       ## at each port
            
            port_ += 1
            
        # initial ballast
        for k_, v_ in cargo_info['ballast'][0].items():
            if v_[0]['quantityMT'] > 0:
                if k_ not in self.loadable.info['ballastOperation']:
                    self.loadable.info['ballastOperation'][k_] = {'0':v_[0]['quantityMT']}
                else:
                    self.loadable.info['ballastOperation'][k_]['0'] = v_[0]['quantityMT']
            
        self.vessel.info['initBallast'] = {}
        self.vessel.info['initBallast']['wt'] = {k_: v_.get('0', 0.) for k_, v_ in self.loadable.info['ballastOperation'].items()}
        
        # final 
        for k_, v_ in cargo_info['ballast'][1].items():
            if v_[0]['quantityMT'] > 0:
                if k_ not in self.loadable.info['ballastOperation']:
                    self.loadable.info['ballastOperation'][k_] = {str(port_-1):v_[0]['quantityMT']}
                else:
                    self.loadable.info['ballastOperation'][k_][str(port_-1)] = v_[0]['quantityMT']
            
        self.loadable.info['fixedBallastPort'] = ['0', str(port_-1)]
        
        self.loadable.info['incInitBallast'] = []
        self.loadable.info['decInitBallast'] = []
        
        
        for t_ in self.vessel.info['ballastTanks']:
            # print(t_)
            if t_ not in self.vessel.info['banBallast']:
                # print(t_)
                in_ = cargo_info['ballast'][0].get(t_, [{}])[0].get('quantityMT', 0.)
                out_ = cargo_info['ballast'][-1].get(t_, [{}])[0].get('quantityMT', 0.)
                
                if float(out_) >= float(in_):
                    self.loadable.info['incInitBallast'].append(t_)
                else:
                    self.loadable.info['decInitBallast'].append(t_)
       
        self.loadable.info['fixCargoPort'] = [str(port_-1)]
        self.loadable.info['fixCargoPortAmt'] = {}
        for k_, v_ in final_plan.items():
            if v_[0]['cargo'] not in self.loadable.info['fixCargoPortAmt']:
                self.loadable.info['fixCargoPortAmt'][v_[0]['cargo']] = {}
                self.loadable.info['fixCargoPortAmt'][v_[0]['cargo']][k_] = {str(port_-1): v_[0]['quantityMT']}
                
            else:
                self.loadable.info['fixCargoPortAmt'][v_[0]['cargo']][k_] = {str(port_-1): v_[0]['quantityMT']}
                
    def get_param(self, base_draft = {}, ave_trim = {}, set_trim = 0, mean_draft = {}):
        ## get param discharge_init
        
        self.module1 = ''
        cargo_info = self.info
        final_plan = self.info['final_plan']
            
        self.ballast_percent = self.config['ballast_percent'] #0.4 
        lightweight_ = self.vessel.info['lightweight']['weight']
        max_deadweight_ = 1000*1000
        cont_weight_ = self.vessel.info['deadweightConst']['weight'] #+ self.vessel.info['onboard']['totalWeight']
        
        # loadline_ = 100.0
        # min_draft_limit_  = 10.425
        
        self.displacement_lower, self.displacement_upper = {}, {}
        self.base_draft = {}
        self.sf_base_value, self.sf_draft_corr, self.sf_trim_corr = {}, {}, {}
        self.bm_base_value, self.bm_draft_corr, self.bm_trim_corr = {}, {}, {}
        
        self.sf_bm_frac = 0.95 ##  _bm_frac, self.feedback_sf_bm_frac)
        sf_bm_frac_ = 0.99

        if self.config['loadableConfig']:
            sf_bm_frac_ = min(self.config['loadableConfig']['SSFLimit'], self.config['loadableConfig']['SBMLimit'])/100
#            print('SF BM Svalue limits', sf_bm_frac_)
            
        self.sf_bm_frac = min(sf_bm_frac_, self.sf_bm_frac)

        # self.full_discharge = True
        self.ave_trim = {}
        ## set trimlimit based on 
        self._set_trim(set_trim = set_trim)
        self.strip_ports = {}
        
        if self.vessel_id in [2]:
            ballast_weight_ = 94000
        else:
            ballast_weight_ = 92000
            

        ballast_ = cargo_info['initBallastWeight']
        # weight_ = cargo_info['initCargoWeight']
        misc_weight_ = cargo_info['depROBweight']
        reduce_disp_limit_ = []
        
        final_ballast_wt_ = sum([v_[0]['quantityMT'] for k_,v_ in self.info['ballast'][-1].items()])
        final_wt_ = sum([v_[0]['quantityMT'] for k_,v_ in self.info['final_plan'].items()])
        
        ballast_add_ = final_ballast_wt_ - ballast_
        cargo_add_ = final_wt_ - self.info['initCargoWeight']

        for p_ in range(1, self.loadable.info['lastVirtualPort']+1):  # exact to virtual
            
            cargo_to_load_ = self.loadable.info['toLoadPort1'][p_]
            # ballast_ = min(ballast_weight_, ballast_- self.ballast_percent*cargo_to_load_)
            ballast_ = min(ballast_weight_, ballast_+ballast_add_*cargo_to_load_/cargo_add_)
            
            # misc_weight_ = 0.0
            # for k1_, v1_ in self.vessel.info['onhand'].items():
            #     misc_weight_ += v1_.get(str(port_)+arr_dep_,{}).get('wt',0.)
#                
#            # get estimate cargo weight
            cargo_weight_  = max(0., self.loadable.info['toLoadPort'][p_])
#            print(str(port_)+arr_dep_, cargo_weight_)

            est_deadweight_ = min(cont_weight_ + misc_weight_ + cargo_weight_ + ballast_, max_deadweight_)
            est_displacement_ = lightweight_ + est_deadweight_
            seawater_density_ = self.seawater_density
            
            min_limit_ = self.config['min_mid_draft_limit']
            min_limit1_ = mean_draft.get(str(p_), 0.5) - 0.5
            
            ## lower bound displacement
            lower_draft_limit_ = max(min_limit_, min_limit1_) #max(self.ports.draft_airdraft[p_], min_draft_limit_)
            lower_displacement_limit_ = np.interp(lower_draft_limit_, self.vessel.info['hydrostatic']['draft'], self.vessel.info['hydrostatic']['displacement'])
            # correct displacement to port seawater density
            lower_displacement_limit_  = lower_displacement_limit_*seawater_density_/1.025
            
            est_draft__ =  np.interp(est_displacement_,  self.vessel.info['hydrostatic']['displacement'], self.vessel.info['hydrostatic']['draft'])
            
            strip_ = {}
            for d_ in self.info['discharging_order2'][p_]: 
                
                first_strip_ = self.set_trim_mode['first_strip'].get(d_, 100) # in the future
                strip_[d_] = True if p_ >= first_strip_ else False
            
            if True in strip_.values():
                self.trim_lower[str(p_)] = 4.0
                self.trim_upper[str(p_)] = 5.95
                if ave_trim:
                    self.ave_trim[str(p_)] = ave_trim[str(p_)]
                else:
                    self.ave_trim[str(p_)] = 5.0
            else:
                self.trim_lower[str(p_)] = 0.5
                self.trim_upper[str(p_)] = 4.0
                if ave_trim:
                    self.ave_trim[str(p_)] = ave_trim[str(p_)]
                else:
                    self.ave_trim[str(p_)] = 2.0
                
            self.strip_ports[str(p_)] = deepcopy(strip_)
#            print('inter_port ave trim', self.ave_trim[str(p_)], "strip_::", strip_)
            
            if (est_draft__ < lower_draft_limit_):
                print('**Need to reduce lower displacement limit')
                reduce_disp_limit_.append(p_)
            
            ## upper bound displacement
            upper_displacement_limit_ = np.interp(min(22,self.max_draft), self.vessel.info['hydrostatic']['draft'], self.vessel.info['hydrostatic']['displacement'])
            upper_displacement_limit_  = upper_displacement_limit_*seawater_density_/1.025
            
            est_displacement_ = min(est_displacement_, upper_displacement_limit_)
            
            self.displacement_lower[str(p_)] = lower_displacement_limit_
            self.displacement_upper[str(p_)] = upper_displacement_limit_
            
            est_draft_ = np.interp(est_displacement_, self.vessel.info['hydrostatic']['displacement'], self.vessel.info['hydrostatic']['draft'])
            
            
            # base draft for BM and SF
            trim_ = self.ave_trim.get(str(p_), 0.0)
             
            if self.vessel_id in [1, '1']:
                base_draft__ = int(np.floor(est_draft_+trim_/2))
            elif self.vessel_id in [2, '2']:
                base_draft__ = int(np.floor(est_draft_))
            
            base_draft_ = base_draft__ if p_  == 1 else min(base_draft__, self.base_draft[str(p_-1)])
            base_draft_ = min(22,base_draft_)
            self.base_draft[str(p_)] = base_draft_
            
            if base_draft.get(str(p_), None):
                self.base_draft[str(p_)] = base_draft[str(p_)]
                base_draft_ = base_draft[str(p_)]
            
            frames_ = self.vessel.info['frames']
            
            df_sf_ = self.vessel.info['SSTable']
            df_bm_ = self.vessel.info['SBTable']
            
            base_value_, draft_corr_, trim_corr_ = [],[],[]
            base_value__, draft_corr__, trim_corr__ = [],[],[]
            for f__,f_ in enumerate(frames_):
                # SF
                df_ = df_sf_[df_sf_["frameNumber"].isin([float(f_)])]  
                df_ = df_[df_['baseDraft'].isin([base_draft_])]
                base_value_.append(float(df_['baseValue']))
                draft_corr_.append(float(df_['draftCorrection']))
                trim_corr_.append(float(df_['trimCorrection']))
                
                # BM
                df_ = df_bm_[df_bm_["frameNumber"].isin([float(f_)])]  
                df_ = df_[df_['baseDraft'].isin([base_draft_])]
                base_value__.append(float(df_['baseValue']))
                draft_corr__.append(float(df_['draftCorrection']))
                trim_corr__.append(float(df_['trimCorrection']))
                
            self.sf_base_value[str(p_)] = base_value_
            self.sf_draft_corr[str(p_)] = draft_corr_
            self.sf_trim_corr[str(p_)] = trim_corr_
                        
            self.bm_base_value[str(p_)] = base_value__
            self.bm_draft_corr[str(p_)] = draft_corr__
            self.bm_trim_corr[str(p_)] = trim_corr__
            
        print('base draft:', self.base_draft)
        
        
    def _set_trim(self, set_trim = 0):
        
        # set_trim = 1
        self.set_trim_mode = {'mode': set_trim, 'strip':{}, 'first_strip':{}}
        if set_trim == 0:
            ## all non-empty tanks except last port
            for k_, v_ in self.info['discharging_order2'].items():
                for l_ in v_:
                    if self.info['discharging_order1'][l_][-1] == k_:
                        
                        # if len(self.info['stripping_tanks'].get(k_, [])) > 0:
                        empty_ = []
                        for v__ in v_:
                            empty_ += self.info['empty_tank'].get(self.info['dsCargoNominationId'][v__], [])
                            
                        if len(empty_) > 0:
                            
                            self.set_trim_mode['strip'][k_] = True
                            
                            if l_ in self.set_trim_mode['first_strip']:
                                self.set_trim_mode['first_strip'][l_] = min(self.set_trim_mode['first_strip'][l_], int(k_))
                            else:
                                self.set_trim_mode['first_strip'][l_] = int(k_)
                        
                            
                            
        elif set_trim == 1:
            ## all non-empty tanks except second last port
            for k_, v_ in self.info['discharging_order2'].items():
                for l_ in v_:
                    l__ = -2 if len(self.info['discharging_order1'][l_]) > 1 else -1
                    if self.info['discharging_order1'][l_][l__] == k_:
                        
                        empty_ = []
                        for v__ in v_:
                            empty_ += self.info['empty_tank'].get(self.info['dsCargoNominationId'][v__], [])
                            
                        if len(empty_) > 0:
                            
                            self.set_trim_mode['strip'][k_] = True
                            
                            if l_ in self.set_trim_mode['first_strip']:
                                self.set_trim_mode['first_strip'][l_] = min(self.set_trim_mode['first_strip'][l_], int(k_))
                            else:
                                self.set_trim_mode['first_strip'][l_] = int(k_)
                        
        print("set_trim_mode::",self.set_trim_mode)
        print("partialDischarge::",self.info['discharging_order1'])
        print(self.info['cargoNominationId'])

            
    def write_ampl(self, file = 'input_discharging.dat', IIS = True, ave_trim = None, incDec_ballast = None, mean_draft = {}, run_time = None):
        
        if not self.error and self.solver in ['AMPL']: #and self.mode not in ['FullManual']:
            
            
            with open(file, "w") as text_file:
                ##
                print('# set of all cargo tanks',file=text_file)
                cargo_tanks_ = []
                str1 = 'set T:= '
                for i_,j_ in self.vessel.info['cargoTanks'].items():
                    str1 += i_ + ' '
                    cargo_tanks_.append(i_)
                print(str1+';', file=text_file)
                
                ##
                print('# cargo tanks with non-pw tcg details',file=text_file)#  
                str1 = 'set T1 := '
                for i_, j_ in self.vessel.info['cargoTanks'].items():
                    if i_ not in self.vessel.info['tankTCG']['tcg_pw']:
                        str1 += i_ + ' '
                print(str1+';', file=text_file)
                
                ##
                print('# set of tanks compatible with cargo c',file=text_file)
                for i_,j_ in self.loadable.info['parcel'].items():
                    str1 = 'set Tc[' + str(i_) + '] := '
                    for j_ in cargo_tanks_:
                        if j_ not in self.vessel.info['banCargo'].get(i_,[]):
                            str1 += j_ + ' '
                    print(str1+';', file=text_file)
                    
                ## 
                print('# set of loaded tanks (preloaded condition)',file=text_file)
                t_loaded_ = []
                str1 = 'set T_loaded:= '
                for k_, v_ in self.loadable.info['preloadOperation0'].items():
                    for k1_, v1_ in v_.items():
                        if k1_ not in t_loaded_:
                            str1 += k1_ + ' '
                            t_loaded_.append(k1_)
                            
                print(str1+';', file=text_file)
                
                ##
                print('# set of all cargoes',file=text_file)
                str1 = 'set C:= '
                for i_, j_ in self.loadable.info['parcel'].items():
                    str1 += i_ + ' '
                print(str1+';', file=text_file)
                
                
                print('# set of all loaded cargoes (partial loading condition)',file=text_file)
                str1 = 'set C_loaded:= '
                for k_, v_ in self.loadable.info['preloadOperation0'].items():
                    str1 += k_ + ' '
                print(str1+';', file=text_file)
                
                
                print('# set of all loaded cargoes (partial loading condition) with auto discharge',file=text_file)
                str1 = 'set C_loaded1:= '
                for k_ in self.info['multiDischarge']:
                    if k_ in self.info['dsCargoNominationId']:
                        str1 += self.info['dsCargoNominationId'][k_] + ' '
                print(str1+';', file=text_file)
                
                print('# if cargo c has been loaded in tank t (partial loading condition)',file=text_file)
                str1 = 'param I_loaded := '
                print(str1, file=text_file)
                for k_, v_ in self.loadable.info['preloadOperation0'].items():  ###
                    str1 = '[' + k_ + ', *] := '
                    for k1_, v1_ in v_.items():
                        if v1_ not in [{}]:
                            str1 += k1_ + ' ' + '1 '
                    print(str1, file=text_file)
                print(';', file=text_file)
                
                #            
                str1 = 'param W_loaded   := ' 
                print(str1, file=text_file) 
                for k_, v_ in self.loadable.info['preloadOperation'].items():
                    for k1_, v1_ in v_.items():
                        for k2_, v2_ in v1_.items():
                            if v2_ not in [{}]:
                                str1 = k_ + ' ' +  ' ' + str(k1_) + ' ' + str(k2_) + ' ' + "{:.1f}".format(v2_) 
                                print(str1, file=text_file)
                print(';', file=text_file)
    
                #
                print('# weight of cargo c remained in tank t at initial state (before ship entering the first port)',file=text_file)#  
                str1 = 'param W0  := ' 
                print(str1, file=text_file) 
                for k_, v_ in self.loadable.info['preloadOperation0'].items(): ###
                    str1 = '[' + k_ + ', *] := '
                    for k1_, v1_ in v_.items():
                        if v1_ not in [{}]:
                            str1 += k1_ + ' ' +  "{:.1f}".format(v1_) + ' ' 
                    print(str1, file=text_file)
                    
                print(';', file=text_file)
                
                
                # fix  
                print('# weight of cargo c  in port p at tank remained',file=text_file)#  
                str1 = 'param W1  := ' ##
                print(str1, file=text_file) 
                for k_, v_ in self.loadable.info['fixCargoPortAmt'].items():
                    for k1_, v1_ in v_.items():
                        for k2_, v2_ in v1_.items():
                            if v2_ not in [{}, 0]:
                                str1 = k_ + ' ' +  ' ' + str(k1_) + ' ' + str(k2_) + ' ' + "{:.1f}".format(v2_) 
                                print(str1, file=text_file)
                print(';', file=text_file)
    
                print('# fixCargoPort',file=text_file)#  ##
                str1 = 'set fixCargoPort := '  # to virtual ports
                for k_ in self.loadable.info['fixCargoPort']:
                    str1 += ' ' + str(k_)
                print(str1+';', file=text_file)
                
                
                
                ## 
                print('# total number of ports in the booking list',file=text_file)#   
                str1 = 'param NP := ' + str(self.loadable.info['lastVirtualPort']) # to virtual ports 
                print(str1+';', file=text_file)
                
                print('# the last loading port',file=text_file)#  
                str1 = 'param LP := ' + str(0) # to virtual ports
                print(str1+';', file=text_file)
                
                print('# P_stable0',file=text_file)#  
                str1 = 'set P_stable0 := '  # to virtual ports
                for k_ in range(1, self.loadable.info['lastVirtualPort']+1):
                    str1 += ' ' + str(k_)
                print(str1+';', file=text_file)
                
                
                #  NP1 = {} for cargo left in last discharge port so to avoid min draft
                # print('# NP1',file=text_file) 
                # if not self.full_discharge:
                #     str1 = 'set NP1 := '  # to virtual ports
                #     print(str1+';', file=text_file)
                
                print('# cargo density @ low temperature (in t/m3)',file=text_file)#  
                str1 = 'param densityCargo_High  := ' 
                for i_,j_ in self.loadable.info['parcel'].items():
                    str1 +=  str(i_) + ' ' + "{:.6f}".format(j_['mintempSG'])  + ' '
                print(str1+';', file=text_file)
     
                print('# cargo density @ high temperature (in t/m3)',file=text_file)#  
                str1 = 'param densityCargo_Low  := ' 
                density_ = []
                for i_,j_ in self.loadable.info['parcel'].items():
                    density_.append(j_['maxtempSG'])
                    str1 +=  str(i_) + ' ' + "{:.6f}".format(j_['maxtempSG'])  + ' '
                print(str1+';', file=text_file)
                
                str1 = 'param aveCargoDensity  := ' 
                str1 += "{:.4f}".format(np.mean(density_))  + ' '
                print(str1+';', file=text_file)
                
                print('# weight (in metric tone) of cargo to be moved at port p',file=text_file)#  
                first_ = {}
                str1 = 'param Wcp  := ' 
                print(str1, file=text_file) 
                for i_, j_ in self.loadable.info['operation'].items():
                    p_ = 100
                    str1 = '[' + str(i_) + ', *] := '
                    for k_,v_ in j_.items():
                        if int(k_) > 0:
                            str1 += str(k_) + ' ' + "{:.1f}".format(int(v_*10)/10) + ' '
                            p_ = min(p_, int(k_))
                    print(str1, file=text_file)
                    first_[i_] = p_
                print(';', file=text_file)
                
                
                ##
                print('# first port for discharging cargo c',file=text_file)
                for i_, j_ in first_.items():
                    str1 = 'set P_stable2[' + str(i_) + '] := '
                    for k_ in range(j_, self.loadable.info['lastVirtualPort']+1):
                        str1 += str(k_) + ' '
                    print(str1+';', file=text_file)
                    
                    
                print('# opt port for discharging cargo ',file=text_file)
                str1 = 'set P_opt := '
                for k_ in self.info['portOpt']:
                    str1 += str(k_) + ' '
                print(str1+';', file=text_file)
                
                print('# discharging and loading port for cargo',file=text_file)
                for k_, v_ in self.loadable.info['operation'].items():
                    v__ = [int(k1_) for k1_, v1_ in v_.items() if v1_ > 0]
                    if len(v__) > 0:
                        str1 = 'set P_dis['+ k_ +']'+ ':= '
                        for p_ in range(max(v__)+1, self.loadable.info['lastVirtualPort']+1):
                            str1 += str(p_) + ' '
                        print(str1+';', file=text_file)
                        
                        str1 = 'set P_load['+ k_ +']'+ ':= '
                        for p_ in range(1, max(v__)+1):
                            str1 += str(p_) + ' '
                        print(str1+';', file=text_file)
                
                
                if self.set_trim_mode['first_strip']:
                    for k_, v_ in self.set_trim_mode['first_strip'].items():
                        if v_-1 > 0:
                            k1_ = self.info['dsCargoNominationId'][k_]
                            str1 = 'set P_load2['+ k1_ +']'+ ':= '
                            for v__ in range(1, v_):
                                str1 += str(v__) + ' '
                            print(str1+';', file=text_file)
                            
                    for k_, v_ in self.loadable.info['preloadOperation0'].items():
                        str1 = 'set T2['+ k_ +']'+ ':= '
                        for k1_, v2_ in v_.items():
                            if v2_ > 0 and k1_ not in self.vessel.info['slopTank']:
                                str1 += str(k1_) + ' '
                        print(str1+';', file=text_file)
                        
                    for k_, v_ in self.loadable.info['inSlop'].items():
                        if len(v_) > 0:
                            k1_ = self.info['cargoNominationId'][k_]
                            str1 = 'set P_load3['+ k_ +']'+ ':= '
                            for v__ in range(1, int(self.info['discharging_order1'][k1_][-1])):
                                str1 += str(v__) + ' '
                            print(str1+';', file=text_file)
                            
                    for k_, v_ in self.loadable.info['preloadOperation0'].items():
                        if len(self.loadable.info['inSlop'][k_]) > 0:
                            str1 = 'set T3['+ k_ +']'+ ':= '
                            k1_ = self.loadable.info['inSlop'][k_][0]
                            str1 += str(k1_) + ' '
                            print(str1+';', file=text_file)
                
                # 30% tank vol
                str1 = 'param vol30percent := '
                for k_, v_ in self.vessel.info['vol30percent'].items():
                    str1 +=  str(k_) + ' ' + "{:.2f}".format(v_)  + ' '
                print(str1+';', file=text_file)         
                
                # 4m sounding vol
                str1 = 'param sounding4mVol := '
                for k_, v_ in self.vessel.info['sounding4mVol'].items():
                    str1 +=  str(k_) + ' ' + "{:.2f}".format(v_)  + ' '
                print(str1+';', file=text_file)
                
                
                # for deballasting amt
                print('# loading ports',file=text_file)#  
                str1 = 'set loadPort  := ' 
                # for i_, j_ in self.loadable['toLoadPort1'].items():
                #     str1 += str(i_) + ' '
                print(str1+';', file=text_file)
                # for deballasting amt 
                str1 = 'param loadingPortAmt  := ' 
                # for i_, j_ in self.loadable['toLoadPort1'].items():
                #     str1 += str(i_)  + ' ' +  "{:.1f}".format(int(j_*10)/10)  + ' '
                print(str1+';', file=text_file)
                
                # for ballasing amt
                print('# discharge ports',file=text_file)#  
                str1 = 'set dischargePort  := ' 
                for i_, j_ in self.loadable.info['toLoadPort1'].items():
                    str1 += str(i_) + ' '
                print(str1+';', file=text_file)
                
                # for ballasting amt
                str1 = 'param dischargePortAmt  := ' 
                for i_, j_ in self.loadable.info['toLoadPort1'].items():
                    str1 += str(i_)  + ' ' +  "{:.1f}".format(-j_)  + ' '
                print(str1+';', file=text_file)
                
                print('# intended cargo to load',file=text_file)#  
                str1 = 'param toLoad  := ' 
                # for i_, j_ in self.loadable['toLoad'].items():
                #     str1 += i_ + ' ' +  "{:.1f}".format(j_)  + ' '
                print(str1+';', file=text_file)
                
                print('# intended cargo to load',file=text_file)#  
                str1 = 'set cargoPriority := ' 
                print(str1+';', file=text_file)
                
                print('# min cargo to must be loaded',file=text_file)#  
                str1 = 'param minCargoLoad  := ' 
                # for i_, j_ in self.loadable.info['toLoadMin'].items():
                #     str1 += i_ + ' ' +  "{:.3f}".format(int(j_*10)/10)  + ' '
                print(str1+';', file=text_file)        
                
                                # if self.loadable.info['numParcel'] == 1:
                #     print('# slop tanks diff cargos',file=text_file)#  
                #     str1 = 'param diffSlop := 10' 
                #     print(str1+';', file=text_file)
                #     # default is 1 in AMPL
                
                print('# Commingle cargos',file=text_file)#  
                str1 = 'set Cm_1 := ' 
                # if self.loadable.info['commingleCargo']:
                #     str1 += self.loadable.info['commingleCargo']['parcel1'] + ' '
                print(str1+';', file=text_file)
                
                str1 = 'set Cm_2 := ' 
                # if self.loadable.info['commingleCargo']:
                #     str1 += self.loadable.info['commingleCargo']['parcel2'] + ' '
                print(str1+';', file=text_file)
                            
                print('# Possible commingled tanks',file=text_file)#
                str1 = 'set Tm := '
                # if self.loadable.info['commingleCargo']:
                #     if self.loadable.info['commingleCargo'].get('tank',[]):
                #         for t_ in self.loadable.info['commingleCargo']['tank']:
                #             str1 +=  self.vessel.info['tankId'][int(t_)]  + ' '
                #     elif not self.loadable.info['commingleCargo']['slopOnly']:
                #         str1 += '2C 3C 4C SLS SLP'
                #     else:
                #         str1 += 'SLS SLP'
                print(str1+';', file=text_file)
                
                # print('# Density commingled cargo',file=text_file)#
                # str1 = 'param density_Cm := '
                # if self.loadable.info['commingleCargo']:
                #     str1 += self.loadable.info['commingleCargo']['parcel1'] + ' ' + "{:.4f}".format(self.loadable.info['commingleCargo']['SG1'])+ ' '
                #     str1 += self.loadable.info['commingleCargo']['parcel2'] + ' ' + "{:.4f}".format(self.loadable.info['commingleCargo']['SG2'])+ ' '
                    
                # print(str1+';', file=text_file)
                
                
                # if self.loadable.info['commingleCargo'].get('mode','0') == '2':
                #     print('# Manual commingled cargo',file=text_file)
                #     str1 = 'param Qm_1 := ' + "{:.3f}".format(self.loadable.info['commingleCargo']['wt1'])
                #     print(str1+';', file=text_file)
                #     str1 = 'param Qm_2 := ' + "{:.3f}".format(self.loadable.info['commingleCargo']['wt2'])
                #     print(str1+';', file=text_file)
                #     str1 = 'param Mm := 0'
                #     print(str1+';', file=text_file)
                
                
                print('# cargo tank capacity (in m3)',file=text_file)#  
                str1 = 'param capacityCargoTank := ' 
                for i_, j_ in self.vessel.info['cargoTanks'].items():
                    o_ = self.vessel.info['onboard'].get(i_,{}).get('vol',0.)
                    if o_ > 0:
                        print(i_,j_['capacityCubm'],o_, 'in input.dat')
                    str1 += i_ + ' ' +  "{:.3f}".format(j_['capacityCubm']-o_/0.98)  + ' '
                print(str1+';', file=text_file)
                
                print('# onboard cargo tank (in mt)',file=text_file)#  
                str1 = 'param onboard := ' 
                # for i_, j_ in self.vessel.info['onboard'].items():
                #     if i_ not in ['totalWeight']:
                #         str1 += i_ + ' ' +  "{:.3f}".format(j_['wt'])  + ' '
                print(str1+';', file=text_file)
                
                
                ##
                print('# locked tank',file=text_file)#   
                locked_tank_ = []
                str1 = 'set T_locked := ' 
                for k_, v_ in self.loadable.info['manualOperation'].items():
                    for k1_, v1_ in v_.items():
                        if k1_ not in locked_tank_:
                            str1 += k1_ + ' ' 
                            locked_tank_.append(k1_)
                        
                                
                print(str1+';', file=text_file)
                
                print('# locked cargo',file=text_file)#  
                locked_cargo_= []
                str1 = 'set C_locked := ' 
                for k_, v_ in self.loadable.info['manualOperation'].items():
                    if k_ not in locked_cargo_:
                        str1 += k_ + ' '
                        locked_cargo_.append(k_)
                        
                print(str1+';', file=text_file)
                
                print('# 1 if tank t is locked for cargo c',file=text_file)#  
                str1 = 'param A_locked  := ' 
                print(str1, file=text_file) 
                for k_, v_ in self.loadable.info['manualOperation'].items():
                    str1 = '[' + k_ + ', *] := '
                    tank_ = []
                    for k1_, v1_ in v_.items():
                        tank__ = k1_
                        if v1_ and tank__  not in tank_:
                            str1 += tank__ + ' ' + '1' + ' '
                            tank_.append(tank__)
                    print(str1, file=text_file)
                print(';', file=text_file)  
    #            
                str1 = 'param W_locked   := ' 
                print(str1, file=text_file) 
                for k_, v_ in self.loadable.info['manualOperation'].items():
                    for k1_, v1_ in v_.items():
                        for k2_, v2_ in v1_.items():
                            # tank_ = self.vessel.info['tankId'][int(v2_['tankId'])]
                            
                            str1 = k_ + ' ' + k1_  + ' ' + str(k2_) + ' ' + "{:.1f}".format(v2_)
                            print(str1, file=text_file)
                print(';', file=text_file)
                
                
                str1 = 'param B_locked := '
                print(str1, file=text_file) 
                for k_, v_ in self.loadable.info['ballastOperation'].items():
                    tank_ = k_
                    str1 = '[' + tank_ + ', *] := '
                    for k__, v__ in v_.items():
                        if k__ not in ['0'] and v_ not in [{}]:
                            str1 += k__ + ' ' + "{:.3f}".format(int(v__*100-1)/100) + ' '
                    print(str1, file=text_file)
                print(';', file=text_file)  
                        
                
                str1 = 'set fixBallastPort := '
                for k_ in self.loadable.info['fixedBallastPort']:
                    if k_ != '0':
                        str1 += k_ + ' ' 
                print(str1+';', file=text_file)
            
                str1 = 'param trim_upper := '
                for k_, v_ in self.trim_upper.items():
                    str1 += k_ + ' ' + "{:.3f}".format(v_) + ' '
                print(str1+';', file=text_file)
                
                str1 = 'param trim_lower := '
                for k_, v_ in self.trim_lower.items():
                    str1 += k_ + ' ' + "{:.3f}".format(v_) + ' '
                print(str1+';', file=text_file)
                
                # set of other tanks, e.g. fuel tanks, water tanks,
                other_tanks_ = {**self.vessel.info['fuelTanks'], **self.vessel.info['dieselTanks'], **self.vessel.info['freshWaterTanks'] }
                str1 = 'set OtherTanks := '
                for i_, j_ in other_tanks_.items():
                    str1 += i_ + ' '
                print(str1+';', file=text_file)
                
                # weight of each tank
                str1 = 'param weightOtherTank := '
                print(str1, file=text_file)
                for i_, j_ in self.info['ROB'][1].items(): ##
                    str1 = '['+ i_ + ',*] = '
                    for p_ in range(1,self.loadable.info['lastVirtualPort']+1):
                        str1 += str(p_) + ' ' + "{:.3f}".format(j_[0]['quantityMT']) + ' '
                            
                    print(str1, file=text_file)
                print(';', file=text_file)
                
                
                ## ballast tanks    
                # ban_ballast_ = ['FPTU','AWBP','AWBS'] # ['APT','FPTU','AWBP','AWBS']
                print('# ballast tanks ',file=text_file)#  
                str1 = 'set TB := '
                ballast_tanks_ = []
                for i_, j_ in self.vessel.info['ballastTanks'].items():
                    if i_ not in  self.vessel.info['banBallast']:
                        str1 += i_ + ' '
                        ballast_tanks_.append(i_)
                print(str1+';', file=text_file)
                
                str1 = 'param minBallastAmt := '
                for i_, j_ in self.vessel.info['ullage30cm'].items():
                    if i_ not in  self.vessel.info['banBallast']:
                        str1 += i_ + ' ' + "{:.3f}".format(j_) + ' '
                      
                print(str1+';', file=text_file)
                
                # min ballast amt before eduction
                str1 = 'set minTB := '
                # for i_ in self.loading.info['eduction']:
                #     if i_ not in  self.vessel.info['banBallast']:
                #         str1 += i_ + ' '
                print(str1+';', file=text_file)
                
                
                
                print('# ballast tanks with non-pw tcg details',file=text_file)#  
                tb_list_ = list(self.vessel.info['tankTCG']['tcg_pw'].keys()) + self.vessel.info['banBallast']
                str1 = 'set TB1 := '
                for i_, j_ in self.vessel.info['ballastTanks'].items():
                    if i_ not in tb_list_:
                        str1 += i_ + ' '
                print(str1+';', file=text_file)

                if incDec_ballast:
                    print('# ballast tanks which can be ballast or deballast anytime',file=text_file)#  
                    str1 = 'set TB3 := '
                    for i_ in incDec_ballast:
                        str1 += i_ + ' '
                    print(str1+';', file=text_file)
                
                print('# ballast tanks with non-pw lcg details',file=text_file)#  
                tb_list_ = list(self.vessel.info['tankLCG']['lcg_pw'].keys()) + self.vessel.info['banBallast']
                # tb_list_ = self.vessel.info['banBallast']
                str1 = 'set TB2 := '
                for i_, j_ in self.vessel.info['ballastTanks'].items():
                    if i_ not in tb_list_:
                        str1 += i_ + ' '
                print(str1+';', file=text_file)
    #            
                # density of seawater
                print('# density of seawater ',file=text_file)#
                str1 = 'param densitySeaWater := '
                for p_ in range(1,self.loadable.info['lastVirtualPort']+1): ##
                    str1 += str(p_) + ' ' + "{:.4f}".format(self.seawater_density)  + ' '
                print(str1+';', file=text_file)
                
                print('# cargo tanks restrictions ',file=text_file)#
                str1 = 'set cargoTankNonSym := '
                # for k__, k_  in enumerate(self.vessel.info['notSym']):
                #     str1 += '('+ k_[0]  + ',' + k_[1] + ') '
                print(str1+';', file=text_file)
                
                str1 = 'set C_max := '
                # for k__, k_  in enumerate(self.vessel.info['maxCargo']):
                #     str1 += k_ + ' '
                print(str1+';', file=text_file)
                
                
                # print('# diff vol ',file=text_file)#
                # str1 = 'param diffVol := 1' 
                # print(str1+';', file=text_file)
                
                # print('# deballast percent ',file=text_file)#  ##
                # str1 = 'param deballastPercent := ' + "{:.4f}".format(self.deballast_percent) 
                # print(str1+';', file=text_file)
                
                
                
                print('# initial ballast ',file=text_file)#
                str1 = 'param initBallast := '
                for k_, v_ in self.info['ballast'][0].items():
                    if k_ not in self.vessel.info['banBallast']:
                        str1 += str(k_) + ' ' + "{:.3f}".format(max(0, int(v_[0]['quantityMT']*100-1)/100))  + ' '
                print(str1+';', file=text_file)
                
                print('# inc initial ballast ',file=text_file)##
                str1 = 'set incTB := '
                for k_ in self.loadable.info['incInitBallast']:
                    str1 += str(k_) + ' '
                print(str1+';', file=text_file)
                
                print('# dec initial ballast ',file=text_file)##
                str1 = 'set decTB := '
                for k_ in self.loadable.info['decInitBallast']:
                    str1 += str(k_) + ' '
                print(str1+';', file=text_file)
                
                               
                
                # ##
                print('# loading ports ',file=text_file)#
                str1 = 'set loadingPort := '
                # for k__, k_  in enumerate(self.vessel.info['loading']):
                #     if k__ < len(self.vessel.info['loading'])-1:
                #         str1 += '('+ str(k_)  + ',' + str(self.vessel.info['loading'][k__+1]) + ') '
                print(str1+';', file=text_file)
                
                print('# loading ports not last ',file=text_file)#
                str1 = 'set loadingPortNotLast := '
                # for k__, k_  in enumerate(self.vessel.info['loading']):
                #     if k__ < len(self.vessel.info['loading'])-2:
                #         str1 += '('+ str(k_)  + ',' + str(self.vessel.info['loading'][k__+1]) + ') '
                print(str1+';', file=text_file)
                
                
                print('# departure arrival ports non-empty and empty ROB',file=text_file)#
                str1 = 'set depArrPort1 := '
                # for k__, k_  in enumerate(self.vessel.info['loading']):
                #     if k__ < len(self.vessel.info['loading'])-1:
                #         if (str(k_), str(k_+1)) not in self.vessel.info['sameROBseawater']:
                #             str1 += '('+ str(k_)  + ',' + str(int(k_)+1) + ') '
                print(str1+';', file=text_file)
                
                # same weight
                str1 = 'set depArrPort2 := '  ##
                # for k__, k_  in enumerate(self.loading.seq['sameBallast']):
                #     str1 += '('+ str(k_)  + ',' + str(k_+1) + ') '
                print(str1+';', file=text_file)
                
                # same weight
                str1 = 'set sameBallastPort := '  ##
                # for k__, k_  in enumerate(self.loading.seq['sameBallast']):
                #     str1 += str(k_)  + ' '
                print(str1+';', file=text_file)
                
                
                print('# rotating ports ',file=text_file)#
                str1 = 'set rotatingPort1 := '
                for k_  in range(0, self.loadable.info['lastVirtualPort']):
                        str1 += '('+ str(k_)  + ',' + str(k_+1)+ ') '
                print(str1+';', file=text_file)
                
                
                str1 = 'set rotatingPort2 := '
                # if len(self.vessel.info['rotationVirtual']) >= 2:
                #     for k__, k_  in enumerate(self.vessel.info['rotationVirtual'][1]):
                #         if k__ < len(self.vessel.info['rotationVirtual'][1])-1:
                #             str1 += '('+ str(k_)  + ',' + str(self.vessel.info['rotationVirtual'][1][k__+1])+ ') '
                print(str1+';', file=text_file)
                
                ##
                print('# lastLoadingPortBallastBan ',file=text_file)#
                str1 = 'set lastLoadingPortBallastBan := ' # WB1P WB1S WB2P WB2S WB3P WB3S WB4P WB4S WB5P WB5S'
                print(str1+';', file=text_file)
                
                ## banned ballast in P
                print('# ballastBan ',file=text_file)#
                str1 = 'set ballastBan := ' ##'AWBP AWBS APT'
                print(str1+';', file=text_file)
                
                # print('# first loading Port',file=text_file)#
                # str1 = 'param firstloadingPort := ' #+ self.loadable.info['arrDepVirtualPort']['1D']
                # print(str1+';', file=text_file)
                
                
                print('# capacity of ballast tanks', file=text_file)
                str1 = 'param capacityBallastTank := ' 
                for i_, j_ in self.vessel.info['ballastTanks'].items():
                    if i_ not in self.vessel.info['banBallast']:
                        str1 += i_ + ' ' +  "{:.3f}".format(j_['capacityCubm']) + ' '
                print(str1+';', file=text_file)
    
                print('# light weight of ship', file=text_file)
                str1 = 'param lightWeight := ' + str(self.vessel.info['lightweight']['weight'])
                print(str1+';', file=text_file)            
                
                print('# LCG of ship', file=text_file)
                str1 = 'param LCGship := ' + str(self.vessel.info['lightweight']['lcg'])
                print(str1+';', file=text_file) 
                
                print('# deadweight constant', file=text_file)
                str1 = 'param deadweightConst := ' + str(self.vessel.info['deadweightConst']['weight']) # deadweight constant
                print(str1+';', file=text_file) 
                            
                print('# LCG of deadweight constant', file=text_file)
                str1 = 'param LCGdw := ' + str(self.vessel.info['deadweightConst']['lcg']) 
                print(str1+';', file=text_file) 
                
                print('# TCG of deadweight constant', file=text_file)
                str1 = 'param TCGdw := ' + str(self.vessel.info['deadweightConst']['tcg']) 
                print(str1+';', file=text_file) 
                
                # print('# max num tanks', file=text_file)
                # if self.maxTankUsed:
                #     str1 = 'param maxTankUsed := ' + str(self.maxTankUsed) 
                #     print(str1+';', file=text_file) 
                
                
                print('# first discharge cargo', file=text_file)
                str1 = 'set firstDisCargo := ' 
                # if self.firstDisCargo not in ['None'] and  'P'+self.firstDisCargo not in ['P']:
                #     str1 += 'P'+self.firstDisCargo
                print(str1+';', file=text_file)
                
                
                print('# slop discharge first', file=text_file)
                str1 = 'set slopTankFirst := '
                for k_, v_ in self.info['slopTankFirst'].items():
                    str1 += '(' + self.info['dsCargoNominationId'][k_] + ',' + v_[0] +','+ str(v_[1]) +  ')'
                print(str1+';', file=text_file)
                    
                
                # print('# cargoweight', file=text_file)
                # str1 = 'param cargoweight := ' + str(self.cargoweight) 
                # print(str1+';', file=text_file) 
                
                # if self.mode in ['Manual', 'FullManual']:
                #     str1 = 'param diffVol := 0.101' 
                #     print(str1+';', file=text_file) 
                    
                
                # str1 = 'set C_equal := '  
                # if len(self.loadable.info['parcel']) == 1:
                #     str1 += list(self.loadable.info['parcel'].keys())[0]
                # print(str1+';', file=text_file) 
                
                str1 = 'set C_slop := '  
                # if len(self.loadable.info['parcel']) == 1:
                #     str1 += list(self.loadable.info['parcel'].keys())[0]
                print(str1+';', file=text_file) 
                    
                
                
                print('# random seed for Gurobi', file=text_file)
                str1 = 'param seed   := ' + str(np.random.randint(0,1000)) 
                # str1 = 'param seed   := 11' 
                print(str1+';', file=text_file)
                
                
                tanks_ = {**self.vessel.info['cargoTanks'], **self.vessel.info['ballastTanks'], 
                          **self.vessel.info['fuelTanks'], **self.vessel.info['dieselTanks'], **self.vessel.info['freshWaterTanks']}
                
                print('# LCGs of tanks', file=text_file)
                str1 = 'param LCGt := '
                for i_, j_ in tanks_.items():
                    if i_ not in  self.vessel.info['banBallast']:
                        str1 += i_ + ' ' +  "{:.4f}".format(j_['lcg']) + ' '
                print(str1+';', file=text_file)   
                
                print('# LCGs for cargo tanks', file=text_file)
                str1 = 'param LCGtport := '
                print(str1, file=text_file)
                for i_, j_ in self.vessel.info['cargoTanks'].items():
                    str1 = '['+ i_ + ',*] = '
                    for k1_ in range(1, self.loadable.info['lastVirtualPort']+1):
                        # lcg_ = j_['lcg']
                        # lcg_ = self.LCGport.get(i_, {}).get(k1_, j_['lcg'])
                        lcg_ = j_['lcg']
                        str1 += str(k1_) + ' ' + "{:.4f}".format(lcg_) + ' '
                                    
                    print(str1, file=text_file)
                print(';', file=text_file)
                
                self.vessel.info['TCGt'] = {}
                print('# TCGs of tanks', file=text_file)
                str1 = 'param TCGt := '
                for i_, j_ in tanks_.items():
                    if i_ not in self.vessel.info['banBallast']:
                        tcg_ = self.vessel.info['tankTCG']['tcg'].get(i_,{}).get('tcg',[0.,0.,0.,0.])[-3] # FPTU missing
                        self.vessel.info['TCGt'][i_] = tcg_
                        str1 += i_ + ' ' +  "{:.4f}".format(tcg_)  + ' '
                print(str1+';', file=text_file)   
                
                
                
                print('# num of pw TCG curves for ballast tank', file=text_file)
                str1 = 'param pwTCG := ' +  str(self.vessel.info['tankTCG']['tcg_pw']['npw'])
                print(str1+';', file=text_file)
                
                print('# slopes of TCG curves for tanks', file=text_file)
                print('param mTankTCG := ', file=text_file)
                for m_ in range(1,self.vessel.info['tankTCG']['tcg_pw']['npw']+1):
                    str1 = '[' + str(m_) + ',*] := '
                    for k_, v_ in self.vessel.info['tankTCG']['tcg_pw'].items():
                        if k_ not in (['npw']+self.vessel.info['banBallast']):
                            str1 += k_ + ' ' + str(round(v_['slopes'][m_-1],8)) + ' '
                    print(str1, file=text_file)
                print(';', file=text_file)    
                    
                print('# breaks of TCG curves for tanks', file=text_file)
                print('param bTankTCG := ', file=text_file)
                for m_ in range(1,self.vessel.info['tankTCG']['tcg_pw']['npw']):
                    str1 = '[' + str(m_) + ',*] := '
                    for k_, v_ in self.vessel.info['tankTCG']['tcg_pw'].items():
                        if k_ not in (['npw']+self.vessel.info['banBallast']):
                            str1 += k_ + ' ' + str(round(v_['breaks'][m_-1],8)) + ' '
                    print(str1, file=text_file)
                print(';', file=text_file)    
                    
                print('# num of pw LCG curves for ballast tank', file=text_file)
                str1 = 'param pwLCG := ' +  str(self.vessel.info['tankLCG']['lcg_pw']['npw'])
                print(str1+';', file=text_file)
                
                print('# slopes of LCG curves for tanks', file=text_file)
                print('param mTankLCG := ', file=text_file)
                for m_ in range(1,self.vessel.info['tankLCG']['lcg_pw']['npw']+1):
                    str1 = '[' + str(m_) + ',*] := '
                    for k_, v_ in self.vessel.info['tankLCG']['lcg_pw'].items():
                        if k_ not in (['npw']+self.vessel.info['banBallast']):
                            str1 += k_ + ' ' + str(round(v_['slopes'][m_-1],8)) + ' '
                    print(str1, file=text_file)
                print(';', file=text_file)
                
                print('# breaks of LCG curves for tanks', file=text_file)
                print('param bTankLCG := ', file=text_file)
                for m_ in range(1,self.vessel.info['tankLCG']['lcg_pw']['npw']):
                    str1 = '[' + str(m_) + ',*] := '
                    for k_, v_ in self.vessel.info['tankLCG']['lcg_pw'].items():
                        if k_ not in (['npw']+self.vessel.info['banBallast']):
                            str1 += k_ + ' ' + str(round(v_['breaks'][m_-1],8)) + ' '
                    print(str1, file=text_file)
                print(';', file=text_file)
                
                print('# TCGs for others tanks', file=text_file) ##
                str1 = 'param TCGtp := '
                print(str1, file=text_file)
                for i_, j_ in self.info['ROB'][1].items():
                    str1 = '['+ i_ + ',*] = '
                    for p_ in range(1,self.loadable.info['lastVirtualPort']+1):
                        str1 += str(p_) + ' ' + "{:.4f}".format(j_[0]['tcg']) + ' '
                            
                    print(str1, file=text_file)
                print(';', file=text_file)
                
                print('# LCGs for others tanks', file=text_file) ##
                str1 = 'param LCGtp := '
                print(str1, file=text_file)
                for i_, j_ in self.info['ROB'][1].items():
                    str1 = '['+ i_ + ',*] = '
                    for p_ in range(1,self.loadable.info['lastVirtualPort']+1):
                        str1 += str(p_) + ' ' + "{:.4f}".format(j_[0]['lcg']) + ' '
                            
                    print(str1, file=text_file)
                print(';', file=text_file)
                
                print('# slopes of LCB x Disp curve', file=text_file)
                str1 = 'param pwLCB := ' +  str(len(self.vessel.info['lcb_mtc']['lcb']['slopes']))
                print(str1+';', file=text_file)
                
                # str1 = 'param adjLCB := ' +  "{:.8f}".format(self.vessel.info['lcb_mtc']['lcb']['adj'])
                # print(str1+';', file=text_file)
                
                str1 = 'param mLCB := '
                for m_ in range(1, len(self.vessel.info['lcb_mtc']['lcb']['slopes'])+1):
                    str1 +=  str(m_) + ' ' + str(round(self.vessel.info['lcb_mtc']['lcb']['slopes'][m_-1],8))  + ' '
                print(str1+';', file=text_file)
                    
                print('# breaks of LCB x Disp curve', file=text_file)
                str1 = 'param bLCB := '
                for m_ in range(1,len(self.vessel.info['lcb_mtc']['lcb']['slopes'])):
                    str1 += str(m_) + ' ' + str(round(self.vessel.info['lcb_mtc']['lcb']['breaks'][m_-1],8))  + ' '
                print(str1+';', file=text_file)
                    
                print('# slopes of MTC curve', file=text_file)
                str1 = 'param pwMTC := ' +  str(len(self.vessel.info['lcb_mtc']['mtc']['slopes']))
                print(str1+';', file=text_file)
                str1 = 'param mMTC := '
                for m_ in range(1, len(self.vessel.info['lcb_mtc']['mtc']['slopes'])+1):
                    str1 += str(m_) + ' ' + str(round(self.vessel.info['lcb_mtc']['mtc']['slopes'][m_-1],10))  + ' '
                print(str1+';', file=text_file)
                    
                print('# breaks of MTC curve', file=text_file)
                str1 = 'param bMTC := ' 
                for m_ in range(1,len(self.vessel.info['lcb_mtc']['mtc']['slopes'])):
                    str1 += str(m_) + ' ' + str(round(self.vessel.info['lcb_mtc']['mtc']['breaks'][m_-1],10))  + ' '
                print(str1+';', file=text_file)
                
                print('# upper limit on displacement', file=text_file)
                # stability - draft
                str1 = 'param displacementLimit := '
                for i_, j_ in self.displacement_upper.items():
                    str1 += str(i_) + ' ' +  "{:.5f}".format(j_) + ' '
                print(str1+';', file=text_file)
                
                print('# lower limit on displacement', file=text_file)
                str1 = 'param displacementLowLimit := '
                for i_, j_ in self.displacement_lower.items():
                    str1 += str(i_) + ' ' +  "{:.5f}".format(j_) + ' '
                print(str1+';', file=text_file)
                
                print('# deadweight constraint', file=text_file)
                #str1 = 'param deadweight   := ' + str(self.vessel.info['draftCondition']['deadweight']) 
                str1 = 'param deadweight   := ' + str(1000000) 
                print(str1+';', file=text_file)
                
                if ave_trim:
                    print('# ave trim', file=text_file)
                    str1 = 'param ave_trim := '
                    for i_, j_ in ave_trim.items():
                        str1 += str(i_) + ' ' +  "{:.2f}".format(j_) + ' '
                    print(str1+';', file=text_file)
                
                print('# base draft', file=text_file)
                str1 = 'param base_draft := '
                for i_, j_ in self.base_draft.items():
                    str1 += str(i_) + ' ' +  "{:.2f}".format(j_) + ' '
                print(str1+';', file=text_file)
                
                print('# draft corr', file=text_file)
                str1 = 'param draft_corr := '
                for k_, v_ in self.trim_upper.items():
                    # if v_ >= 3.8:
                    #     if self.base_draft[k_] <= 13:
                    #         str1 += str(k_) + ' ' +  "0.2" + ' '
                    #     else:
                    #         str1 += str(k_) + ' ' +  "0.1" + ' '
                            
                    if mean_draft.get(k_, 22.0) <= 10:
                        str1 += str(k_) + ' ' +  "0.2" + ' '
                    else:
                        str1 += str(k_) + ' ' +  "0.1" + ' '
                    
                    # if v_ > 0.5:
                    #     str1 += str(k_) + ' ' +  "0.1" + ' '
                print(str1+';', file=text_file)
                
                print('# slopes of draft curve', file=text_file)
                str1 = 'param pwDraft := ' +  str(len(self.vessel.info['lcb_mtc']['draft']['slopes']))
                print(str1+';', file=text_file)
                str1 = 'param mDraft := '
                for m_ in range(1, len(self.vessel.info['lcb_mtc']['draft']['slopes'])+1):
                    str1 += str(m_) + ' ' + str(round(self.vessel.info['lcb_mtc']['draft']['slopes'][m_-1],18))  + ' '
                print(str1+';', file=text_file)
                    
                print('# breaks of draft curve', file=text_file)
                str1 = 'param bDraft :='
                for m_ in range(1,len(self.vessel.info['lcb_mtc']['draft']['slopes'])):
                    str1 += str(m_) + ' ' + str(round(self.vessel.info['lcb_mtc']['draft']['breaks'][m_-1],8))  + ' '
                print(str1+';', file=text_file)
                
                print('# number of frames ',file=text_file)#
                str1 = 'param Fr := ' + str(len(self.vessel.info['frames'])) 
                print(str1+';', file=text_file)
                
                print('# weight ratio for SF and BM',file=text_file)#
                str1 = 'param weightRatio_ct := '
                print(str1, file=text_file)
                for i_, j_ in self.vessel.info['tankGroup'].items():
                    str1 = '['+ str(i_) + ',*] = '
                    for u_, v_ in j_.items():
                        if u_ in cargo_tanks_:
                            str1 += u_ + ' ' + str(round(v_['wr'],4)) + ' '
                    
                    if str1 != '['+ str(i_) + ',*] = ':
                        print(str1, file=text_file)
                print(';', file=text_file)
                
                str1 = 'param weightRatio_bt := '
                print(str1, file=text_file)
                for i_, j_ in self.vessel.info['tankGroup'].items():
                    str1 = '['+ str(i_) + ',*] = '
                    for u_, v_ in j_.items():
                        if u_ in ballast_tanks_:
                            str1 += u_ + ' ' + str(round(v_['wr'],4)) + ' '
                    
                    if str1 != '['+ str(i_) + ',*] = ':
                        print(str1, file=text_file)
                print(';', file=text_file)
                
                str1 = 'param weightRatio_ot := '
                print(str1, file=text_file)
                for i_, j_ in self.vessel.info['tankGroup'].items():
                    str1 = '['+ str(i_) + ',*] = '
                    for u_, v_ in j_.items():
                        if u_ in other_tanks_:
                            str1 += u_ + ' ' + str(round(v_['wr'],4)) + ' '
                    
                    if str1 != '['+ str(i_) + ',*] = ':
                        print(str1, file=text_file)
                print(';', file=text_file)
                
                
                print('# LCG for SF and BM ',file=text_file)#
                str1 = 'param LCG_ct := '
                print(str1, file=text_file)
                for i_, j_ in self.vessel.info['tankGroup'].items():
                    str1 = '['+ str(i_) + ',*] = '
                    for u_, v_ in j_.items():
                        if u_ in cargo_tanks_:
                            str1 += u_ + ' ' + str(round(v_['lcg'],4)) + ' '
                    
                    if str1 != '['+ str(i_) + ',*] = ':
                        print(str1, file=text_file)
                print(';', file=text_file)
                
                str1 = 'param LCG_bt := '
                print(str1, file=text_file)
                for i_, j_ in self.vessel.info['tankGroup'].items():
                    str1 = '['+ str(i_) + ',*] = '
                    for u_, v_ in j_.items():
                        if u_ in ballast_tanks_:
                            str1 += u_ + ' ' + str(round(v_['lcg'],4)) + ' '
                    
                    if str1 != '['+ str(i_) + ',*] = ':
                        print(str1, file=text_file)
                print(';', file=text_file)
               
                str1 = 'param LCG_ot := '
                print(str1, file=text_file)
                for i_, j_ in self.vessel.info['tankGroup'].items():
                    str1 = '['+ str(i_) + ',*] = '
                    for u_, v_ in j_.items():
                        if u_ in other_tanks_:
                            str1 += u_ + ' ' + str(round(v_['lcg'],4)) + ' '
                    
                    if str1 != '['+ str(i_) + ',*] = ':
                        print(str1, file=text_file)
                print(';', file=text_file)
                 
                str1 = 'param LCG_fr := '
                for i_, j_ in self.vessel.info['tankGroupLCG'].items():
                    str1 += str(i_) + ' ' + str(round(j_,3)) + ' '
                print(str1+';', file=text_file)
                
                print('# lower limit SF ',file=text_file)#
                str1 = 'param lowerSFlimit := '
                for i_, j_ in enumerate(self.vessel.info['frames']):
                    str1 += str(i_+1) + ' ' +  str(round(float(self.vessel.info['SFlimits'][j_][0])/1000*self.sf_bm_frac,5)) + ' '      
                print(str1+';', file=text_file)
                
                print('# upper limit SF ',file=text_file)#
                str1 = 'param upperSFlimit := '
                for i_, j_ in enumerate(self.vessel.info['frames']):
                    str1 += str(i_+1) + ' ' +  str(round(float(self.vessel.info['SFlimits'][j_][1])/1000*self.sf_bm_frac,5)) + ' '      
                print(str1+';', file=text_file)
                
                str1 = 'param BV_SF := '
                print(str1, file=text_file)
                for i_, j_ in self.vessel.info['tankGroup'].items():
                    str1 = '['+ str(i_) + ',*] = '
                    for k_, v_ in self.sf_base_value.items():
                        str1 += str(k_) + ' ' + str(round(v_[int(i_)-1],5)) + ' '
                    print(str1, file=text_file)
                print(';', file=text_file)
                
                str1 = 'param CD_SF := '
                print(str1, file=text_file)
                for i_, j_ in self.vessel.info['tankGroup'].items():
                    str1 = '['+ str(i_) + ',*] = '
                    for k_, v_ in self.sf_draft_corr.items():
                        str1 += str(k_) + ' ' + str(round(v_[int(i_)-1],5)) + ' '
                    print(str1, file=text_file)
                print(';', file=text_file)
                
                str1 = 'param CT_SF := '
                print(str1, file=text_file)
                for i_, j_ in self.vessel.info['tankGroup'].items():
                    str1 = '['+ str(i_) + ',*] = '
                    for k_, v_ in self.sf_trim_corr.items():
                        str1 += str(k_) + ' ' + str(round(v_[int(i_)-1],5)) + ' '
                    print(str1, file=text_file)
                print(';', file=text_file)
                
                
                
                print('# lower limit BM ',file=text_file)#
                str1 = 'param lowerBMlimit := '
                for i_, j_ in enumerate(self.vessel.info['frames']):
                    str1 += str(i_+1) + ' ' +  str(round(float(self.vessel.info['BMlimits'][j_][0])/1000*self.sf_bm_frac,5)) + ' '      
                print(str1+';', file=text_file)
                
                print('# upper limit BM ',file=text_file)#
                str1 = 'param upperBMlimit := '
                for i_, j_ in enumerate(self.vessel.info['frames']):
                    str1 += str(i_+1) + ' ' +  str(round(float(self.vessel.info['BMlimits'][j_][1])/1000*self.sf_bm_frac,5)) + ' '      
                print(str1+';', file=text_file)
                
                
                str1 = 'param BV_BM := '
                print(str1, file=text_file)
                for i_, j_ in self.vessel.info['tankGroup'].items():
                    str1 = '['+ str(i_) + ',*] = '
                    for k_, v_ in self.bm_base_value.items():
                        str1 += str(k_) + ' ' + str(round(v_[int(i_)-1],5)) + ' '
                    print(str1, file=text_file)
                print(';', file=text_file)
                
                str1 = 'param CD_BM := '
                print(str1, file=text_file)
                for i_, j_ in self.vessel.info['tankGroup'].items():
                    str1 = '['+ str(i_) + ',*] = '
                    for k_, v_ in self.bm_draft_corr.items():
                        str1 += str(k_) + ' ' + str(round(v_[int(i_)-1],5)) + ' '
                    print(str1, file=text_file)
                print(';', file=text_file)
                
                str1 = 'param CT_BM := '
                print(str1, file=text_file)
                for i_, j_ in self.vessel.info['tankGroup'].items():
                    str1 = '['+ str(i_) + ',*] = '
                    for k_, v_ in self.bm_trim_corr.items():
                        str1 += str(k_) + ' ' + str(round(v_[int(i_)-1],5)) + ' '
                    print(str1, file=text_file)
                print(';', file=text_file)
                
                str1 = 'param IIS := ' 
                str1 += '1' if IIS else '0'
                print(str1+';', file=text_file)
                
                print('# runtime limit ',file=text_file)#  
                str1 = 'param runtimeLimit := 30'
                print(str1+';', file=text_file)

                
              
        
        
    def _get_plan(self, stowageDetails, cargo_info_, cargoDetails, commingleDetails = [], initial = True, not_cargo = [], strip_info = False):
        
        arr_plan_ =  cargo_info_['cargo_plans'][0] if len(cargo_info_['cargo_plans']) > 0 else []
        if not initial:
            init_tanks_ = [k_ for k_, v_ in arr_plan_.items() if v_[0]['quantityMT'] > 0]
        else:
            init_tanks_ = []
        
        if strip_info:
            cur_cargo_ = cargo_info_['discharging_order'][len(cargo_info_['cargo_plans'])-1]
            cur_cargo_ = cargo_info_['dsCargoNominationId'][cur_cargo_] 
        
        plan_, tanks_ = {}, []
        wt_ = 0.0
        
        
            
        for d_ in stowageDetails:
            tank_ = self.vessel.info['tankId'][d_['tankId']]
            
            cargo_ = d_.get('cargoNominationId', None)
            if cargo_ not in [None]:
                cargo_ = 'P' + str(cargo_)
                tanks_.append(tank_)
            
            if not cargo_:
                continue
            elif cargo_info_['cargoNominationId'][cargo_] not in not_cargo:
                
                self._get_plan1(d_["cargoNominationId"], d_["tankId"], d_["quantityMT"], 
                                d_.get('cargoId',None), d_.get('colorCode',None), d_.get('abbreviation',None),
                                plan_, cargo_info_, cargoDetails, initial)
                
                wt_ += float(d_["quantityMT"])
                
                if strip_info and float(d_["quantityMT"]) == 0 and cargo_ == cur_cargo_:
                    cargo_info_['stripping_tanks'][len(cargo_info_['cargo_plans'])].append(tank_)
                    
            else:
                # print('Get from arr_plan_')
                plan_[tank_] = arr_plan_[tank_]
                
            
        # for d_ in commingleDetails:
        #     ## not supported
        #     if initial:
        #         self.commingle_preloaded = True 
        #     else:
        #         self.commingle_loading = True
            
        #     self._get_plan2(d_, plan_, cargo_info_, cargoDetails, initial, not_cargo)
            
        # print(set(init_tanks_)-set(tanks_))
        
        if not initial:
            for t_ in set(init_tanks_)-set(tanks_):
                
                if strip_info and arr_plan_[t_][0]['cargo'] == cur_cargo_:
                    cargo_info_['stripping_tanks'][len(cargo_info_['cargo_plans'])].append(t_)
                    
                plan_[t_] = deepcopy(arr_plan_[t_])
                plan_[t_][0]['quantityMT'] = 0.
                plan_[t_][0]['quantityM3'] = 0.
                
        for t_ in self.vessel.info['cargoTanks']:
            if t_ not in plan_:
                plan_[t_] = [{'quantityMT': 0., 'cargo': None, 
                              'quantityM3': 0., 
                              'SG': None, 'tankId': 25580, 'api': None, 
                              'temperature': None, 
                              'tcg': None, 'lcg': None, 'corrUallage': None, 
                              'cargoId': None, 'colorCode': None, 'abbreviation': None}]
                
        cargo_info_['cargo_plans'].append(plan_)   
        
        if initial:
            cargo_info_['initCargoWeight'] = wt_
            cargo_info_['initCargoWeight1'] = {}
            
            for k_, v_ in plan_.items():
                if v_[0]['cargo'] not in cargo_info_['initCargoWeight1'].keys():
                    cargo_info_['initCargoWeight1'][v_[0]['cargo']] = v_[0]['quantityMT']
                else:
                    cargo_info_['initCargoWeight1'][v_[0]['cargo']] += v_[0]['quantityMT']
                    
                    


    def _get_plan1(self, cargoNominationId, tankId, quantityMT, cargoId, color, abbrev, plan_, cargo_info_, cargoDetails, initial):
        
        cargo_, tank_, wt_ = 'P'+str(cargoNominationId), tankId, quantityMT
            
        if cargo_ not in cargo_info_['density']:
            i_ = [j_ for j_ in cargoDetails if j_["cargoNominationId"] == cargoNominationId][0]
            cargo_info_['density'][cargo_] = self._cal_density(float(i_['estimatedAPI']),float(i_['estimatedTemp']))
            cargo_info_['api'][cargo_] = float(i_['estimatedAPI'])
            cargo_info_['temperature'][cargo_] = float(i_['estimatedTemp'])
            cargo_info_['cargoId'][cargo_] = cargoId
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
            
        
        # if tankName_[-1] == 'C' or tankName_ in ['SLS', 'SLP']:
        #     tank1_ = tankName_ 
        # else:
        #     tank1_ = tankName_[:-1] + 'W'
            
        tank1_ = tankName_
            
        
        if cargo_ not in cargo_info_['cargo_tank']:
            cargo_info_['cargo_tank'][cargo_] = [tank1_]
            
        elif tank1_ not in cargo_info_['cargo_tank'][cargo_]:
            cargo_info_['cargo_tank'][cargo_].append(tank1_)
            
        if initial and cargo_ not in self.preloaded_cargos :
            self.preloaded_cargos.append(cargo_)
            
        # elif (cargo_ not in self.to_load_cargos) and (cargo_ not in self.preloaded_cargos):
        #     self.to_load_cargos.append(cargo_)
        
    def _get_plan2(self, d_, plan_, cargo_info_, cargoDetails, initial, not_cargo):
        
        cargo1_, cargo2_ = 'P'+str(d_['cargo1NominationId']), 'P'+str(d_['cargo2NominationId'])
        
        if cargo1_ not in not_cargo:
            # load cargo 1
            self._get_plan1(d_["cargo1NominationId"], d_["tankId"], d_["cargo1QuantityMT"],
                            d_.get('cargoId',None), d_.get('colorCode',None), d_.get('abbreviation',None),
                            plan_, cargo_info_, cargoDetails, initial)
        
        if cargo2_ not in not_cargo:
            # load cargo 2
            self._get_plan1(d_["cargo2NominationId"], d_["tankId"], d_["cargo2QuantityMT"],
                            d_.get('cargoId',None), d_.get('colorCode',None), d_.get('abbreviation',None),
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
        
               
        
    def _get_rob(self, onhand, cargo_info_):
        
        DENSITY = self.config['rob_density']
        
        plan_i_, plan_f_ = {}, {}
        wt_i_, wt_f_  = 0., 0.
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
                
                wt_f_ += float(wt_)
                
        cargo_info_['ROB'] = [plan_i_, plan_f_]
        cargo_info_['depROBweight'] = wt_f_
        
        
    def _get_ballast(self, ballast, cargo_info_):
        
        density_ = 1.025 #  ballast density
        # density_ = self.seawater_density
        plan_ = {}
        wt1_ = 0
        for d_ in ballast:
            tank_, wt_ = d_['tankId'], d_['quantityMT']
            tankName_ = self.vessel.info['tankId'][tank_]
            color_ = d_.get('colorCode', None)
            
            if tankName_ not in cargo_info_['ballastTanksUsed'] and tankName_ not in self.vessel.info['banBallast']:
                cargo_info_['ballastTanksUsed'].append(tankName_)
                # print(tankName_)
                
            
            self.ballast_color[tankName_] = color_
            
            if wt_ not in [None, '0', 'null']:
               
               wt1_ += float(wt_) 
               
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
        
        if len(cargo_info_['ballast']) == 0:
            cargo_info_['initBallastWeight'] = wt1_
            
        cargo_info_['ballast'].append(plan_)
        
    def _cal_density(self, api, temperature_F):
        
        ## https://www.myseatime.com/blog/detail/cargo-calculations-on-tankers-astm-tables
    
        a60 = 341.0957/(141360.198/(api+131.5))**2
        dt = temperature_F-60
        vcf_ = np.exp(-a60*dt*(1+0.8*a60*dt))
        t13_ = (535.1911/(api+131.5)-0.0046189)*0.42/10
        density = t13_*vcf_*6.2898
        
    
        return round(density,6)
                
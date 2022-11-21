# -*- coding: utf-8 -*-
"""
Created on Sat Oct 23 23:59:50 2021

@author: I2R
"""

from copy import deepcopy
import numpy as np

STAGE_INFO = ['time', 'foreDraft', 'meanDraft', 'afterDraft', 'trim', 'heel', 'airDraft', 'bendinMoment', 'shearForce', 'gom', 'UKC' ]


class Discharging_seq:
    def __init__(self, data, stability):
        
        self.plans = data   # .ship_status_dep, .ballast_weight 
        self.stability = stability[0]  # single plan only
        
        self.stages = []
        self.pre_port = 0 # for collecting ballast weight
        self.delay = data.input.initial_delay
        self.last_plan = None
        self.interval = {}
        self.start_time = data.input.start_time # start time only
   
    
    def _stage(self, info, cargo, cargo_order, final_event = 0):
        ##print(info['stage'])
        
        # EVENTS = ["initialCondition", "floodSeparator", "warmPumps",
        #           "initialRate", "increaseToMaxRate", "dischargingAtMaxRate", 
        #           "reducedRate"]
        
        # 'initialCondition' -> "initialCondition", "floodSeparator", "warmPumps"
        # 'initialRate' -> "initialRate"
        # 'increaseToMaxRate' -> "increaseToMaxRate"
        # 'dischargingAtMaxRate' -> "dischargingAtMaxRate"
        # 'stripping' -> "reducedRate"
        
        start_time_ = self.plans.input.discharging.seq[str(cargo_order)]['startTime'] + self.start_time + self.delay
        self.start1 = start_time_
        if info['stage'] == 'initialCondition' and cargo_order > 1:
            # delay
            self.delay += self.plans.input.discharging.info['timing_delay1'][cargo_order-2]
            
        
        
        
        # info["timeStart"] = ''
        # info["timeEnd"] = ''
        info["toLoadicator"] = False
        info["jumpStep"] = False
        info['dischargePlanPortWiseDetails'] = []
        info["cargoValves"] = []
        info["ballastValves"] = []
        
        info["ballastRateM3_Hr"] = {}
        info["deballastingRateM3_Hr"] = {}
        info["cargoDischargingRatePerTankM3_Hr"] = []
        info["cargoDischargingRateM3_Hr"] = {}
        info["ballast"] = {}
        info["TCP"] = {}
        info["STPED"] = {}
        info["STP"] = {}
        info["cargo"] = {}
        info["simCargoDischargingRatePerTankM3_Hr"] = []
        info["simBallastingRatePerTankM3_Hr"] = [{}] # USELESS
        info["simDeballatingRatePerTankM3_Hr"] = [{}] # USELESS
        
        info["Cleaning"] = {"TopClean":[], "BtmClean":[], "FullClean":[]}
        info["stripping"] = []
        info["transfer"] = [{}]
        info["cowStartTime"] = None
        
        if info['stage'] == 'initialCondition':
            
            info["simCargoDischargingRatePerTankM3_Hr"] = [{}]
            info["simDeballastingRateM3_Hr"] = [{}]
            info["simBallastingRateM3_Hr"] = [{}]
            
        
            # print('----', info['stage'])
            info["toLoadicator"] = True
            info["jumpStep"] = True
            start_ = int(0 + start_time_ + self.delay)
            end_   = int(0 + start_time_ + self.delay)
            info["timeStart"] = str(start_)
            info["timeEnd"] = str(end_)
            
#            print('initialCondition', start_, end_)
            
            plan_ = {'time': str(int(info["timeStart"])), 
                     "dischargeQuantityCommingleCargoDetails":[],
                     "dischargePlanStowageDetails":[],
                     "dischargePlanBallastDetails":[],
                     "dischargePlanRoBDetails":[]}
            
            if cargo_order == 1:
                self._get_plan(plan_)
            else:
                plan_ = {k_: v_ for k_, v_ in self.last_plan.items() if k_ in ['time', \
                   'dischargeQuantityCommingleCargoDetails', 'dischargePlanStowageDetails', \
                   'dischargePlanBallastDetails', 'dischargePlanRoBDetails', 'ballastVol', \
                'cargoVol', 'foreDraft', 'meanDraft', 'afterDraft', 'trim', 'heel', 'airDraft', \
                    'bendinMoment', 'shearForce', 'UKC', 'displacement']}
            
            plan_['time'] = info["timeEnd"]
            info['dischargePlanPortWiseDetails'].append(plan_)
            
            if cargo_order == 1:
                self.initial_plan = plan_
            
            if len(self.stages) > 0 and (self.stages[-1]['time'] == plan_['time']):
                pass
            else:
                
                info_ = {'time': plan_['time'], 
                         'foreDraft': plan_['foreDraft'], 
                         'meanDraft': plan_['meanDraft'], 
                         'afterDraft': plan_['afterDraft'], 
                         'trim': plan_['trim'], 
                         'heel': None, 
                         'gom': None,
                         'airDraft': plan_['airDraft'],
                         'bendinMoment': plan_['bendinMoment'], 
                         'shearForce': plan_['shearForce'],
                         'UKC':plan_.get('UKC', None),
                         'displacement': plan_.get('displacement', None)
                         }
                self.stages.append(info_) # add displacement info
            
            
            
        elif info['stage'] == 'floodSeparator':
            
            info["simCargoDischargingRatePerTankM3_Hr"] = [{}]
            info["simDeballastingRateM3_Hr"] = [{}]
            info["simBallastingRateM3_Hr"] = [{}]
            
            self.interval['floodSeparator'] = self.plans.input.discharging.seq[str(cargo_order)]['info']['stages_timing']['Flood Separator'][1] - \
                self.plans.input.discharging.seq[str(cargo_order)]['info']['stages_timing']['Flood Separator'][0] 
           
            
            start_ = int(0 + start_time_ + self.delay)
            end_   = int(self.interval['floodSeparator'] + start_time_ + self.delay)
            info["timeStart"] = str(start_)
            info["timeEnd"] = str(end_)
            
#            print('floodSeparator', start_, end_)
            
            info["dischargePlanPortWiseDetails"] = [{"time": str(end_),
                                                     "dischargeQuantityCommingleCargoDetails": [],
                                                     "dischargePlanStowageDetails": [],
                                                     "dischargePlanBallastDetails": [],
                                                     "dischargePlanRoBDetails": []
                                                     }]
            
            
        
        elif info['stage'] == 'warmPumps':
            
            info["simCargoDischargingRatePerTankM3_Hr"] = [{}]
            info["simDeballastingRateM3_Hr"] = [{}]
            info["simBallastingRateM3_Hr"] = [{}]
            
            self.interval['warmPumps'] = self.plans.input.discharging.seq[str(cargo_order)]['info']['stages_timing']['Warming Pumps'][1] - \
                self.plans.input.discharging.seq[str(cargo_order)]['info']['stages_timing']['Warming Pumps'][0] 
                
            time_ = self.interval['floodSeparator']    
            start_ = int(time_ + start_time_ + self.delay)
            time_ += self.interval['warmPumps']  
            end_   = int(time_ + start_time_ + self.delay)
            info["timeStart"] = str(start_)
            info["timeEnd"] = str(end_)
            
#            print("warmPumps", start_, end_)
            info["dischargePlanPortWiseDetails"] = [{"time": str(end_),
                                                     "dischargeQuantityCommingleCargoDetails": [],
                                                     "dischargePlanStowageDetails": [],
                                                     "dischargePlanBallastDetails": [],
                                                     "dischargePlanRoBDetails": []
                                                     }]
            
            
            local_time_start_ = start_ - self.plans.input.discharging.seq[str(cargo_order)]['startTime'] - self.delay - \
                           self.start_time
            pump_ = [k_ for k_, v_ in self.plans.input.discharging.seq[str(cargo_order)]['pump'].items() \
                  if "COP" in k_ and int(v_[0]) <= local_time_start_ <= int(v_[1])]# and v_[0] <= time_end__ <= v_[1] ]
            
#            print('pump used', pump_, local_time_start_)
            if len(pump_) > 0:
                # rate_ = total_rate_/len(pump_)
                # vol_ = rate_*(int(info["timeEnd"]) - int(info["timeStart"]))/60
                for pp_ in pump_:
                    id_ = self.plans.input.vessel.info['cargoPumpId'][pp_]['id']
                    
                    if id_ not in  info["cargo"]:
                        info["cargo"][id_] = [{"rateM3_Hr": "",
                                              "quantityM3": "",
                                              "timeStart": str(start_),
                                              "timeEnd": str(end_)}]    
                    else:
                        info["cargo"][id_].append({"rateM3_Hr": "",
                                              "quantityM3": "",
                                              "timeStart": str(start_),
                                              "timeEnd": str(end_)})
                        
#            print(info["cargo"])

        elif info['stage'] == 'initialRate':
            
            # info["simCargoDischargingRatePerTankM3_Hr"] = [{}]
           
            
            start_ = int(self.plans.input.discharging.seq[str(cargo_order)]['stageInterval'][info['stage']][0] + start_time_ + self.delay)
            end_   = int(self.plans.input.discharging.seq[str(cargo_order)]['stageInterval'][info['stage']][1] + start_time_ + self.delay)
            info["timeStart"] = str(start_)
            info["timeEnd"] = str(end_)
#            print('initialRate', start_, end_)
            
            info["dischargePlanPortWiseDetails"] = [{"time": str(end_),
                                                     "dischargeQuantityCommingleCargoDetails": [],
                                                     "dischargePlanStowageDetails": [],
                                                     "dischargePlanBallastDetails": [],
                                                     "dischargePlanRoBDetails": []
                                                     }]
            
            # info["cargoDischargingRatePerTankM3_Hr"] 
            # info["simCargoDischargingRatePerTankM3_Hr"] 
            # info["cargo"] cargo pump
            self._get_cargo_rate(info, cargo_order, 'InitialRatePerTank', start_, end_)   
            
            
            # print(info)
            
        elif info['stage'] == 'increaseToMaxRate':
            start_ = int(self.plans.input.discharging.seq[str(cargo_order)]['stageInterval'][info['stage']][0] + start_time_ + self.delay)
            end_   = int(self.plans.input.discharging.seq[str(cargo_order)]['stageInterval'][info['stage']][1] + start_time_ + self.delay)
            info["timeStart"] = str(start_)
            info["timeEnd"] = str(end_)
#            print('increaseToMaxRate', start_, end_)
            
            info["dischargePlanPortWiseDetails"] = [{"time": str(end_),
                                                     "dischargeQuantityCommingleCargoDetails": [],
                                                     "dischargePlanStowageDetails": [],
                                                     "dischargePlanBallastDetails": [],
                                                     "dischargePlanRoBDetails": []
                                                     }]
            
            # info["cargoDischargingRatePerTankM3_Hr"] 
            # info["simCargoDischargingRatePerTankM3_Hr"] 
            # info["cargo"] cargo pump flow
            self._get_cargo_rate(info, cargo_order, 'IncMaxPerTank', start_, end_) 
            
            
            ## 
            # print(pump_)
            
           
            
        elif info['stage'] == 'dischargingAtMaxRate':
            
            start_ = int(self.plans.input.discharging.seq[str(cargo_order)]['stageInterval'][info['stage']][0] + start_time_ + self.delay)
            end_   = int(self.plans.input.discharging.seq[str(cargo_order)]['stageInterval'][info['stage']][1] + start_time_ + self.delay)
            info["timeStart"] = str(start_)
            info["timeEnd"] = str(end_)
#            print('dischargingAtMaxRate', start_, end_)
            
            info['simDeballastingRateM3_Hr'] = []
            info['simBallastingRateM3_Hr'] = []
            
            info['totDeballastingRateM3_Hr'] = []
            info['totBallastingRateM3_Hr'] = []
            
            max_rate_ = self.plans.input.discharging.discharging_rate[cargo_order]
            info["cargoDischargingRateM3_Hr"] = {0:str(max_rate_)}
           
            
            # tot_num_ = len(self.plans.input.discharging.seq[cargo]['tanks'])
            info["cargoDischargingRatePerTankM3_Hr"] = []
            info["simCargoDischargingRatePerTankM3_Hr"] = []
            
            time_start__ = start_
            info['simIniDeballastingRateM3_Hr'] = {}
            info['simIniBallastingRateM3_Hr'] = {}
            info['iniDeballastingRateM3_Hr'] = {}
            info['iniBallastingRateM3_Hr'] = {}
            info['iniTotDeballastingRateM3_Hr'] = 0.
            info['iniTotBallastingRateM3_Hr'] = 0.
            info['stageEndTime'] = {}
            info['port'] = []
            pre_port_ = self.pre_port
            
            port__, rm_ = 0, 0
            for k_ in self.plans.input.discharging.seq[str(cargo_order)]['gantt'].keys():
                if k_[:3] in ['Max']:
                    
                    time_end__ = self.plans.input.discharging.seq[str(cargo_order)]['gantt'][k_]['Time'] + \
                                start_time_ + self.delay
                                
#                    print(k_, time_start__, time_end__)
                    self._get_cargo_rate(info, cargo_order, k_+'PerTank', time_start__, time_end__) 
                    
                    
                    ## ballast
                    ballast_plan_ = {'deballastingRateM3_Hr':{}, 'ballastingRateM3_Hr':{}}
                    port_ = 0
                    v_ = k_+str(cargo_order)
                    for a_, b_ in self.plans.input.loadable.info['stages'].items():
                        if b_ == v_:
                            port_ = a_
                            port__ = port_
                            break
                    
                    if port_ == 0:
                        port_ = port__+1
                        rm_ = -1
                        
#                    print(port_, v_)
                        
                    # pre_time_ = time_start__
                    # time_ = cur_time_-pre_time_
                    self._get_ballast_rate(ballast_plan_, port_)
                    
                    # if pre_port_ == self.pre_port:
                    #     pre_time_ += start_  # start of maxloading1
                        # print(pre_port_, self.pre_port, pre_time_, v_)
                            
                    # print(port_,pre_port_,cur_time_,pre_time_)
                    # print()
                    start1_ = int(time_start__)
                    end1_ = int(time_end__)
                    
                    info_ = {}
                    for k1_, v1_ in  ballast_plan_['deballastingRateM3_Hr'].items():
                        info_[k1_] = {'tankShortName': self.plans.input.vessel.info['tankId'][k1_],
                                     'rate': v1_,
                                     "timeStart": str(start1_), "timeEnd": str(end1_)}
                    info['simDeballastingRateM3_Hr'].append(info_)
                    
                    info_ = {}
                    for k1_, v1_ in  ballast_plan_['ballastingRateM3_Hr'].items():
                        info_[k1_] = {'tankShortName': self.plans.input.vessel.info['tankId'][k1_],
                                     'rate': v1_,
                                     "timeStart": str(start1_), 
                                     "timeEnd": str(end1_)}
                    info['simBallastingRateM3_Hr'].append(info_)
                    
                    info['totDeballastingRateM3_Hr'].append(ballast_plan_['totDeballastingRateM3_Hr'])
                    info['totBallastingRateM3_Hr'].append(ballast_plan_['totBallastingRateM3_Hr'])
                    
                    pre_port_ = port_ + rm_
                    
                    if k_== 'MaxDischarging1':
                        
                        # pass to other stage prior to MaxLoading1
                        info['iniDeballastingRateM3_Hr'] = deepcopy(ballast_plan_['deballastingRateM3_Hr'])
                        info['iniBallastingRateM3_Hr'] = deepcopy(ballast_plan_['ballastingRateM3_Hr'])
                        
                        info['iniTotDeballastingRateM3_Hr'] = deepcopy(ballast_plan_['totDeballastingRateM3_Hr'])
                        info['iniTotBallastingRateM3_Hr'] = deepcopy(ballast_plan_['totBallastingRateM3_Hr'])
                        
                        info['iniSimDeballastingRateM3_Hr'] = deepcopy(info['simDeballastingRateM3_Hr'][0])
                        info['iniSimBallastingRateM3_Hr'] = deepcopy(info['simBallastingRateM3_Hr'][0])
                        
                    
                    
                    time_start__ = time_end__
                    
            info["toLoadicator"] = True      
            info["jumpStep"] = True
            
            # print('self.pre_port', self.pre_port)
            # {1: 'MaxLoading11', 2: 'MaxLoading21', 3: 'MaxLoading31', 4: 'MaxLoading41', 5: 'MaxLoading51', 6: 'MaxLoading61', 7: 'Topping61', 8: 'MaxLoading12', 9: 'MaxLoading22', 10: 'MaxLoading32', 11: 'Topping42'}
            
            for k_, v_ in self.plans.input.loadable.info['stages'].items():
                
                if v_[:3] in ['Max'] and v_[-1] == str(cargo_order):
                    
                    # print(k_, v_)
                    # last_max_stage_ = v_[:-1]
                    # all stages before last max stages
                    time_ = int(self.plans.input.discharging.seq[str(cargo_order)]['gantt'][v_[:-1]]['Time'] +
                                    start_time_ + self.delay)
                    
                    plan_ = {'time': str(time_), 
                            "dischargeQuantityCommingleCargoDetails":[],
                            "dischargePlanStowageDetails":[],
                            "dischargePlanBallastDetails":[],
                            "dischargePlanRoBDetails":[]}
                
                    port_ = [a_ for a_, b_ in self.plans.input.loadable.info['stages'].items() if b_ == v_][0]
                    self._get_plan(plan_, port_)
                    
                    info['port'].append(port_)
                    
                    info['dischargePlanPortWiseDetails'].append(plan_)
                        
                    info['stageEndTime'][v_[:-1]] = time_
                    
                    info_ = {} # get stability info
                    for a_, b_ in plan_.items():
                        if a_ in STAGE_INFO:
                            info_[a_] = b_
                            # if a_ in ['time']:
                            #     info_[a_] = str(int(info_[a_]) + self.delay)
                            
                    self.stages.append(info_)    

            self.pre_port = pre_port_
#            print('pre_port_:',pre_port_)
                    
            
        elif info['stage'] == 'reducedRate':
            
            if len(self.plans.input.discharging.seq[str(cargo_order)]['info']['tanksCOWed']) > 0:
                info['stage'] = 'COWStripping'
            
            if len(self.plans.input.discharging.info['stripping_tanks'][cargo_order]) > 0:
                info['stage'] = 'COWStripping'
            
            start_ = int(self.plans.input.discharging.seq[str(cargo_order)]['stageInterval']['stripping'][0] + start_time_ + self.delay)
            end_   = int(self.plans.input.discharging.seq[str(cargo_order)]['stageInterval']['stripping'][1] + start_time_ + self.delay)
            info["timeStart"] = str(start_)
            info["timeEnd"] = str(end_)
            
#            print('reducedRate', start_, end_)
            
            info['simDeballastingRateM3_Hr'] = [{}]
            info["cargoDischargingRatePerTankM3_Hr"] = []
            info["simCargoDischargingRatePerTankM3_Hr"] = []
            
            
            info['simBallastingRateM3_Hr'] = []
            
            info['totDeballastingRateM3_Hr'] = []
            info['totBallastingRateM3_Hr'] = []
            info['port'] = []
            timing_ = {}
            time_start__ = start_
            for k_ in self.plans.input.discharging.seq[str(cargo_order)]['gantt'].keys():
                if k_[:3] in ['Str']:
                    
                    time_end__ = self.plans.input.discharging.seq[str(cargo_order)]['gantt'][k_]['Time'] + \
                                start_time_ + self.delay
                                
#                    print(k_, time_start__, time_end__)
                    timing_[k_] = [time_start__, time_end__]
                    
                    self._get_cargo_rate(info, cargo_order, k_+'PerTank', time_start__, time_end__) 
                    
                    ## ballast
                    v_ = k_+str(cargo_order)
                    ballast_plan_ = {'deballastingRateM3_Hr':{}, 'ballastingRateM3_Hr':{}}
                    port_ = self.plans.input.discharging.seq['stripToPort'][v_]
#                    print(port_, v_)
                        
                    self._get_ballast_rate(ballast_plan_, port_)
                    
                    start1_ = int(time_start__)
                    end1_ = int(time_end__)
                    
                    info_ = {}
                    for k1_, v1_ in  ballast_plan_['deballastingRateM3_Hr'].items():
                        info_[k1_] = {'tankShortName': self.plans.input.vessel.info['tankId'][k1_],
                                     'rate': v1_,
                                     "timeStart": str(start1_), "timeEnd": str(end1_)}
                    info['simDeballastingRateM3_Hr'].append(info_)
                    
                    info_ = {}
                    for k1_, v1_ in  ballast_plan_['ballastingRateM3_Hr'].items():
                        info_[k1_] = {'tankShortName': self.plans.input.vessel.info['tankId'][k1_],
                                     'rate': v1_,
                                     "timeStart": str(start1_), 
                                     "timeEnd": str(end1_)}
                    info['simBallastingRateM3_Hr'].append(info_)
                    
                    info['totDeballastingRateM3_Hr'].append(ballast_plan_['totDeballastingRateM3_Hr'])
                    info['totBallastingRateM3_Hr'].append(ballast_plan_['totBallastingRateM3_Hr'])
                    
                    
                    time_start__ = time_end__
                    
            
            max_rate_ = self.plans.input.discharging.discharging_rate[cargo_order]
            info["cargoDischargingRateM3_Hr"] = {0: str(max_rate_)}
            
            
            info["toLoadicator"] = True
            info["jumpStep"] = True
            pre_port_ = self.pre_port
            
            self.slop_discharge_plan = []
            self.fresh_oil_discharge_plan = []
                    
            for k_, v_ in self.plans.input.loadable.info['stages'].items():
                
                if v_[:3] in ['Dep'] and v_[-1] == str(cargo_order): 
                    
                    port_ = [a_ for a_, b_ in self.plans.input.loadable.info['stages'].items() if b_ == v_][0]
                    # time_ = self.plans.input.discharging.seq[str(cargo_order)]['gantt'][v_[:-1]]['Time'] + \
                    #         self.plans.input.discharging.seq[str(cargo_order)]['startTime']
                    
                    time_ = int(self.plans.input.discharging.seq[str(cargo_order)]['gantt'][v_[:-1]]['Time'] +
                                    start_time_ + self.delay)  
                    
                    plan_ = {'time': str(int(time_)), 
                             "dischargeQuantityCommingleCargoDetails":[],
                             "dischargePlanStowageDetails":[],
                             "dischargePlanBallastDetails":[],
                             "dischargePlanRoBDetails":[]}
                    
                    
                    self._get_plan(plan_, port_)
                    self.final_plan = deepcopy(plan_)
                    
                    # info_ = {} # get stability info
                    # for a_, b_ in plan_.items():
                    #     if a_ in STAGE_INFO:
                    #         info_[a_] = b_
                    #         # if a_ in ['time']:
                    #         #     info_[a_] = str(int(info_[a_]) + self.delay)
                            
                    # self.stages.append(info_)    
                    # print("info_",info_)
                    
                    
                    # self.final_ballast = plan_
                
                elif v_[:3] in ['Str'] and v_[-1] == str(cargo_order):
                    
                    # time_ = self.plans.input.discharging.seq[str(cargo_order)]['gantt'][v_[:-1]]['Time'] + \
                    #     self.plans.input.discharging.seq[str(cargo_order)]['startTime']
                    time_ = int(self.plans.input.discharging.seq[str(cargo_order)]['gantt'][v_[:-1]]['Time'] +
                                    start_time_ + self.delay)    

                    time1_ = self.plans.input.discharging.seq[str(cargo_order)]['gantt'][v_[:-1]]['Time'] 
                    
                    if v_[:-1] !=  self.plans.input.discharging.seq[str(cargo_order)]['lastStage']:
                        pass
                        # print(time_)
                        # time0_ = time_
                        # # c_ = self.plans.input.discharging.info['discharging_order'][int(v_[-1])-1]
                        # # c1_ = self.plans.input.discharging.info['dsCargoNominationId'][c_]
                        # time_interval_ = self.plans.input.discharging.seq[str(cargo_order)]['timeInterval']
                        # time_ = time_interval_ * round(time1_/time_interval_) + start_time_ + self.delay
                        # print(v_, time0_, '->', time_)

                    plan_ = {'time': str(time_), 
                            "dischargeQuantityCommingleCargoDetails":[],
                            "dischargePlanStowageDetails":[],
                            "dischargePlanBallastDetails":[],
                            "dischargePlanRoBDetails":[]}
                
                    port_ = [a_ for a_, b_ in self.plans.input.loadable.info['stages'].items() if b_ == v_][0]
                    self._get_plan(plan_, port_)
                    
                    info['dischargePlanPortWiseDetails'].append(plan_)
                    info['port'].append(port_)    
                    # info['stageEndTime'][v_[:-1]] = time_
                    
                    info_ = {} # get stability info
                    for a_, b_ in plan_.items():
                        if a_ in STAGE_INFO:
                            info_[a_] = b_
                            # if a_ in ['time']:
                            #     info_[a_] = str(int(info_[a_]) + self.delay)
                            
                    self.stages.append(info_)    
                    # print("info_",info_)
                    pre_port_ = port_
                    
                    ## self.second_last_plan = deepcopy(plan_)
                    if len(self.slop_discharge_plan) == 0:
                        for t_ in self.plans.input.discharging.seq[str(cargo_order)]['Slop Discharge']:
                            plan__ = next(qq_ for qq_ in plan_['dischargePlanStowageDetails'] if qq_['tankShortName'] == t_)
                            self.slop_discharge_plan.append(deepcopy(plan__))
                            print('slop::',cargo_order, plan__)
                        
                    
                    if len(self.fresh_oil_discharge_plan) == 0:
                        for t_ in self.plans.input.discharging.seq[str(cargo_order)]['Fresh Oil Discharge']:
                            plan__ = next(qq_ for qq_ in plan_['dischargePlanStowageDetails'] if qq_['tankShortName'] == t_)
                            self.fresh_oil_discharge_plan.append(deepcopy(plan__))
                            print('fresh::',cargo_order,plan__)
                    
                    
            self.pre_port = pre_port_
            self.last_plan = plan_
#            print('reduce stage:','pre_port_', pre_port_)
        
        elif info['stage'] == 'dryCheck':
            info["simCargoDischargingRatePerTankM3_Hr"] = [{}]
            
            start_ = int(self.plans.input.discharging.seq[cargo]['info']['stages_timing']['Dry Check'][0] + start_time_ + self.delay)
            end_   = int(self.plans.input.discharging.seq[cargo]['info']['stages_timing']['Dry Check'][1] + start_time_ + self.delay)
            info["timeStart"] = str(start_)
            info["timeEnd"] = str(end_)
            
#            print('dryCheck', info["timeStart"], info["timeEnd"])
            
            info['simDeballastingRateM3_Hr'] = []
            info['simBallastingRateM3_Hr'] = []
            
            info['totDeballastingRateM3_Hr'] = []
            info['totBallastingRateM3_Hr'] = []
            
            info["toLoadicator"] = True
            info["jumpStep"] = True
            ## ballast
            ballast_plan_ = {'deballastingRateM3_Hr':{}, 'ballastingRateM3_Hr':{}}
            port_ = len(self.plans.input.discharging.seq['stages'])
            print(port_, info['stage'])
                
            self._get_ballast_rate(ballast_plan_, port_)
            self._get_final_ballast(info, start_, end_, ballast_plan_, port_)
            self._get_final_plan(info, start_, end_, cargo, cargo_order)

            # start1_ = int(start_)
            # end1_ = int(end_)
            
            # info_ = {}
            # for k1_, v1_ in  ballast_plan_['deballastingRateM3_Hr'].items():
            #     info_[k1_] = {'tankShortName': self.plans.input.vessel.info['tankId'][k1_],
            #                  'rate': v1_,
            #                  "timeStart": str(start1_), "timeEnd": str(end1_)}
            # info['simDeballastingRateM3_Hr'].append(info_)
            
            # info_ = {}
            # for k1_, v1_ in  ballast_plan_['ballastingRateM3_Hr'].items():
            #     info_[k1_] = {'tankShortName': self.plans.input.vessel.info['tankId'][k1_],
            #                  'rate': v1_,
            #                  "timeStart": str(start1_), 
            #                  "timeEnd": str(end1_)}
            # info['simBallastingRateM3_Hr'].append(info_)
            
            # info['totDeballastingRateM3_Hr'].append(ballast_plan_['totDeballastingRateM3_Hr'])
            # info['totBallastingRateM3_Hr'].append(ballast_plan_['totBallastingRateM3_Hr'])
            # info['port'] = port_
            
            
            info_ = {} # get stability info
            for a_, b_ in info['dischargePlanPortWiseDetails'][0].items():
                if a_ in STAGE_INFO:
                    info_[a_] = b_
                    # if a_ in ['time']:
                    #     info_[a_] = str(int(info_[a_]) + self.delay)
                    
            self.stages.append(info_)    
            
        elif info['stage'] == 'slopDischarge':
            
            start_ = int(self.plans.input.discharging.seq[cargo]['info']['stages_timing']['Slop Discharge'][0] + start_time_ + self.delay)
            end_   = int(self.plans.input.discharging.seq[cargo]['info']['stages_timing']['Slop Discharge'][1] + start_time_ + self.delay)
            info["timeStart"] = str(start_)
            info["timeEnd"] = str(end_)
#            print('slopDischarge', info["timeStart"], info["timeEnd"])
            info["toLoadicator"] = True
            info["jumpStep"] = True
            # if self.plans.input.discharging.seq[cargo]['driveTank']:
            # local start
            start__ = self.plans.input.discharging.seq[cargo]['info']['stages_timing']['Slop Discharge'][0]
            #cargo_pump_ = self.plans.input.discharging.seq[cargo]['info']['fixedPumpTimes'].index[self.plans.input.discharging.seq[cargo]['info']['fixedPumpTimes'][start__] == 'open'].to_list()[0]
            pump_ = [] 
            for k_, v_ in self.plans.input.discharging.seq[str(cargo_order)]['pump'].items():
                if "COP" in k_:
                    if len(v_) == 2 and (v_[0] <= start__ <= v_[1]):
                        pump_.append(k_)
                        
                    if len(v_) == 4 and (v_[2] <= start__ <= v_[3]):
                        pump_.append(k_)
#            print(pump_)
            
            rate_per_tanks__ = {}
            for t_ in self.plans.input.discharging.seq[str(cargo_order)]['Slop Discharge']:
                
                # info['stripping'].append({'tankShortName':t_, 
                #                       'tankId':self.plans.input.vessel.info['tankName'][t_],
                #                       "timeStart":str(start_),
                #                       "timeEnd":str(end_)})
                rate_ = self.plans.input.discharging.seq[str(cargo_order)]['dischargingRate']['slopDischargePerTank'][t_]
                rate_per_tanks__[self.plans.input.vessel.info['tankName'][t_]] = {'tankShortName': t_,
                                                                                  "rate": str(round(rate_,2)), 
                                                                                  "timeStart": str(start_),
                                                                                  "timeEnd": str(end_)}
#                print('stripping', t_)
                pp_ = self.plans.input.vessel.info['tankCargoPump'][t_]
                if pp_ in pump_:
                    id_ = self.plans.input.vessel.info['cargoPumpId'][pp_]['id']
                    vol_ = self.plans.input.discharging.seq[cargo]['info']['gantt_chart_volume'][start__][t_]
                    rate_ = vol_/(end_-start_)*60 ## m3/hr
                    info["cargo"][id_] = [{"rateM3_Hr": str(round(rate_,2)),
                                          "quantityM3": str(round(vol_,2)),
                                          "timeStart": info["timeStart"],
                                          "timeEnd": info["timeEnd"]}]
                else:
                    print('Missing pump in slop discharge!!')
                    
            info["simCargoDischargingRatePerTankM3_Hr"] = [deepcopy(rate_per_tanks__)]
            
            for k_, v_ in rate_per_tanks__.items():
                rate_per_tanks__[k_]['vol'] = self.plans.input.discharging.seq[str(cargo_order)]['dischargingRate']['slopDischargePerTank']['other']['vol'][k_]
                rate_per_tanks__[k_]['qty'] = self.plans.input.discharging.seq[str(cargo_order)]['dischargingRate']['slopDischargePerTank']['other']['qty'][k_]
                rate_per_tanks__[k_]['ullage'] = self.plans.input.discharging.seq[str(cargo_order)]['dischargingRate']['slopDischargePerTank']['other']['ullage'][k_]
                rate_per_tanks__[k_]['dsCargoNominationId'] = self.plans.input.discharging.seq[str(cargo_order)]['dischargingRate']['slopDischargePerTank']['other']['dsCargoNominationId'][k_]
                
            
            info["cargoDischargingRatePerTankM3_Hr"] = [rate_per_tanks__]

            ## ballast
            info['simDeballastingRateM3_Hr'] = []
            info['simBallastingRateM3_Hr'] = []
            
            info['totDeballastingRateM3_Hr'] = []
            info['totBallastingRateM3_Hr'] = []
            
            ## ballast
            ballast_plan_ = {'deballastingRateM3_Hr':{}, 'ballastingRateM3_Hr':{}}
            port_ = len(self.plans.input.discharging.seq['stages'])
            print(port_, info['stage'])
                
            self._get_ballast_rate(ballast_plan_, port_)
            self._get_final_ballast(info, start_, end_, ballast_plan_, port_)
            self._get_final_plan(info, start_, end_, cargo, cargo_order)
            
            
            info_ = {} # get stability info
            for a_, b_ in info['dischargePlanPortWiseDetails'][0].items():
                if a_ in STAGE_INFO:
                    info_[a_] = b_
                    # if a_ in ['time']:
                    #     info_[a_] = str(int(info_[a_]) + self.delay)
                    
            self.stages.append(info_)    
            # start1_ = int(start_)
            # end1_ = int(end_)
            
            # info_ = {}
            # for k1_, v1_ in  ballast_plan_['deballastingRateM3_Hr'].items():
            #     info_[k1_] = {'tankShortName': self.plans.input.vessel.info['tankId'][k1_],
            #                  'rate': v1_,
            #                  "timeStart": str(start1_), "timeEnd": str(end1_)}
            # info['simDeballastingRateM3_Hr'].append(info_)
            
            # info_ = {}
            # for k1_, v1_ in  ballast_plan_['ballastingRateM3_Hr'].items():
            #     info_[k1_] = {'tankShortName': self.plans.input.vessel.info['tankId'][k1_],
            #                  'rate': v1_,
            #                  "timeStart": str(start1_), 
            #                  "timeEnd": str(end1_)}
            # info['simBallastingRateM3_Hr'].append(info_)
            
            # info['totDeballastingRateM3_Hr'].append(ballast_plan_['totDeballastingRateM3_Hr'])
            # info['totBallastingRateM3_Hr'].append(ballast_plan_['totBallastingRateM3_Hr'])
            # info['port'] = port_

        elif info['stage'] == 'freshOilDischarge':
            
            start_ = int(self.plans.input.discharging.seq[cargo]['info']['stages_timing']['Fresh Oil Discharge'][0] + start_time_ + self.delay)
            end_   = int(self.plans.input.discharging.seq[cargo]['info']['stages_timing']['Fresh Oil Discharge'][1] + start_time_ + self.delay)
            info["timeStart"] = str(start_)
            info["timeEnd"] = str(end_)
#            print('freshOilDischarge', info["timeStart"], info["timeEnd"], '------------------------------------')
            
            start__ = self.plans.input.discharging.seq[cargo]['info']['stages_timing']['Fresh Oil Discharge'][0]
            #cargo_pump_ = self.plans.input.discharging.seq[cargo]['info']['fixedPumpTimes'].index[self.plans.input.discharging.seq[cargo]['info']['fixedPumpTimes'][start__] == 'open'].to_list()[0]
            pump_ = [] 
            for k_, v_ in self.plans.input.discharging.seq[str(cargo_order)]['pump'].items():
                if "COP" in k_:
                    if (v_[-2] <= start__ <= v_[-1]):
                        pump_.append(k_)
#            print("pump_", pump_)
            
            rate_per_tanks__ = {}
            t_ = self.plans.input.discharging.seq[cargo]['info']['freshOilDischarge'][-1]
                
            # info['stripping'].append({'tankShortName':t_, 
            #                       'tankId':self.plans.input.vessel.info['tankName'][t_],
            #                       "timeStart":str(start_),
            #                       "timeEnd":str(end_)})
            
            rate_ = self.plans.input.discharging.seq[str(cargo_order)]['dischargingRate']['freshOilDischargePerTank'][t_]
            rate_per_tanks__[self.plans.input.vessel.info['tankName'][t_]] = {'tankShortName': t_,
                                                                              "rate": str(round(rate_,2)), 
                                                                              "timeStart": str(start_),
                                                                              "timeEnd": str(end_)}
#            print('stripping', t_)
            
            info["toLoadicator"] = True
            info["jumpStep"] = True
            
            pp_ = self.plans.input.vessel.info['tankCargoPump'][t_]
            if pp_ in pump_:
                id_ = self.plans.input.vessel.info['cargoPumpId'][pp_]['id']
                vol_ = self.plans.input.discharging.seq[cargo]['info']['gantt_chart_volume'][start__][t_]
                rate_ = vol_/(end_-start_)*60 ## m3/hr
                info["cargo"][id_] = [{"rateM3_Hr": str(round(rate_,2)),
                                      "quantityM3": str(round(vol_,2)),
                                      "timeStart": info["timeStart"],
                                      "timeEnd": info["timeEnd"]}]
            else:
                print('Missing pump in slop discharge!!')
                    
            info["simCargoDischargingRatePerTankM3_Hr"] = [deepcopy(rate_per_tanks__)]
            
            for k_, v_ in rate_per_tanks__.items():
                rate_per_tanks__[k_]['vol'] = self.plans.input.discharging.seq[str(cargo_order)]['dischargingRate']['freshOilDischargePerTank']['other']['vol'][k_]
                rate_per_tanks__[k_]['qty'] = self.plans.input.discharging.seq[str(cargo_order)]['dischargingRate']['freshOilDischargePerTank']['other']['qty'][k_]
                rate_per_tanks__[k_]['ullage'] = self.plans.input.discharging.seq[str(cargo_order)]['dischargingRate']['freshOilDischargePerTank']['other']['ullage'][k_]
                rate_per_tanks__[k_]['dsCargoNominationId'] = self.plans.input.discharging.seq[str(cargo_order)]['dischargingRate']['freshOilDischargePerTank']['other']['dsCargoNominationId'][k_]
                
            
            info["cargoDischargingRatePerTankM3_Hr"] = [rate_per_tanks__]
            
            
            ## ballast
            info['simDeballastingRateM3_Hr'] = []
            info['simBallastingRateM3_Hr'] = []
            
            info['totDeballastingRateM3_Hr'] = []
            info['totBallastingRateM3_Hr'] = []
            
            ## ballast
            ballast_plan_ = {'deballastingRateM3_Hr':{}, 'ballastingRateM3_Hr':{}}
            port_ = len(self.plans.input.discharging.seq['stages'])
            print(port_, info['stage'])
                
            self._get_ballast_rate(ballast_plan_, port_)
            self._get_final_ballast(info, start_, end_, ballast_plan_, port_)
            self._get_final_plan(info, start_, end_, cargo, cargo_order)
            
            info_ = {} # get stability info
            for a_, b_ in info['dischargePlanPortWiseDetails'][0].items():
                if a_ in STAGE_INFO:
                    info_[a_] = b_
                    # if a_ in ['time']:
                    #     info_[a_] = str(int(info_[a_]) + self.delay)
                    
            self.stages.append(info_)    

        elif info['stage'] == 'finalStripping':
            
            info["simCargoDischargingRatePerTankM3_Hr"] = [{}]

            start_ = int(self.plans.input.discharging.seq[cargo]['info']['stages_timing']['Final Stripping'][0] + start_time_ + self.delay)
            end_   = int(self.plans.input.discharging.seq[cargo]['info']['stages_timing']['Final Stripping'][1] + start_time_ + self.delay)
            info["timeStart"] = str(start_)
            info["timeEnd"] = str(end_)
            
            start__ = self.plans.input.discharging.seq[cargo]['info']['stages_timing']['Final Stripping'][0]
            stp_pump_ = self.plans.input.discharging.seq[cargo]['info']['fixedPumpTimes'].index[self.plans.input.discharging.seq[cargo]['info']['fixedPumpTimes'][start__] == 'open'].to_list()[0]
            id_ = self.plans.input.vessel.info['cargoPumpId']['STP']['id']
            info["STP"][id_] = [{"rateM3_Hr": "",
                                     "quantityM3": "",
                                     "timeStart": info["timeStart"],
                                     "timeEnd": info["timeEnd"]}]
            
#            print('finalStripping', 'STP', info["timeStart"], info["timeEnd"])
            
            
            info["toLoadicator"] = True
            info["jumpStep"] = True
            
            ## ballast
            info['simDeballastingRateM3_Hr'] = []
            info['simBallastingRateM3_Hr'] = []
            
            info['totDeballastingRateM3_Hr'] = []
            info['totBallastingRateM3_Hr'] = []
            
            ## ballast
            ballast_plan_ = {'deballastingRateM3_Hr':{}, 'ballastingRateM3_Hr':{}}
            port_ = len(self.plans.input.discharging.seq['stages'])
            print(port_, info['stage'])
                
            self._get_ballast_rate(ballast_plan_, port_)
            self._get_final_ballast(info, start_, end_, ballast_plan_, port_)
            self._get_final_plan(info, start_, end_, cargo, cargo_order)
            
            info_ = {} # get stability info
            for a_, b_ in info['dischargePlanPortWiseDetails'][0].items():
                if a_ in STAGE_INFO:
                    info_[a_] = b_
                    # if a_ in ['time']:
                    #     info_[a_] = str(int(info_[a_]) + self.delay)
                    
            self.stages.append(info_)    

        else:
            print(info['stage'])
            exit(1)
    
    
    
    def _get_final_plan(self, info, start_, end_, cargo, cargo_order):
        start1_ = int(start_)
        end1_ = int(end_)
        plan1_ = deepcopy(self.final_plan)
        end_time_ = int(plan1_['time'])
        plan1_['time'] = str(end_)
        
        tanks_ = []
        if info['stage'] in ['dryCheck']:
            plan2_ = []
            for pp_ in self.slop_discharge_plan:
                plan2_.append(pp_)
                tanks_.append(pp_['tankShortName'])
                
            for pp_ in self.fresh_oil_discharge_plan:
                plan2_.append(pp_)
                tanks_.append(pp_['tankShortName'])
                
            for pp_ in  plan1_['dischargePlanStowageDetails']:
                if pp_['tankShortName'] not in tanks_:
                    plan2_.append(pp_)
                    tanks_.append(pp_['tankShortName'])
                    
            plan1_['dischargePlanStowageDetails'] = plan2_
        
        elif info['stage'] in ['slopDischarge']:
            plan2_ = []
            
            for pp_ in self.fresh_oil_discharge_plan:
                plan2_.append(pp_)
                tanks_.append(pp_['tankShortName'])
                
            for pp_ in  plan1_['dischargePlanStowageDetails']:
                if pp_['tankShortName'] not in tanks_:
                    plan2_.append(pp_)
                    tanks_.append(pp_['tankShortName'])
                    
            plan1_['dischargePlanStowageDetails'] = plan2_
            
        elif info['stage'] in ['finalStripping', 'freshOilDischarge']:
            pass
                
        ballast_plan_ = {bb_['tankId']:bb_ for bb_ in plan1_['dischargePlanBallastDetails']}
        
        if info['stage'] not in ['finalStripping']:
            # plan3_ = []
            
            for k_, v_ in info['simBallastingRateM3_Hr'][0].items():
                
                vol_ = float(ballast_plan_[k_]['quantityM3']) - float(v_['rate'])*(end_time_-end_)/60
                wt_ = 1.025*vol_
                
                ballast_plan_[k_]['quantityMT'] = str(round(wt_,2))
                ballast_plan_[k_]['quantityM3'] = str(round(vol_,2))
                
                try:
                    corrLevel_ = self.plans.input.vessel.info['ullage'][str(k_)](vol_).tolist()
                except:
                    print(k_, vol_, ': correctLevel not available!!')
                    corrLevel_ = 0.
                
                ballast_plan_[k_]['sounding'] = str(round(corrLevel_,3))
            
                
            for k_, v_ in info['simDeballastingRateM3_Hr'][0].items():
                
                vol_ = float(ballast_plan_[k_]['quantityM3']) + float(v_['rate'])*(end_time_-end_)/60
                wt_ = 1.025*vol_
                
                ballast_plan_[k_]['quantityMT'] = str(round(wt_,2))
                ballast_plan_[k_]['quantityM3'] = str(round(vol_,2))
                
                try:
                    corrLevel_ = self.plans.input.vessel.info['ullage'][str(k_)](vol_).tolist()
                except:
                    print(k_, vol_, ': correctLevel not available!!')
                    corrLevel_ = 0.
                
                ballast_plan_[k_]['sounding'] = str(round(corrLevel_,3))
            
            
            plan1_['dischargePlanBallastDetails'] = [v_ for k_, v_ in ballast_plan_.items()]
            
            
        info['dischargePlanPortWiseDetails'].append(plan1_)
        
        
    def _get_final_ballast(self, info, start_, end_, ballast_plan_, port_):
        start1_ = int(start_)
        end1_ = int(end_)
        
        info_ = {}
        for k1_, v1_ in  ballast_plan_['deballastingRateM3_Hr'].items():
            info_[k1_] = {'tankShortName': self.plans.input.vessel.info['tankId'][k1_],
                         'rate': v1_,
                         "timeStart": str(start1_), "timeEnd": str(end1_)}
        info['simDeballastingRateM3_Hr'].append(info_)
        
        info_ = {}
        for k1_, v1_ in  ballast_plan_['ballastingRateM3_Hr'].items():
            info_[k1_] = {'tankShortName': self.plans.input.vessel.info['tankId'][k1_],
                         'rate': v1_,
                         "timeStart": str(start1_), 
                         "timeEnd": str(end1_)}
        info['simBallastingRateM3_Hr'].append(info_)
        
        info['totDeballastingRateM3_Hr'].append(ballast_plan_['totDeballastingRateM3_Hr'])
        info['totBallastingRateM3_Hr'].append(ballast_plan_['totBallastingRateM3_Hr'])
        info['port'] = port_
            
    def _get_cargo_rate(self, info, cargo_order, stage, time_start__, time_end__):   
        
        # stage = 'IncMaxPerTank' ''InitialRatePerTank''
        # print('_get_cargo_rate', time_start__, time_end__)
        total_rate_ = self.plans.input.discharging.seq[str(cargo_order)]['dischargingRate'][stage]['total']
        info["cargoDischargingRateM3_Hr"] = {0:str(total_rate_)}
        rate_per_tanks_, rate_per_tanks__ = {}, {}    
        for t_ in self.plans.input.discharging.seq[str(cargo_order)]['info']['tanksDischarged']:
            rate_ = str(round(self.plans.input.discharging.seq[str(cargo_order)]['dischargingRate'][stage][t_],2))
            if float(rate_) > 0:
                rate_per_tanks_[self.plans.input.vessel.info['tankName'][t_]] = rate_
                rate_per_tanks__[self.plans.input.vessel.info['tankName'][t_]] = {'tankShortName': t_,
                                                                                  "rate": rate_, 
                                                                                  "timeStart": str(time_start__),
                                                                                  "timeEnd": str(time_end__)}

        # info["cargoDischargingRatePerTankM3_Hr"].append(rate_per_tanks_)
        info["simCargoDischargingRatePerTankM3_Hr"].append(deepcopy(rate_per_tanks__))
        
        for k_, v_ in rate_per_tanks__.items():
                rate_per_tanks__[k_]['vol'] = self.plans.input.discharging.seq[str(cargo_order)]['dischargingRate'][stage]['other']['vol'][k_]
                rate_per_tanks__[k_]['qty'] = self.plans.input.discharging.seq[str(cargo_order)]['dischargingRate'][stage]['other']['qty'][k_]
                rate_per_tanks__[k_]['ullage'] = self.plans.input.discharging.seq[str(cargo_order)]['dischargingRate'][stage]['other']['ullage'][k_]
                rate_per_tanks__[k_]['dsCargoNominationId'] = self.plans.input.discharging.seq[str(cargo_order)]['dischargingRate'][stage]['other']['dsCargoNominationId'][k_]
                
        info["cargoDischargingRatePerTankM3_Hr"].append(rate_per_tanks__)
        
        local_time_start_ = time_start__ - self.plans.input.discharging.seq[str(cargo_order)]['startTime'] - self.delay - \
                           self.start_time
        pump_ = [k_ for k_, v_ in self.plans.input.discharging.seq[str(cargo_order)]['pump'].items() \
                 if "COP" in k_ and int(v_[0]) <= local_time_start_ < int(v_[1])]# and v_[0] <= time_end__ <= v_[1] ]
            
        # print('pump used', pump_, local_time_start_)
        if len(pump_) > 0:
            rate_ = total_rate_/len(pump_)
            vol_ = rate_*(int(info["timeEnd"]) - int(info["timeStart"]))/60
            for pp_ in pump_:
                id_ = self.plans.input.vessel.info['cargoPumpId'][pp_]['id']
                
                if id_ not in  info["cargo"]:
                    info["cargo"][id_] = [{"rateM3_Hr": str(round(rate_,2)),
                                          "quantityM3": str(round(vol_,2)),
                                          "timeStart": str(time_start__),
                                          "timeEnd": str(time_end__)}]    
#                    print(id_, time_start__,time_end__ )
                else:
                    info["cargo"][id_].append({"rateM3_Hr": str(round(rate_,2)),
                                          "quantityM3": str(round(vol_,2)),
                                          "timeStart": str(time_start__),
                                          "timeEnd": str(time_end__)})
#                    print(id_, time_start__,time_end__ )
        
        
            
        # print(info["cargo"])
            
    def _get_ballast_rate(self, ballast_plan_, port_):
        
        for a_, b_ in self.plans.ballast_info['vol_and_rate'][port_].items():
            if a_ not in ['Time', 'ballastRate', 'deballastRate', 'rate', 'pump', 'BP1', 'BP2']:
                if round(b_,2) < 0:
                    ballast_plan_['deballastingRateM3_Hr'][self.plans.input.vessel.info['tankName'][a_]] = str(round(-b_,2))
                elif round(b_ ,2) > 0:
                    ballast_plan_['ballastingRateM3_Hr'][self.plans.input.vessel.info['tankName'][a_]] = str(round(b_,2))
                
        ballast_plan_['totBallastingRateM3_Hr'] = str(round(self.plans.ballast_info['vol_and_rate'][port_]['ballastRate'],2))     
        ballast_plan_['totDeballastingRateM3_Hr'] = str(round(-self.plans.ballast_info['vol_and_rate'][port_]['deballastRate'],2))    
        
#        for a_, b_ in ballast_plan_['ballastingRateM3_Hr'].items():
#            print('ballasting', self.plans.input.vessel.info['tankId'][a_], b_)
            
#        for a_, b_ in ballast_plan_['deballastingRateM3_Hr'].items():
#            print('deballastingRate', self.plans.input.vessel.info['tankId'][a_], b_)
                    
        
        
        
    #     # stage_ = self.plans.input.loadable['stages'][port]
    #     # print(port, prev_port, time)
    #     pre_ballast_ = self.plans.input.discharging.info['ballast'][0] if prev_port == 0 else self.plans.ballast_weight[0][str(prev_port)]
    #     cur_ballast_ = self.plans.ballast_weight[0][str(port)]
        
    #     deballast_amt_ = 0.
    #     ballast_amt_ = 0.
        
    #     for k_, v_ in cur_ballast_.items():
    #         cur_vol_ = v_[0]['vol']
    #         pre_vol_ = pre_ballast_.get(k_, [{}])[0].get('quantityM3',0.) if prev_port == 0 else  pre_ballast_.get(k_, [{}])[0].get('vol',0.)
            
    #         k1_ = self.plans.input.vessel.info['tankName'][k_]
    #         # print(k_, cur_vol_, pre_vol_)
    #         if round(cur_vol_,3) < round(pre_vol_,3):
    #             plan['deballastingRateM3_Hr'][k1_] = str(round((-cur_vol_ + pre_vol_)/time*60,2))
    #             deballast_amt_ += (-cur_vol_ + pre_vol_)
                
    #         elif round(cur_vol_,3) > round(pre_vol_,3):
    #             plan['ballastingRateM3_Hr'][k1_] = str(round((cur_vol_ - pre_vol_)/time*60,2))
    #             ballast_amt_ += (cur_vol_ - pre_vol_)
        
    #     for k_, v_ in pre_ballast_.items():         
    #        k1_ = self.plans.input.vessel.info['tankName'][k_]
           
    #        if k1_ not in plan['deballastingRateM3_Hr']  and k1_ not in plan['ballastingRateM3_Hr']:
    #            cur_vol_ = cur_ballast_.get(k_, [{}])[0].get('vol',0.)
    #            pre_vol_ = v_[0]['quantityM3'] if prev_port == 0 else  v_[0]['vol']
               
    #            # print(k_, cur_vol_, pre_vol_)
    #            if round(cur_vol_,3) < round(pre_vol_,3):
    #                 plan['deballastingRateM3_Hr'][k1_] = str(round((-cur_vol_ + pre_vol_)/time*60,2))
    #                 deballast_amt_ += (-cur_vol_ + pre_vol_)
    #            elif round(cur_vol_,3) > round(pre_vol_,3):
    #                 plan['ballastingRateM3_Hr'][k1_] = str(round((cur_vol_ - pre_vol_)/time*60,2))
    #                 ballast_amt_ += (cur_vol_ - pre_vol_)
               
    #     # print(deballast_amt_, ballast_amt_)
    #     plan['totBallastingRateM3_Hr'] = str(round(ballast_amt_/time*60,12))
    #     plan['totDeballastingRateM3_Hr'] = str(round(deballast_amt_/time*60,12))
        
        
        
               
            
          
        
    
    def _get_plan(self, plan, port=0):
        
        cargo_ = self.plans.plans['ship_status'][0][str(port)]['cargo'] # single plan
        if port not in [0]:
            ballast_ = self.plans.ballast_weight[0][str(port)] # single plan
        else:
            ballast_ = self.plans.initial_ballast_weight
        
        other_weight_ = self.plans.other_weight[str(port)]
        
        plan["ballastVol"] = 0.
        plan["cargoVol"] = {}
        
        cargo_tanks_added_, ballast_tanks_added_, other_tanks_added_ = [], [], []
        
        for k_, v_ in cargo_.items():
            #print(k_, v_)
            info_ = {}
            
            if  type(v_[0]['parcel']) == str: # single cargo
                info_['tankShortName'] = k_
                info_['tankName'] =  self.plans.input.vessel.info['cargoTanks'][k_]['name']
                info_['tankId'] = int(self.plans.input.vessel.info['tankName'][k_])
                info_['quantityMT'] = str(round(abs(v_[0]['wt']),2))
                info_['quantityM3'] = str(round(abs(v_[0]['wt']/v_[0]['SG']),2))
                info_['api'] = str(round(abs(v_[0]['api']),2))
                info_['temperature'] = str(round(abs(v_[0]['temperature']),2))
                info_['ullage'] = str(round(abs(v_[0]['corrUllage']),3))
                info_['cargoNominationId'] = int(v_[0]['parcel'][1:])
                
                
                info_['dsCargoNominationId'] = int(self.plans.input.discharging.info['cargoNominationId'][v_[0]['parcel']][1:])
                info_['cargoId'] = self.plans.input.discharging.info['cargoId'][v_[0]['parcel']]
                info_['colorCode'] = self.plans.input.discharging.info['colorCode'][v_[0]['parcel']]
                info_['cargoAbbreviation'] = self.plans.input.discharging.info['abbreviation'][v_[0]['parcel']]
                info_['abbreviation'] = self.plans.input.discharging.info['abbreviation'][v_[0]['parcel']]
                
                    
                if v_[0]['parcel'] not in plan["cargoVol"]:
                    plan["cargoVol"][v_[0]['parcel']] = v_[0]['wt']/v_[0]['SG']
                else:
                    plan["cargoVol"][v_[0]['parcel']] += v_[0]['wt']/v_[0]['SG']
                
                plan["dischargePlanStowageDetails"].append(info_)
            
            else: # commingle
                
                info_['tankShortName'] = k_
                info_['tankName'] =  self.plans.input.vessel.info['cargoTanks'][k_]['name']
                info_['tankId'] = int(self.plans.input.vessel.info['tankName'][k_])
                info_['quantityMT'] = str(round(abs(v_[0]['wt']),1))
                info_['quantityM3'] = str(round(abs(v_[0]['vol']),2))
                info_['api'] = str(round(abs(v_[0]['api']),2))
                info_['temperature'] = str(round(abs(v_[0]['temperature']),2))
                info_['ullage'] = str(round(abs(v_[0]['corrUllage']),3))
                info_['cargoNomination1Id'] = int(v_[0]['parcel'][0][1:])
                info_['cargoNomination2Id'] = int(v_[0]['parcel'][1][1:])
                
                info_['cargo1Id'] = self.plans.input.loading.info['cargoId']['P'+str(info_['cargoNomination1Id'])]
                info_['cargo2Id'] = self.plans.input.loading.info['cargoId']['P'+str(info_['cargoNomination2Id'])]
                
                info_['colorCode'] = self.plans.input.loading.info['commingle'].get('colorCode', None)
                info_['cargoAbbreviation'] = self.plans.input.loading.info['commingle'].get('abbreviation', None)
                info_['abbreviation'] = self.plans.input.loading.info['commingle'].get('abbreviation', None)
                
                
                info_['quantity1MT'] = str(round(abs(v_[0]['wt1']),1))
                info_['quantity2MT'] = str(round(abs(v_[0]['wt2']),1))
                info_['ullage1'] = str(round(abs(v_[0]['corrUllage1']),3))
                info_['ullage2'] = str(round(abs(v_[0]['corrUllage2']),3))
                info_['quantity1M3'] = str(round(abs(v_[0]['vol1']),2))
                info_['quantity2M3'] = str(round(abs(v_[0]['vol2']),2))
                
                plan["loadableQuantityCommingleCargoDetails"].append(info_)
                
            if k_ not in cargo_tanks_added_:
                cargo_tanks_added_.append(k_)
                
                
                
            
        ##
        empty_ = set(self.plans.input.vessel.info['cargoTankNames']) - set(cargo_tanks_added_)
#        print(empty_)
        for k_ in empty_:
            info_ = {}
            info_['tankShortName'] = k_
            info_['tankName'] =  self.plans.input.vessel.info['cargoTanks'][k_]['name']
            info_['tankId'] = int(self.plans.input.vessel.info['tankName'][k_])
            info_['quantityMT'] = "0.0"
            info_['quantityM3'] = "0.0"
            info_['api'] = None 
            info_['temperature'] = None
            info_['ullage'] = str(round(self.plans.input.vessel.info['ullageEmpty'][str(info_['tankId'])],3))
            
            parcel_ = self.plans.input.discharging.info['tank_cargo'].get(k_, None)
            
            if parcel_:
                info_['cargoNominationId'] = int(parcel_[1:])
                info_['dsCargoNominationId'] = int(self.plans.input.discharging.info['cargoNominationId'][parcel_][1:])
                    
                
                info_['cargoId'] = self.plans.input.discharging.info['cargoId'][parcel_]
                info_['colorCode'] = self.plans.input.discharging.info['colorCode'][parcel_]
                info_['cargoAbbreviation'] = self.plans.input.discharging.info['abbreviation'][parcel_]
                info_['abbreviation'] = self.plans.input.discharging.info['abbreviation'][parcel_]
            else:
                info_['cargoNominationId'] = None
                info_['dsCargoNominationId'] = None
                
                info_['cargoId'] = None
                info_['colorCode'] = None
                info_['cargoAbbreviation'] = None
                info_['abbreviation'] = None
                
                
            
            plan["dischargePlanStowageDetails"].append(info_)
            
                
        for k_, v_ in plan["cargoVol"].items():
            plan["cargoVol"][k_] = str(round(v_,2))
            
        for k_, v_ in ballast_.items():
            # print(k_, v_)
            info_ = {}
            info_['tankShortName'] = k_
            info_['tankName'] =  self.plans.input.vessel.info['ballastTanks'][k_]['name']
            info_['tankId'] = int(self.plans.input.vessel.info['tankName'][k_])
            info_['quantityMT'] = str(round(abs(v_[0]['wt']),2))
            info_['quantityM3'] = str(round(abs(v_[0]['vol']),2))
            info_['sounding'] = str(round(v_[0]['corrLevel'],3))
            
            info_['sg'] = str(v_[0]['SG'])
            info_['colorCode'] = self.plans.input.discharging.ballast_color.get(k_,None)
            
            if k_ not in ballast_tanks_added_:
                ballast_tanks_added_.append(k_)
                
            plan["ballastVol"] += v_[0]['vol']
            
            plan["dischargePlanBallastDetails"].append(info_)
            
            
        ##
        empty_ = set(self.plans.input.vessel.info['ballastTankNames']) - set(ballast_tanks_added_) - set(self.plans.input.vessel.info['banBallast'])
#        print(empty_)
        for k_ in empty_:
            info_ = {}
            info_['tankShortName'] = k_
            info_['tankName'] =  self.plans.input.vessel.info['ballastTanks'][k_]['name']
            info_['tankId'] = int(self.plans.input.vessel.info['tankName'][k_])
            info_['quantityMT'] = "0.00"
            info_['quantityM3'] = "0.00"
            info_['sounding'] = str(round(self.plans.input.vessel.info['ullageEmpty'][str(info_['tankId'])],3))
            
            info_['sg'] = '1.025'
            info_['colorCode'] = self.plans.input.discharging.ballast_color.get(k_,None)
            plan["dischargePlanBallastDetails"].append(info_)
            
            
        plan["ballastVol"] = str(round(plan["ballastVol"],2))    
        
        
        for k_, v_ in other_weight_.items():
            info_ = {}
            info_['tankShortName'] = k_
            info_['tankName'] =  self.plans.input.vessel.info['tankFullName'][k_]
            info_['tankId'] = int(self.plans.input.vessel.info['tankName'][k_])
            info_['quantityMT'] = str(round(abs(v_[0]['wt']),2))
            info_['quantityM3'] = str(round(abs(v_[0]['vol']),2))
            
            info_['density'] = str(self.plans.input.config['rob_density'][k_])
            info_['colorCode'] = self.plans.input.discharging.rob_color[k_]
            
            if k_ not in other_tanks_added_:
                other_tanks_added_.append(k_)
            
            plan["dischargePlanRoBDetails"].append(info_)
            
            
        empty_ = set(self.plans.input.vessel.info['otherTankNames']) - set(other_tanks_added_)
#        print(empty_)
        for k_ in empty_:
            info_ = {}
            info_['tankShortName'] = k_
            info_['tankName'] =  self.plans.input.vessel.info['tankFullName'][k_]
            info_['tankId'] = int(self.plans.input.vessel.info['tankName'][k_])
            info_['quantityMT'] = str("0.00")
            info_['quantityM3'] = str("0.00")
            
            info_['density'] = None
            info_['colorCode'] = self.plans.input.discharging.rob_color[k_]
            plan["dischargePlanRoBDetails"].append(info_)
            
            
        
        
        ##
        plan["foreDraft"] = self.stability[str(port)]['forwardDraft']
        plan["meanDraft"] = self.stability[str(port)]['meanDraft']
        plan["afterDraft"] = self.stability[str(port)]['afterDraft']
        plan["trim"] = self.stability[str(port)]['trim']
        plan["heel"] = self.stability[str(port)]['heel']
        plan["airDraft"] = self.stability[str(port)]['airDraft']
        plan["bendinMoment"] = self.stability[str(port)]['bendinMoment']
        plan["shearForce"] = self.stability[str(port)]['shearForce']
        plan["gom"] = self.stability[str(port)].get('gom', None)
        plan["manifoldHeight"] = self.stability[str(port)]['manifoldHeight']
        plan["freeboard"] = self.stability[str(port)]['freeboard']
        plan["UKC"] = self.stability[str(port)].get('UKC', None)
        plan["displacement"] = self.stability[str(port)].get('displacement', None)
        
        
        
        
        
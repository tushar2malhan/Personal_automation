# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 14:57:49 2020

@author: I2R
"""

from vlcc_vessel import Vessel
from vlcc_load import Loadable
from vlcc_port import Port

import numpy as np

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False


DEC_PLACE = 3
_SOLVER_ = 'AMPL' # AMPL or ORTOOLS

class Process_input(object):
    def __init__(self, data):

        # gather info
        self.data = data
        self.vessel_json = {'vessel': data['vessel'],
                            'onBoard': data['loadable']['onBoardQuantity'],
                            'onHand': data['loadable']['onHandQuantity'],
                            }
        #
        self.port_json = {'portDetails': data['loadable']['portDetails'],
                         'portRotation': data['loadable']['loadableStudyPortRotation']}
        #
        self.loadable_json = {'loadableQuantity': data['loadable']['loadableQuantity'],
                              'cargoNomination': data['loadable']['cargoNomination'],
                              'cargoOperation': data['loadable']['cargoNominationOperationDetails'],
                              'commingleCargo': data['loadable'].get('commingleCargos',[]),
                              'loadingPlan': data['loadable'].get('loadingPlan',{}), # 
                              'ballastPlan': data['loadable'].get('ballastPlan',{}), # 
                              'planDetails': data.get('loadablePlanPortWiseDetails',[]), # for full and manual modes
                              'voyageHistory': data['loadable'].get('voyageCargoHistories',[]) }
        
        self.rules_json = data['loadable'].get("loadableStudyRuleList", [])
        
        self.user = data['loadable'].get('user', None)
        self.role = data['loadable'].get('role', None)                              
        self.loadable_id = data['loadable']['id']
        self.vessel_id   = data['loadable']['vesselId']
        self.voyage_id   = data['loadable']['voyageId']
        self.process_id  = data.get('processId',None)
        self.loadline_id = data['loadable']['loadlineId']
        self.draft_mark = data['loadable']['draftMark']
        
        # data['config']['loadable_config'] = True
        
        self._set_config(data['config'])
        
        self.module = data['module']
        
        print('module:', self.module)
        
        
        self.loadOnTop = data['loadable'].get('loadOnTopForSlopTank', False)
        # self.cargoweight = data['loadable'].get("loadableQuantity", {})
        
        self.cargoweight = data['loadable']['loadableQuantity'].get("totalQuantity", '1000000')
        self.draftsag    = data['loadable']['loadableQuantity'].get("estSagging", '0')
        
        self.firstDisCargo = str(data['loadable'].get("cargoToBeDischargeFirstId", ''))
                
        self.solver = self.config.get('solver', 'AMPL')#_SOLVER_ ## config
                
        self.preloaded_cargo = []
        
        self.error = {}
        self.cargo_rotation = [] #['P10520', 'P10522']
        self.maxTankUsed = 100
        self.gen_distinct_plan = True
        # self.constraint = {}
        
        self.air_temperature = data['loadable'].get('maxAirTemp',None)
        if self.air_temperature in [None, ""]:
            self.air_temperature = 0.
        else:
            self.air_temperature = round(float(self.air_temperature)*1.8+32,2)
            
        if self.loadable_json['planDetails']:
            if not data.get('ballastEdited', False):
                self.mode = 'Manual'
            else:
                self.mode = 'FullManual'
        else:
            self.mode = 'Auto'
            
        
        self.case_number = data.get('caseNumber', None)
        self.deballast_percent =  self.config.get('loadableConfig',{}).get('deballastAmt', self.config['deballast_percent'])
        self.ballast_percent = self.config['ballast_percent'] #0.4 ## config
        
        self.commingle_temperature = None
        
        self.has_loadicator = self.vessel_json['vessel']['vessel'].get('hasLoadicator',False)
        
        ## for auto only
        self.feedbackLoop      = data['loadable'].get('feedbackLoop', False)
        self.feedbackLoopCount = data['loadable'].get('feedbackLoopCount', 0)
        self.feedback_sf_bm_frac = data['loadable'].get('feedbackLoopBMSF', 1)
        
        self.accurate = False # False lower complexity

        self.tide_info = None
    
    def _set_config(self, config):
        
        RULES = {"151":"trimLimit", "152": "loadingTrim", "153": "listLimit", 
                 "154": "SFLimit", "155": "BMLimit",  "156": "SSFLimit", "157": "SBMLimit", 
                 "301":"cargoTankUpperLimit", "302":"cargoTankLowerLimit", 
                 "303":"ballastTankUpperLimit", "304":"ballastTankLowerLimit", 
                 "305":"slopTankUpperLimit", "306":"slopTankLowerLimit", 
                 "308":"valveSegregation",
                 "312": "sameWeightTanks", "317":"commingleTanks",
                 "319": "lastLoadingPortBallast", 
                 "321": "deballastAmt",
                 "324": "initBallastTanksAmt", 
                 "401": "airDraft",
                 "501":"condensateCargoBanTank", "502":"hrvpCargoBanTank",
                 "701": "condensateCargoInterval",
                 "902":"numPlans", "903": "timeLimit", "904":"objective",
                 "963": "changeROB",
                 "984": "banCargoTanks"}
        
        # self.config = config
        
        config_ = {}
        for l__, l_ in enumerate(self.rules_json):
            
            if l_['header'] == 'Vessel Stability Rules':
                ## sea or port limit for SF and BM not considered
                ## Ensure draft not over the load line always true
                # continue
                for k__, k_ in enumerate(l_['rules']):
                    
                    v_ =  RULES.get(k_['ruleTemplateId'], None)
                    # print(k_['ruleTemplateId'], v_)
                    
                    if v_ in ["SSFLimit", "SBMLimit"]:
                        config_[v_] = float(k_['inputs'][0]['value'])
                        
            elif l_['header'] == 'Algorithm Rules':
                    
                    for k__, k_ in enumerate(l_['rules']):
                        # print(k_['ruleTemplateId'])
                        v_ =  RULES.get(k_['ruleTemplateId'], None)
                        # print(k_['ruleTemplateId'], v_)
                        if v_ not in [None, ""]:
                            config_[v_] = k_['inputs'][0]['value']
                            
                            if v_ == "objective":
                                config_[v_] = "1" ##if config_[v_] == "46" else "3"
                # print(config_)
        
        
        if config.get("loadable_config", False):
        
        
            for l__, l_ in enumerate(self.rules_json):
                
                if l_['header'] == 'Vessel Stability Rules':
                    ## sea or port limit for SF and BM not considered
                    ## Ensure draft not over the load line always true
                    # continue
                    for k__, k_ in enumerate(l_['rules']):
                        
                        v_ =  RULES.get(k_['ruleTemplateId'], None)
                        # print(k_['ruleTemplateId'], v_)
                        
                        if v_ in ["trimLimit", "listLimit"]:
                            config_[v_] = [float(k_['inputs'][0]['value']), float(k_['inputs'][1]['value'])]
                        elif v_ in ["loadingTrim", "SFLimit", "BMLimit", "SSFLimit", "SBMLimit"]:
                            config_[v_] = float(k_['inputs'][0]['value'])
                    
                    # print(config_)
                            
                        
                elif l_['header'] == 'Vessel Facility Rules':
                    # continue
                
                    ## 309 "Different types of cargoes in slop tanks" always true
                    ## 310 "Slop tanks must be used" always true
                    ## 311 "Loading Pattern Symmetric" always true
                    ## 312 Symmeteric vol different 
                        # 1W, 2W, 4W and 5W same weight
                        # 3W and Slop tanks 5% different
                    ## 313 "Each row(1W+1C, 2W+2C etc.) must at least have 1 tank for large nomination cargo" always true
                    ## 314 ""2 consecutive rows of tank with the same large cargo nomination not allowed. This is applicable to multiple cargo parcels""
                    ## 315 "Do not load cargo in a row if no cargo have nomination larger than 5 wing tanks"
                    ## 316 "Ensure propeller immersion draft should be more than 50 % of the draft value" Need min draft
                    ## 317 "tank can be filled with commingled cargo" 2C, 3C, 4C and slop tanks
                    ## 319 "Ballast Tank Usage Restriction to at last loading port"
                       # LFPT, APT, AWBP, AWBS for KAZUSA
                       # APT, FPT, WB6P, WB6S for AP
                    ## 322 "Zero ballast for arrival of first discharge port" zero if possible else non-zero
                    ## 323 "Decreasing ballast except for last loading port" always true
                    ## 324 "Ballast tanks are assumed to be filled at" Need modification
                    ## 325 "Only filled ballast tanks in the departure port can be used to adjust the ballast at the next arrival port"
                    ## 326 "Change in ballast can only be increasing or decreasing for ballast movement during cargo rotation"
                    ## 327 "1 tank can only take in 1 cargo except for tank with commingled cargo"
                    ## 328 "Commingle can be done with maximum two cargoes"
                    
                    for k__, k_ in enumerate(l_['rules']):
                        #print(k_['ruleTemplateId'])
                        v_ =  RULES.get(k_['ruleTemplateId'], None)
                        # print(k_['ruleTemplateId'], v_)
                        if v_ in ["cargoTankUpperLimit", "cargoTankLowerLimit", 
                                  "ballastTankUpperLimit", "ballastTankLowerLimit", 
                                  "slopTankUpperLimit", "slopTankUpperLimit", "changeROB"]:
                            
                            config_[v_] = float(k_['inputs'][0]['value'])
                            
                        if v_ in ["deballastAmt" ]:
                            
                            config_[v_] = float(k_['inputs'][0]['value'])/100
                            
                            
                            
                        if v_ in ["sameWeightTanks"]:
                            if k_['inputs'][0]['value'] in ['0']:
                                config_[v_] = k_['inputs'][1]['value'].split(',')
                                
                        if v_ in ["commingleTanks"]:
                            poss_tanks_ = {str(l_['id']): l_['value'] for l_ in k_['inputs'][0]['ruleDropDownMaster']}
                            config_[v_] = [poss_tanks_[l_] for l_ in k_['inputs'][0]['value'].split(',')]
                            
                        if v_ in ["lastLoadingPortBallast"]:
                            poss_tanks_ = {str(l_['id']): l_['value'] for l_ in k_['inputs'][0]['ruleDropDownMaster']}
                            config_[v_] = [poss_tanks_[l_] for l_ in k_['inputs'][0]['value'].split(',')]

                        if v_ in ["initBallastTanksAmt"]:
                            poss_tanks_ = {str(l_['id']): l_['value'] for l_ in k_['inputs'][0]['ruleDropDownMaster']}
                            config_[v_] = {'tanks': [poss_tanks_[l_] for l_ in k_['inputs'][0]['value'].split(',')]}
                            config_[v_]['amt'] = int(k_['inputs'][1]['value'])/100
                            
                        if v_ in ["banCargoTanks"]:
                            poss_tanks_ = {str(l_['id']): l_['value'] for l_ in k_['inputs'][0]['ruleDropDownMaster']}
                            config_[v_] = [poss_tanks_[l_] for l_ in k_['inputs'][0]['value'].split(',')]
                            
                elif l_['header'] == 'Port/Berth/Terminal Clearance Rules':
                    ## 401
                    # continue
                    for k__, k_ in enumerate(l_['rules']):
                        # print(k_['ruleTemplateId'])
                        v_ =  RULES.get(k_['ruleTemplateId'], None)
                        config_[v_] = k_['inputs'][0]['value']
                    
                elif l_['header'] == 'Vessel Tank Compatibility Rules':
                    
                    ## "501" "Condensate Cargo cannot be placed in " Modify tank short name
                    ## "502" "High Reid Vapour Cargo cannot be placed in " Modify tank short name
                    # continue
                    for k__, k_ in enumerate(l_['rules']):
                        # print(k_['ruleTemplateId'])
                        v_ =  RULES.get(k_['ruleTemplateId'], None)
                        # print(k_['ruleTemplateId'], v_)
                        if k_['inputs'][0]["value"] not in [None]:
                            tanks_ = k_['inputs'][0]["value"].split(',')
                            tanksId_ = {str(r_['id']): r_['value']   for r_ in k_['inputs'][0]["ruleDropDownMaster"]}
                            config_[v_] = [tanksId_[t_] for t_ in tanks_]
                        
                    # print(config_)
                     
                elif l_['header'] == 'Prior Cargo List Rules':
                    
                    
                    ## 710 "Condensate cargo can only be put in a tank for" Missing History
                    
                    for k__, k_ in enumerate(l_['rules']):
                        # print(k_['ruleTemplateId'])
                        v_ =  RULES.get(k_['ruleTemplateId'], None)
                        # print(k_['ruleTemplateId'], v_)
                        config_[v_] = k_['inputs'][0]['value']
                        
                    # print(config_)
                        
                elif l_['header'] == 'Definition of Constant/System Rules':
                    
                    ## 901 "Extra loading time" Need modification
                    for k__, k_ in enumerate(l_['rules']):
                        # print(k_['ruleTemplateId'])
                        pass
                    
                    
                    
                elif l_['header'] == 'Algorithm Rules':
                    
                    for k__, k_ in enumerate(l_['rules']):
                        # print(k_['ruleTemplateId'])
                        v_ =  RULES.get(k_['ruleTemplateId'], None)
                        # print(k_['ruleTemplateId'], v_)
                        if v_ not in [None, ""]:
                            config_[v_] = k_['inputs'][0]['value']
                            
                            if v_ == "objective":
                                config_[v_] = "1" if config_[v_] == "46" else "3"
                                # "45": min tank -> model4i.mod/
                                # "46": max load -> model1i.mod
                
        # config_['cargoTankUpperLimit'] = 97
        # config_['slopTankUpperLimit'] = 96
        # config_['objective'] = "3"
        
        
        config1_ = {}        
        config1_['loadableConfig'] = config_
        self.config = {**config, **config1_}          
        
        
                    
        # print(config_)    
            
            
            
            # if l_['header'] == 'Vessel Stability Rules':
            #     for k__, k_ in enumerate(l_['rules']):
            #         if k_['id'] == '11167':
            #             config_['loadingTrim'] = float(k_['inputs'][0]['value'])
                        
            
        
        
        
    def prepare_dat_file(self, ballast_weight=1000):
        
        if not self.error:
        # prepare dat file for AMPL
            self.port = Port(self)
            
        if not self.error:
            self.loadable = Loadable(self) # basic info
            if self.mode in ['Auto']:
                self.loadable._create_operations(self) # operation and commingle
            elif self.mode in ['Manual', 'FullManual']:
                self.loadable._create_man_operations(self) # operation and commingle
                
            self.vessel = Vessel(self)
            self.vessel._get_onhand(self) # ROB
            self.vessel._get_onboard(self) # Arrival condition
            self.get_stability_param()
            self.infeasible_analysis()
            self.get_voyage_history()
        
        
    def get_stability_param(self, ballast_weight_ = 92000, sf_bm_frac = 0.95, trim_upper = 0, trim_lower = 0, trim_load = 1, reduce_disp_limit = 0):
        
        # ARR_DEP_ = {0:'A', 1:'D'}
#        self.trim_range = [-0.1,0.1]

        ## config
        # trim_upper # trim_lower
        
        if self.vessel_id in [2]:
            ballast_weight_ = 96000
        self.displacement_lower, self.displacement_upper = {}, {}
        self.base_draft = {}
        self.sf_base_value, self.sf_draft_corr, self.sf_trim_corr = {}, {}, {}
        self.bm_base_value, self.bm_draft_corr, self.bm_trim_corr = {}, {}, {}
        
        
        sf_bm_frac_ = sf_bm_frac
        if self.config['loadableConfig']:
            sf_bm_frac_ = min(self.config['loadableConfig']['SSFLimit'], self.config['loadableConfig']['SBMLimit'])/100
            print('SF BM Svalue limits', sf_bm_frac_)
            
        self.sf_bm_frac = min(sf_bm_frac_, self.feedback_sf_bm_frac)
        
        
        self.limits = {'draft':{}}
        
        ## config 
        # min_draft_limit_  = 10.425
#        min_draft_limit_  = self.config['min_aft_draft_limit']
        loadline_ = self.vessel.info['draftCondition']['draftExtreme']
        self.limits['draft']['loadline'] = loadline_
        # self.limits['draft'] = {**self.limits['draft'], **{k_[:-1]:v_  for k_, v_ in self.port.info['maxDraft'].items()}}
        self.limits['operationId'] = {k_:str(v_)[-1] for k_, v_ in self.port.info['portRotationId'].items()}
        self.limits['seawaterDensity'] = {k_[:-1]:v_  for k_, v_ in self.port.info['seawaterDensity'].items()} 
        self.limits['tide'] = {k_[:-1]:v_  for k_, v_ in self.port.info['tide'].items()}  
        self.limits['id'] = self.loadable_id
        self.limits['vesselId'] = self.vessel_id
        self.limits['voyageId'] = self.voyage_id
        # self.limits['airDraft'] = {k_[:-1]:v_  for k_, v_ in self.port.info['maxAirDraft'].items()} 
        self.limits['airDraft'] = {}
        for p_ in range(1, len(self.port.info['portOrderId'])+1):
            # print(p_)
            cur_ = self.port.info['portOrderId'][str(p_)]
            self.limits['airDraft'][cur_[:-1]] = self.port.info['maxAirDraft'][cur_]
            self.limits['draft'][cur_[:-1]] = self.port.info['maxDraft'][cur_]
            # if p_ < len(self.port.info['portOrderId']):
            #     next_ =  self.port.info['portOrderId'][str(p_+1)]
            #     self.limits['airDraft'][cur_[:-1]] = min(self.port.info['maxAirDraft'][cur_], self.port.info['maxAirDraft'][next_])
            #     self.limits['draft'][cur_[:-1]] = min(self.port.info['maxDraft'][cur_], self.port.info['maxDraft'][next_])
            # else:
            #     self.limits['airDraft'][cur_[:-1]] = self.port.info['maxAirDraft'][cur_]
            #     self.limits['draft'][cur_[:-1]] = self.port.info['maxDraft'][cur_]

        self.limits['sfbm'] = self.sf_bm_frac
        self.limits['feedback'] = {'feedbackLoop': self.feedbackLoop,'feedbackLoopCount':self.feedbackLoopCount}
        self.limits['portOrderId'] = self.port.info['portOrderId']
        
        if self.config['loadableConfig'].get('trimLimit', []):
            self.limits['trimLimit'] = self.config['loadableConfig']['trimLimit']
        else:
            self.limits['trimLimit'] = [-0.1, 0.1]
            
        if self.config['loadableConfig'].get('listLimit', []):
            self.limits['listLimit'] = self.config['loadableConfig']['listLimit']
        else:
            self.limits['listLimit'] = [-0.1, 0.1]
            
        if self.config['loadableConfig'].get('SFLimit', []):
            self.limits['SFLimit'] = self.config['loadableConfig']['SFLimit']
        else:
            self.limits['SFLimit'] = 100
        
        if self.config['loadableConfig'].get('BMLimit', []):
            self.limits['BMLimit'] = self.config['loadableConfig']['BMLimit']
        else:
            self.limits['BMLimit'] = 100
        
        
        
        # for loading limits
        last_loading_ = self.port.info['portOrderId'][str(self.port.info['numPort']-1)]
        first_discharge_ = self.port.info['portOrderId'][str(self.port.info['numPort'])]
        self.limits['draft']['maxDraft'] = min(self.port.info['maxDraft'][last_loading_], self.port.info['maxDraft'][first_discharge_])
        self.limits['maxAirDraft'] = min(self.port.info['maxAirDraft'][last_loading_], self.port.info['maxAirDraft'][first_discharge_])
        
        
        
        # print(self.limits)
        # set deballast_percent 
        # if self.loadable.info['toLoadPort1'].get(1, None):
        #     first_cargo_ = self.loadable.info['toLoadPort1'][1]
        # elif self.loadable.info['toLoadPort1'].get(3, None):
        #     first_cargo_ = self.loadable.info['toLoadPort1'][3]
 
        # if first_cargo_ >= 60000:
        #     self.deballast_percent = max(1.,self.deballast_percent)
        #     print('Change deballast_percent:', self.deballast_percent)
        
        
#        lpp_ = self.vessel.info['LPP']
        lightweight_ = self.vessel.info['lightweight']['weight']
        max_deadweight_ = self.vessel.info['draftCondition']['deadweight']
        
        cont_weight_ = self.vessel.info['deadweightConst']['weight'] + self.vessel.info['onboard']['totalWeight']
        
        self._set_trim(trim_upper=trim_upper, trim_lower=trim_lower, trim_load_upper=trim_load, trim_load_lower=trim_load)
        
        # ballast_ = sum([v_ for k_, v_ in self.vessel.info['initBallast']['wt'].items()])
        ballast_, pre_ballast_ = ballast_weight_, ballast_weight_
        
        for p_ in range(0, self.loadable.info['lastVirtualPort']+1):  # exact to virtual
        
            port__ = self.loadable.info['virtualArrDepPort'][str(p_)] # 1D, 2D
            port_, arr_dep_ = int(port__[:-1]), port__[-1] # convert virtual port to exact port
            port_code_ = self.port.info['portOrder'][str(port_)]
            
            order_ = port__[:-1]
            cur_, next_ = self.port.info['portOrder'][order_], self.port.info['portOrder'].get(str(int(order_)+1), None)
            if next_ in [None]:
                next_ = cur_
            
            draft_limit_ = min(self.port.info['portRotation'][cur_]['maxDraft'], self.port.info['portRotation'][next_]['maxDraft'])
            displacement_limit_ = np.interp(draft_limit_, self.vessel.info['hydrostatic']['draft'], self.vessel.info['hydrostatic']['displacement'])

            misc_weight_ = 0.0
            for k1_, v1_ in self.vessel.info['onhand'].items():
                misc_weight_ += v1_.get(str(port_)+arr_dep_,{}).get('wt',0.)
#                
#            # get estimate cargo weight
            cargo_weight_  = self.loadable.info['toLoadPort'][p_] * 0.98
            cargo_to_load_ = self.loadable.info['toLoadPort'][p_]  - self.loadable.info['toLoadPort'][p_-1] 
            
            
            ## find deballast_percent
            deballast_percent_ = self.deballast_percent
            ballast1_ = max(0.,ballast_- deballast_percent_*cargo_to_load_)
            est_deadweight_ = min(cont_weight_ + misc_weight_ + cargo_weight_ + ballast1_, max_deadweight_)
            est_displacement_ = lightweight_ + est_deadweight_
            if displacement_limit_ > est_displacement_:
                ballast_ = ballast1_
            else:
                print('Change deballast to 1:', p_)
                ballast_ = max(0.,ballast_- cargo_to_load_)
            
            est_deadweight_ = min(cont_weight_ + misc_weight_ + cargo_weight_ + ballast_, max_deadweight_)
            est_displacement_ = lightweight_ + est_deadweight_
            seawater_density_ = self.port.info['portRotation'][port_code_]['seawaterDensity']
                        
            ## lower bound displacement
            min_draft_limit_ = self.config['min_aft_draft_limit'] if round(cargo_weight_) > 0 else self.config['min_ballast_aft_draft_limit']
            lower_draft_limit_ = min_draft_limit_ #max(self.ports.draft_airdraft[p_], min_draft_limit_)
            lower_displacement_limit_ = np.interp(lower_draft_limit_, self.vessel.info['hydrostatic']['draft'], self.vessel.info['hydrostatic']['displacement'])
            # correct displacement to port seawater density
            lower_displacement_limit_  = lower_displacement_limit_*seawater_density_/1.025
            
            est_draft__ =  np.interp(est_displacement_,  self.vessel.info['hydrostatic']['displacement'], self.vessel.info['hydrostatic']['draft'])
            # trim_ = self.trim_lower.get(str(p_),-0.0001)
            if est_draft__ > lower_draft_limit_:
                est_displacement_ = max(lower_displacement_limit_, est_displacement_)   
            # elif round(self.trim_upper.get(str(p_), 0),2) != 0 and round(self.trim_lower.get(str(p_), 0),2) != 0:
            #     print("Intermediate port but aft draft not met:", p_)
            elif cargo_weight_ > 0:
                print('port:',p_,'Remove ballast too fast')
                ballast__ = lower_displacement_limit_ -  (cont_weight_ + misc_weight_ + cargo_weight_)
                print(ballast_, ballast__)
            else: 
                
                low_trim_ = min(2.9, 2*(min_draft_limit_ - est_draft__)) #2.5
                ## est_draft__ + 0.1 = mid_draft_
                est_draft__ = min_draft_limit_ - low_trim_/2 - 0.1 # max trim = 3m 
                self.trim_lower[str(p_)], self.trim_upper[str(p_)] = low_trim_, 2.95
                lower_displacement_limit_ = np.interp(est_draft__, self.vessel.info['hydrostatic']['draft'], self.vessel.info['hydrostatic']['displacement'])
                print('port', p_, round(est_draft__,2), round(self.trim_lower[str(p_)],2), round(self.trim_upper[str(p_)],2))
                
                lower_draft_limit_ = est_draft__ #max(self.ports.draft_airdraft[p_], min_draft_limit_)
                lower_displacement_limit_ = np.interp(lower_draft_limit_, self.vessel.info['hydrostatic']['draft'], self.vessel.info['hydrostatic']['displacement'])
                print("lower:", round(lower_displacement_limit_), "est:", round(est_displacement_), "ballast:", ballast_)
                print("da:", est_draft__+self.trim_lower[str(p_)]/2+0.1)
                lower_displacement_limit_ = min(est_displacement_, lower_displacement_limit_)  - reduce_disp_limit
                if reduce_disp_limit > 0:
                    print("reduce_disp_limit:", reduce_disp_limit)
                    draft_ = np.interp(lower_displacement_limit_, self.vessel.info['hydrostatic']['displacement'], self.vessel.info['hydrostatic']['draft'])
                    # print('new da:', draft_+self.trim_lower[str(p_)]/2)
                    self.trim_lower[str(p_)] = min(self.trim_lower[str(p_)]+0.4, 2.9)
                    print('new da:', draft_+self.trim_lower[str(p_)]/2+0.1, self.trim_lower[str(p_)])

                # correct displacement to port seawater density
                lower_displacement_limit_  = lower_displacement_limit_*seawater_density_/1.025

            
            ## upper bound displacement
            
            est_sag_ = float(self.loadable_json['loadableQuantity'].get('estSagging', 0.0))
            port_draft_ = self.port.info['portRotation'][port_code_]['maxDraft'] - 0.25*est_sag_/100
            loadline__ = loadline_ - 0.25*est_sag_/100
            
            # print('port_draft_', port_draft_)
            upper_draft_limit_ = min(loadline__, port_draft_) - 0.001

            # check uplimit not exceeed for min load
            est_displacement_wo_ballast_ =  self.loadable.info['toLoadMinPort'][p_]  + cont_weight_ + misc_weight_ + lightweight_
            est_draft_wo_ballast_ =  np.interp(est_displacement_wo_ballast_, self.vessel.info['hydrostatic']['displacement'], self.vessel.info['hydrostatic']['draft'])
            
            if est_draft_wo_ballast_ > upper_draft_limit_:
                message_ = 'Draft error at '+ port_code_ + '!!'
                #print('Draft error')
                if 'Draft Error' not in self.error.keys():
                    self.error['Draft Error'] = [message_]
                elif message_ not in self.error['Draft Error']:
                    self.error['Draft Error'].append(message_)
                
            upper_displacement_limit_ = np.interp(upper_draft_limit_, self.vessel.info['hydrostatic']['draft'], self.vessel.info['hydrostatic']['displacement'])
            # correct displacement to port seawater density
            upper_displacement_limit_  = upper_displacement_limit_*seawater_density_/1.025
            
            est_displacement_ = min(est_displacement_, upper_displacement_limit_)
#            
            # print(p_, lower_displacement_limit_,est_displacement_,upper_displacement_limit_)
            self.displacement_lower[str(p_)] = lower_displacement_limit_
            self.displacement_upper[str(p_)] = upper_displacement_limit_
            
            est_draft_ = np.interp(est_displacement_, self.vessel.info['hydrostatic']['displacement'], self.vessel.info['hydrostatic']['draft'])
            
            pre_ballast_ = ballast_
            # base draft for BM and SF
            trim_ = 0.5*(self.trim_lower.get(str(p_),0.0) + self.trim_upper.get(str(p_),0.0))
            # trim_ = self.ave_trim.get(str(p_), 0.0)
            
            if self.vessel_id in [1]:
                base_draft__ = int(np.floor(est_draft_+trim_/2))
            elif self.vessel_id in [2]:
                base_draft__ = int(np.floor(est_draft_))
                
            base_draft_ = base_draft__ if p_  == 0 else max(base_draft__, self.base_draft[str(p_-1)])
            self.base_draft[str(p_)] = base_draft_
            # print(p_,trim_,base_draft_)
            
            
            # self.base_draft ={'1': 11, '2': 13, '3': 13, '4': 17, '5': 19, '6': 19, '7': 9}
            
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

        self.limits['upperTrimLimit'] = {}
        for l_ in range(1, len(self.loadable.info['cargoPort'])+1):
            p1_, p2_ = str(l_)+'A', str(l_)+'D'
            pp_ = self.loadable.info['arrDepVirtualPort'][p1_]
            self.limits['upperTrimLimit'][str(2*l_-2)] = max(0.1, round(self.trim_upper.get(pp_,0.0)))
            pp_ = self.loadable.info['arrDepVirtualPort'][p2_]
            self.limits['upperTrimLimit'][str(2*l_-1)] = max(0.1, round(self.trim_upper.get(pp_,0.0)))
            
            
        print('upperTrimLimit',self.limits['upperTrimLimit'])     
            
            
    def _set_trim(self, trim_upper = 0, trim_lower = 0, trim_load_upper = 1, trim_load_lower = 1):
        
        if trim_upper == trim_lower:
            trim_upper_ = trim_upper + 1e-4
            trim_lower_ = trim_lower - 1e-4
        else:
            trim_upper_ = trim_upper 
            trim_lower_ = trim_lower
        
        self.trim_lower = {str(p_): trim_lower_ for p_ in range(1,self.loadable.info['lastVirtualPort'])}
        self.trim_upper = {str(p_): trim_upper_ for p_ in range(1,self.loadable.info['lastVirtualPort'])}
        
        
        if self.config['loadableConfig'].get('loadingTrim', None):
            trim_load_upper_, trim_load_lower_ = self.config['loadableConfig']['loadingTrim'], self.config['loadableConfig']['loadingTrim']
        else:
            trim_load_upper_, trim_load_lower_ = trim_load_upper, trim_load_lower 
        
        for p_ in self.loadable.info.get('rotationVirtual',[]):
            for p__ in p_[:-1]:
                self.trim_upper[str(p__)] = trim_load_upper_ + 1e-4
                self.trim_lower[str(p__)] = max(0.0001, trim_load_lower_ - 1e-4)
                
    def get_voyage_history(self):
        
        hist_ = self.loadable_json['voyageHistory']
        self.condensate_cargo_tank = self.vessel.info['slopTank'] + ['5C']
        
        if hist_:
            id_ = [h_['voyageId'] for h_ in hist_]
            id_ = sorted((e_,i_) for i_, e_ in enumerate(id_))
            # last two voyage
            hist_ = [h_ for h__, h_ in enumerate(hist_) if h__ in [id_[-1][1]]]
            # print(hist_)
            
            ## cannot be in two consecutive voyage
            for h__, h_ in enumerate(hist_):
                condensate_cargo_ = [c_['id'] for c__, c_ in enumerate(h_['cargoNominations']) if c_['isCondensateCargo']]
                for c__, c_ in  enumerate(condensate_cargo_):
                    for p__, p_ in enumerate(h_['planStowageDetails']):
                        if p_['cargoNominationId'] == c_:
                            tank_ = self.vessel.info['tankId'][p_['tankId']]
                            if tank_ not in self.condensate_cargo_tank:
                                self.condensate_cargo_tank.append(tank_)
                        
                # print(self.condensate_cargo_tank)       
            # print(self.condensate_cargo_tank)
        if self.condensate_cargo_tank:
            for  c__, c_ in  enumerate(self.loadable.info['condensateCargo']):
                self.vessel.info['banCargo'][c_] += self.condensate_cargo_tank
                if len(self.vessel.info['banCargo'][c_]) == len(self.vessel.info['cargoTanks']):
                    self.error['Condensate Cargo Error'] = ['Cargo ' + self.loadable.info['parcel'][c_]['abbreviation'] + ' cannot be loaded!!']
               
                
    def infeasible_analysis(self):
        
        # deadweight
        # dw_ = self.vessel.info['draftCondition']['deadweight']
        # wt_onboard_ = self.vessel.info['onboard']['totalWeight']
        # min_load_ = sum([v_ for k_,v_ in self.loadable.info['toLoadMin'].items()])
        # tot_capacity_ = sum([v_['capacityCubm'] for k_,v_ in self.vessel.info['cargoTanks'].items()])
        # ave_density_  = np.mean([v_[''] for k_,v_ in self.loadable.info['parcel'].items()])
        # self.error.append('Infeasible')
        
         
        
        tank_cargo_ = {}
        for k_, v_ in self.loadable.info['manualOperation'].items():
            density_ = self.loadable.info['parcel'][k_]['maxtempSG']
            cargo_ =  self.loadable.info['parcel'][k_]['abbreviation']
            for k1_, v1_ in v_.items():
                for v2_ in v1_:
                    tank_ = self.vessel.info['tankId'][v2_['tankId']]
                    capacity_ = self.vessel.info['cargoTanks'][tank_]['capacityCubm']
                    filling_ = v2_['qty']/density_/capacity_
                    
                    if tank_ not in tank_cargo_:
                        tank_cargo_[tank_] = [(k_, v2_['qty'])]
                    elif (k_, v2_['qty']) not in tank_cargo_[tank_]:
                        tank_cargo_[tank_].append((k_, v2_['qty']))
                        
                        
                    # print(k_, v2_, filling_)
                    # filling_ = .99
                    if filling_ > .9801:
                        print('filling_', filling_)
                        if 'Vol Error' not in self.error:
                            self.error['Vol Error'] = [cargo_ + ' at ' + tank_ + ' fails 98% max volume check!!']
                        else:
                            self.error['Vol Error'].append(cargo_ + ' at ' + tank_ + ' fails 98% max volume check!!')
                    
        for k_, v_ in   tank_cargo_.items():
            if len(v_) > 1:
                print("Commingle cargo in tank k!!")
                wt1_ = self.loadable.info['commingleCargo']['wt1']
                wt2_ = self.loadable.info['commingleCargo']['wt2']
                capacity_ = self.vessel.info['cargoTanks'][k_]['capacityCubm']
                wt__ = [wt1_,wt2_]
                            
                api__ = [self.loadable.info['commingleCargo']['api1'], self.loadable.info['commingleCargo']['api2']]
                temp__ = [self.loadable.info['commingleCargo']['t1'], self.loadable.info['commingleCargo']['t2']]
                    
                api_, temp_ = self._get_commingleAPI(api__, wt__, temp__)
                density_ = self.loadable._cal_density(round(api_,2), round(temp_,1))
                vol_ = (wt1_ + wt2_)/density_ 
                filling_ = round(vol_/capacity_,3)
                
                if filling_ > .9801:
                    print('filling_', filling_)
                    if 'Vol Error' not in self.error:
                        self.error['Vol Error'] = ['Commingle at ' + k_ + ' fails 98% max volume check!!']
                    else:
                        self.error['Vol Error'].append('Commingle at ' + k_ + ' fails 98% max volume check!!')
                    
                            
                
                
    def _get_commingleAPI(self, api, weight, temp):
        weight_api_ , weight_temp_ = 0., 0.
        
        sg60_ = [141.5/(a_+131.5) for a_ in api]
        t13_ = [(535.1911/(a_+131.5)-0.0046189)*0.042 for a_ in api]
        vol_bbls_60_ = [w_/t_ for (w_,t_) in zip(weight,t13_)]
        
        weight_sg60_ = sum([v_*s_ for (v_,s_) in zip(vol_bbls_60_,sg60_)])/sum(vol_bbls_60_)
        weight_api_ = 141.5/weight_sg60_ - 131.5
        
        weight_temp_ = sum([v_*s_ for (v_,s_) in zip(vol_bbls_60_,temp)])/sum(vol_bbls_60_)
        
        return weight_api_, weight_temp_
                    
        
        
    def write_dat_file(self, file = 'input.dat', IIS = True, lcg_port = None, weight = None, incDec_ballast = None):
        
        if not self.error and self.solver in ['AMPL']: #and self.mode not in ['FullManual']:
            
            slopP = [t_ for t_ in self.vessel.info['slopTank'] if t_[-1] == 'P'][0]
            slopS = [t_ for t_ in self.vessel.info['slopTank'] if t_[-1] == 'S'][0]
        
            with open(file, "w") as text_file:
                
                print('# set of all cargo tanks',file=text_file)
                cargo_tanks_ = []
                str1 = 'set T:= '
                for i_,j_ in self.vessel.info['cargoTanks'].items():
                    str1 += i_ + ' '
                    cargo_tanks_.append(i_)
                print(str1+';', file=text_file)
                
                print('# cargo tanks with non-pw tcg details',file=text_file)#  
                str1 = 'set T1 := '
                for i_, j_ in self.vessel.info['cargoTanks'].items():
                    if i_ not in self.vessel.info['tankTCG']['tcg_pw']:
                        str1 += i_ + ' '
                print(str1+';', file=text_file)
                
                if self.accurate: 
	                print('# cargo tanks with non-pw lcg details',file=text_file)#  
	                str1 = 'set T2 := '
	                for i_, j_ in self.vessel.info['cargoTanks'].items():
	                    if i_ not in self.vessel.info['tankLCG']['lcg_pw']:
	                        str1 += i_ + ' '
	                print(str1+';', file=text_file)
                    
                str1 = 'set slopP := '
                str1 += slopP
                print(str1+';', file=text_file) 
                
                str1 = 'set slopS := '
                str1 += slopS
                print(str1+';', file=text_file) 
 
                print('# set of tanks compatible with cargo c',file=text_file)
                for i_,j_ in self.loadable.info['parcel'].items():
                    str1 = 'set Tc[' + str(i_) + '] := '
                    for j_ in cargo_tanks_:
                        if j_ not in self.vessel.info['banCargo'][i_]+self.config.get('loadableConfig',{}).get('banCargoTanks',[]):
                            str1 += j_ + ' '
                    print(str1+';', file=text_file)
                
                print('# set of loaded tanks (partial loading condition)',file=text_file)
                str1 = 'set T_loaded:= '
                for k_ in self.preloaded_cargo:
                    for k1_ in self.loadable.info['preloadOperation'][k_]['0']:
                        str1 += k1_['tank'] + ' '
                print(str1+';', file=text_file)
                
                print('# set of all cargoes',file=text_file)
                str1 = 'set C:= '
                for i_,j_ in self.loadable.info['parcel'].items():
                    str1 += i_ + ' '
                print(str1+';', file=text_file)
                
                print('# set of all loaded cargoes (partial loading condition)',file=text_file)
                str1 = 'set C_loaded:= '
                for k_ in self.preloaded_cargo:
                    str1 += k_ + ' '
                print(str1+';', file=text_file)
                
                print('# 1 if cargo c has been loaded in tank t (partial loading condition)',file=text_file)
                str1 = 'param I_loaded := '
                print(str1, file=text_file)
                for k_ in self.preloaded_cargo:
                    str1 = '[' + k_ + ', *] := '
                    for k1_ in self.loadable.info['preloadOperation'][k_]['0']:
                        str1 += k1_['tank'] + ' ' + '1 '
                    print(str1, file=text_file)
                print(';', file=text_file)
                
                #            
                str1 = 'param W_loaded   := ' 
                print(str1, file=text_file) 
                for k_ in self.preloaded_cargo:
                    pass
                    # for k1_, v1_ in v_.items():
                    #     for k2_, v2_ in v1_.items():
                    #         if v2_ < 0.0:
                    #             str1 = k_ + ' ' + self.tanks.cargo_tanks[k1_]['tankName'] + ' ' + str(k2_) + ' ' + str(v2_)
                    #             print(str1, file=text_file)
                print(';', file=text_file)
    
                #
                print('# weight of cargo c remained in tank t at initial state (before ship entering the first port)',file=text_file)#  
                str1 = 'param W0  := ' 
                print(str1, file=text_file) 
                for k_ in self.preloaded_cargo:
                    str1 = '[' + k_ + ', *] := '
                    for k1_ in self.loadable.info['preloadOperation'][k_]['0']:
                        str1 += k1_['tank'] + ' ' +  "{:.3f}".format(k1_['qty']) + ' ' 
                    print(str1, file=text_file)
                    
                print(';', file=text_file)
                
                if lcg_port and weight:
                    print('# QW')
                    str1 = 'param QW := '
                    print(str1, file=text_file)
                    for k_ in self.loadable.info['parcel']:
                        str1 = '[' + k_ + ', *] := '
                        for k1_, v1_ in weight.items():
                            if v1_[0]['parcel'] == k_:
                                str1 += k1_ + ' ' + str(v1_[0]['wt']) + ' '
                            elif len(v1_[0]['parcel']) == 2:
                                if v1_[0]['parcel'][0] == k_:
                                    str1 += k1_ + ' ' + str(v1_[0]['wt1']) + ' '
                                elif v1_[0]['parcel'][1] == k_:
                                    str1 += k1_ + ' ' + str(v1_[0]['wt2']) + ' ' 
                                
                            else:
                                str1 += k1_ + ' ' + str(0.0) + ' '
                        print(str1, file=text_file)
                    print(';', file=text_file)
                    
                    print('# QWT')
                    for i_,j_ in self.loadable.info['parcel'].items():
                        str1 = 'set QWT[' + str(i_) + '] := '
                        for j_ in cargo_tanks_:
                            str1 += j_ + ' '
                        print(str1+';', file=text_file)
   
                
    #            print('# cargo priority',file=text_file)
    #            str1 = 'set P1cargos := '
    #            for i_  in self.cargos.p1_cargos:
    #                #str1 += str(j_['priority']) + ' '
    #                str1 += i_ + ' '
    #            print(str1+';', file=text_file)
    #            str1 = 'set P2cargos := '
    #            for i_  in self.cargos.p2_cargos:
    #                #str1 += str(j_['priority']) + ' '
    #                str1 += i_ + ' '
    #            print(str1+';', file=text_file)
                
    #            str1 = 'param intendedLoad := '
    #            for i_,j_  in self.ports.max_cargos_in_port.items():
    #                #str1 += str(j_['priority']) + ' '
    #                str1 += i_ + ' ' + str(round(max(j_),3)) + ' '
    #            print(str1+';', file=text_file)
                
    #            print('# set of tanks compatible with cargo c (consider tank coating, cargo history, tank heating)',file=text_file)
    #            for i_ in self.cargos.info:
    #                str1 = 'set Tc[' + str(i_) + '] := '
    #                for j_ in self.compatible_tanks[i_]:
    #                    str1 += j_ + ' '
    #                print(str1+';', file=text_file)
    #            
    #            print('# set of tanks compatible with cargo c (consider tank coating, cargo history, tank heating)',file=text_file)
    #            for i_,j_ in self.tanks.cargo_tanks.items():
    #                str1 = 'set Ct[' + j_['tankName'] + '] := '
    #                for j_ in self.compatible_cargos[j_['tankName']]:
    #                    str1 +=  str(j_) + ' '
    #                    
    #                print(str1+';', file=text_file)
    #                
    #            print('# set of adjacent tanks of tank t',file=text_file)
    #            for i_ in self.tanks.neighbor_tanks:
    #                str1 = 'set Tadj[' + i_ + '] := '
    #                for j_ in self.tanks.neighbor_tanks[i_]:
    #                    str1 += j_ + ' '
    #                print(str1+';', file=text_file)
    #                
    #            print('# set of cargoes in conflict with cargo c (consider USCG list)',file=text_file)#            
    #            for i_ in self.cargos.info:
    #                str1 = 'set Cbarc['+ str(i_) + '] := ' 
    #                for j_ in self.incompatible_cargos[i_]:
    #                    str1 +=  str(j_) + ' '
    #                print(str1+';', file=text_file)
                
                
    #            print('# maximum number of adjacent tanks of tank t',file=text_file)#   
    #            str1 = 'param M := '
    #            for i_ in self.tanks.num_neighbor_tanks:
    #                str1 += i_ + ' ' + str(self.tanks.num_neighbor_tanks[i_]) + ' '
    #            print(str1+';', file=text_file)
                
                print('# total number of ports in the booking list',file=text_file)#   
                str1 = 'param NP := ' + str(self.loadable.info['lastVirtualPort']) # to virtual ports 
                print(str1+';', file=text_file)
                
                print('# the last loading port',file=text_file)#  
                str1 = 'param LP := ' + str(self.loadable.info['lastVirtualPort']-1) # to virtual ports
                print(str1+';', file=text_file)
                
                print('# initial port',file=text_file)#  
                str1 = 'set P0 :=  0' 
                print(str1+';', file=text_file)
                
                if self.port.info['lastDraft'] <= 19.8:
                     print('# zero ballast port',file=text_file)#  
                     str1 = 'set zeroBallastPort := ' + str(self.loadable.info['lastVirtualPort']-1) # to virtual ports
                     print(str1+';', file=text_file)
    
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
    #           
                str1 = 'param aveCargoDensity  := ' 
                str1 += "{:.4f}".format(np.mean(density_))  + ' '
                print(str1+';', file=text_file)
                
                print('# weight (in metric tone) of cargo to be moved at port p',file=text_file)#  
                str1 = 'param Wcp  := ' 
                print(str1, file=text_file) 
                for i_, j_ in self.loadable.info['operation'].items():
                    str1 = '[' + str(i_) + ', *] := '
                    for k_,v_ in j_.items():
                        if int(k_) > 0:
                            str1 += str(k_) + ' ' + "{:.1f}".format(int(v_*10)/10) + ' '
                    print(str1, file=text_file)
                print(';', file=text_file)
                
                print('# loading ports',file=text_file)#  
                str1 = 'set loadPort  := ' 
                for i_, j_ in self.loadable.info['toLoadPort1'].items():
                    str1 += str(i_) + ' '
                print(str1+';', file=text_file)
                
                str1 = 'param loadingPortAmt  := ' 
                for i_, j_ in self.loadable.info['toLoadPort1'].items():
                    str1 += str(i_)  + ' ' +  "{:.3f}".format(int(j_*10)/10)  + ' '
                print(str1+';', file=text_file)
                
                
                print('# intended cargo to load',file=text_file)#  
                str1 = 'param toLoad  := ' 
                for i_, j_ in self.loadable.info['toLoad'].items():
                    str1 += i_ + ' ' +  "{:.3f}".format(int(j_*10)/10)  + ' '
                print(str1+';', file=text_file)
                
                print('# intended cargo to load',file=text_file)#  
                str1 = 'set cargoPriority := ' 
                
                if self.mode in ['Auto']:
                    for i_ in range(self.loadable.info['maxPriority'],1,-1):
                        # print(i_)
                        for l1_ in self.loadable.info['priority'][i_]:
                            # print(l1_)
                            for j_ in range(i_-1,0,-1):
                                # print(j_)
                                for l2_ in self.loadable.info['priority'][j_]:
                                    # print(l2_) # higher priority
                                    str1 += '(' + l2_ + ',' + l1_ + ')' + ' '
                                    
                    
                    
                print(str1+';', file=text_file)
                
                    
                print('# min cargo to must be loaded',file=text_file)#  
                str1 = 'param minCargoLoad  := ' 
                for i_, j_ in self.loadable.info['toLoadMin'].items():
                    str1 += i_ + ' ' +  "{:.3f}".format(int(j_*10)/10)  + ' '
                print(str1+';', file=text_file)
                
                if self.loadable.info['numParcel'] == 1:
                    print('# slop tanks diff cargos',file=text_file)#  
                    str1 = 'param diffSlop := 10' 
                    print(str1+';', file=text_file)
                    # default is 1 in AMPL
                
                print('# Commingle cargos',file=text_file)#  
                str1 = 'set Cm_1 := ' 
                if self.loadable.info['commingleCargo']:
                    str1 += self.loadable.info['commingleCargo']['parcel1'] + ' '
                print(str1+';', file=text_file)
                
                str1 = 'set Cm_2 := ' 
                if self.loadable.info['commingleCargo']:
                    str1 += self.loadable.info['commingleCargo']['parcel2'] + ' '
                print(str1+';', file=text_file)
                            
                print('# Possible commingled tanks',file=text_file)#
                str1 = 'set Tm := '
                if self.loadable.info['commingleCargo']:
                    if self.config['loadableConfig'].get('commingleTanks', []):
                        str1 += ''.join(e_+' ' for e_ in self.config['loadableConfig']['commingleTanks'])
                    elif self.loadable.info['commingleCargo']['slopOnly']:
                        str1 +=  slopS + ' ' + slopP
                    else:
                        str1 += '2C 3C 4C' + ' ' + slopS + ' ' + slopP
                        
                print(str1+';', file=text_file)
                
                print('# Density commingled cargo',file=text_file)#
                str1 = 'param density_Cm := '
                if self.loadable.info['commingleCargo']:
                    str1 += self.loadable.info['commingleCargo']['parcel1'] + ' ' + "{:.4f}".format(self.loadable.info['commingleCargo']['SG1'])+ ' '
                    str1 += self.loadable.info['commingleCargo']['parcel2'] + ' ' + "{:.4f}".format(self.loadable.info['commingleCargo']['SG2'])+ ' '
                    
                print(str1+';', file=text_file)
                
                
                if self.loadable.info['commingleCargo'].get('mode','0') == '2':
                    print('# Manual commingled cargo',file=text_file)
                    str1 = 'param Qm_1 := ' + "{:.3f}".format(self.loadable.info['commingleCargo']['wt1'])
                    print(str1+';', file=text_file)
                    str1 = 'param Qm_2 := ' + "{:.3f}".format(self.loadable.info['commingleCargo']['wt2'])
                    print(str1+';', file=text_file)
                    str1 = 'param Mm := 0'
                    print(str1+';', file=text_file)
                        
                    
                
                print('# cargo tank capacity (in m3)',file=text_file)#  
                str1 = 'param capacityCargoTank := ' 
                for i_, j_ in self.vessel.info['cargoTanks'].items():
                    o_ = self.vessel.info['onboard'].get(i_,{}).get('vol',0.)
                    if o_ > 0:
                        print('onboard:', i_,j_['capacityCubm'],o_, 'in input.dat')
                    str1 += i_ + ' ' +  "{:.3f}".format(j_['capacityCubm']-o_/0.98)  + ' '
                print(str1+';', file=text_file)
                
                print('# onboard cargo tank (in mt)',file=text_file)#  
                str1 = 'param onboard := ' 
                for i_, j_ in self.vessel.info['onboard'].items():
                    if i_ not in ['totalWeight']:
                        str1 += i_ + ' ' +  "{:.3f}".format(j_['wt'])  + ' '
                print(str1+';', file=text_file)
                
                
                
    #
    #            print('# cargo tank density (in t/m3)',file=text_file)#  
    #            str1 = 'param dt := ' 
    #            for i_, j_ in self.tanks.cargo_tanks.items():
    #                str1 += j_['tankName'] + ' ' +  str(j_['cargoTankDensity']) + ' '
    #            print(str1+';', file=text_file)
    
                if self.config['loadableConfig'].get('slopTankUpperLimit', None):
                    print('#upper loading bound for each tank',file=text_file)#  
                    str1 = 'param upperBound := ' 
                    for i_, j_ in self.vessel.info['cargoTanks'].items():
                        if i_ in self.vessel.info['slopTank']: #['SLS', 'SLP']:
                            str1 += i_ + ' ' +  "{:.2f}".format(self.config['loadableConfig']['slopTankUpperLimit']/100)  + ' '
                        else:
                            str1 += i_ + ' ' +  "{:.2f}".format(self.config['loadableConfig']['cargoTankUpperLimit']/100) + ' '
                    print(str1+';', file=text_file)
                        
                    print('#upper loading bound for each ballast tank',file=text_file)#  
                    str1 = 'param upperBoundB1 := ' 
                    for i_, j_ in self.vessel.info['ballastTanks'].items():
                        if i_ not in self.vessel.info['banBallast']:
                            str1 += i_ + ' ' +  "{:.2f}".format(self.config['loadableConfig']['ballastTankUpperLimit']/100) + ' '
                    print(str1+';', file=text_file)
                    
                    
                    # print('#equal weight cargo tank',file=text_file)#  
                    # str1 = 'set  equalWeightTank := ' 
                    # for i_ in self.config['loadableConfig']['sameWeightTanks']:
                    #     str1 += '('+ i_+'P' + ',' + i_+'S'+ ') '
                    # print(str1+';', file=text_file)
                    
                        
                        
                
                print('#lower loading bound for each tank',file=text_file)#  
                str1 = 'param lowerBound := ' 
                for i_, j_ in self.vessel.info['cargoTanks'].items():
                    str1 += i_ + ' ' +  str(self.vessel.info['sounding3mVol'][i_]) + ' '
                print(str1+';', file=text_file)
                
                print('# locked tank',file=text_file)#   
                locked_tank_ = []
                str1 = 'set T_locked := ' 
                for k_, v_ in self.loadable.info['manualOperation'].items():
                    for k1_, v1_ in v_.items():
                        for v2_ in v1_:
                            if 'tankId' in v2_.keys():
                                tank_ = self.vessel.info['tankId'][int(v2_['tankId'])]
                            else:
                                tank_ = v2_['tank']
                            if tank_ not in locked_tank_:
                                str1 += tank_ + ' ' 
                                locked_tank_.append(tank_)
                                
                print(str1+';', file=text_file)
    #            
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
                        for v2_ in v1_:
                            # tank__ =  self.vessel.info['tankId'][int(v2_['tankId'])]
                            
                            if 'tankId' in v2_.keys():
                                tank__ = self.vessel.info['tankId'][int(v2_['tankId'])]
                            else:
                                tank__ = v2_['tank']
                            
                            if tank__  not in tank_:
                                str1 += tank__ + ' ' + '1' + ' '
                                tank_.append(tank__)
                    print(str1, file=text_file)
                print(';', file=text_file)  
    #            
                str1 = 'param W_locked   := ' 
                print(str1, file=text_file) 
                for k_, v_ in self.loadable.info['manualOperation'].items():
                    for k1_, v1_ in v_.items():
                        for v2_ in v1_:
                            # tank_ = self.vessel.info['tankId'][int(v2_['tankId'])]
                            if 'tankId' in v2_.keys():
                                tank_ = self.vessel.info['tankId'][int(v2_['tankId'])]
                            else:
                                tank_ = v2_['tank']
                            
                            str1 = k_ + ' ' + tank_  + ' ' + str(k1_) + ' ' + "{:.1f}".format(v2_['qty'])
                            print(str1, file=text_file)
                print(';', file=text_file)
                
                
                
                str1 = 'param B_locked := '
                print(str1, file=text_file) 
                if self.mode in ['Auto']:
                    for k_, v_ in self.loadable.info['ballastOperation'].items():
                        tank_ = k_
                        str1 = '[' + tank_ + ', *] := '
                        for v__ in v_:
                            if v__['order'] != '0':
                                str1 += v__['order'] + ' ' + "{:.3f}".format(v__['qty']) + ' '
                        print(str1, file=text_file)
                print(';', file=text_file)  
                        
                
                str1 = 'set fixBallastPort := '
                for k_ in self.loadable.info['fixedBallastPort']:
                    if k_ != '0':
                        str1 += k_ + ' ' 
                print(str1+';', file=text_file)
                
                str1 = 'param trim_upper := '
                for k_, v_ in self.trim_upper.items():
                    str1 += k_ + ' ' + "{:.6f}".format(v_) + ' '
                print(str1+';', file=text_file)
                
                str1 = 'param trim_lower := '
                for k_, v_ in self.trim_lower.items():
                    str1 += k_ + ' ' + "{:.6f}".format(v_) + ' '
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
                for i_, j_ in self.vessel.info['onhand'].items():
                    str1 = '['+ i_ + ',*] = '
                    for k_, v_ in j_.items():
                        if k_ not in ['0A']:
                            for k1_, v1_ in self.loadable.info['virtualArrDepPort'].items():
                                if v1_ == k_:
                                    wt_ = j_[k_]['wt']
                                    str1 += str(k1_) + ' ' + "{:.3f}".format(wt_) + ' '
                            
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
                
                
                print('# ballast tanks with non-pw tcg details',file=text_file)#  
                tb_list_ = list(self.vessel.info['tankTCG']['tcg_pw'].keys()) + self.vessel.info['banBallast']
                str1 = 'set TB1 := '
                for i_, j_ in self.vessel.info['ballastTanks'].items():
                    if i_ not in tb_list_:
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
                
                if incDec_ballast:
                    print('# ballast tanks which can be ballast or deballast anytime',file=text_file)#  
                    str1 = 'set TB3 := '
                    for i_ in incDec_ballast:
                        str1 += i_ + ' '
                    print(str1+';', file=text_file)
                    
                print('# empty ballast tanks at arrival',file=text_file)#     
                if self.vessel_id in [1]:
                    str1 = 'set TBinit := APT AWBP AWBS'
                elif self.vessel_id in [2]:
                    str1 = 'set TBinit := APT WB6P WB6S'
                print(str1+';', file=text_file)     
    #            
                # density of seawater
                print('# density of seawater ',file=text_file)#
                str1 = 'param densitySeaWater := '
                for p_ in range(1,self.loadable.info['lastVirtualPort']+1):
                    port_ = self.loadable.info['virtualArrDepPort'][str(p_)][:-1]
                    portName_ = self.port.info['portOrder'][port_] # convert virtual port to exact port
                    density_ = self.port.info['portRotation'][portName_]['seawaterDensity']
                    str1 += str(p_) + ' ' + "{:.4f}".format(density_)  + ' '
                print(str1+';', file=text_file)
                
                print('# cargo tank restrictions ',file=text_file)# tank pair cannot carried same cargo (1P,1C) ... 
                str1 = 'set cargoTankNonSym := '
                for k__, k_  in enumerate(self.vessel.info['notSym']):
                    str1 += '('+ k_[0]  + ',' + k_[1] + ') '
                print(str1+';', file=text_file)
                
                print('# cargo tank vol restrictions ',file=text_file)# 5% vol diff
                str1 = 'set symmetricVolTank := '
                for k__, k_  in enumerate(self.config['sym_vol_tanks']):
                    if k_[0] not in self.vessel.info.get('notOnTop', []) and   k_[1] not in self.vessel.info.get('notOnTop', []):
                        str1 += '('+ k_[0]  + ',' + k_[1] + ') '
                print(str1+';', file=text_file)
                
                
                str1 = 'set C_max := '
                for k__, k_  in enumerate(self.vessel.info['maxCargo']):
                    str1 += k_ + ' '
                print(str1+';', file=text_file)
                
                print('# deballast percent ',file=text_file)#
                str1 = 'param deballastPercent := ' + "{:.4f}".format(1.0) 
                print(str1+';', file=text_file)
                
                print('# initial ballast values ',file=text_file)#
                str1 = 'param initBallast := '
                # for k_, v_ in self.vessel.info['initBallast']['wt'].items():
                #     str1 += str(k_) + ' ' + "{:.4f}".format(v_)  + ' '
                print(str1+';', file=text_file)
                
                print('# inc initial ballast ',file=text_file)#
                str1 = 'set incTB := '
                # for k_ in self.vessel.info['initBallast']['inc']:
                #     str1 += str(k_) + ' '
                print(str1+';', file=text_file)
                
                print('# dec initial ballast ',file=text_file)#
                str1 = 'set decTB := '
                # for k_ in self.vessel.info['initBallast']['dec']:
                #     str1 += str(k_) + ' '
                print(str1+';', file=text_file)
                
                print('# ballast tanks for deballasting percentage',file=text_file)#
                str1 = 'set TB0 := '
                for k_, v_ in self.vessel.info['initBallast']['wt'].items():
                    str1 += str(k_) + ' ' 
                print(str1+';', file=text_file)
                
                print('# zero list ports (ignore trim for these ports) ',file=text_file) # ignore trim for these ports
                str1 = 'set zeroListPort := '
                for k__, k_  in enumerate(self.loadable.info['zeroListPorts']):
                    str1 += k_  + ' '
                print(str1+';', file=text_file)
                
                print('# loading ports ',file=text_file)#
                str1 = 'set loadingPort := '
                # for k__, k_  in enumerate(self.vessel.info['loading']):
                #     if k__ < len(self.vessel.info['loading'])-1:
                #         str1 += '('+ str(k_)  + ',' + str(self.vessel.info['loading'][k__+1]) + ') '
                print(str1+';', file=text_file)
                
                print('# loading ports not last ',file=text_file)#
                # loadingPortNotLast_ = []
                last_port_ = 0
                str1 = 'set loadingPortNotLast := '
                for k__, k_  in enumerate(self.vessel.info['loading'][:-1]):
                    # print('k_',k_)
                    for q__, q_ in enumerate(range(k_, last_port_, -1)):
                        # print(q_-1,q_)
                        str1 += '('+ str(q_-1)  + ',' + str(q_) + ') '
                        # loadingPortNotLast_.append(k_)
                    last_port_ = k_+1
                print(str1+';', file=text_file)

                
                print('# departure arrival ports same weight ROB',file=text_file) # same weight
                depArrPort2, same_ballast = [], []
                str1 = 'set depArrPort2 := '
                for (a_, b_) in self.vessel.info['sameROB']:
                    if int(b_) < self.loadable.info['lastVirtualPort']-1:
                        str1 += '('+ str(a_)  + ',' + str(b_) + ') '
                        depArrPort2.append((a_,b_))
                        same_ballast.append(b_)
                print(str1+';', file=text_file)
                        
                
                # for k__, k_  in enumerate(self.vessel.info['loading']):
                #     if k__ < len(self.vessel.info['loading'])-1:
                #         if (str(k_), str(k_+1)) not in self.vessel.info['sameROBseawater']:
                #             str1 += '('+ str(k_)  + ',' + str(int(k_)+1) + ') '
                            
                # print(str1+';', file=text_file)
                
                print('# departure arrival ports diff weight ROB',file=text_file) # 
                str1 = 'set depArrPort1 := '
                # for k__, k_  in enumerate(self.vessel.info['loading']): # same tank
                    # if k__ < len(self.vessel.info['loading'])-1:
                    #     if (str(k_), str(k_+1)) not in depArrPort2:
                    #         str1 += '('+ str(k_)  + ',' + str(int(k_)+1) + ') '
                print(str1+';', file=text_file)
                
                str1 = 'set sameBallastPort := '
                for k__, k_  in  enumerate(same_ballast):
                    str1 += k_ + ' '
                print(str1+';', file=text_file)
                
                print('# rotating ports ',file=text_file)#
                str1 = 'set rotatingPort1 := '
                for k__, k_  in enumerate([self.vessel.info['loading'][-1]]):
                    # print('k_',k_)
                    for q__, q_ in enumerate(range(k_, last_port_, -1)):
                        # print(q_-1,q_)
                        str1 += '('+ str(q_-1)  + ',' + str(q_) + ') '
                        # loadingPortNotLast_.append(k_)
                    last_port_ = k_+1
                print(str1+';', file=text_file)
                
                
                # if len(self.vessel.info['rotationVirtual']) >= 1:
                #     for k__, k_  in enumerate(self.vessel.info['rotationVirtual'][0]):
                #         if k__ < len(self.vessel.info['rotationVirtual'][0])-1:
                #             str1 += '('+ str(k_)  + ',' + str(self.vessel.info['rotationVirtual'][0][k__+1])+ ') '
                # print(str1+';', file=text_file)
                
                str1 = 'set rotatingPort2 := '
                # if len(self.vessel.info['rotationVirtual']) >= 2:
                #     exit()
                    # for k__, k_  in enumerate(self.vessel.info['rotationVirtual'][1]):
                    #     if k__ < len(self.vessel.info['rotationVirtual'][1])-1:
                    #         str1 += '('+ str(k_)  + ',' + str(self.vessel.info['rotationVirtual'][1][k__+1])+ ') '
                print(str1+';', file=text_file)
                
                print('# departure arrival ports diff ballast ',file=text_file)#
                str1 = 'set depArrPort3 := '
                for k_, v_ in self.vessel.info['changeROB'].items():
                    str1 += '('+ str(k_[0])  + ',' + str(k_[1]) + ') '
                print(str1+';', file=text_file)
                
                print('# departure arrival ports diff ballast amount',file=text_file)#
                str1 = 'param diffBallastAmt := '
                for k_, v_ in self.vessel.info['changeROB'].items():
                    str1 += str(k_[0])  + ' ' + str(int(max(v_,500))) + ' '
                print(str1+';', file=text_file)
                
                if len(self.vessel.info['rotationVirtual']) >= 3:
                    self.error['Multiple Cargo Port Error'] = ['Num of ports with multiple cargos > 2!!']
                
                print('# lastLoadingPortBallastBan ',file=text_file) ## config
                str1 = 'set lastLoadingPortBallastBan := '
                if self.config['loadableConfig'].get('lastLoadingPortBallast',[]):
                    for k__, k_  in enumerate(self.vessel.info['ballastTanks'].keys()):
                        if k_ not in self.vessel.info['banBallast'] + self.config['loadableConfig'].get('lastLoadingPortBallast',[]):
                            str1 += k_ + ' '
                else:
                        
                    for k__, k_  in enumerate(self.config['last_loading_port_ballast_ban']):
                        str1 += k_ + ' '
                print(str1+';', file=text_file)
                
                print('# ban ballast tanks',file=text_file)
                if self.vessel_id in [1]:
                    str1 = 'set ballastBan := APT AWBP AWBS'
                elif self.vessel_id in [2]:
                    str1 = 'set ballastBan := APT WB6P WB6S'
                print(str1+';', file=text_file)
                
                print('# ban ballast tanks in ports',file=text_file)
                
                if self.vessel.info['initialROBweight'] < 2500:
                    print('Small bunker')
                    str1 = 'set P_ban_ballast := ' #+ str(self.vessel.info['loading'][-1]-1)
                    for k_ in range(1,self.vessel.info['loading'][-1]):
                        str1 += str(k_) + ' '
                        
                    print(str1+';', file=text_file)
                    
                    str1 = 'set TB5 := APT'
                    print(str1+';', file=text_file)
                    
                else:
                        
                    str1 = 'set P_ban_ballast := ' #+ str(self.vessel.info['loading'][-1]-1)
                    for k_ in range(0,self.vessel.info['loading'][-1]):
                        str1 += str(k_) + ' '
                        
                    print(str1+';', file=text_file)
                
                
                
                    
                # print('# first loading Port',file=text_file)#
                # if len(self.port.info['portRotation']) <= 2:
                #     str1 = 'param firstloadingPort := 0'
                #     print(str1+';', file=text_file)
                # else:
                #     str1 = 'param firstloadingPort := ' + self.loadable.info['arrDepVirtualPort']['1D']
                #     print(str1+';', file=text_file)
                
                                

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
                
                print('# max num tanks', file=text_file)
                if self.maxTankUsed:
                    str1 = 'param maxTankUsed := ' + str(self.maxTankUsed) 
                    print(str1+';', file=text_file) 
                
                
                print('# first discharge cargo', file=text_file)
                str1 = 'set firstDisCargo := ' 
                if self.firstDisCargo not in ['None'] and  'P'+self.firstDisCargo not in ['P']:
                    str1 += 'P'+self.firstDisCargo
                print(str1+';', file=text_file)
                
                
                print('# cargoweight', file=text_file)
                str1 = 'param cargoweight := ' + str(int(float(self.cargoweight)*10)/10) 
                print(str1+';', file=text_file) 
                
                if self.mode in ['Manual', 'FullManual']:
                    str1 = 'param diffVol := 0.101' 
                    print(str1+';', file=text_file) 
                    
                
                # str1 = 'set Cequal := '  
                # # if len(self.loadable.info['parcel']) == 1:
                # #     str1 += list(self.loadable.info['parcel'].keys())[0]
                # print(str1+';', file=text_file) 
                    
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
                    for k1_,v1_ in self.loadable.info['virtualArrDepPort'].items():
                        if v1_ not in  ['0A']:
                            if lcg_port in [None]:
                                lcg_ = j_['lcg']
                            else:
                                lcg_ = lcg_port.get(k1_, {}).get(i_, j_['lcg'])
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
                    
                print('# TCGs for others tanks', file=text_file)
                str1 = 'param TCGtp := '
                print(str1, file=text_file)
                for i_, j_ in self.vessel.info['onhand'].items():
                    str1 = '['+ i_ + ',*] = '
                    for k_, v_ in j_.items():
                        tcg_ = j_[k_]['tcg']
                        if k_ not in ['0A']:
                            for k1_,v1_ in self.loadable.info['virtualArrDepPort'].items():
                                if v1_ == k_:
                                    str1 += str(k1_) + ' ' + "{:.4f}".format(tcg_) + ' '
                                    
                    print(str1, file=text_file)
                print(';', file=text_file)
                
                print('# LCGs for others tanks', file=text_file)
                str1 = 'param LCGtp := '
                print(str1, file=text_file)
                for i_, j_ in self.vessel.info['onhand'].items():
                    str1 = '['+ i_ + ',*] = '
                    for k_, v_ in j_.items():
                        lcg_ = j_[k_]['lcg']
                        if k_ not in ['0A']:
                            for k1_,v1_ in self.loadable.info['virtualArrDepPort'].items():
                                if v1_ == k_:
                                    str1 += str(k1_) + ' ' + "{:.4f}".format(lcg_) + ' '
                                    
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
                str1 = 'param deadweight   := ' + str(self.vessel.info['draftCondition']['deadweight']) 
                print(str1+';', file=text_file)
                
                
                print('# base draft', file=text_file)
                str1 = 'param base_draft := '
                for i_, j_ in self.base_draft.items():
                    str1 += str(i_) + ' ' +  "{:.2f}".format(j_) + ' '
                print(str1+';', file=text_file)
                
                print('# draft corr', file=text_file)
                str1 = 'param draft_corr := '
                for k_, v_ in self.trim_upper.items():
                    if v_ > 0.5:
                        str1 += str(k_) + ' ' +  "0.1" + ' '
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
                str1 += '1;' if IIS else '0;'
                print(str1, file=text_file)
                
                print('# adjustment for LCB, MTC and draft ',file=text_file)#                
                str1 = 'param adjLCB := ' + str(self.config['adj_LCB'])
                print(str1+';', file=text_file)
                str1 = 'param adjMeanDraft := ' + str(self.config['adj_mean_draft'])
                print(str1+';', file=text_file)
                str1 = 'param adjMTC := ' + str(self.config['adj_MTC'])
                print(str1+';', file=text_file)
                
                print('# runtime limit ',file=text_file)#  
                if self.config['loadableConfig'].get('timeLimit', None):
                    str1 = 'param runtimeLimit := ' + str(self.config['loadableConfig']['timeLimit'])
                else:
                    str1 = 'param runtimeLimit := ' + str(self.config.get('timeLimit', 60))
                print(str1+';', file=text_file)
                
                
                
        
                
                
                
                
                
                
                
                
                
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
        
        
        
        
   

# -*- coding: utf-8 -*-
"""
Created on Thu Aug 19 15:05:14 2021

@author: I2R
"""
from vlcc_port import Port
from vlcc_load import Loadable 
from vlcc_vessel import Vessel
from copy import deepcopy
import numpy as np

DEC_PLACE = 3
_SOLVER_ = 'AMPL' # AMPL or ORTOOLS

class Process_input1(object):
    def __init__(self, data):

        # gather info
        self.vessel_json = {'vessel': data['vessel'],
                            'onHand': data['discharge']['onHandQuantity']
                            }
        #
        self.port_json = {'portDetails': data['discharge']['portDetails'],
                          'portRotation': data['discharge']['dischargeStudyPortRotation']}
        
        
        self.discharge_json = {'cargoNomination': data['discharge']['cargoNomination'],
                              'cargoOperation': data['discharge']['cargoNominationOperationDetails'],
                              'commingleCargo': data['discharge'].get('commingleCargos',[]),
                              'arrivalPlan': data['discharge'].get('loadablePlanPortWiseDetails',{}),
                              'cowHistory': data['discharge'].get('cowHistory', []),
                              "cowDetails": data['discharge'].get('cowDetails', []),
                              "existingDischargePlanDetails":data['discharge'].get("existingDischargePlanDetails",{})
                              }

        
        self.user = data['discharge'].get('user', None)
        self.role = data['discharge'].get('role', None)                              
        self.loadable_id = data['discharge']['id']
        self.vessel_id   = data['discharge']['vesselId']
        self.voyage_id   = data['discharge']['voyageId']
        self.process_id  = data.get('processId',None)
        # self.loadline_id = data['loadable']['loadlineId']
        # self.draft_mark = data['loadable']['draftMark']
        self.config = data['config']
        self.module = data['module']
        
        print('module:', self.module)
        
        self.solver = self.config['solver'] #_SOLVER_
                
        self.preloaded_cargo = []
        
        self.rules_json = data['discharge'].get("dischargeStudyRuleList", [])
        # self.config = data['config']
        self._set_config(data['config'])
        self.error = {}
        
        
        self.deballast_percent = self.config['deballast_percent'] #0.4
        self.commingle_temperature = None
        
        self.has_loadicator = self.vessel_json['vessel']['vessel'].get('hasLoadicator',False)
        
        self.feedback_sf_bm_frac = 95
        
        self.mode = ""
        
        self.accurate = True
        
        self.cargo_rotation = []
        
        ## for reballast
        self.lcg_port = None
        self.weight = None
        self.tide_info = None
        
        
    def _set_config(self, config):
        
        RULES = {"918": "SSFLimit", "919": "SBMLimit"}
        
        # self.config = config
        
        config_ = {}
        for l__, l_ in enumerate(self.rules_json):
            
            if l_['header'] == 'Vessel Stability Rules':
                ## sea or port limit for SF and BM not considered
                ## Ensure draft not over the load line always true
                # continue
                for k__, k_ in enumerate(l_['rules']):
                    
                    # print(k_)
                    
                    v_ =  RULES.get(k_['ruleTemplateId'], None)
                    # print(k_['ruleTemplateId'], v_)
                    
                    if v_ in ["SSFLimit", "SBMLimit"]:
                        config_[v_] = float(k_['inputs'][0]['value'])
                        
            elif l_['header'] == 'Algorithm Rules':
                    pass
                 
                    
        # config_['SSFLimit'] = 90
        # config_['SBMLimit'] = 90         
        config1_ = {}        
        config1_['loadableConfig'] = config_
        self.config = {**config, **config1_}          
        
    def prepare_dat_file(self, ballast_weight=1000):
        
        # prepare dat file for AMPL
        if not self.error:
            self.port = Port(self)
            
        if not self.error:
            self.loadable = Loadable(self) # basic info
            self.loadable._create_discharge_operations(self) # operation and commingle
        if not self.error:
            self.vessel = Vessel(self)
            self.vessel._get_onhand(self) # ROB
            self.vessel.info['onboard'] = {}
            self.vessel._set_preloaded(self) # change tankId to tankName for preloaded
            
            self.loadable._get_COW(self) # get COW
        if not self.error:
            self.get_stability_param()
            
        
    def get_stability_param(self, ballast_weight_ = 92000, sf_bm_frac = 0.95, trim_upper = 3.0, trim_lower = 2.5, \
                            reduce_disp_limit = 0, base_draft = None, set_trim = 0, mean_draft = None):
        
        if self.vessel_id in [2]:
            ballast_weight_ = 94000
        self.ballast_percent = self.config['ballast_percent'] #0.4 
        if self.loadable.info['lastVirtualPort'] == 1:
            self.ballast_percent = 1
            print("Change ballast_percent to 1.0")
 
        lightweight_ = self.vessel.info['lightweight']['weight']
        max_deadweight_ = 1000*1000
        cont_weight_ = self.vessel.info['deadweightConst']['weight'] #+ self.vessel.info['onboard']['totalWeight']
        
        loadline_ = 100.0
        # min_draft_limit_ = 10.425
        
        # min_aft_draft_limit_ = self.config['min_aft_draft_limit']
        # min_draft_limit_ = self.config['min_mid_draft_limit']
        # min_for_draft_limit_ = self.config['min_for_draft_limit']
        
        
        self.displacement_lower, self.displacement_upper = {}, {}
        self.base_draft, self.est_draft = {}, {}
        self.sf_base_value, self.sf_draft_corr, self.sf_trim_corr = {}, {}, {}
        self.bm_base_value, self.bm_draft_corr, self.bm_trim_corr = {}, {}, {}
        self.trim_lower, self.trim_upper = {}, {}
        
        
        self.sf_bm_frac = sf_bm_frac ##  _bm_frac, self.feedback_sf_bm_frac)
        sf_bm_frac_ = 0.99
        if self.config['loadableConfig']:
            sf_bm_frac_ = min(self.config['loadableConfig']['SSFLimit'], self.config['loadableConfig']['SBMLimit'])/100

        self.sf_bm_frac = min(sf_bm_frac_, self.sf_bm_frac)
        print('SF BM Svalue limits', self.sf_bm_frac)

        # self.trim_lower[str(self.loadable.info['lastVirtualPort'])] = 2.0
        # self.trim_upper[str(self.loadable.info['lastVirtualPort'])] = 3.0
        
        self.limits = {'draft':{}}
        
        self.limits['draft']['loadline'] = loadline_
        self.limits['draft'] = {**self.limits['draft'], **{k_[:-1]:v_  for k_, v_ in self.port.info['maxDraft'].items()}}
        self.limits['operationId'] = {k_:str(v_)[-1] for k_, v_ in self.port.info['portRotationId'].items()}
        self.limits['seawaterDensity'] = {k_[:-1]:v_  for k_, v_ in self.port.info['seawaterDensity'].items()} 
        self.limits['tide'] = {k_[:-1]:v_  for k_, v_ in self.port.info['tide'].items()}  
        self.limits['id'] = self.loadable_id
        self.limits['vesselId'] = self.vessel_id
        self.limits['voyageId'] = self.voyage_id
        self.limits['airDraft'] = {k_[:-1]:v_  for k_, v_ in self.port.info['maxAirDraft'].items()} 
        self.limits['portOrderId'] = self.port.info['portOrderId']
        
        
        inter_port_ = []
        for r_ in self.loadable.info['rotationVirtual']:
            inter_port_ += r_[:-1]
            
        print('inter_port:', inter_port_)
        
        # self.full_discharge = True
        self.ave_trim = {}
        ## set trimlimit based on 
        self._set_trim(set_trim = set_trim)
        
        self.strip_ports = {}

        ballast_ = sum([v_ for k_, v_ in self.vessel.info['initBallast']['wt'].items()])
        weight_ = sum([v1_ for k_, v_ in self.loadable.info['preloadOperation'].items() for k1_, v1_ in v_.items()])
        arr_weight_, arr_ballast_ = weight_, ballast_
        
        auto_discharge_ = np.zeros(self.loadable.info['lastVirtualPort']+1)
        auto_discharge1_ = np.zeros(self.loadable.info['lastVirtualPort']+1)
        auto_cargo_discharge_ = {}
        reduce_disp_limit_ = []
        
        print(self.loadable.info['preload'])
        for p_ in range(1, self.loadable.info['lastVirtualPort']+1):  # exact to virtual
            print('port:', p_, "-----------------------------------------------")
            port__ = self.loadable.info['virtualArrDepPort'][str(p_)] # 1D, 2D
            port_, arr_dep_ = int(port__[:-1]), port__[-1] # convert virtual port to exact port
            port_code_ = self.port.info['portOrder'][str(port_)]
            
            if arr_dep_ == 'A':
                arr_weight_, arr_ballast_ = weight_, ballast_
                
            discharge_cargos_ = self.loadable.info['virtualPort1'].get(str(p_), [])
            
            # if len(discharge_cargos_) > 2:
            #     self.error['Multiple discharge error'] = ['Not tested yet!!']
            #     return
            
            disc_mode_ =  {1:'balance', 2:'manual', 3:'remaining', None:'loading'}

            for d_ in discharge_cargos_:
                mode_ = self.loadable.info['mode'][d_][str(p_)]
                print('discharge cargos:', str(p_), d_, 'auto mode:', mode_, disc_mode_[mode_])
                
                if mode_ in [1]:
                    vp_ = self.loadable.info['arrDepVirtualPort'][str(port_+1)+'A']
                    # amt to discharge
                    to_discharge_ = self.loadable.info['toDischargePort'][int(vp_)]
                    to_discharge_ += auto_discharge1_[int(vp_)] # cum amt discharge
                    
                    next_port_ = self.port.info['portOrder'][str(port_+1)]
                    draft_limit_ = self.port.info['portRotation'][next_port_]['maxDraft']
                    displacement_limit_ = np.interp(draft_limit_, self.vessel.info['hydrostatic']['draft'], self.vessel.info['hydrostatic']['displacement'])
                    print('displacement_limit:', displacement_limit_)
                    
                    misc_weight_ = 0.0
                    for k1_, v1_ in self.vessel.info['onhand'].items():
                        misc_weight_ += v1_.get(str(port_+1) + 'A',{}).get('wt',0.)
                    
                    cargo_to_load_ = displacement_limit_ - cont_weight_ - misc_weight_ - lightweight_  - arr_weight_ - arr_ballast_
                    cargo_to_load_ = cargo_to_load_/(1-self.ballast_percent)
                    
                    if ballast_- self.ballast_percent*cargo_to_load_ > ballast_weight_:
                        print('Ballast overloaded')
                        cargo_to_load_ = displacement_limit_ - cont_weight_ - misc_weight_ - lightweight_  - arr_weight_ - ballast_weight_
                    
                    est_discharge_= min(0,round(cargo_to_load_ - to_discharge_,1))
                    
                    if -est_discharge_ > self.loadable.info['preload'][d_]:
                        self.error['Discharge error'] = ['Balance cannot meet draft limit!!']
                        return
                    
                    if d_ not in auto_cargo_discharge_:
                        auto_cargo_discharge_[d_] = {str(p_): est_discharge_}
                    else:
                        auto_cargo_discharge_[d_][str(p_)] = est_discharge_
                        
                    
                    auto_discharge_[int(p_)] +=  est_discharge_
                    auto_discharge1_ = np.cumsum(auto_discharge_)
                    print('balance', 'confirm', to_discharge_, 'extra est:', est_discharge_)
                    
                elif mode_ in [3]:
                     # Remaining or entire
                    discharged_ = [v_ for k_, v_ in auto_cargo_discharge_.get(d_,{}).items()] + \
                                      [v_ for k_, v_ in self.loadable.info['operation'].get(d_,{}).items()]
                        
                    to_discharge_ = round(-self.loadable.info['preload'][d_] - sum(discharged_),1)
                    
                    if d_ not in auto_cargo_discharge_:
                        auto_cargo_discharge_[d_] = {str(p_): to_discharge_}
                    else:
                        auto_cargo_discharge_[d_][str(p_)] = to_discharge_
                        
                    auto_discharge_[int(p_)] +=  to_discharge_
                    auto_discharge1_ = np.cumsum(auto_discharge_)
                    
                    print('remaining or entire',  to_discharge_)
                    
            # estimate cargo to discharge and ballast amt needed to balance        
            cargo_to_load_ = self.loadable.info['toDischargePort'][p_]  - self.loadable.info['toDischargePort'][p_-1] + \
                             auto_discharge1_[p_]  - auto_discharge1_[p_-1]
                             
            ballast_ = min(ballast_weight_,ballast_- self.ballast_percent*cargo_to_load_)
            print('cargo_to_load::', round(cargo_to_load_,1), 'ballast::', round(ballast_,2))

#           # cargo remaing onboard
            cargo_weight_  = max(0., weight_ + self.loadable.info['toDischargePort'][p_] + auto_discharge1_[p_])
#            print(str(port_)+arr_dep_, cargo_weight_)
    
            misc_weight_ = 0.0
            for k1_, v1_ in self.vessel.info['onhand'].items():
                misc_weight_ += v1_.get(port__,{}).get('wt',0.)
            # if p_ == self.loadable.info['lastVirtualPort'] and cargo_weight_ > 100:
            #     # last port dep
            #     self.full_discharge = False
               
            
##            ballast_weight_ = 20000
            est_deadweight_ = min(cont_weight_ + misc_weight_ + cargo_weight_ + ballast_, max_deadweight_)
            est_displacement_ = lightweight_ + est_deadweight_
            seawater_density_ = self.port.info['portRotation'][port_code_]['seawaterDensity']
            
            
            # if p_ == self.loadable.info['lastVirtualPort'] and self.full_discharge:
            #     min_draft_limit_ -= 2
            #     print('last virtual port:', p_, min_draft_limit_)
                
            min_limit_ = self.config['min_aft_draft_limit'] if round(cargo_weight_) > 0 else self.config['min_ballast_aft_draft_limit']
            ## lower bound displacement
            lower_draft_limit_ = min_limit_ #max(self.ports.draft_airdraft[p_], min_draft_limit_)
            lower_displacement_limit_ = np.interp(lower_draft_limit_, self.vessel.info['hydrostatic']['draft'], self.vessel.info['hydrostatic']['displacement'])
            ###
            est_draft__ =  np.interp(est_displacement_,  self.vessel.info['hydrostatic']['displacement'], self.vessel.info['hydrostatic']['draft'])
            # correct displacement to port seawater density
            lower_displacement_limit_  = lower_displacement_limit_*seawater_density_/1.025
            
            # disp1_ = lower_displacement_limit_*1.025/seawater_density_
            # d1_ = np.interp(disp1_, self.vessel.info['hydrostatic']['displacement'], self.vessel.info['hydrostatic']['draft'])
            # print(port__,d1_,seawater_density_,disp1_,lower_displacement_limit_)
            # trim_ = self.trim_lower.get(str(p_),.0)
            if (est_draft__ > lower_draft_limit_) or (p_ in inter_port_):
                print('Est draft > min required for propeller immersion')
                est_displacement_ = max(lower_displacement_limit_, est_displacement_)   
                
                if p_ in inter_port_ and cargo_to_load_ < 0:
                    
                    strip_ = {}
                    for d_ in discharge_cargos_: 
                        
                        # if -cargo_to_load_ < 500 + self.loadable.info['minAmount'][d_]:
                        #     pass
                        # else:
                            
                        first_strip_ = self.set_trim_mode['first_strip'][d_]
                        strip_[d_] = True if p_ >= first_strip_ else False
                            
                    if True in strip_.values():
                        self.trim_lower[str(p_)] = 4.01
                        self.trim_upper[str(p_)] = 5.95
                        self.ave_trim[str(p_)] = 5.0
                    else:
                        self.trim_lower[str(p_)] = 0.5
                        self.trim_upper[str(p_)] = 4.0
                        self.ave_trim[str(p_)] = 2.0
                        
                    self.strip_ports[str(p_)] = deepcopy(strip_)
                    print('inter_port ave trim', self.ave_trim[str(p_)], "strip_::", strip_)
                    
                    if (est_draft__ < lower_draft_limit_):
                        print('**Need to reduce lower displacement limit')
                        reduce_disp_limit_.append(p_)
               
            else:
                    
                low_trim_ = min(2.9, 2*(min_limit_ - est_draft__)) #2.5
                ## est_draft__ + 0.1 = mid_draft_
                est_draft__ = min_limit_ - low_trim_/2 - 0.1 # max trim = 3m 
                self.trim_lower[str(p_)], self.trim_upper[str(p_)] = low_trim_, 2.95 #min(low_trim_+.1, 2.95)
                lower_displacement_limit_ = np.interp(est_draft__, self.vessel.info['hydrostatic']['draft'], self.vessel.info['hydrostatic']['displacement'])
                print(p_, round(est_draft__,2), round(self.trim_lower[str(p_)],2), round(self.trim_upper[str(p_)],2))
                self.ave_trim[str(p_)] = 3.0
                
                lower_draft_limit_ = est_draft__ #max(self.ports.draft_airdraft[p_], min_draft_limit_)
                lower_displacement_limit_ = np.interp(lower_draft_limit_, self.vessel.info['hydrostatic']['draft'], self.vessel.info['hydrostatic']['displacement'])
                print(min_limit_, round(lower_displacement_limit_), est_displacement_)
                lower_displacement_limit_ = min(est_displacement_, lower_displacement_limit_) - reduce_disp_limit
                # correct displacement to port seawater density
                lower_displacement_limit_  = lower_displacement_limit_*seawater_density_/1.025
                
             
           
            ## upper bound displacement
            upper_draft_limit_ = min(loadline_, float(self.port.info['portRotation'][port_code_]['maxDraft'])) - 0.001
            upper_displacement_limit_ = np.interp(upper_draft_limit_, self.vessel.info['hydrostatic']['draft'], self.vessel.info['hydrostatic']['displacement'])
            # correct displacement to port seawater density
            upper_displacement_limit_  = upper_displacement_limit_*seawater_density_/1.025
            
            est_displacement_ = min(est_displacement_, upper_displacement_limit_)

            # print(p_, lower_displacement_limit_,est_displacement_,upper_displacement_limit_)
            self.displacement_lower[str(p_)] = lower_displacement_limit_
            self.displacement_upper[str(p_)] = upper_displacement_limit_
            
            est_draft_ = np.interp(est_displacement_, self.vessel.info['hydrostatic']['displacement'], self.vessel.info['hydrostatic']['draft'])
            
            self.est_draft[str(p_)] = int(round(est_draft_))
            # base draft for BM and SF
            # trim_ = 0.5*(self.trim_lower.get(str(p_),0.0) + self.trim_upper.get(str(p_),0.0))
            trim_ = self.ave_trim.get(str(p_), 0.0)
            
            if self.vessel_id in [1, '1']:
                base_draft__ = int(np.floor(est_draft_+trim_/2))
            elif self.vessel_id in [2, '2']:
                base_draft__ = int(np.floor(est_draft_))
                
            base_draft_ = base_draft__ if p_  == 1 else min(base_draft__, self.base_draft[str(p_-1)])
            base_draft_ = min(22,base_draft_)
            
            if base_draft:
                self.base_draft[str(p_)] = base_draft[str(p_)]
                base_draft_ = base_draft[str(p_)]
            else:
                self.base_draft[str(p_)] = base_draft_
            
            
            # self.base_draft[str(p_)] = base_draft_
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
        self.auto_cargo_discharge = auto_cargo_discharge_

        ##----------------------------------------------
        for p_ in reduce_disp_limit_:
            self.displacement_lower[str(p_)] = self.displacement_lower[str(self.loadable.info['lastVirtualPort'])]+1000

        self.limits['upperTrimLimit'] = {}
        for l_ in range(1, len(self.loadable.info['cargoPort'])+1):
            p1_, p2_ = str(l_)+'A', str(l_)+'D'
            pp_ = self.loadable.info['arrDepVirtualPort'][p1_]
            self.limits['upperTrimLimit'][str(2*l_-2)] = max(0.1, round(self.trim_upper.get(pp_,0.0)))
            pp_ = self.loadable.info['arrDepVirtualPort'][p2_]
            self.limits['upperTrimLimit'][str(2*l_-1)] = max(0.1, round(self.trim_upper.get(pp_,0.0)))
            
            
        print('upperTrimLimit (not vitual ports)',self.limits['upperTrimLimit'])     
        
    def _set_trim(self, set_trim = 0):
        
        
        if self.loadable.info.get('backLoadingCargo', []):
            set_trim = 1
            
        # set_trim = 1
        self.set_trim_mode = {'mode': set_trim, 'strip':{}, 'first_strip':{}}
        if set_trim == 0:
            ## all non-empty tanks except last port
            for k_, v_ in self.loadable.info['virtualPort1'].items():
                for l_ in v_:
                    if len(self.loadable.info['partialDischarge2'][l_]) > 0:
                        if self.loadable.info['partialDischarge2'][l_][-1] == k_:
                            self.set_trim_mode['strip'][k_] = True
                            
                            if l_ in self.set_trim_mode['first_strip']:
                                self.set_trim_mode['first_strip'][l_] = min(self.set_trim_mode['first_strip'][l_], int(k_))
                            else:
                                self.set_trim_mode['first_strip'][l_] = int(k_)
                            
        elif set_trim == 1:
            ## all non-empty tanks except second last port
            for k_, v_ in self.loadable.info['virtualPort1'].items():
                for l_ in v_:
                    if len(self.loadable.info['partialDischarge2'][l_]) > 0:
                        
                        l__ = -2 if len(self.loadable.info['partialDischarge2'][l_]) > 1 else -1
                        
                        cargo_ = self.loadable.info['operation'][l_].get(k_, 0.)
                        if cargo_ < 0 and (-cargo_ < self.loadable.info['minAmount'].get(l_, 0.)):
                            pass
                        
                        elif (self.loadable.info['partialDischarge2'][l_][l__] == k_):
                            self.set_trim_mode['strip'][k_] = True
                            
                            if l_ in self.set_trim_mode['first_strip']:
                                self.set_trim_mode['first_strip'][l_] = min(self.set_trim_mode['first_strip'][l_], int(k_))
                            else:
                                self.set_trim_mode['first_strip'][l_] = int(k_)
                        
                        
        for k_, v_ in self.loadable.info['partialDischarge2'].items():
            if len(self.loadable.info['partialDischarge2'][k_]) > 0:
                if self.set_trim_mode['first_strip'].get(k_, None) in [None]:
                    self.set_trim_mode['first_strip'][k_] = int(v_[-1])
        print("set_trim_mode::",self.set_trim_mode)
        print("partialDischarge2::",self.loadable.info['partialDischarge2'])

    def write_dat_file(self, file = 'input_discharge.dat', IIS = True, lcg_port = None, weight = None, drop_BM = False, \
                               incDec_ballast = None, ave_trim = None, port_ballast_ban = True):
        
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
                str1 = 'set T_loaded:= '
                for k_, v_ in self.loadable.info['preloadOperation'].items():
                    for k1_, v1_ in v_.items():
                        str1 += k1_ + ' '
                print(str1+';', file=text_file)
                
                ##
                print('# set of all cargoes',file=text_file)
                str1 = 'set C:= '
                for i_,j_ in self.loadable.info['parcel'].items():
                    str1 += i_ + ' '
                print(str1+';', file=text_file)
                
                
                print('# set of all loaded cargoes (partial loading condition)',file=text_file)
                str1 = 'set C_loaded:= '
                for k_, v_ in self.loadable.info['preloadOperation'].items():
                    str1 += k_ + ' '
                print(str1+';', file=text_file)
                
                
                print('# set of back loading cargoes ',file=text_file)
                str1 = 'set C_backload:= '
                for k_ in self.loadable.info['backLoadingCargo']:
                    str1 += k_ + ' '
                print(str1+';', file=text_file)
                
                
                print('# if cargo c has been loaded in tank t (partial loading condition)',file=text_file)
                str1 = 'param I_loaded := '
                print(str1, file=text_file)
                for k_, v_ in self.loadable.info['preloadOperation'].items():
                    str1 = '[' + k_ + ', *] := '
                    for k1_, v1_ in v_.items():
                        str1 += k1_ + ' ' + '1 '
                    print(str1, file=text_file)
                print(';', file=text_file)
                
                #            
                str1 = 'param W_loaded   := ' 
                print(str1, file=text_file) 
                # no discharging of the preloaded cargo
                
                # for k_, v_ in self.loadable['preloadOperation'].items():
                #     for k1_, v1_ in v_.items():
                #         str1 = k_ + ' ' + self.tanks.cargo_tanks[k1_]['tankName'] + ' ' + str(k1_) + ' ' + str(v1_)
                #         print(str1, file=text_file)
                print(';', file=text_file)
    
                #
                print('# weight of cargo c remained in tank t at initial state (before ship entering the first port)',file=text_file)#  
                str1 = 'param W0  := ' 
                print(str1, file=text_file) 
                for k_, v_ in self.loadable.info['preloadOperation'].items():
                    str1 = '[' + k_ + ', *] := '
                    for k1_, v1_ in v_.items():
                        str1 += k1_ + ' ' +  "{:.1f}".format(v1_) + ' ' 
                    print(str1, file=text_file)
                    
                print(';', file=text_file)
                
                if lcg_port and weight:
                    
                    print('# QW1')
                    str1 = 'param QW1 := '
                    print(str1, file=text_file)
                    for k1_, v1_ in weight.items():
                        str1 = '[*, *, ' + str(k1_) + '] := '
                        for k2_, v2_ in v1_.items():
                            str1 += v2_[0]['parcel'] + ' ' + k2_ + ' ' + str(v2_[0]['wt']) + ' '
                        print(str1, file=text_file)
                    
                    print(';', file=text_file)
                    
                    print('# QWT')
                    for i_,j_ in self.loadable.info['parcel'].items():
                        str1 = 'set QWT1[' + str(i_) + '] := '
                        for j_ in cargo_tanks_:
                            str1 += j_ + ' '
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
                
                print('# NP1',file=text_file)#  
                # if not self.full_discharge:
                str1 = 'set NP1 := '  # to virtual ports
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
                    P_load2_, P_load3_ = {}, {}
                    for k_, v_ in self.set_trim_mode['first_strip'].items():
                        if v_-1 > 0:
                            P_load2_[k_] = []
                            str1 = 'set P_load2['+ k_ +']'+ ':= '
                            for v__ in range(1, v_):
                                str1 += str(v__) + ' '
                                P_load2_[k_].append(v__)
                                
                            print(str1+';', file=text_file)
                            
                    for k_, v_ in self.loadable.info['preloadOperation'].items():
                        str1 = 'set T2['+ k_ +']'+ ':= '
                        for k1_, v2_ in v_.items():
                            if v2_ > 0 and k1_ not in self.vessel.info['slopTank']:
                                str1 += str(k1_) + ' '
                        print(str1+';', file=text_file)
                        
                    for k_, v_ in self.loadable.info['inSlop'].items():
                        if len(v_) > 0:
                            P_load3_[k_] = []
                            str1 = 'set P_load3['+ k_ +']'+ ':= '
                            for v__ in range(1, int(self.loadable.info['partialDischarge2'][k_][-1])):
                                str1 += str(v__) + ' '
                                P_load3_[k_].append(v__)
                            print(str1+';', file=text_file)
                            
                    for k_, v_ in self.loadable.info['preloadOperation'].items():
                        if len(self.loadable.info['inSlop'][k_]) > 0:
                            str1 = 'set T3['+ k_ +']'+ ':= '
                            k1_ = self.loadable.info['inSlop'][k_][0]
                            str1 += str(k1_) + ' '
                            print(str1+';', file=text_file)
                            
                    for k_, v_ in self.loadable.info['inSlop'].items():
                        if len(v_) > 0:
                            ports_ = set(P_load3_.get(k_, [])) - set(P_load2_.get(k_, []))
                            str1 = 'set P_load4['+ k_ +']'+ ':= '
                            for v__ in ports_:
                                str1 += str(v__) + ' '
                                P_load3_[k_].append(v__)
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

                if self.loadable.info['emptyTank']:
                    print('# maxEmptyTankWeight',file=text_file)#  
                    # if not self.full_discharge:
                    str1 = 'param maxEmptyTankWeight := 10000'  # to virtual ports
                    print(str1+';', file=text_file)
                    
                    
                    print('# P_opt',file=text_file)#  
                    str1 = 'set  P_opt := '  # to virtual ports
                    for i_ in self.loadable.info['emptyTank']:
                        str1 += '('+ i_[0] + ',' + i_[1] +') '
                        
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
                
                str1 = 'param aveCargoDensity  := ' 
                str1 += "{:.4f}".format(np.mean(density_))  + ' '
                print(str1+';', file=text_file)
                
                print('# weight (in metric tone) of cargo to be moved at port p',file=text_file)#  
                str1 = 'param Wcp  := ' 
                print(str1, file=text_file) 
                for i_, j_ in self.loadable.info['operation'].items():
                    str1 = '[' + str(i_) + ', *] := '
                    for k_,v_ in j_.items():
                        if int(k_) > 0 :
                            if v_ < 0 or i_ in self.loadable.info['backLoadingCargo']:
                                str1 += str(k_) + ' ' + "{:.1f}".format(round(v_,1)) + ' '
                            elif self.loadable.info['mode'][i_][k_] in [3]:
                                str1 += str(k_) + ' ' + "{:.1f}".format(round(-self.loadable.info['preload'][i_],1)) + ' '
                            else:
                                str1 += str(k_) + ' ' + "{:.1f}".format(round(self.auto_cargo_discharge.get(i_,{}).get(k_,0.0),1)) + ' '
                    print(str1, file=text_file)
                print(';', file=text_file)
                
                
                print('# discharge sets')
                str1 = 'set manual := ' 
                for k_, v_ in self.loadable.info['mode'].items():
                    for k1_, v1_ in  v_.items():
                        if v1_ in [2] and k_ in self.loadable.info['preloadOperation']:
                            for k3_ in self.loadable.info['preloadOperation'][k_]:
                                str1 += '(' + k_ + ',' + k3_ +','+ k1_ + ')' + ' '
                            
                print(str1+';', file=text_file)
                str1 = 'set balance := ' 
                for k_, v_ in self.loadable.info['mode'].items():
                    for k1_, v1_ in  v_.items():
                        if v1_ in [1]:
                            for k3_ in self.loadable.info['preloadOperation'][k_]:
                                str1 += '(' + k_ + ',' + k3_ +','+ k1_ + ')' + ' '
                print(str1+';', file=text_file)
                str1 = 'set remain := ' 
                for k_, v_ in self.loadable.info['mode'].items():
                    for k1_, v1_ in  v_.items():
                        if v1_ in [3]:
                            for k3_ in self.loadable.info['preloadOperation'][k_]:
                                str1 += '(' + k_ + ',' + k3_ +','+ k1_ + ')' + ' '
                print(str1+';', file=text_file)
                
                str1 = 'set manual1 := ' 
                for k_, v_ in self.loadable.info['mode'].items():
                    for k1_, v1_ in  v_.items():
                        if v1_ in [2]:
                            str1 += '(' + k_ + ',' + k1_ + ')' + ' '
                            
                print(str1+';', file=text_file)
                str1 = 'set balance1 := ' 
                for k_, v_ in self.loadable.info['mode'].items():
                    for k1_, v1_ in  v_.items():
                        if v1_ in [1]:
                            str1 += '(' + k_ + ',' + k1_ + ')' + ' '
                print(str1+';', file=text_file)
                str1 = 'set remain1 := ' 
                for k_, v_ in self.loadable.info['mode'].items():
                    for k1_, v1_ in  v_.items():
                        if v1_ in [3]:
                            str1 += '(' + k_ + ',' + k1_ + ')' + ' '
                print(str1+';', file=text_file)
                
                
             
                print('# loading ports',file=text_file)#  
                str1 = 'set loadPort  := ' 
                # for i_, j_ in self.loadable['toLoadPort1'].items():
                #     str1 += str(i_) + ' '
                print(str1+';', file=text_file)
                
                str1 = 'param loadingPortAmt  := ' 
                # for i_, j_ in self.loadable['toLoadPort1'].items():
                #     str1 += str(i_)  + ' ' +  "{:.1f}".format(int(j_*10)/10)  + ' '
                print(str1+';', file=text_file)
                
                print('# discharge ports',file=text_file)#  
                str1 = 'set dischargePort  := ' 
                for i_ in self.loadable.info['toDischargePort2']:
                    str1 += str(i_) + ' '
                print(str1+';', file=text_file)
                
                str1 = 'param dischargePortAmt  := ' 
                for i_, j_ in self.loadable.info['toDischargePort1'].items():
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
                for i_, j_ in self.vessel.info['onboard'].items():
                    if i_ not in ['totalWeight']:
                        str1 += i_ + ' ' +  "{:.3f}".format(j_['wt'])  + ' '
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
                        if k__ not in ['0']:
                            str1 += k__ + ' ' + "{:.3f}".format(v__) + ' '
                    print(str1, file=text_file)
                print(';', file=text_file)  
                        
                
                str1 = 'set fixBallastPort := '
                # for k_ in self.loadable.info['fixedBallastPort']:
                #     if k_ != '0':
                #         str1 += k_ + ' ' 
                print(str1+';', file=text_file)
            
                str1 = 'param trim_upper := '
                for k_, v_ in self.trim_upper.items():
                    str1 += k_ + ' ' + "{:.3f}".format(v_) + ' '
                print(str1+';', file=text_file)
                
                str1 = 'param trim_lower := '
                for k_, v_ in self.trim_lower.items():
                    str1 += k_ + ' ' + "{:.3f}".format(v_) + ' '
                print(str1+';', file=text_file)
                
                if ave_trim:
                    print('# ave trim', file=text_file)
                    str1 = 'param ave_trim := '
                    for i_, j_ in ave_trim.items():
                        str1 += str(i_) + ' ' +  "{:.2f}".format(j_) + ' '
                    print(str1+';', file=text_file)
                
                elif self.ave_trim:
                    str1 = 'param ave_trim := '
                    for k_, v_ in self.ave_trim.items():
                        str1 += k_ + ' ' + "{:.3f}".format(v_) + ' '
                    print(str1+';', file=text_file)
                
                if drop_BM:
                    str1 = 'set P_bm := '
                    for k_, v_ in self.ave_trim.items():
                        str1 += k_ + ' ' 
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
                        if k_ not in ['1A']:
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
                    
                    if not port_ballast_ban:
                        print('# ballast tanks which can be ballast or deballast anytime',file=text_file)#  
                        str1 = 'set P_ban :='
                        for k_ in range(1,len(self.port.info['portOrder'])+1):
                            str1 += self.loadable.info["arrDepVirtualPort"][str(k_)+'D']+ ' '
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
                for p_ in range(1,self.loadable.info['lastVirtualPort']+1):
                    port_ = self.loadable.info['virtualArrDepPort'][str(p_)][:-1]
                    portName_ = self.port.info['portOrder'][port_] # convert virtual port to exact port
                    density_ = self.port.info['portRotation'][portName_]['seawaterDensity']
                    str1 += str(p_) + ' ' + "{:.4f}".format(density_)  + ' '
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
                
                print('# ballast percent ',file=text_file)#
                str1 = 'param ballastPercent := ' + "{:.4f}".format(self.ballast_percent) 
                print(str1+';', file=text_file)
                
                
                
                print('# initial ballast ',file=text_file)#
                str1 = 'param initBallast := '
                for k_, v_ in self.vessel.info['initBallast']['wt'].items():
                    if k_ not in self.vessel.info['banBallast']:
                        str1 += str(k_) + ' ' + "{:.4f}".format(v_)  + ' '
                print(str1+';', file=text_file)
                
                print('# inc initial ballast ',file=text_file)#
                str1 = 'set incTB := '
                for k_ in self.vessel.info['initBallast']['inc']:
                    str1 += str(k_) + ' '
                print(str1+';', file=text_file)
                
                print('# dec initial ballast ',file=text_file)#
                str1 = 'set decTB := '
                for k_ in self.vessel.info['initBallast']['dec']:
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
                
                
                print('# departure arrival ports non-empty and empty ROB',file=text_file) # same weight
                depArrPort2, same_ballast = [], []
                str1 = 'set depArrPort2 := '
                for (a_, b_) in self.vessel.info['sameROB']:
                    # if int(b_) < self.loadable.info['lastVirtualPort']-1:
                        str1 += '('+ str(a_)  + ',' + str(b_) + ') '
                        depArrPort2.append((a_,b_))
                        same_ballast.append(b_)
                print(str1+';', file=text_file)
                
                str1 = 'set depArrPort1 := '
                # for k__, k_  in enumerate(self.vessel.info['loading']): # same tank
                #     if k__ < len(self.vessel.info['loading'])-1:
                #         if (str(k_), str(k_+1)) not in depArrPort2:
                #             str1 += '('+ str(k_)  + ',' + str(int(k_)+1) + ') '
                print(str1+';', file=text_file)
                
                str1 = 'set sameBallastPort := '
                for k__, k_  in  enumerate(same_ballast):
                    str1 += k_ + ' '
                print(str1+';', file=text_file)
                
                
                # print('# rotating ports ',file=text_file)#
                str1 = 'set rotatingPort1 := '
                for k_  in range(0, self.loadable.info['lastVirtualPort']):
                    p_ = (str(k_), str(k_+1))
                    if p_ not in self.vessel.info.get('draftRestriction', []):
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
                
                ##
                print('# ballastBan ',file=text_file)#
                str1 = 'set ballastBan := '
                for k_  in self.config['ban_ballast_discharge']:
                    str1 +=  str(k_)  + ' ' 
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
                
                str1 = 'set slopP := '
                slopP = [t_ for t_ in self.vessel.info['slopTank'] if t_[-1] == 'P']
                str1 += slopP[0]
                print(str1+';', file=text_file) 
                
                str1 = 'set slopS := '
                slopS = [t_ for t_ in self.vessel.info['slopTank'] if t_[-1] == 'S']
                str1 += slopS[0]
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
                    for k1_,v1_ in self.loadable.info['virtualArrDepPort'].items():
                        if v1_ != '1A':
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
                        if k_ not in ['1A']:
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
                        if k_ not in ['1A']:
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
                #str1 = 'param deadweight   := ' + str(self.vessel.info['draftCondition']['deadweight']) 
                str1 = 'param deadweight   := ' + str(1000000) 
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
                
                # print('# runtime limit ',file=text_file)#  
                # if self.config['loadableConfig']:
                #     str1 = 'param runtimeLimit := ' + str(self.config['loadableConfig']['timeLimit'])
                # else:
                #     str1 = 'param runtimeLimit := ' + str(self.config.get('timeLimit', 60))
                # print(str1+';', file=text_file)
                
                
             
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
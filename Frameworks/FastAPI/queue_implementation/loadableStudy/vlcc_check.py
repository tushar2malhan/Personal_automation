# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 14:50:33 2020

@author: I2R
"""
import numpy as np
import json
import pandas as pd
from vlcc_gen import Generate_plan
# from api_vlcc import manual_mode
# from vlcc_init import Process_input
# from vlcc_ullage import get_correction
from scipy.interpolate import interp1d

DEC_PLACE = 3


class Check_plans:
    def __init__(self, inputs, reballast = True, indx = None):
#        self.outfile   = 'resmsg.json'
        self.input = inputs
        self.stability_values = []
        # self.outputs = outputs
        self.reballast = reballast
        self.index = indx # index plan
        
        self.replan = True
        self.tide_func = None
        if hasattr(self.input, 'tide_info') and self.input.tide_info:
            if 'time' in self.input.tide_info:
                self.tide_func = interp1d(self.input.tide_info['time'], self.input.tide_info['tide'])

    def _check_plans(self, outputs):
        
        plans, cargo_tank = outputs.plans.get('ship_status',[]), outputs.plans.get('cargo_tank',[])
        
        if not self.input.error:
            
            if self.input.module in ['LOADING']:
                print(self.input.loading.seq['stages'])
            elif self.input.module in ['LOADABLE', 'DISCHARGE']:
                print('port:', self.input.port.info.get('portOrder',[]))
                print('sea density', self.input.loadable.info.get('seawaterDensity',[]))
                print('same ROB', self.input.vessel.info['sameROB'])
                print(self.input.vessel.info['changeROB'])
        
            if hasattr(self.input, 'base_draft'):
                print(self.input.base_draft)
                
            if self.index not in [None]:
                print('Check only:', self.index)
                plans = [plans[self.index]]
                cargo_tank = [cargo_tank[self.index]]
                
            for p__, p_ in enumerate(plans):
                print('plan:', p__, '---------------------------------------------------------------------------------------------')            
                stability_ = {}
                if len(cargo_tank) > 0:
                    for a_, b_ in cargo_tank[p__].items():
                        print(a_,b_)
                for k_, v_ in p_.items(): # each port
                    plan_ = {**v_['cargo'], **v_['ballast'], **v_['other']}
                    
                    
                    if self.input.module in ['LOADABLE', 'DISCHARGE', "ULLAGE"]: #hasattr(self.input.loadable, "info"):
                        seawater_density_ = self.input.loadable.info['seawaterDensity'][k_]
                    else:
                        seawater_density_ = self.input.seawater_density
                    
                    
                    result = self._check_plan(plan_, k_, seawater_density=seawater_density_)
                    
                    print('Port: ',k_,'Cargo:', round(result['wt']['cargoTanks'],DEC_PLACE), 'Ballast:', round(result['wt']['ballastTanks'],DEC_PLACE), 'Displacement:', round(result['disp'],DEC_PLACE), 'tcg_moment:', round(result['tcg_mom'],DEC_PLACE), 'Mean Draft:', round(result['dm'],4), 'Trim:', round(result['trim'],5))
                    print('frame:', result.get('maxBM',['NA','NA'])[0], 'BM:', result.get('maxBM',['NA','NA'])[1],'frame:', result.get('maxSF',['NA','NA'])[0], 'SF:', result.get('maxSF',['NA','NA'])[1])
                    print('da:', round(result.get('da', 0),4), 'dc:', round(result.get('dc', 0),4), 'df:', round(result.get('df', 0),4), 'ukc:', round(result['UKC'],3))
                    stability_[k_] = {'forwardDraft': "{:.2f}".format(result['df']), 
                                      'meanDraft': "{:.2f}".format(result['dm']),
                                      'afterDraft': "{:.2f}".format(result['da']),
                                      'trim': "{:.2f}".format(0.00 if round(result['trim'],2) == 0 else result['trim']),
                                      'heel': None,
                                      'gom': None,
                                      'airDraft': "{:.2f}".format(result['airDraft']),
                                      'freeboard':"{:.2f}".format(result['freeboard']),
                                      'manifoldHeight':"{:.2f}".format(result['manifoldHeight']),
                                      'bendinMoment': "{:.2f}".format(result.get('maxBM',[None, 10000])[1]),
                                      'shearForce':  "{:.2f}".format(result.get('maxSF',[None, 10000])[1]),
                                      'sdraft': "{:.2f}".format(result['sdraft']),
                                      'UKC': "{:.2f}".format(result['UKC']),
                                      'displacement': "{:.2f}".format(result['displacement']),
                                      'empty': result['empty'],
                                      'cargo': str(round(result['wt']['cargoTanks'],1))
                                      }
                    
                    # update correction ullage
                    trim_ = round(result['trim'],2)
                    
                    for a_, b_ in plans[p__][k_]['cargo'].items():
                        tankId_ = self.input.vessel.info['tankName'][a_]
                        if str(tankId_) in self.input.vessel.info['ullageCorr'].keys():
                            cf_ = self._get_correction(str(tankId_), b_[0]['corrUllage'], min(5.99,trim_))
                            rdgUllage_ = b_[0]['corrUllage'] - cf_/100 if cf_ not in [None] else ""
                            plans[p__][k_]['cargo'][a_][0]['correctionFactor'] = round(cf_/100,3) if cf_ not in [None] else ""
                            plans[p__][k_]['cargo'][a_][0]['rdgUllage'] = round(rdgUllage_,7) if cf_ not in [None] else ""
                            
                        else:
                            # print(str(tankId_), a_, 'Missing correction data!!')
                            plans[p__][k_]['cargo'][a_][0]['correctionFactor'] = ""
                            plans[p__][k_]['cargo'][a_][0]['rdgUllage'] = ""
                            
                        
                    for a_, b_ in plans[p__][k_]['ballast'].items():
                        tankId_ = self.input.vessel.info['tankName'][a_]
                        if str(tankId_) in self.input.vessel.info['ullageCorr'].keys():
                            # print(b_[0].keys())
                            cf_ = self._get_correction(str(tankId_), b_[0]['corrLevel'], min(5.99,trim_))
                            rdgLevel_ = b_[0]['corrLevel'] - cf_/100 if cf_ not in [None] else ""
                            
                            plans[p__][k_]['ballast'][a_][0]['correctionFactor'] = round(cf_/100,3) if cf_ not in [None] else ""
                            plans[p__][k_]['ballast'][a_][0]['rdgLevel'] = round(rdgLevel_,6) if cf_ not in [None] else ""
                            
                            # print(tankId_, cf_, rdgLevel_)
                            
                        else:
                            # print(str(tankId_), a_, 'Missing correction data!!')
                            plans[p__][k_]['ballast'][a_][0]['correctionFactor'] = ""
                            plans[p__][k_]['ballast'][a_][0]['rdgLevel'] = ""
                
                # check BM                                
                if self.input.module in ['DISCHARGING'] and self.reballast:
                    fail_bm_, base_draft_, ave_trim_, mean_draft_ = False, {}, {}, {}
                    for q_ in range(1, self.input.loadable.info['lastVirtualPort'] + 1):
                        bm_ = float(stability_[str(q_)]['bendinMoment'])
                        base_draft_[str(q_)] = int(float(stability_[str(q_)]['afterDraft']))
                        mean_draft_[str(q_)] = float(stability_[str(q_)]['meanDraft'])
                        ave_trim_[str(q_)] = min(float(stability_[str(q_)]['trim']), 5.9)
                        # base_draft_[str(q_)] = int(float(stability_[str(q_)]['sdraft']))
                        # if self.input.trim_lower.get(str(q_), 0.) < 4.:
                        #     ave_trim_[str(q_)] = min(float(stability_[str(q_)]['trim']), 5.5)
                        # else:
                        #     ave_trim_[str(q_)] = 0.5*(self.input.trim_lower.get(str(q_), 0.) + self.input.trim_upper.get(str(q_), 0.))
                            
                        if bm_ > self.input.sf_bm_frac*100 or bm_ < -self.input.sf_bm_frac*100:
                            fail_bm_ = True
                            print('port:', q_, bm_, ' failed BM check!!')
                            
                    if fail_bm_:
                        ## check with 
                        set_trim_ = self.input.set_trim_mode.get('mode', 0)
                        self.input.get_param(base_draft = base_draft_, ave_trim = ave_trim_, set_trim = set_trim_, mean_draft = mean_draft_)
                        if outputs.opt_mode == 0:
                            self.input.write_ampl(IIS = False, ave_trim = ave_trim_, mean_draft = mean_draft_, run_time = outputs.run_time)
                            
                        elif outputs.opt_mode == 1:
                            self.input.write_ampl(incDec_ballast = ['APT'], IIS = False, ave_trim = ave_trim_, mean_draft = mean_draft_, run_time = outputs.run_time) # relax list mom to 100000
                            
                        elif outputs.opt_mode == 2:
                            if self.input.vessel_id in [1, '1']:
                                 self.input.write_ampl(incDec_ballast = ['APT', 'AWBP', 'AWBS'], IIS = False, ave_trim = ave_trim_, mean_draft = mean_draft_, run_time = outputs.run_time) # relax list mom to 100000
                            elif self.input.vessel_id in [2, '2']:
                                 self.input.write_ampl(incDec_ballast = ['APT'], IIS = False, ave_trim = ave_trim_, mean_draft = mean_draft_, run_time = outputs.run_time) # relax list mom to 100000

                            
                        else:
                            print('No reballasting!!')
                            
#                        input("Press Enter to continue...")    
                            
                        if outputs.opt_mode in [0,1,2]:                    
                            # collect plan from AMPL
                            gen_output_ = Generate_plan(self.input)
                            gen_output_.run(num_plans=1, reballast = True)
                            
                            replan_, restability_ = self._check_reballast_plans(gen_output_)
                            
                            self.replan = replan_
                            if replan_:
                                print('Replaced plan:', p__)
                                
                                stability_ = restability_[0]
                                for name_ in ['cargo_status', 'operation', 'obj', 'ship_status', 'cargo_tank', 'slop_qty']:
                                    outputs.plans[name_][0] = gen_output_.plans[name_][0]
                                    
                                outputs.ballast_weight = gen_output_.ballast_weight
                           
                    
                elif self.input.module in ['LOADING'] and self.reballast:
                    fail_bm_, base_draft_, ave_trim_ = False, {}, {}
                    for q_ in range(1, self.input.loadable['lastVirtualPort'] + 1):
                        bm_ = float(stability_[str(q_)]['bendinMoment'])
                        # base_draft_[str(q_)] = int(float(stability_[str(q_)]['afterDraft']))
                        # base_draft_[str(q_)] = int(float(stability_[str(q_)]['sdraft']))
                        ave_trim_[str(q_)] = float(stability_[str(q_)]['trim'])
                        if bm_ > self.input.sf_bm_frac*100 or bm_ < -self.input.sf_bm_frac*100:
                            fail_bm_ = True
                            print('port:', q_, bm_, ' failed BM check!!')
                            
                    if fail_bm_:
                        
                        ## check with 
                        if outputs.opt_mode == 0:
                            self.input.get_param(base_draft = base_draft_)
                            self.input.write_ampl(IIS = False, ave_trim = ave_trim_)
                            
                        elif outputs.opt_mode == 1:    
                            print('Relax intermitted trim ...')
                            self.input.get_param(min_int_trim = 0.5, max_int_trim = 1.5, base_draft = base_draft_)
                            self.input.write_ampl(IIS = False, ave_trim = ave_trim_)
                            
                        elif outputs.opt_mode == 2: 
                            self.input.get_param(base_draft = base_draft_)
                            self.input.write_ampl(incDec_ballast = ['APT'], IIS = False, ave_trim = ave_trim_) # 
                            
                        elif outputs.opt_mode == 3: 
                            self.input.get_param(base_draft = base_draft_)
                            if self.input.vessel_id in [1]:
                                self.input.write_ampl(incDec_ballast = ['LFPT'], IIS = False, ave_trim = ave_trim_) # 
                            elif self.input.vessel_id in [2]:
                                self.input.write_ampl(incDec_ballast = ['FPT'], IIS = False, ave_trim = ave_trim_) #
                                
                        elif outputs.opt_mode == 4:
                            self.input.get_param(base_draft = base_draft_)
                            self.input.write_ampl(incDec_ballast = ['AWBP'], IIS = False, ave_trim = ave_trim_) # 
                        
                        elif outputs.opt_mode == 5:
                            self.input.get_param(base_draft = base_draft_)
                            self.input.write_ampl(incDec_ballast = ['AWBS'], IIS = False, ave_trim = ave_trim_) # 
   
                            
                        if outputs.opt_mode in [0, 1, 2, 3, 4, 5]:                    
                            # collect plan from AMPL
                            gen_output_ = Generate_plan(self.input)
                            gen_output_.run(num_plans=1, reballast = True)
                            
                            replan_, restability_ = self._check_reballast_plans(gen_output_)
                            if replan_:
                                print('Replaced plan:', p__)
                                
                                stability_ = restability_[0]
                                for name_ in ['cargo_status', 'operation', 'obj', 'ship_status', 'cargo_tank', 'slop_qty']:
                                    outputs.plans[name_][0] = gen_output_.plans[name_][0]
                                    
                                outputs.ballast_weight = gen_output_.ballast_weight


                        # input("Press Enter to continue...")
                        
                # check trim
                elif self.input.module in ['LOADABLE'] and self.reballast:
                    for q_ in  self.input.vessel.info['loading'] + [self.input.loadable.info['lastVirtualPort']-1]:
                        trim__  = round(float(stability_[str(q_)]['trim']),2)
                        if round(self.input.trim_lower.get(str(q_), -0.01),2) == 0:
                            lower_limit_ = -0.01
                        else:
                            lower_limit_ = round(self.input.trim_lower.get(str(q_), -0.01),2)-0.01
                            
                        if round(self.input.trim_upper.get(str(q_), 0.01),2) == 0:
                            upper_limit_ = 0.01
                        else:
                            upper_limit_ = round(self.input.trim_upper.get(str(q_), 0.01),2)+0.01
                        
                        if (trim__ > upper_limit_ or trim__ < lower_limit_) :
                            print('Rebalancing needed:', q_, trim__, lower_limit_, upper_limit_)
                            # input("Press Enter to continue...")
                             
                            cur_plan_ = {'constraint':[], "message":[], "rotation":[[]]}
                            for kk_ in ['ship_status', 'obj', 'operation', 'cargo_status', 'slop_qty', 'cargo_order', 'loading_hrs', 'topping', 'loading_rate', 'cargo_tank']:
                                cur_plan_[kk_] = [outputs.plans[kk_][p__]]
                                
                            # get lcg
                            lcg_port_, qw_ = {}, {}
                            for i_, j_ in cur_plan_['ship_status'][0].items():
                                # print(i_, j_)
                                lcg_port_[i_] = {}
                                for i1_, j1_ in j_['cargo'].items():
                                    lcg_port_[i_][i1_] = j1_[0]['lcg']
                                    
                            qw_ =  cur_plan_['ship_status'][0][str(self.input.loadable.info['lastVirtualPort']-1)]['cargo']
                            
                            self.input.write_dat_file(lcg_port = lcg_port_, weight = qw_)
                            
                            # collect plan from AMPL
                            gen_output_ = Generate_plan(self.input)
                            gen_output_.run(num_plans=1)
                            
                            replan_, restability_ = self._check_reballast_plans(gen_output_)
                            if replan_:
                                print('Replaced plan:', p__)
                                
                                stability_ = restability_[0]
                                
                                if self.index not in [None]:
                                    
                                    for name_ in ['cargo_status', 'operation', 'cargo_tank', 'slop_qty', 'topping', 'loading_rate', 'loading_hrs']:
                                        outputs.plans[name_][self.index] = gen_output_.plans[name_][0]
                                        
                                    outputs.plans['ship_status'][self.index] = replan_[0]
                                    outputs.ballast_weight[self.index] = gen_output_.ballast_weight[0]
                                    
                                else:
                                   for name_ in ['cargo_status', 'operation', 'cargo_tank', 'slop_qty', 'topping', 'loading_rate', 'loading_hrs']:
                                        outputs.plans[name_][p__] = gen_output_.plans[name_][0]
                                   
                                   outputs.plans['ship_status'][p__] = replan_[0]
                                   outputs.ballast_weight[0] = gen_output_.ballast_weight[0]
                                
                                
                            # input("Press Enter to continue...")
                            break
                        
                elif self.input.module in ['DISCHARGE'] and self.reballast:
                    
                    for q_ in  self.input.loadable.info['toDischargePort2']: #[*self.input.loadable.info['toDischargePort1']]:
                        trim__  = round(float(stability_[str(q_)]['trim']),2)
                        
                        if round(self.input.trim_lower.get(str(q_), -0.01),2) == 0:
                            lower_limit_ = -0.01
                        elif round(self.input.trim_lower.get(str(q_), 0.01),2) == 0.5:
                            lower_limit_ = 0.45
                        else:
                            lower_limit_ = round(self.input.trim_lower.get(str(q_), -0.01),2)
                            
                        if round(self.input.trim_upper.get(str(q_), 0.01),2) == 0:
                            upper_limit_ = 0.01
                        elif round(self.input.trim_upper.get(str(q_), 0.01),2) == 2.95:
                            upper_limit_ = 2.97
                        else:
                            upper_limit_ = round(self.input.trim_upper.get(str(q_), 0.01),2)
                            
                            
                        # print(q_, lower_limit_,upper_limit_)

                        fail_bm_, base_draft_, ave_trim_, mean_draft_ = False, {}, {}, {}
                        for qq_ in range(1, self.input.loadable.info['lastVirtualPort'] + 1):
                            bm_ = float(stability_[str(qq_)]['bendinMoment'])
                            base_draft_[str(qq_)] = int(float(stability_[str(qq_)]['afterDraft']))
                            # base_draft_[str(q_)] = int(float(stability_[str(q_)]['sdraft']))
                            # if self.input.trim_lower.get(str(q_), 0.) < 4.:
                            ave_trim_[str(qq_)] = min(float(stability_[str(qq_)]['trim']), 5.95)
                            mean_draft_[str(qq_)] = int(float(stability_[str(qq_)]['meanDraft']))
                            # else:
                            #     ave_trim_[str(q_)] = 0.5*(self.input.trim_lower.get(str(q_), 0.) + self.input.trim_upper.get(str(q_), 0.))
                                
                            if bm_ > self.input.sf_bm_frac*100 or bm_ < -self.input.sf_bm_frac*100:
                                fail_bm_ = True
                                print('port:', qq_, bm_, ' failed BM check!!')
                        
                        if (trim__ > upper_limit_ or trim__ < lower_limit_) or fail_bm_:
                            print('Rebalancing needed:', q_, "trim::", trim__, "(", lower_limit_, upper_limit_, ")")
                            # input("Press Enter to continue...")
                            
                            cur_plan_ = {'constraint':[], "message":[], "rotation":[[]]}
                            for kk_ in ['ship_status', 'obj', 'operation', 'cargo_status', 'slop_qty', 'cargo_order', 'loading_hrs', 'topping', 'loading_rate', 'cargo_tank']:
                                # print(kk_)
                                cur_plan_[kk_] = [outputs.plans[kk_][p__]] if len(outputs.plans[kk_]) > 0 else []
                                
                            # get lcg
                            lcg_port_, qw_ = {}, {}
                            for i_, j_ in cur_plan_['ship_status'][0].items():
                                # print(i_, j_)
                                lcg_port_[i_] = {}
                                for i1_, j1_ in j_['cargo'].items():
                                    lcg_port_[i_][i1_] = j1_[0]['lcg']
                                    
                            qw_ = {}
                            for qq_ in  self.input.loadable.info['toDischargePort2']:
                                qw_[qq_] =  cur_plan_['ship_status'][0][str(qq_)]['cargo']
                            
                            self.input.lcg_port, self.input.weight = lcg_port_, qw_
                            
                            if outputs.opt_mode in [0,1]:
                                # self.input.write_dat_file(lcg_port = lcg_port_, weight = qw_, IIS = False)
                                self.input.get_stability_param(base_draft = base_draft_, set_trim = self.input.set_trim_mode['mode'])
                                self.input.write_dat_file(lcg_port = lcg_port_, weight = qw_, IIS = False, ave_trim = ave_trim_)
                                
                            elif outputs.opt_mode in [2]:
                                # self.input.write_dat_file(lcg_port = lcg_port_, weight = qw_, IIS = False)
                                self.input.get_stability_param(reduce_disp_limit = 2000, base_draft = base_draft_, set_trim = self.input.set_trim_mode['mode'])
                                self.input.write_dat_file(lcg_port = lcg_port_, weight = qw_, IIS = False, ave_trim = ave_trim_)
                            
                            elif outputs.opt_mode in [3]:
                                # self.input.write_dat_file(lcg_port = lcg_port_, weight = qw_, IIS = False)
                                self.input.get_stability_param(reduce_disp_limit = 2000, set_trim = self.input.set_trim_mode['mode'], base_draft = base_draft_)
                            
                                if self.input.vessel_id in [1,'1']: # ['APT', 'AWBP', 'AWBS']
                                    self.input.write_dat_file(IIS = False,incDec_ballast = ['APT'],
                                                              lcg_port = self.input.lcg_port, weight = self.input.weight, port_ballast_ban = False,  ave_trim = ave_trim_) # relax list mom to 100000
                                elif self.input.vessel_id in [2,'2']:
                                    self.input.write_dat_file(IIS = False,incDec_ballast = ['FPT'],
                                                              lcg_port = self.input.lcg_port, weight = self.input.weight,  ave_trim = ave_trim_) # relax list mom to 100000
                        
                            
                            elif outputs.opt_mode == 4:
                                self.input.get_stability_param(reduce_disp_limit = 2000, set_trim = self.input.set_trim_mode['mode'], base_draft = base_draft_)
                            
                                if self.input.vessel_id in [1,'1']: # ['APT', 'AWBP', 'AWBS']
                                    self.input.write_dat_file(IIS = False,incDec_ballast = ['APT', 'AWBP', 'AWBS'],
                                                              lcg_port = self.input.lcg_port, weight = self.input.weight, port_ballast_ban = False,  ave_trim = ave_trim_) # relax list mom to 100000
                                elif self.input.vessel_id in [2,'2']:
                                    self.input.write_dat_file(IIS = False,incDec_ballast = ['FPT'],
                                                              lcg_port = self.input.lcg_port, weight = self.input.weight,  ave_trim = ave_trim_) # relax list mom to 100000
                        

#                            input("Press Enter to continue...")
                             # collect plan from AMPL
                            gen_output_ = Generate_plan(self.input)
                            gen_output_.run(num_plans=1, reballast = True)

                            replan_, restability_ = self._check_reballast_plans(gen_output_)
                            if replan_:
                                print('Replaced plan:', p__)
                                
                                stability_ = restability_[0]
                                
                                if self.index not in [None]:
                                    
                                    for name_ in ['cargo_status', 'operation', 'cargo_tank', 'slop_qty', 'topping', 'loading_rate', 'loading_hrs']:
                                        outputs.plans[name_][self.index] = gen_output_.plans[name_][0]
                                        
                                    outputs.plans['ship_status'][self.index] = replan_[0]
                                    outputs.ballast_weight[self.index] = gen_output_.ballast_weight[0]
                                    
                                else:
                                   for name_ in ['cargo_status', 'operation', 'cargo_tank', 'slop_qty', 'topping', 'loading_rate', 'loading_hrs']:
                                       if  len(outputs.plans[name_]) > 0:
                                           outputs.plans[name_][p__] = gen_output_.plans[name_][0] if len(gen_output_.plans[name_]) > 0 else []
                                   
                                   outputs.plans['ship_status'][p__] = replan_[0]
                                   outputs.ballast_weight[0] = gen_output_.ballast_weight[0]
                                
                            # input("Press Enter to continue...")
                            break
                             
                        
                self.stability_values.append(stability_)
                
            with open('ship_status.json', 'w') as fp:
                json.dump(plans, fp)     
            
                
    def _get_correction(self, tank, ullage, trim):
        
       
        # out = 0
        data = self.input.vessel.info['ullageCorr'][tank]
        data = pd.DataFrame(data,  dtype=np.float, columns=[ 'id', 'tankId', 'ullageDepth', 'trimM1', 'trim0', 'trim1', 'trim2', 'trim3', 'trim4', 'trim5', 'trim6'])
        # print(tank, ullage , trim)
        ullage_range = data['ullageDepth'].to_numpy()
        if trim < -1 or trim > 6 or ullage < ullage_range[0] or ullage > ullage_range[-1]:
            # print(self.input.vessel.info['tankId'][int(tank)], ullage, trim, ullage_range[0], ullage_range[-1])
            #return None
            return 0.
        
        a_ = np.where(data['ullageDepth'] <= ullage)[0][-1]     
          # b_ = np.where(data['ullageDepth'] >= ullage)[0][0]
        
        trim_range = np.array([-1,0,1,2,3,4,5,6])
        a__ = np.where(trim_range <= trim)[0][-1]     
          # b__ = np.where(trim_range >= trim)[0][0]
        
          # ullage x trim
        data_ = data.iloc[a_:a_+2,a__+3:a__+5].to_numpy()
        x_ = ullage_range[a_:a_+2]
        y_ = trim_range[a__:a__+2]
        
        z1_ = [(ullage-x_[0])*(data_[1][0]-data_[0][0])/(x_[1]-x_[0]) + data_[0][0], 
                (ullage-x_[0])*(data_[1][1]-data_[0][1])/(x_[1]-x_[0]) +  data_[0][1]]
        
        
        out = (trim-y_[0])*(z1_[1]-z1_[0])/(y_[1]-y_[0]) + z1_[0]
        
        #  print(x_,y_,data_)
        
        # print(tank, out)
        
        return out
    
                
                
    def _check_reballast_plans(self, outputs):
        
        # self.reballast_input = inputs
        self.reballast_output = outputs
        
        plans, cargo_tank = outputs.plans.get('ship_status',[]), outputs.plans.get('cargo_tank',[])
        stability = []
        
        for p__, p_ in enumerate(plans):
            print('plan:', p__, '---------------------------------------------------------------------------------------------')            
            stability_ = {}
            if len(cargo_tank) > 0:
                for a_, b_ in cargo_tank[p__].items():
                    print(a_,b_)
            for k_, v_ in p_.items(): # each port
                plan_ = {**v_['cargo'], **v_['ballast'], **v_['other']}
                
                
                if self.input.module in ['LOADABLE', 'DISCHARGE', "ULLAGE"]: #hasattr(self.input.loadable, "info"):
                    seawater_density_ = self.input.loadable.info['seawaterDensity'][k_]
                else:
                    seawater_density_ = self.input.seawater_density
                
                
                result = self._check_plan(plan_, k_, seawater_density=seawater_density_)
                
                print('Port: ',k_,'Cargo:', round(result['wt']['cargoTanks'],DEC_PLACE), 'Ballast:', round(result['wt']['ballastTanks'],DEC_PLACE), 'Displacement:', round(result['disp'],DEC_PLACE), 'tcg_moment:', round(result['tcg_mom'],DEC_PLACE), 'Mean Draft:', round(result['dm'],4), 'Trim:', round(result['trim'],5))
                print('frame:', result.get('maxBM',['NA','NA'])[0], 'BM:', result.get('maxBM',['NA','NA'])[1],'frame:', result.get('maxSF',['NA','NA'])[0], 'SF:', result.get('maxSF',['NA','NA'])[1])
                print('da:', round(result.get('da', 0),4), 'dc:', round(result.get('dc', 0),4), 'df:', round(result.get('df', 0),4), 'ukc:', round(result['UKC'],3))
                
                stability_[k_] = {'forwardDraft': "{:.2f}".format(result['df']), 
                                  'meanDraft': "{:.2f}".format(result['dm']),
                                  'afterDraft': "{:.2f}".format(result['da']),
                                  'trim': "{:.2f}".format(0.00 if round(result['trim'],2) == 0 else result['trim']),
                                  'heel': None,
                                  'gom': None,
                                  'airDraft': "{:.2f}".format(result['airDraft']),
                                  'freeboard':"{:.2f}".format(result['freeboard']),
                                  'manifoldHeight':"{:.2f}".format(result['manifoldHeight']),
                                  'bendinMoment': "{:.2f}".format(result.get('maxBM',[None, 10000])[1]),
                                  'shearForce':  "{:.2f}".format(result.get('maxSF',[None, 10000])[1]),
                                  'UKC': "{:.2f}".format(result['UKC']),
                                  'displacement': "{:.2f}".format(result['displacement']),
                                  'empty': result['empty'],
                                  'cargo': str(round(result['wt']['cargoTanks'],1))
                                  }
                
                # update correction ullage
                trim_ = min(5.99, round(result['trim'],2))
                
                for a_, b_ in plans[p__][k_]['cargo'].items():
                    tankId_ = self.input.vessel.info['tankName'][a_]
                    if str(tankId_) in self.input.vessel.info['ullageCorr'].keys():
                        cf_ = self._get_correction(str(tankId_), b_[0]['corrUllage'], trim_)
                        rdgUllage_ = b_[0]['corrUllage'] - cf_/100 if cf_ not in [None] else ""
                        plans[p__][k_]['cargo'][a_][0]['correctionFactor'] = round(cf_/100,3) if cf_ not in [None] else ""
                        plans[p__][k_]['cargo'][a_][0]['rdgUllage'] = round(rdgUllage_,6) if cf_ not in [None] else ""
                        
                    else:
                        # print(str(tankId_), a_, 'Missing correction data!!')
                        plans[p__][k_]['cargo'][a_][0]['correctionFactor'] = ""
                        plans[p__][k_]['cargo'][a_][0]['rdgUllage'] = ""
                        
                    
                for a_, b_ in plans[p__][k_]['ballast'].items():
                    tankId_ = self.input.vessel.info['tankName'][a_]
                    if str(tankId_) in self.input.vessel.info['ullageCorr'].keys():
                        # print(b_[0].keys())
                        cf_ = self._get_correction(str(tankId_), b_[0]['corrLevel'], trim_)
                        rdgLevel_ = b_[0]['corrLevel'] - cf_/100 if cf_ not in [None] else ""
                        
                        plans[p__][k_]['ballast'][a_][0]['correctionFactor'] = round(cf_/100,3) if cf_ not in [None] else ""
                        plans[p__][k_]['ballast'][a_][0]['rdgLevel'] = round(rdgLevel_,6) if cf_ not in [None] else ""
                        
                        # print(tankId_, cf_, rdgLevel_)
                        
                    else:
                        # print(str(tankId_), a_, 'Missing correction data!!')
                        plans[p__][k_]['ballast'][a_][0]['correctionFactor'] = ""
                        plans[p__][k_]['ballast'][a_][0]['rdgLevel'] = ""
                        
                        
            stability.append(stability_) 
                        
        return plans, stability
        
        
        
        
        
        
    def _check_plan(self, plan, virtual_port, seawater_density = 1.025):
#        print(plan)
        # print('seawater_density', seawater_density)
        result = {}
        
        lpp_ = self.input.vessel.info['LPP']
        
        lightweight_lmom_ = self.input.vessel.info['lightweight']['weight']*self.input.vessel.info['lightweight']['lcg']
        lightweight_vmom_ = self.input.vessel.info['lightweight']['weight']*self.input.vessel.info['lightweight']['vcg']
        
        other_lmom_ = self.input.vessel.info['deadweightConst']['weight']*self.input.vessel.info['deadweightConst']['lcg']
        other_vmom_ = self.input.vessel.info['deadweightConst']['weight']*self.input.vessel.info['deadweightConst']['vcg']
        
        
#        print(self.input_param.vessel.info['lightweight']['weight'], self.input_param.vessel.info['lightweight']['vcg'])
#        print(self.input_param.vessel.info['deadweight_const']['weight'], self.input_param.vessel.info['deadweight_const']['vcg'])
        
        total_ = {'cargoTanks':0, 'ballastTanks':0, 'fuelTanks':0, 'dieselTanks':0, 'freshWaterTanks':0}
        l_mom_ = lightweight_lmom_ + other_lmom_
        v_mom_ = lightweight_vmom_ + other_vmom_
        
        t_mom_ = 0.
        disp_ = self.input.vessel.info['lightweight']['weight'] + self.input.vessel.info['deadweightConst']['weight']

        for k_, v_ in plan.items():
            # print(k_,v_)
            
            type_ = self.input.vessel.info['category'][k_]
           
            if type_ not in ['cargoTanks'] or (type_ in ['cargoTanks'] and v_[0]['parcel'] not in [None]):
            
                # l_mom_ += v_[0]['wt']*self.input.vessel.info[type_][k_]['lcg']
                l_mom_ += v_[0]['wt']*v_[0]['lcg']
                v_mom_ += v_[0]['wt']*self.input.vessel.info[type_][k_]['vcg']
                t_mom_ += v_[0]['wt']*v_[0]['tcg']
                
                
                # if type_ in ['ballastTanks','cargoTanks']: # and abs(self.input.vessel.info[type_][k_]['lcg'] - v_[0]['lcg']) > 0.01:
                #     print(k_, self.input.vessel.info[type_][k_]['lcg'], v_[0]['lcg'], v_[0].get('wt',0), v_[0]['fillRatio'])
                # print(k_, v_[0]['wt'], v_[0]['tcg'], v_[0]['wt']*v_[0]['tcg'])
                # print(k_, v_[0]['wt'], v_[0]['lcg'], v_[0]['wt']*v_[0]['lcg'])
                
                # print(k_, v_[0]['wt'], v_[0]['lcg'], v_[0]['tcg'])
                
                # print(k_, v_[0]['wt'], self.input.vessel.info[type_][k_]['lcg'], v_[0]['wt']*self.input.vessel.info[type_][k_]['lcg'])
                
                total_[type_] +=  v_[0]['wt']
                disp_ += v_[0]['wt']
                
        empty_ = False
        for k_, v_ in self.input.vessel.info['cargoTanks'].items():
            fill_ratio_ = plan.get(k_,[{}])[0].get('fillRatio', 0.)
            if fill_ratio_ in [None] or fill_ratio_ < 0.98:
                # print('Empty tank (< 0.98):', k_)
                empty_ = True
                
                    
        # print(l_mom_)        
        result['disp'] =  disp_
        result['wt'] = total_
        result['tcg_mom'] = t_mom_
        result['displacement'] = disp_
        result['empty'] = empty_
#        print(disp_,cargo_total_,fuel_total_, diesel_total_, fresh_total_)
#        print(l_mom_,v_mom_)
        
#        l_mom_,v_mom_ = -3802896, 5744799

        disp1_ = disp_*1.025/seawater_density

        draft_ = np.interp(disp1_, self.input.vessel.info['hydrostatic']['displacement'], self.input.vessel.info['hydrostatic']['draft'])
        mtc_   = np.interp(disp1_, self.input.vessel.info['hydrostatic']['displacement'], self.input.vessel.info['hydrostatic']['mtc'])
        lcb_ = np.interp(disp1_, self.input.vessel.info['hydrostatic']['displacement'], self.input.vessel.info['hydrostatic']['lcb'])
        lcf_   = np.interp(disp1_, self.input.vessel.info['hydrostatic']['displacement'], self.input.vessel.info['hydrostatic']['lcf'])
        # mid.f = lcf; mid.b = lcb
        # print(draft_,mtc_,lcb_,lcf_)
        lcg_ = l_mom_/ disp_
        bg_ = lcg_ - lcb_
        trim_ = bg_*disp_/mtc_/100
        
        # print(disp_, lcb_, mtc_, trim_)
        
        df_ = draft_ -  (0.5*lpp_ + lcf_)/lpp_*trim_
        da_ = df_ + trim_
        dm_ = (df_ + da_)/2
#        print("{:.2f}".format(trim_),"{:.2f}".format(df_),"{:.2f}".format(da_),"{:.2f}".format(dm_))
        result['trim'] = trim_
        result['df'] = df_
        result['da'] = da_
        result['dm'] = dm_
        result['dc'] = draft_
        
        # print(da_,df_)
        km_ = np.interp(disp_, self.input.vessel.info['hydrostatic']['displacement'], self.input.vessel.info['hydrostatic']['tkm'])
        kg_ = v_mom_/disp_
        gm_ = km_ - kg_
#        print(km_,gm_)
        
        result['km'] = km_
        result['gm'] = gm_
        
        depth_ = 99
        if self.input.module in ['DISCHARGING'] and hasattr(self.input, 'discharging'):
            
            if virtual_port in ['0']:
                time_ = self.input.start_time + self.input.initial_delay
            else:
                time_ = self.input.start_time + self.input.discharging.seq['times'][int(virtual_port)-1]
                
            tide_ = 0    
            if self.tide_func:
                if  min(self.input.tide_info['time']) <= time_ <= max(self.input.tide_info['time']):
                    tide_ = float(self.tide_func(time_))
                    
            depth_ = self.input.tide_info.get('depth', 99)
            print('depth', depth_, 'tide', tide_, "time", time_)
            
        elif self.input.module in ['LOADABLE']:
            # air draft
            port_order_ =  self.input.loadable.info['virtualArrDepPort'][virtual_port][:-1]
            origin_port_ = self.input.port.info['portOrder'][port_order_]
            tide_ = self.input.port.info['portRotation'][origin_port_]['tideHeight']
            
        elif self.input.module in ['LOADING']:
            if virtual_port in ['0']:
                time_ = self.input.start_time + self.input.initial_delay
            else:
                time_ = self.input.start_time + self.input.loading.seq['times'][int(virtual_port)-1]
                
            tide_ = 0    
            if self.tide_func:
                if  min(self.input.tide_info['time']) <= time_ <= max(self.input.tide_info['time']):
                    tide_ = float(self.tide_func(time_))
                    
            depth_ = self.input.tide_info.get('depth', 99)
            print('depth', depth_, 'tide', tide_, "time", time_)
                
        elif self.input.module in ['DISCHARGE', 'DISCHARGING']:

            tide_ = 0.
        elif self.input.module in ["ULLAGE"]:
            tide_ = self.input.port.info['tide']
            depth_ = self.input.port.info.get('portDepth', 99)
            
        result['airDraft'] = self.input.vessel.info['height'] - da_ + tide_
        result['freeboard'] = self.input.vessel.info['depth'] - dm_
        result['manifoldHeight'] = result['freeboard'] + self.input.vessel.info['manifoldHeight'] + tide_
        result['UKC'] = -max(da_,df_) + tide_ + depth_

            
        # print('airDraft:', result['airDraft'])
        
        #
#        
        
        #
#        plan = {'1C':{'wt':25997},'1P':{'wt':17886},'1S':{'wt':17886},
#                   '2C':{'wt':24253},'2P':{'wt':17450},'2S':{'wt':17450},
#                   '3C':{'wt':24253},'3P':{'wt':17450},'3S':{'wt':17450},
#                   '4C':{'wt':24253},'4P':{'wt':17450},'4S':{'wt':17450},
#                   '5C':{'wt':29004},'5P':{'wt':14858},'5S':{'wt':14858},
#                   'SLP':{'wt':3541},'SLS':{'wt':3541},
#                   'da':20.74,
#                   'df':21.14,
#                   'trim':-0.4
#                   }
#        
#        da_,  trim_ = 20.74, -0.4
        
        # use back default seawater density
        draft_ = np.interp(disp_, self.input.vessel.info['hydrostatic']['displacement'], self.input.vessel.info['hydrostatic']['draft'])
        mtc_   = np.interp(disp_, self.input.vessel.info['hydrostatic']['displacement'], self.input.vessel.info['hydrostatic']['mtc'])
        lcb_ = np.interp(disp_, self.input.vessel.info['hydrostatic']['displacement'], self.input.vessel.info['hydrostatic']['lcb'])
        lcf_   = np.interp(disp_, self.input.vessel.info['hydrostatic']['displacement'], self.input.vessel.info['hydrostatic']['lcf'])
        # mid.f = lcf; mid.b = lcb
        # print(draft_,mtc_,lcb_,lcf_)
        lcg_ = l_mom_/ disp_
        bg_ = lcg_ - lcb_
        trim_ = bg_*disp_/mtc_/100
        
        # print(l_mom_, lcb_, mtc_)
        # print(disp_, mtc_, lcb_)
        
        df_ = draft_ -  (0.5*lpp_ + lcf_)/lpp_*trim_
        da_ = df_ + trim_
        dm_ = (df_ + da_)/2
        
        # print(df_,da_,dm_,trim_)

        if int(self.input.vessel_id) in [1]:
            sdraft_ = da_ 
        elif int(self.input.vessel_id) in [2]:
            sdraft_ = dm_
            
        result['sdraft'] = sdraft_
        
        base_drafts, indx = np.unique(self.input.vessel.info['SSTable']['baseDraft'].to_numpy(dtype=np.float), return_index=True)
        ind_ = np.where(sdraft_ >= base_drafts)
        if len(ind_[0]) > 0:
            base_draft_ = base_drafts[ind_[0][-1]]
            
            frames_ = self.input.vessel.info['frames']
            tankGroup_ = self.input.vessel.info['tankGroup']
            tankGroupLCG_ = self.input.vessel.info['tankGroupLCG']
            df_sf_ = self.input.vessel.info['SSTable']
            df_bm_ = self.input.vessel.info['SBTable']
            SFlimits_ = self.input.vessel.info['SFlimits']
            BMlimits_ = self.input.vessel.info['BMlimits']
            
            locations_ = self.input.vessel.info['locations']
            center_tanks_ = self.input.vessel.info['centerTank']
            wing_tanks_ = self.input.vessel.info['wingTank']
            ballast_tanks_ = self.input.vessel.info['ballastTankBSF']
            alpha_ = self.input.vessel.info['alpha']
            BWCorr_ = self.input.vessel.info['BWCorr']
            dist_AP_ = [47.5, 62.2, 62.2, 106.3, 106.3, 155.3, 155.3, 204.3, 204.3, 253.3, 253.3, 308.9]
            C4_ = self.input.vessel.info['C4']
            BSFLimits_ = self.input.vessel.info['BSFlimits']
            dist_station_  = self.input.vessel.info['distStation']
            
            W_, W0_ = np.zeros(len(frames_)), 0.
            M_, M0_ = np.zeros(len(frames_)), 0.
            SF_, BM_ = np.zeros(len(frames_)), np.zeros(len(frames_))
            SF_limits_,BM_limits_ = np.zeros(len(frames_)),np.zeros(len(frames_))
            SF_percent, BM_percent = np.zeros(len(frames_)), np.zeros(len(frames_))
            max_sf_, max_bm_ = [0.,0.], [0.,0.]
#
            for f__,f_ in enumerate(frames_):
    #            print('frame:', f_, '-----------------------------------------------------')
                w_, m_ = 0., 0.
                for k_, v_ in tankGroup_[str(f__+1)].items(): # 
                    load_ = plan.get(k_,{})[0].get('wt',0.)/1000 if plan.get(k_,{}) else 0.
                    ratio_ = v_.get('wr',0.)
                    lcg_ = v_.get('lcg',0.)
                    w__ = ratio_*load_
                    w_ += w__
                    m__ = w__ * lcg_
                    m_ += m__
                    
                    # if load_ > 0:
                    #     print(k_, 'wi:', w__, 'mi:', w__ ,'x', lcg_,'=',m__)
            
                W_[f__] = w_ + W0_
                W0_ += w_ 
                M_[f__] = m_ + M0_
                M0_ += m_ 
            
                # print('sum wi:',W_[f__], 'sum mi:',M_[f__] )
                
                # SF
                df_ = df_sf_[df_sf_["frameNumber"].isin([float(f_)])]  
                df_ = df_[df_['baseDraft'].isin([base_draft_])]
                ss_ = df_['baseValue'].to_numpy()[0] + (sdraft_ -  base_draft_)*df_['draftCorrection'].to_numpy()[0] + trim_*df_['trimCorrection'].to_numpy()[0]
           
                SF_[f__] = (ss_ - W_[f__])*1000
                SF_limits_[f__] = SFlimits_[str(f_)][0] if SF_[f__] < 0 else SFlimits_[str(f_)][1]
                SF_percent[f__] = SF_[f__]/SF_limits_[f__]*100
                if SF_percent[f__] > max_sf_[1]:
                    max_sf_ = [f_, round(SF_percent[f__],2)]
                # BM
                df_ = df_bm_[df_bm_["frameNumber"].isin([float(f_)])]
                df_ = df_[df_['baseDraft'].isin([base_draft_])]
                # print(df_)
                sb_ = df_['baseValue'].to_numpy()[0] + (sdraft_-base_draft_)*df_['draftCorrection'].to_numpy()[0] + trim_*df_['trimCorrection'].to_numpy()[0]
                # print(f_, ss_, sb_)
                BM_[f__] = (W_[f__] * tankGroupLCG_[str(f__+1)] - sb_ + M_[f__])*1000
                BM_limits_[f__] = BMlimits_[str(f_)][0] if BM_[f__] < 0 else BMlimits_[str(f_)][1]
                BM_percent[f__] = BM_[f__]/BM_limits_[f__]*100
                
                if BM_percent[f__] > max_bm_[1]:
                    max_bm_ = [f_, round(BM_percent[f__],2)]
                    
                # print(sb_, W_[f__] * tankGroupLCG_[str(f__+1)],  M_[f__], BM_[f__]/1000)
                    
                # print(df_['baseValue'].to_numpy()[0], df_['draftCorrection'].to_numpy()[0], df_['trimCorrection'].to_numpy()[0])
                
                # print(f_, round(sdraft_,3), round(BM_[f__],3), round(BM_limits_[f__]*9.8,3), round(BM_percent[f__],2))
                
                # print(f_, round(da_,3), round(W_[f__],3),round(ss_,3), round(SF_[f__]/1000,3))
                # print(f_, round(da_,3), round(W_[f__],3),round(sb_,3), round(BM_[f__]/1000,3), BM_percent[f__])
                
                # print(f_, ss_ ,sb_)
                #print(f_ ,SF_[f__]/1000,BM_[f__]/1000)
                # print(f_,  sdraft_ )
    #            
    #        
            
            result['SF'] = {f_:SF_percent[f__] for f__,f_ in enumerate(frames_)}   
            result['BM'] = {f_:BM_percent[f__] for f__,f_ in enumerate(frames_)}   
            result['maxSF'] = max_sf_  
            result['maxBM'] = max_bm_
            # print(W_)
            
                
            
#        #
#        ##
            if self.input.vessel_id in [1]:
                zero_crossing = np.where(np.diff(np.sign(SF_)))[0]
                # print(SF_)
                # print(zero_crossing)
                max_BM_ = 0
                for z_ in zero_crossing:
                    
                    frm_ = str(frames_[z_]) + '-' + str(frames_[z_+1])
                    dist_ = float(dist_station_[frm_])
                    SFA, SFF = SF_[frames_.index(frames_[z_+1])], SF_[frames_.index(frames_[z_])]
                    L1 = abs(SFA)/(abs(SFA) + abs(SFF)) * dist_
                    L2 = dist_ - L1
                    
                    if 0 < L1 < dist_/3:
                        max_BM = BM_[z_+1] + 0.5*SFA*L1
                    elif 0 < L2 < dist_/3:
                        max_BM = BM_[z_] + 0.5*SFA*L2
                    else:
                        max_BM = 0.5*(BM_[z_+1] + BM_[z_])
                
                    
                    if max_BM > 0:
                        max_BM = max_BM/830000.*100
                    else:
                        max_BM = max_BM/-770800.*100
                        
                    # print(z_,'max_BM:', max_BM)
                    if max_BM_ < max_BM:
                        max_BM_ = max_BM
                        
                if max_BM_ >= 90:
                    print(max_bm_,max_BM_)
                    
            ## -------------------------------------------------------------------------------
            BSF_limits_ = np.zeros(len(locations_))
            BSF_ = np.zeros(len(locations_))
            BSF_percent = np.zeros(len(locations_))
            max_bsf_ = [0.,0.]
            bsf_ = {}
            if self.input.vessel_id in [1]:
                # print('BSF----------------------------------------------------')
                for t__, t_ in enumerate(zip(center_tanks_, wing_tanks_, ballast_tanks_)):
                    loc_ = locations_[t__]
                
                    sf_ = SF_[frames_.index(loc_[:-1])]*9.8
                    x3_ = sf_*alpha_[t__]
                    # print(sf_,x3_)
                    # centre tanks
                    load_ = sum([plan.get(i_,{})[0].get('wt',0.) if plan.get(i_,{}) else 0. for i_ in t_[0]['tanks']])*9.8
                    x6_ = load_*t_[0]['C1']
                    # print(load_,x6_)
                    # wing_tanks
                    load_ = sum([plan.get(i_,{})[0].get('wt',0.) if plan.get(i_,{}) else 0. for i_ in t_[1]['tanks']])*9.8
                    x9_ = load_*t_[1]['C2']
                    # print(load_,x9_)
                    # ballast_tanks
                    load_ = sum([plan.get(i_,{})[0].get('wt',0.) if plan.get(i_,{}) else 0. for i_ in t_[2]['tanks']])*9.8
                    x12_ = load_*t_[2]['C3']
                    # print(load_,x12_)
                    
                    x13_ = BWCorr_[t__]
                    draft_ = da_ - trim_*dist_AP_[t__]/lpp_
                    x16_ = draft_*C4_[t__]
                    
                    if load_ > 0:
                        x17_ = x6_ + x9_ + x12_ + x13_ + x16_
                    else:
                        x17_ = x6_ + x9_ + x16_
                        
                    # print(x17_)
                    fl_ = x3_ + x17_
                    # print(fl_)
                    
                    BSF_[t__] = fl_
                    BSF_limits_[t__] = BSFLimits_[loc_][0] if fl_ < 0 else BSFLimits_[loc_][1]
                    BSF_percent[t__] = BSF_[t__]/BSF_limits_[t__]*100
                    bsf_[loc_] = BSF_percent[t__]
                    if BSF_percent[t__] > max_bsf_[1]:
                        max_bsf_ = [loc_, BSF_percent[t__]]
                        
                result['BSF'] = bsf_ 
            
        return result
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
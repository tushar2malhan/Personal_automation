# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 14:39:08 2021

@author: I2R
"""

from itertools import permutations
from copy import deepcopy
# import time

# from vlcc_init_rotate import Process_input_rotate
from vlcc_gen import Generate_plan
from vlcc_check import Check_plans

class Check_rotations:
    def __init__(self, data, inputs):
#        self.outfile   = 'resmsg.json'
        self.input = inputs # original input
        self.json = data # original loadable
        self.rotation_input = deepcopy(inputs)
        # self.permute_list = permute_list
        
        
    def _check_plans(self, plans, permute_list, permute_list1):
        
        self.constraints = {str(p__):[] for p__,p_ in enumerate(plans['ship_status'])}
        # time.sleep(10) 
        # input("Press Enter to continue...")
        for s__, s_ in enumerate(plans.get('operation',[])):
            print('main plan:', s__, plans['rotation'][s__])
            ballast_plan_ = {k1_:v1_['ballast']  for k1_,v1_ in plans['ship_status'][s__].items()}
            if self.input.loadable.info['rotationCheck'] and permute_list:
                
                cur_list_ = [permute_list1[r__] for r__, r_ in enumerate(permute_list) if plans['rotation'][s__] == r_][0]
                
                for r__, r_ in enumerate(permute_list):
                    
                    if plans['rotation'][s__] != r_:
                        print('check rotation ...', r_) 
                        new_list_ = permute_list1[r__]
                        self._check_rotations(new_list_, s_, ballast_plan_, s__, r__, cur_list_, r_)
                    else:
                        str1 = ''
                        for l__,l_ in enumerate(permute_list1[r__]):
                            str1 += self.input.loadable.info['parcel'][l_]['abbreviation'] + ' -> '
                        
                        self.constraints[str(s__)].append(str1[:-3] + 'is fine!!')
                        
            else:
                print('no rotation needed ...')
            
                        
                    
            
        
    def _check_rotations(self, new_rotation, loading_plan, ballast_plan, plan_id, rotation_id, cur_rotation, new_rotation1):
        
        dat_file = 'input_rotate'+str(plan_id+rotation_id)+'.dat'
        loading_plan_ = dict(loading_plan)
        
        if len(self.input.loadable.info['rotationVirtual']) == 1:
            port_ = self.input.loadable.info['rotationVirtual'][0]
            
            
        elif len(self.input.loadable.info['rotationVirtual']) == 2:
            port_ = self.input.loadable.info['rotationVirtual'][0] + self.input.loadable.info['rotationVirtual'][1]
        
        new_port_ = {}
        for p__, p_ in enumerate(port_):
            new_port_[str(p_)] =  str(port_[cur_rotation.index(new_rotation[p__])])
            
        for k_, v_ in new_port_.items():
            loading_plan_[k_] = loading_plan[v_]
        
        # print(cur_rotation)
        # print(new_rotation)
        # print(new_port_)
            
        empty_ballast_port_ = []
        for  p_ in self.input.loadable.info['rotationVirtual']:
            empty_ballast_port_ += p_[:-1]
            
        ballast_plan_ = {k_:v_ for k_, v_ in ballast_plan.items() if int(k_) not in  empty_ballast_port_}
        
        # loadable_json = deepcopy(self.json['loadable'])
        # loadable_json['loadingPlan'] = loading_plan_
        # loadable_json['ballastPlan'] = ballast_plan_
        
            
                # plan = {k_:v_ for k_,v_ in s_.items() if k_[:-1] == port}
        # loadable_json = self._recreate_loadable(loading_plan, ballast_plan)
        
        # data = {}
        # data['vessel'] = self.json['vessel']
        # data['loadable'] = loadable_json
        
        new_input = self.rotation_input
        # new_input.port = Port(new_input)
        # new_input.loadable = Loadable(self) # basic info
        new_input.cargo_rotation = new_rotation1
        
        new_input.loadable_json['loadingPlan'] = loading_plan_
        new_input.loadable_json['ballastPlan'] = ballast_plan_
        new_input.loadable._create_operations(new_input) # operation and commingle
        # new_input.vessel = Vessel(self)
        # new_input.vessel._get_onhand(self) # ROB
        # new_input.vessel._get_onboard(self) # Arrival condition
        new_input.get_stability_param()
        new_input.write_dat_file(file = dat_file, IIS = False)
        
        new_output = Generate_plan(new_input)
        new_output.IIS = False
        new_output.run(dat_file=dat_file,num_plans=1)
        
        
        rotationCargo = []
        for r_ in new_input.loadable.info['rotationCargo']:
            rotationCargo += list(r_)
            
        
        str1 = ''
        for l__,l_ in enumerate(rotationCargo):
            str1 += self.input.loadable.info['parcel'][l_]['abbreviation'] + ' -> '
        
        # new_output.plan['ship_status'] = []
        if new_output.plans['ship_status']:
            plan_check = Check_plans(new_input, reballast = False)
            plan_check._check_plans(new_output)
            
            error_ = []
            for k_, v_ in plan_check.stability_values[0].items():
                if float(v_['shearForce']) > 100:
                    error_.append('Port ' + k_ + ' fails shear force check!!')
                
                if float(v_['bendinMoment']) > 100:
                    error_.append('Port ' + k_ + ' fails bending moment check!!')
                
            if not error_:
                self.constraints[str(plan_id)].append(str1[:-3] + 'is fine!!')
            else:
                self.constraints[str(plan_id)].append(str1[:-3] + 'is not possible!!')
                self.constraints[str(plan_id)] += error_
        else:
            # input("Press Enter to continue...")
            ## set positive trim < 2
            print('set 0 < trim <= 2')
            # new_input.trim_upper = {str(p_):str(2) for p_ in range(1,new_input.loadable.info['lastVirtualPort']) if str(p_) not in new_input.loadable.info['fixedBallastPort']}
            new_input._set_trim(trim_load_upper = 2.0, trim_load_lower = 0.0)
            new_input.write_dat_file(file = dat_file, IIS = False)
        
            new_output = Generate_plan(new_input)
            new_output.IIS = False
            new_output.run(dat_file=dat_file,num_plans=1)
            
            
                        
            if new_output.plans['ship_status']:
                plan_check = Check_plans(new_input, reballast = False)
                plan_check._check_plans(new_output)
                
                
                error_ = []
                for k_, v_ in plan_check.stability_values[0].items():
                    if float(v_['shearForce']) > 100:
                        error_.append('Port ' + k_ + ' fail shear force check!!')
                    
                    if float(v_['bendinMoment']) > 100:
                        error_.append('Port ' + k_ + ' fail bending moment check!!')
                    
                if not error_:
                    self.constraints[str(plan_id)].append(str1[:-3] + 'is fine with 0 < trim <= 2!!')
                else:
                    self.constraints[str(plan_id)].append(str1[:-3] + 'is not possible!!')
                    self.constraints[str(plan_id)] += error_
           
                # self.constraints[str(plan_id)].append(str1[:-3] + 'is fine with 0 < trim <= 2!!')
            else:
                self.constraints[str(plan_id)].append(str1[:-3] + 'is not possible!!')
            
          
            
        
        ## check and modify plans    
        # print('main plan:', plan_id, new_rotation)
        
        
        # time.sleep(10) 
        # input("Press Enter to continue...")
                
   
   
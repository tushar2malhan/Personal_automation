# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 17:19:26 2021

@author: I2R
"""

from copy import deepcopy
from vlcc_gen import Generate_plan
import numpy as np
from itertools import permutations
from vlcc_check import Check_plans
# import json

DEC_PLACE = 3

class Multiple_plans(object):
    
    def __init__(self, data, inputs):
#        self.outfile   = 'resmsg.json'
        self.input = inputs # original input
        self.json = data # original loadable
        self.multiple_input = deepcopy(inputs)
        self.permute_list, self.permute_list1 = [], []
        # self.out = []
        
        
    def run(self):
        
        self.plans = {'ship_status':[], 'cargo_status':[], 'slop_qty':[], 'cargo_order':[], 'stability':[],
                              'constraint':[], 'obj':[], 'cargo_tank':[], 'base_draft':[],
                              'loading_hrs':[], 'topping':[], 'loading_rate':[],
                              'operation':[], 'rotation':[], 'message':{}}
        self.tanks = []
        
        if not self.input.error:
            
            if self.input.gen_distinct_plan and len(self.input.loadable.info['cargoRotation']) > 0:
                
                len_ = len(self.input.loadable.info['cargoRotation'])
                if len_ == 1:
                    port_ = list(self.input.loadable.info['cargoRotation'].keys())[0]
                    list_ = list(self.input.loadable.info['cargoRotation'].values())[0]
                    
                    permute_list_, permute_list1_= [], []
                    for r__, r_ in enumerate(permutations(list_)):
                        permute_list_.append({port_:r_})
                        permute_list1_.append(r_)
                        
                elif len_ == 2:
                    port1_ = list(self.input.loadable.info['cargoRotation'].keys())[0]
                    port2_ = list(self.input.loadable.info['cargoRotation'].keys())[1]
                    
                    order1_ = int(self.input.port.info['idPortOrder'][port1_])
                    order2_ = int(self.input.port.info['idPortOrder'][port2_])
                    
                    list1_ = list(self.input.loadable.info['cargoRotation'].values())[0]
                    list2_ = list(self.input.loadable.info['cargoRotation'].values())[1]
                    
                    permute_list_, permute_list1_= [], []
                    for r1__, r1_ in enumerate(permutations(list1_)):
                        for r2__, r2_ in enumerate(permutations(list2_)):
                            permute_list_.append({port1_:r1_, port2_:r2_})
                            if order1_ < order2_:
                                permute_list1_.append(r1_+r2_)
                            else:
                                permute_list1_.append(r2_+r1_)
                                
                        
                else:
                    print('Not support for multiple cargos at more than 2 ports!!')
                    return
                
                self.permute_list, self.permute_list1 = permute_list_, permute_list1_
                
                for r__, r_ in enumerate(permute_list_):
                    print('possible permutation: ',r__, r_)
                    if r__ <= 6:
                        if r__ == 0:
                            # first permutation; input already generated
                            gen_output = Generate_plan(self.input)
                            base_draft_ = self.input.base_draft
                        else:
                            new_input = self.multiple_input
                            new_input.cargo_rotation = r_
                            new_input.loadable._create_operations(new_input) # operation and commingle
                            new_input.get_stability_param()
                            new_input.write_dat_file()
                            gen_output = Generate_plan(new_input)
                            base_draft_ = new_input.base_draft
                        
                        gen_output.run()
                        # gen_output.plan = {}
                        
                        if gen_output.plans.get('obj',[]):
                            ind_ = gen_output.plans['obj'].index(max(gen_output.plans['obj']))
                            
                            plan_check = Check_plans(self.input, indx = ind_)
                            # plan_check._check_plans(outputs.plans.get('ship_status',[]), outputs.plans.get('cargo_tank',[]))
                            plan_check._check_plans(gen_output)
                            
                            tanks_ = [sorted(b_)  for a_, b_ in gen_output.cargo_in_tank[ind_].items()]
                            
                            if tanks_ not in self.tanks:
                                self.tanks.append(tanks_)
                            
                                self.plans['ship_status'].append(gen_output.plans['ship_status'][ind_])
                                self.plans['cargo_status'].append(gen_output.plans['cargo_status'][ind_])
                                self.plans['obj'].append(gen_output.plans['obj'][ind_])
                                self.plans['operation'].append(gen_output.plans['operation'][ind_])
                                self.plans['rotation'].append(dict(r_))
                                self.plans['cargo_tank'].append(dict(gen_output.plans['cargo_tank'][ind_]))
                                self.plans['slop_qty'].append(gen_output.plans['slop_qty'][ind_])
                                self.plans['cargo_order'].append(gen_output.plans['cargo_order'][ind_])
                                self.plans['base_draft'].append(base_draft_)
                                self.plans['topping'].append(gen_output.plans['topping'][ind_])
                                self.plans['loading_rate'].append(gen_output.plans['loading_rate'][ind_])
                                self.plans['loading_hrs'].append(gen_output.plans['loading_hrs'][ind_])
                                self.plans['stability'].append(plan_check.stability_values[0])

                            
                            
                            # with open('plan_status.json', 'w') as f_:  
                            #     json.dump(gen_output.plans['ship_status'][ind_], f_)
                            
                            
                        else:
                            self.plans['message'] = {**self.plans['message'],**gen_output.plans.get('message',{})}
                
            elif self.input.gen_distinct_plan and len(self.input.loadable.info['parcel']) > 1:
                # single cargo at each port
                gen_output = Generate_plan(self.input)
                gen_output.run()
                
                
                # input("Press Enter to continue...")
                if gen_output.plans.get('obj',[]):
                    ind_ = gen_output.plans['obj'].index(max(gen_output.plans['obj']))
                    
                    plan_check = Check_plans(self.input, indx = ind_)
                    # plan_check._check_plans(outputs.plans.get('ship_status',[]), outputs.plans.get('cargo_tank',[]))
                    plan_check._check_plans(gen_output)
                    
                    tanks_ = [sorted(b_)  for a_, b_ in gen_output.cargo_in_tank[ind_].items()]
                    self.tanks.append(tanks_)
                    self.plans['ship_status'].append(gen_output.plans['ship_status'][ind_])
                    self.plans['cargo_status'].append(gen_output.plans['cargo_status'][ind_])
                    self.plans['obj'].append(gen_output.plans['obj'][ind_])
                    self.plans['operation'].append(gen_output.plans['operation'][ind_])
                    self.plans['rotation'].append([])
                    self.plans['cargo_tank'].append(dict(gen_output.plans['cargo_tank'][ind_]))
                    self.plans['slop_qty'].append(gen_output.plans['slop_qty'][ind_])
                    self.plans['cargo_order'].append(gen_output.plans['cargo_order'][ind_])
                    self.plans['topping'].append(gen_output.plans['topping'][ind_])
                    self.plans['loading_rate'].append(gen_output.plans['loading_rate'][ind_])
                    self.plans['loading_hrs'].append(gen_output.plans['loading_hrs'][ind_])
                    self.plans['stability'].append(plan_check.stability_values[0])
                            
                    
                    max_cargo_ = gen_output.max_tank_parcel
                    max_cargo_tank_ = list(gen_output.cargo_in_tank[ind_][max_cargo_])
                    
                    print('0 plan:',max_cargo_, max_cargo_tank_)
                    
                    for t_ in range(1,6): 
                        print('cargo max tank:',max_cargo_)
                        ban_tank_ = list(self.input.vessel.info['banCargo'][max_cargo_])
                        
                        rerun_ = False
                        if str(t_)+'C' in max_cargo_tank_:
                            ban_tank_ += [str(t_)+'C'] #[str(t_)+'P', str(t_)+'S']
                            rerun_ = True
                        elif str(t_)+'P' in max_cargo_tank_:
                            ban_tank_ += [str(t_)+'P', str(t_)+'S']
                            rerun_ = True
    
                             
                        if rerun_:
                            print('ban_tank:',ban_tank_)
                            new_input = self.multiple_input
                            new_input.vessel.info['banCargo'][max_cargo_] = ban_tank_
                            new_input.write_dat_file()
                            gen_output = Generate_plan(new_input)
                            gen_output.run()
                            
                            # input("Press Enter to continue...")
                            
                            if gen_output.plans.get('obj',[]):
                                ind_ = gen_output.plans['obj'].index(max(gen_output.plans['obj']))
                                
                                plan_check = Check_plans(self.input, indx = ind_)
                                # plan_check._check_plans(outputs.plans.get('ship_status',[]), outputs.plans.get('cargo_tank',[]))
                                plan_check._check_plans(gen_output)
                                tanks_ = [sorted(b_)  for a_, b_ in gen_output.cargo_in_tank[ind_].items()]
                                
                                if tanks_ not in self.tanks:
                                    
                                    self.tanks.append(tanks_)
                                
                                    self.plans['ship_status'].append(gen_output.plans['ship_status'][ind_])
                                    self.plans['cargo_status'].append(gen_output.plans['cargo_status'][ind_])
                                    self.plans['obj'].append(gen_output.plans['obj'][ind_])
                                    self.plans['operation'].append(gen_output.plans['operation'][ind_])
                                    self.plans['rotation'].append([])
                                    self.plans['cargo_tank'].append(dict(gen_output.plans['cargo_tank'][ind_]))
                                    self.plans['slop_qty'].append(gen_output.plans['slop_qty'][ind_])
                                    self.plans['cargo_order'].append(gen_output.plans['cargo_order'][ind_])
                                    self.plans['topping'].append(gen_output.plans['topping'][ind_])
                                    self.plans['loading_rate'].append(gen_output.plans['loading_rate'][ind_])
                                    self.plans['loading_hrs'].append(gen_output.plans['loading_hrs'][ind_])
                                    self.plans['stability'].append(plan_check.stability_values[0])
                            
                    
                else:
                    self.plans['message'] = {**self.plans['message'], **gen_output.plans['message']}
                    
            else:
                
                gen_output = Generate_plan(self.input)
                num_plans = 1 if len(self.input.loadable.info['parcel']) == 1 else 100
                gen_output.run(num_plans=num_plans)
                
                if gen_output.plans.get('obj',[]):
                    
                    plan_check = Check_plans(self.input, reballast = True)
                    # plan_check._check_plans(outputs.plans.get('ship_status',[]), outputs.plans.get('cargo_tank',[]))
                    plan_check._check_plans(gen_output)
                    
                    self.plans = gen_output.plans
                    self.plans['rotation'] = [[] for p_ in range(len(gen_output.plans['ship_status']))]
                    
                    self.plans['stability'] = plan_check.stability_values
                
                else:
                    self.plans['message'] = {**self.plans['message'], **gen_output.plans['message']}
                        
                
                
                
               
            # final sorting
            if len(self.plans['obj']) > 0:
                sort_ = np.argsort(-np.array(self.plans['obj']))
                self.plans['ship_status'] = [self.plans['ship_status'][i_] for i_ in sort_]
                self.plans['cargo_status'] = [self.plans['cargo_status'][i_] for i_ in sort_]
                self.plans['obj'] = [self.plans['obj'][i_] for i_ in sort_]
                self.plans['operation'] = [self.plans['operation'][i_] for i_ in sort_]
                self.plans['rotation'] = [self.plans['rotation'][i_] for i_ in sort_]
                self.plans['cargo_tank'] = [self.plans['cargo_tank'][i_] for i_ in sort_]
                self.plans['slop_qty'] = [self.plans['slop_qty'][i_] for i_ in sort_]
                self.plans['cargo_order'] = [self.plans['cargo_order'][i_] for i_ in sort_]
                self.plans['topping'] = [self.plans['topping'][i_] for i_ in sort_]
                self.plans['loading_rate'] = [self.plans['loading_rate'][i_] for i_ in sort_]
                self.plans['loading_hrs'] = [self.plans['loading_hrs'][i_] for i_ in sort_]
                
                
            
    def gen_json(self, constraints, stability_values):
        gen_output = Generate_plan(self.input)
        gen_output.plans = self.plans
        
        out =  gen_output.gen_json(constraints, stability_values)
        
        return out
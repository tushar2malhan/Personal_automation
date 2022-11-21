# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 15:55:30 2020

@author: I2R
"""
#import amplpy
from amplpy import AMPL
import numpy as np
import json

from vlcc_ortools import vlcc_ortools
from loading_seq import Loading_seq
from discharging_seq import Discharging_seq
import pandas as pd
from copy import deepcopy

DEC_PLACE = 3

CONS = {'Condition01z': 'Min tolerance constraints violated!!',
        'Constr122': 'Priority constraints violated!!',
        'Condition112d1': '1P and 1S cannot have same weight!!',
        'Condition112d2': '2P and 2S cannot have same weight!!',
        'Condition112d3': '4P and 4S cannot have same weight!!',
        'Condition112d4': '5P and 5S cannot have same weight!!',
        'Condition114g1': 'Deballast amt during loading cargo issue!!',
        'Condition114g2': 'Ballast amt during discharging cargo issue!!',
        'Constr13': 'Displacement bound issue!!',
        'Constr13b': 'Deadweight bound issue!!',
        'Constr16a': 'Trim lower bound issue!!',
        'Constr16b': 'Trim upper bound issue!!',
        'Condition20b': 'SF lower bound issue!!',
        'Condition20c': 'SF upper bound issue!!',
        'Condition21b': 'BM lower bound issue!!',
        'Condition21c': 'BM upper bound issue!!',
        'Condition111': "Load all cargo issue!!",
        'Condition115': "Deballast limitation issue!!",
        'Condition112g1': "SLP has to be used issue!!",
        'Condition112g2': "SLS has to be used issue!!",
        'Condition114j1': 'WB1P and WB1S cannot have same weight at arrival of first port!!',
        'Condition114j2': 'WB2P and WB2S cannot have same weight at arrival of first port!!',
        'Condition114j3': 'WB3P and WB3S cannot have same weight at arrival of first port!!',
        'Condition114j4': 'WB4P and WB4S cannot have same weight at arrival of first port!!'
       }


# FIXCONS =  []
FIXCONS = ['Condition0', 'Condition01', 'Condition03', 
            'Condition04', 'Condition05',
            'Condition041', 'Condition050', 'Condition050a', 
            'Condition050b', 'Condition050b1',
            'Condition050c', 'Condition050c1',
            'Condition052', 'Condition06', 'condition22',
            'condition23', 'condition23a', 'condition23b',
            'condition24', 'condition24a', 'condition25', 'condition27',
            'Constr5a',
            'Constr8', 'Constr11', 'Constr12a1',
            'Condition112a', 'Condition112b', 'Condition112c1', 'Condition112c2', 'Condition112c3',
            'Condition112a1', 'Condition112a2',
            'Condition112b1', 'Condition112b2',
            'Condition112f', 
            'Condition112g1', 'Condition112g2', 
            'Condition113d1', 'Condition113d2', 'Condition113d3',
            'Condition114a1', 'Condition114a2', 'Condition114a3',
            "Condition114b", "Condition114c", "Condition114d2",
            'Condition114e1', 'Condition114e2', 'Condition114e3', 'Condition114e4', 'Condition114e5', 'Condition114e6',
            'Condition114f1',
            'Constr17a', 'Constr13c1', 'Constr13c2',
            'Constr13a',
            'Constr15b1', 'Constr15b2', 'Constr15c1', 'Constr15c2', 'Constr153', 'Constr154',
            'Constr16b1', 'Constr16b2', 'Constr161', 'Constr163', 'Constr164',
            'Constr18a', 'Constr18b', 'Constr19a', 'Constr19b', 'Constr18d', 'Condition200a',
            'Condition20a1', 'Condition21a1', 'Condition20a2', 'Condition21a2']

DENSITY = {'DSWP':1.0, 'DWP':1.0, 'FWS':1.0, 'DSWS':1.0,
                   'FO2P':0.98, 'FO2S':0.98, 'FO1P':0.98, 'FO1S':0.98, 'BFOSV':0.98, 'FOST':0.98, 'FOSV':0.98,
                   'DO1S':0.88,  'DO2S':0.88, 'DOSV1':0.88, 'DOSV2':0.88}
        
class Generate_plan:
    def __init__(self, data):

        self.input = data
        self.commingled = False
        self.rerun = False
        self.full_load = False
        self.IIS = True
        self.commingled_ratio = {}
        self.opt_mode = 0
        self.run_time = 60

    def run(self, dat_file='input.dat', num_plans=100, reballast = False):
        
        self.plans = {}
        self.plans['ship_status'] = []
        self.plans['message'] = {}
        self.plans['constraint'] = []

        if not self.input.error:
            
            # if self.input.mode in ['FullManual']:
            #     print('run Assemble ....')
            #     self._assemble()
                
            # else:
            if self.input.solver in ['AMPL']:
                print('run AMPL ....')
                result = self._run_ampl(dat_file=dat_file) 
            else:
                print('run ORTOOLS ....')
                result = self._run_ortools()
            
            if result['succeed']:
                self._process_ampl(result, num_plans=num_plans)
                
                # self.commingled_ratio = False
                if self.commingled_ratio:
                    print('Rerun due to miss temperature in commingle cargo!!')
                    result1 = deepcopy(result)
                    temp_ = 0.
                    for k_, v_ in self.commingled_temp.items():
                        if v_ > temp_:
                            temp_ = v_
                            self.input.loadable.commingled_ratio = self.commingled_ratio[k_]
                    
                    self.input.loadable._create_operations(self.input) # operation and commingle
                    
                    if self.input.solver in ['AMPL']:
                        print('run AMPL ....')
                        self.input.write_dat_file()
                        result = self._run_ampl(dat_file=dat_file) 
                    else:
                        print('run ORTOOLS ....')
                        result = self._run_ortools()
                        
                    if not result['succeed']:
                        print('Second AMPL for commingle failed!!')
#                        result = result1
                    else:
                        self._process_ampl(result, num_plans=num_plans)
                        self._process_checking_plans(result)
                    
                else:
                    self._process_checking_plans(result)
                
                
            elif self.input.module in ['LOADABLE'] and not reballast:
                result1 = deepcopy(result)

                # print('Rerun for loading module')
#                if self.input.solver in ['AMPL']:
#                    print('Rerun AMPL ....')
#                else:
#                    print("Rerun ORTools ....")
                    
                if not result['succeed'] and dat_file in ['input.dat']:
                    if self.input.solver in ['AMPL']:
                        print('##**Rerun AMPL relax init trim and  reduce displacement limit  ....')
                    else:
                        print('##**Rerun ORTools relax init trim and  reduce displacement limit  ....')
                    # print(self.input.trim)
                    self.input.get_stability_param(reduce_disp_limit = 4000)
                    for a_, b_ in self.input.trim_upper.items():
                        if round(b_,2) == 1:
                            self.input.trim_lower[a_] = 0.5
                            
                    # self.input.get_stability_param(reduce_disp_limit = 3000)
                    
                    if self.input.solver in ['AMPL']:
                        self.input.write_dat_file(file=dat_file, IIS = False)
                        result = self._run_ampl(dat_file=dat_file)
                    else:
                        result = self._run_ortools()

                    if result['succeed']:
                        self._process_ampl(result, num_plans=num_plans)

                        if self.commingled_ratio:
                            print('Rerun due to miss temperature in commingle cargo!!')
                            result1 = deepcopy(result)
                            temp_ = 0.
                            for k_, v_ in self.commingled_temp.items():
                                if v_ > temp_:
                                    temp_ = v_
                                    self.input.loadable.commingled_ratio = self.commingled_ratio[k_]
                            
                            self.input.loadable._create_operations(self.input) # operation and commingle
                            
                            
                            if self.input.solver in ['AMPL']:
                                print('run AMPL ....')
                                self.input.write_dat_file(file=dat_file, IIS = False)
                                result = self._run_ampl(dat_file=dat_file) 
                            else:
                                print('run ORTOOLS ....')
                                result = self._run_ortools()
                                
                            if not result['succeed']:
                                print('Second AMPL for commingle failed!!')
                                result = result1
                            else:
                                self._process_ampl(result, num_plans=num_plans)
                                self._process_checking_plans(result)
                        else:
                            self._process_checking_plans(result)
                
                # case 1: -----------------------------------------------
                # input("Press Enter to continue...")
                if not result['succeed'] and dat_file in ['input.dat']:
                    if self.input.solver in ['AMPL']:
                        print('##**Rerun AMPL relax FPT  ....')
                    else:
                        print('##**Rerun ORTools relax FPT  ....')
                              
                    
                    if self.input.solver in ['AMPL']:
                        if self.input.vessel_id in [1]:
                            self.input.write_dat_file(file=dat_file, incDec_ballast = ['LFPT'], IIS = False) # 
                        elif self.input.vessel_id in [2]:
                            self.input.write_dat_file(file=dat_file, incDec_ballast = ['FPT'], IIS = False) # 
                        result = self._run_ampl(dat_file=dat_file)
                    else:
                        result = self._run_ortools()
                        
                    if result['succeed']:
                        self._process_ampl(result, num_plans=num_plans)
                        self._process_checking_plans(result)
                    
                    
                if not result['succeed']:
                    self.plans['message']['Optimization Error'] = result1['message']
                    
                
                 
                
            elif self.input.module in ['DISCHARGING'] and not reballast:

                self.opt_mode = 0
                
                if result['solve_result'] in ['limit']:
                    print('Increase time to get solutions!!!')
                    self.run_time = 180

                result1 = deepcopy(result)
                
                list_ = [0,1] if self.input.module1 in [""] else [0]
                # print('Rerun for loading module')
                if self.input.solver in ['AMPL']:
                    
                    if not result['succeed'] and self.input.module1 in [""]:
                        print('Rerun AMPL .... change set_trim 1')
                        self.opt_mode = 0
                        
                        self.input.get_param(set_trim = 1)
                        self.input.write_ampl(IIS = False)
#                        input("Press Enter to continue...")

                        result = self._run_ampl(dat_file='input_discharging.dat') 
                        if result['succeed']:
                            self._process_ampl(result, num_plans=num_plans)
                            self._process_checking_plans(result)
                        
                    
                    if not result['succeed']:
                        print('Rerun AMPL .... Relax Ballast 1')
                        self.opt_mode = 1
                        
                        for set_trim in list_:
                            self.input.get_param(set_trim = set_trim)
                            self.input.write_ampl(incDec_ballast = ['APT'], IIS = False, ave_trim = self.input.ave_trim, run_time = self.run_time) # relax list mom to 100000
                       
                            # drop_const = ['Condition21c'] #, 'Constr16b']
                            result = self._run_ampl(dat_file='input_discharging.dat') 
                            if result['succeed']:
                                self._process_ampl(result, num_plans=num_plans)
                                self._process_checking_plans(result)
                                break
                        
                        
                    if not result['succeed']:
                        print('Rerun AMPL .... Relax Ballast 2')
                        self.opt_mode = 2
                        # case 1:
                        for set_trim in list_:
                            self.input.get_param(set_trim = set_trim)
                            if self.input.vessel_id in [1, '1']:
                                self.input.write_ampl(incDec_ballast = ['APT', 'AWBP', 'AWBS'], IIS = False, ave_trim = self.input.ave_trim, run_time = self.run_time) # relax list mom to 100000
                            elif self.input.vessel_id in [2, '2']:
                                self.input.write_ampl(incDec_ballast = ['APT'], IIS = False, ave_trim = self.input.ave_trim, run_time = self.run_time) # relax list mom to 100000
                        
                            result = self._run_ampl(dat_file='input_discharging.dat') 
                            if result['succeed']:
                                self._process_ampl(result, num_plans=num_plans)
                                self._process_checking_plans(result)
                                break
                            
                    # if not result['succeed']:    
                    #     self.opt_mode = 3
                    #     print('Rerun AMPL .... Relax constraints')
                    #     drop_const = ['Condition21c', 'Condition21b', 'Constr16b', 'Constr16a'] #['Condition21c', 'Condition21b', 'Constr16b']
                        
                    #     input("Press Enter to continue...")
                    #     result = self._run_ampl(dat_file='input_discharging.dat', drop_const = drop_const) 
                        
                    #     if result['succeed']:
                    #         self._process_ampl(result, num_plans=num_plans)
                    #         self._process_checking_plans(result)

                    if not result['succeed']:
                        self.plans['message']['Optimization Error'] = result1['message']
                        
            elif self.input.module in ['DISCHARGE'] and not reballast:
                
                result1 = deepcopy(result)
                # print('Rerun for loading module')
                if self.input.solver in ['AMPL']:
                    
                    if not result['succeed']:
                        print('##**Rerun AMPL change set_trim mode ...')
                        self.opt_mode = 1
                        self.input.get_stability_param(set_trim = 1)
                        self.input.write_dat_file(IIS = False, lcg_port = self.input.lcg_port, weight = self.input.weight)
#                        input("Press Enter to continue...")
                        result = self._run_ampl(dat_file='input_discharge.dat') 
                        
                        if result['succeed']:
                            self._process_ampl(result, num_plans=num_plans)
                            self._process_checking_plans(result)
                    
                    if not result['succeed']:
                        # case 0: -----------------------------------------------
                        print('##**Rerun AMPL reduce lower displacement limit ....')
                        self.opt_mode = 2
                        for set_trim in [0,1]:
                            # input("Press Enter to continue...")
                            self.input.get_stability_param(reduce_disp_limit = 2000, set_trim = set_trim)
                            self.input.write_dat_file(IIS = False, lcg_port = self.input.lcg_port, weight = self.input.weight)
#                            input("Press Enter to continue...")
                            result = self._run_ampl(dat_file='input_discharge.dat') 
                            
                            if result['succeed']:
                                self._process_ampl(result, num_plans=num_plans)
                                self._process_checking_plans(result)
                                break
                    
                    # if not result['succeed']:
                    #     print('##**Rerun AMPL drop upper BM ....')
                    #     # input("Press Enter to continue...")
                    #     self.input.write_dat_file(drop_BM = True, IIS = False, lcg_port = self.input.lcg_port, weight = self.input.weight)
                    #     result = self._run_ampl(dat_file='input_discharge.dat') 
                        
                    #     if result['succeed']:
                    #         self._process_ampl(result, num_plans=num_plans)
                    #         self._process_checking_plans(result)

                    if not result['succeed']:
                        # relax increase and decrease ballast:
                        print('##**Rerun AMPL relax increase and decrease ballast....')
                        self.opt_mode = 3
                        for set_trim in [0,1]:
                            
                            self.input.get_stability_param(reduce_disp_limit = 2000, set_trim = set_trim)
                        
                            if self.input.vessel_id in [1,'1']: # ['APT', 'AWBP', 'AWBS']
                                self.input.write_dat_file(IIS = False,incDec_ballast = ['APT'],
                                                          lcg_port = self.input.lcg_port, weight = self.input.weight, port_ballast_ban = False) # relax list mom to 100000
                            elif self.input.vessel_id in [2,'2']:
                                self.input.write_dat_file(IIS = False,incDec_ballast = ['FPT'],
                                                          lcg_port = self.input.lcg_port, weight = self.input.weight) # relax list mom to 100000
                                
#                            input("Press Enter to continue...")    
                            result = self._run_ampl(dat_file='input_discharge.dat') 
                            
                            if result['succeed']:
                                self._process_ampl(result, num_plans=num_plans)
                                self._process_checking_plans(result)
                                break
                            
                    if not result['succeed']:
                        # relax increase and decrease ballast:
                        print('##**Rerun AMPL relax increase and decrease ballast....')
                        self.opt_mode = 4

                        for set_trim in [0,1]:
                            
                            self.input.get_stability_param(reduce_disp_limit = 2000, set_trim = set_trim)
                        
                            if self.input.vessel_id in [1,'1']: # ['APT', 'AWBP', 'AWBS']
                                self.input.write_dat_file(IIS = False,incDec_ballast = ['APT', 'AWBP', 'AWBS'],
                                                          lcg_port = self.input.lcg_port, weight = self.input.weight, port_ballast_ban = False) # relax list mom to 100000
                            elif self.input.vessel_id in [2,'2']:
                                self.input.write_dat_file(IIS = False,incDec_ballast = ['FPT'],
                                                          lcg_port = self.input.lcg_port, weight = self.input.weight) # relax list mom to 100000
                                
#                            input("Press Enter to continue...")    
                            result = self._run_ampl(dat_file='input_discharge.dat') 
                            
                            if result['succeed']:
                                self._process_ampl(result, num_plans=num_plans)
                                self._process_checking_plans(result)
                                break
                            
                    # if not result['succeed']:
                    #     # relax increase and decrease ballast:
                    #     print('##**Rerun AMPL relax increase and decrease ballast....')
                        
                    #     if self.input.vessel_id in [1,'1']:
                    #         self.input.write_dat_file(IIS = False,incDec_ballast = ['LFPT', 'WB1P', 'WB1S', 'WB2P', 'WB2S', 'WB3P', 'WB3S', 'WB4P', 'WB4S', 'WB5P', 'WB5S'],
                    #                                   lcg_port = self.input.lcg_port, weight = self.input.weight, port_ballast_ban = False) # relax list mom to 100000
                    #     elif self.input.vessel_id in [2,'2']:
                    #         self.input.write_dat_file(IIS = False,incDec_ballast = ['FPT'],
                    #                                   lcg_port = self.input.lcg_port, weight = self.input.weight) # relax list mom to 100000
                            
                    #     input("Press Enter to continue...")    
                    #     result = self._run_ampl(dat_file='input_discharge.dat') 
                        
                    #     if result['succeed']:
                    #         self._process_ampl(result, num_plans=num_plans)
                    #         self._process_checking_plans(result)
                            
                    # if not result['succeed']:
                        
                    #     print('##**Rerun AMPL drop BM and upper trim....')
                    #     drop_const = ['Condition21c', 'Constr16b']
                    #     result = self._run_ampl(dat_file='input_discharge.dat', drop_const = drop_const) 
                        
                if not result['succeed']:
                    self.plans['message']['Optimization Error'] = result1['message']

            elif self.input.module in ['LOADING'] and not reballast:
                self.opt_mode = 0
                result1 = deepcopy(result)
                # print('Rerun for loading module')
                if self.input.solver in ['AMPL']:
                    print('Rerun AMPL ....')
                    
                    if not result['succeed'] and len(self.input.loading.info['loading_order1']) > 1:
                        print('Relax intermitted trim ...')
                        # input("Press Enter to continue...")
                        self.opt_mode = 1
                        self.input.get_param(min_int_trim = 0.5, max_int_trim = 1.5)
                        self.input.write_ampl(IIS = False)
                        result = self._run_ampl(dat_file='input_load.dat') 
                        
                        
                        if result['succeed']:
                            self._process_ampl(result, num_plans=num_plans)
                            self._process_checking_plans(result)
                            
                    if not result['succeed']:
                        print('Relax use APT for trim ...')
                        # input("Press Enter to continue...")
                        self.opt_mode = 2
                        # case 1a:
                        self.input.write_ampl(incDec_ballast = ['APT'], IIS = False) # 
                        result = self._run_ampl(dat_file='input_load.dat') 
                        
                        if result['succeed']:
                            self._process_ampl(result, num_plans=num_plans)
                            self._process_checking_plans(result)
                        
                    if not result['succeed']:
                        print('Relax use FPT for trim ...')
                        # input("Press Enter to continue...")
                        self.opt_mode = 3
                        # case 1b:
                        if self.input.vessel_id in [1]:
                            self.input.write_ampl(incDec_ballast = ['LFPT'], IIS = False) # 
                        elif self.input.vessel_id in [2]:
                            self.input.write_ampl(incDec_ballast = ['FPT'], IIS = False) #
                            
                        result = self._run_ampl(dat_file='input_load.dat') 
                        
                        if result['succeed']:
                            self._process_ampl(result, num_plans=num_plans)
                            self._process_checking_plans(result)
                        
                        
                    if not result['succeed']:
                        print('Relax AWB ballast for List...')
                        # input("Press Enter to continue...")
                        # case 2:
                        if self.input.vessel_id in [1]:
                            self.opt_mode = 4
                            self.input.write_ampl(incDec_ballast = ['AWBP'], IIS = False) # 
                            result = self._run_ampl(dat_file='input_load.dat') 
                            
                            if result['succeed']:
                                self._process_ampl(result, num_plans=num_plans)
                                self._process_checking_plans(result)
                                
                            self.opt_mode = 5
                            if not result['succeed']:
                                self.input.write_ampl(incDec_ballast = ['AWBS'], IIS = False) # 
                                result = self._run_ampl(dat_file='input_load.dat') 
                                
                                if result['succeed']:
                                    self._process_ampl(result, num_plans=num_plans)
                                    self._process_checking_plans(result)
                                    
                    if not result['succeed']:
                        print('Relax use FPT for trim ...')
                        # input("Press Enter to continue...")
                        self.opt_mode = 7
                        # case 1b:
                        if self.input.vessel_id in [1]:
                            self.input.write_ampl(incDec_ballast = ['LFPT', 'WB1P', 'WB1S', 'WB2P', 'WB2S', 'WB3P', 'WB3S', 'WB4P', 'WB4S'], IIS = False) # 
                        elif self.input.vessel_id in [2]:
                            self.input.write_ampl(incDec_ballast = ['FPT'], IIS = False) #
                            
                        result = self._run_ampl(dat_file='input_load.dat') 
                        
                        if result['succeed']:
                            self._process_ampl(result, num_plans=num_plans)
                            self._process_checking_plans(result)                
                                    
                    
                    if not result['succeed'] and (self.input.loading.info['deballastAmt'] < 1200):
                        print('For small ballast amt ...')
                        # input("Press Enter to continue...")
                        self.opt_mode = 6
                        self.input.write_ampl(listMOM = False, IIS = False) # 
                        drop_const = ['Condition21c']
                        result = self._run_ampl(dat_file='input_load.dat', drop_const = drop_const) 
                         
                        
                        if result['succeed']:
                            self._process_ampl(result, num_plans=num_plans)
                            self._process_checking_plans(result)
                            
                        else:
                            
                            self.input.write_ampl(listMOM = False, IIS = self.IIS) # 
                            drop_const = ['Condition21c', 'Constr16a']
                            result = self._run_ampl(dat_file='input_load.dat', drop_const = drop_const) 
                        
                            # input("Press Enter to continue...")
                            if result['succeed']:
                                self._process_ampl(result, num_plans=num_plans)
                                self._process_checking_plans(result)
                    
                    if not result['succeed']:
                        self.plans['message']['Optimization Error'] = result1['message']
                    
                else:
                    self.plans['message']['Optimization Error'] = result1['message']
            else:
                self.plans['message']['Optimization Error'] = result['message']
        else:
            self.plans['message'] = self.input.error
            
        
    def _run_ampl(self, drop_const = [], dat_file='input.dat'):
                
        is_succeed, num_solutions = False, 0
        solve_result, obj, plan, ship_status, ballast_weight, cargo_loaded, xx, cargo_loaded_port = [], [], [], [], [], [], [], []
        message = []
    
        try:
            # model_1i.mod : max loaded
            # model_3i.mod : min tank 
            
            if self.input.module in ['LOADING']:
                model_ = 'model_1i.mod'
                dat_file = 'input_load.dat'
            elif self.input.module in ['LOADABLE']:
                if self.input.mode in ['FullManual']:
                    model_ = 'model_2i.mod'
                else:
                    
                    if self.input.config['loadableConfig']:
                        if self.input.config['loadableConfig'].get('objective','1') in ['1']:
                            model_ = 'model_1i.mod' ## model_1ii.mod
                        else:
                            model_ = 'model_3i.mod'
                    else:
                        
                        # if self.input.accurate:
                        #     model_ = 'model_1ii.mod' ## model_1ii.mod
                        # else:
                        model_ = 'model_1i.mod' ## model_1ii.mod
                        
                            
                        
            elif self.input.module in ['DISCHARGE']:
                model_ = 'model_5i.mod'
                # model_ = 'model_1ii.mod'
                dat_file = 'input_discharge.dat'
                
            elif self.input.module in ['DISCHARGING']:
                model_ = 'model_4i.mod'
                dat_file = 'input_discharging.dat'
                
            print(model_)
            ampl = AMPL()
            # ampl.option['show_presolve_messages'] = True
            
            if self.input.module in ['LOADING']:
                # ampl.option['presolve'] = False
                pass
            elif self.input.module in ['LOADABLE']:
                if self.input.mode in ['Manual'] or not self.IIS:
                    ampl.option['presolve'] = False
                
            ampl.read(model_)
            
            ## module dependent constraints    
            if self.input.module in ['LOADABLE']:
                
                if self.input.mode not in ['FullManual']:
                    # auto and manual modes
                    c1_ = ampl.getConstraint('Condition112d5') # only for discharging
                    c2_ = ampl.getConstraint('Condition114g2') # only for discharging
                    c1_.drop()
                    c2_.drop()
                    
                if self.input.mode in ['Manual']:
                    c3_ = ampl.getConstraint('Constr5b') # commingle 98%
                    c3_.drop()
                    
                    c4_ = ampl.getConstraint('Condition112d1') # equal weight
                    c4_.drop()
                    
                if self.input.vessel.info['onboard']:
                    
                    slopP = [t_ for t_ in self.input.vessel.info['slopTank'] if t_[-1] == 'P'][0]
                    if slopP in self.input.vessel.info.get('notOnTop', []):
                        slp_ = ampl.getConstraint('Condition112g1') # SLP must be used
                        slp_.drop()
                        
                    slopS = [t_ for t_ in self.input.vessel.info['slopTank'] if t_[-1] == 'S'][0]
                    if slopS in self.input.vessel.info.get('notOnTop', []): # SLS must be used
                        sls_ = ampl.getConstraint('Condition112g2')
                        sls_.drop()
                    
            elif self.input.module in ['LOADING']:
                c1_ = ampl.getConstraint('Condition112d5') # only for discharging
                c2_ = ampl.getConstraint('Condition114g2') # only for discharging
                c3_ = ampl.getConstraint('Condition01') # one tank can only take in one cargo
                c1_.drop()
                c2_.drop()
                c3_.drop()
                
                # drop slop tanks must be used constraints
                slp_ = ampl.getConstraint('Condition112g1') # SLP must be used
                sls_ = ampl.getConstraint('Condition112g2') # SLS must be used
                slp_.drop()
                sls_.drop()
                
            elif self.input.module in ['DISCHARGE']:
                cw_ = ampl.getConstraint('Constr13b')
                cw_.drop()
                # drop slop tanks must be used constraints
                # slp_ = ampl.getConstraint('Condition112g1') # SLP must be used
                # sls_ = ampl.getConstraint('Condition112g2')  # SLS must be used
                # slp_.drop()
                # sls_.drop()
                #
                wwt_ = ampl.getConstraint('condition24a')
                wwt_.drop()
                
                # 5% different in vol
                # c3_ = ampl.getConstraint('Condition112a1')
                # c4_ = ampl.getConstraint('Condition112a2')
                # c3_.drop()
                # c4_.drop()
                
            elif self.input.module in ['DISCHARGING']:
                 # drop slop tanks must be used constraints
                # c1_ = ampl.getConstraint('Condition112g1') # SLP must be used
                # c2_ = ampl.getConstraint('Condition112g2') # SLS must be used
                # c1_.drop()
                # c2_.drop()
                
                # # 5% different in vol
                # c3_ = ampl.getConstraint('Condition112a1')
                # c4_ = ampl.getConstraint('Condition112a2')
                # c3_.drop()
                # c4_.drop()
                
                cw_ = ampl.getConstraint('Constr13b') 
                cw_.drop()
                
                if self.input.module1 in ['DISCHARGING']:
                    # min amount to discharge
                    c1_ = ampl.getConstraint('Condition120a') 
                    c1_.drop()
                    
                    c2_ = ampl.getConstraint('Condition120b') 
                    c2_.drop()

            ## vessel dependent constraints    
            if int(self.input.vessel_id) in [1] and self.input.mode not in ['FullManual']:
                # pass
                ##drop mean draft in BF and SF
                c4_ = ampl.getConstraint('Condition20a2')
                c5_ = ampl.getConstraint('Condition21a2')
                c4_.drop()
                c5_.drop()
                
            elif int(self.input.vessel_id) in [2]:
                # drop aft draft in BF and SF
                # pass
                c4_ = ampl.getConstraint('Condition20a1')
                c5_ = ampl.getConstraint('Condition21a1')
                c4_.drop()
                c5_.drop()
                    
            # drop constraints
            for d_ in drop_const:
                print('Drop:', d_)
                d1_ = ampl.getConstraint(d_)
                d1_.drop()
                
            ampl.readData(dat_file)
            ampl.read('run_ampl.run')
            
            solve_result = ampl.getValue('solve_result')
            solve_result_num = int(ampl.getValue('solve_result_num'))
            num_solutions = int(ampl.getValue('Action_Amount.npool')) 
            print(solve_result,solve_result_num, num_solutions)
            
#            solve_result_num, solve_result = 99, 'timelimit'
            if (num_solutions > 0) and (solve_result_num in [0, 2, 403] or solve_result == 'solved'):
                # Solve
                # Get the solution
                
                tot_load = ampl.getData('totloaded').toList()
                plan = ampl.getData('res').toList()
                obj = ampl.getData('totloaded').toList()
                ship_status = ampl.getData('shipStatus').toList()
                ballast_weight = ampl.getData('wtB').toList()
                cargo_loaded = ampl.getData('cargoloaded').toList()

                if self.input.module in ['LOADABLE']:
                    cargo_loaded_port = ampl.getData('cargoloadedport').toList()
                else:
                    cargo_loaded_port = ampl.getData('cargoOper').toList()

                xx = ampl.getData('xx').toList()
                
                # self._other_AMPL_data(ampl)
                
                is_succeed = True
                
                toLoadPortMax_ = -1
                if self.input.module in ['LOADABLE']:
                    toLoadPortMax_ = round(self.input.loadable.info['toLoadPort'].max(),3)
                elif self.input.module in ['LOADING']:
                    toLoadPortMax_ = round(max([j_ for i_, j_ in  self.input.loadable['toLoadPort'].items()]),3)
                
                print("{:.3f}".format(toLoadPortMax_), "{:.3f}".format(tot_load[0][1]))
                
                if round(toLoadPortMax_,3) == round(tot_load[0][1],3):
                    self.full_load = True

            elif solve_result in ['limit']    :
                pass
                
            else:
                message = ['Solve result: ' + solve_result +'. No solution is available!!']
                print(message)
                
                if solve_result in ['infeasible'] and self.IIS:
                    cons = ampl.getData('_conname').toList() # constraint list
                    violated_cons = ampl.getData('_con.iis').toList() # violated constraint list
                    
                    violated_cons_ = []
                    print('The following constraints are violated:')
                    for v_ in violated_cons:
                        if v_[1] not in ['non', '0']:
                            # print(cons[int(v_[0])-1][1])
                            
                            if cons[int(v_[0])-1][1].split('[')[0] not in violated_cons_:
                                violated_cons_.append(cons[int(v_[0])-1][1].split('[')[0])
                                
                                
                    if len(violated_cons_) == 0 :
                        ampl = AMPL()
                        ampl.option['presolve'] = False
                        ampl.read(model_)
                        
                        ## module dependent constraints    
                        if self.input.module in ['LOADABLE']:
                            if self.input.mode not in ['FullManual']:
                                # auto and manual modes
                                c1_ = ampl.getConstraint('Condition112d5') # only for discharging
                                c2_ = ampl.getConstraint('Condition114g2') # only for discharging
                                c1_.drop()
                                c2_.drop()
                                
                            if self.input.mode in ['Manual']:
                                c3_ = ampl.getConstraint('Constr5b') # commingle 98%
                                c3_.drop()
                                
                            if self.input.vessel.info['onboard']:
                                slopP = [t_ for t_ in self.input.vessel.info['slopTank'] if t_[-1] == 'P'][0]
                                if slopP in self.input.vessel.info.get('notOnTop', []):
                                    slp_ = ampl.getConstraint('Condition112g1') # SLP must be used
                                    slp_.drop()
                                    
                                slopS = [t_ for t_ in self.input.vessel.info['slopTank'] if t_[-1] == 'S'][0]
                                if slopS in self.input.vessel.info.get('notOnTop', []): # SLS must be used
                                    sls_ = ampl.getConstraint('Condition112g2')
                                    sls_.drop()
                            
                        elif self.input.module in ['LOADING']:
                            c1_ = ampl.getConstraint('Condition112d5')
                            c2_ = ampl.getConstraint('Condition114g2')
                            c3_ = ampl.getConstraint('Condition01')
                            c1_.drop()
                            c2_.drop()
                            c3_.drop()
                            
                            # drop slop tanks must be used constraints
                            slp_ = ampl.getConstraint('Condition112g1')
                            sls_ = ampl.getConstraint('Condition112g2')
                            slp_.drop()
                            sls_.drop()
                            
                        elif self.input.module in ['DISCHARGE']:
                            cw_ = ampl.getConstraint('Constr13b')
                            cw_.drop()
                            # drop slop tanks must be used constraints
                            # slp_ = ampl.getConstraint('Condition112g1')
                            # sls_ = ampl.getConstraint('Condition112g2')
                            # slp_.drop()
                            # sls_.drop()
                            #
                            wwt_ = ampl.getConstraint('condition24a')
                            wwt_.drop()
                            
                        elif self.input.module in ['DISCHARGING']:
                            
                            # drop slop tanks must be used constraints
                            # c1_ = ampl.getConstraint('Condition112g1')
                            # c2_ = ampl.getConstraint('Condition112g2')
                            # c1_.drop()
                            # c2_.drop()
                            
                            # # 5% different in vol
                            # c3_ = ampl.getConstraint('Condition112a1')
                            # c4_ = ampl.getConstraint('Condition112a2')
                            # c3_.drop()
                            # c4_.drop()
                            
                            cw_ = ampl.getConstraint('Constr13b')
                            cw_.drop()
                            
                        ## vessel dependent constraints    
                        if int(self.input.vessel_id) in [1]:
                            
                            # drop mean draft in BF and SF
                            c4_ = ampl.getConstraint('Condition20a2')
                            c5_ = ampl.getConstraint('Condition21a2')
                            c4_.drop()
                            c5_.drop()
                            
                        elif int(self.input.vessel_id) in [2]:
                            # drop aft draft in BF and SF
                            c4_ = ampl.getConstraint('Condition20a1')
                            c5_ = ampl.getConstraint('Condition21a1')
                            c4_.drop()
                            c5_.drop()
                            
                            
                        ampl.readData(dat_file)
                        ampl.read('run_ampl.run')
                        
                        print('Run AMPL with no presolve')
                        cons = ampl.getData('_conname').toList() # constraint list
                        violated_cons = ampl.getData('_con.iis').toList() # violated constraint list
                        
                        violated_cons_ = []
                        print('The following constraints are violated:')
                        for v_ in violated_cons:
                            if v_[1] not in ['non', '0']:
                                print(cons[int(v_[0])-1][1])
                                
                                if cons[int(v_[0])-1][1].split('[')[0] not in violated_cons_:
                                    violated_cons_.append(cons[int(v_[0])-1][1].split('[')[0])
                        
                        
                        
                    # print({'volatedConstraints':violated_cons_})
                    
                    remove_ = True
                    
                    for l_ in violated_cons_:
                        
                         con_ = CONS.get(l_,None)
                         if con_ not in [None]:
                             message.append(con_)
                         elif remove_ and l_ not in FIXCONS:
                             message.append(l_ + ' violated!!')
                         elif not remove_:
                             message.append(l_ + ' violated!!')

                             
                    print(message)
                         
                    
           
        except Exception as err:
            print('AMPL Error:',err)
            message = err
        
        return {'solve_result':solve_result, 
            'succeed':is_succeed,
            'obj':obj, 
            'plan':plan, 
            'ship_status':ship_status, 
            'ballast_weight':ballast_weight, 
            'cargo_loaded':cargo_loaded, 
            'xx':xx, 
            'cargo_loaded_port':cargo_loaded_port,
            'num_plans':num_solutions,
            'message':message}
    
    def _run_ortools(self):
        
        is_succeed = False
        solve_result, obj, plan, ship_status, ballast_weight, cargo_loaded, xx, cargo_loaded_port = [], [], [], [], [], [], [], []
        num_solutions = 0
        message = []

        try:
            result = vlcc_ortools(self.input)
            status = result['status']
            
            if status in [0,1]:
                solve_result = 'solved' # objective
                tot_load = result['totloaded'] # totloaded
                plan = result['res']
                obj = result['obj']  
                ship_status = result['shipStatus']
                ballast_weight = result['wtB']
                cargo_loaded = result['cargoloaded']
                cargo_loaded_port = result['cargoloadedport'] ###### NEED TO CHANGE
                xx = result['xx']
                num_solutions = 1

                is_succeed = True
                
                # print("{:.3f}".format(self.input.loadable.info['toLoadPort'].max()), "{:.3f}".format(tot_load[0][1]))
                toLoadPortMax_ = -1
                if self.input.module in ['LOADABLE']:
                    toLoadPortMax_ = round(self.input.loadable.info['toLoadPort'].max(),3)
                elif self.input.module in ['LOADING']:
                    toLoadPortMax_ = round(max([j_ for i_, j_ in  self.input.loadable['toLoadPort'].items()]),3)
                
                print("{:.3f}".format(toLoadPortMax_), "{:.3f}".format(tot_load[0][1]))
                
                
            
            else:
                message = ['Solve result: No solution is available!!']
                print(message)
                
        except Exception as err:
            print('ORTOOLS Error:',err)
            message = err
            
        return {'solve_result':solve_result, 
                'succeed':is_succeed,
                'obj':obj,
                'plan':plan, 
                'ship_status':ship_status, 
                'ballast_weight':ballast_weight, 
                'cargo_loaded':cargo_loaded, 
                'xx':xx, 
                'cargo_loaded_port':cargo_loaded_port,
                'message':message,
                'num_plans':num_solutions
                }
        
        
            
    def _other_AMPL_data(self, ampl):
        
        lcg = ampl.getData('lcg_T').toList()
        lcg_tb = ampl.getData('lcg_TB').toList()
        
        # print(lcg)
        # print(lcg_tb)
        
        
        # sf = ampl.getData('sf').toList()
        # bm = ampl.getData('bm').toList()
        
        # SF, BM = [], []
        # for p__, p_ in enumerate(self.input.base_draft):
        #     SF.append([round(d_[3],3) for d_ in sf if d_[0] == 1 and d_[2] == p__+1 ]) # sol, frame, port, sf
        #     BM.append([round(d_[3],3) for d_ in bm if d_[0] == 1 and d_[2] == p__+1 ]) # sol, frame, port, bm
                        
        
        with open('ampl_data.json', 'w') as f_:  
            json.dump({'lcg':lcg, 'lcg_tb':lcg_tb}, f_)

        
        
    def _process_ampl(self, result, num_plans=100):
        
        
        self.plans['obj'] = []
        self.plans['operation'] = []
        self.plans['ship_status'] = []
        self.plans['cargo_status'] = []
        self.plans['constraint'] = []
        self.plans['slop_qty'] = []
        self.plans['cargo_order'] = []
        self.plans['loading_hrs'] = []
        self.plans['topping'] = []
        self.plans['loading_rate'] = []
        
        self.num_plans = min(num_plans,result['num_plans'])
        
        self.ship_status_dep, self.ballast_weight = [], []
        
        self.other_weight, self.initial_ballast_weight = {}, {}
        self.cargo_in_tank = []
        self.loading_rate = []
        self.topping_seq = [] 
        
        for p_ in range(self.num_plans):
            
            commingled_ = False
            tank_cargo_ = {t_:[]  for t_ in self.input.vessel.info['cargoTanks']}
            for q_ in result['xx']:
                if (p_+1) == int(q_[0]): # and q_[3] > .0:
                    xx_ = next((l_ for l_ in result['ship_status'] if abs(l_[-1]) > 0.1 and  q_[1] == l_[1] and q_[2] == l_[2]), None)
                    
                    if xx_ not in [None]:
                        tank_cargo_[q_[2]].append(q_[1])
                    
                    if len(tank_cargo_[q_[2]]) > 1 and self.input.module not in ['DISCHARGE','DISCHARGING']:
                        commingled_ = True
            
            if hasattr(self.input.loadable, "info"):
                operation_ = {str(pp_):{} for pp_ in range(0,self.input.loadable.info['lastVirtualPort']+1)} 
            else:
                operation_ = {str(pp_):{} for pp_ in range(0,self.input.loadable['lastVirtualPort']+1)}
            
            for i_ in result['plan']: # (1.0, 'P101', '1S', 3.0, -10000.0)
                if int(i_[0]) == (p_+1) and round(abs(i_[4]),DEC_PLACE) >= 0.01 and i_[1] in tank_cargo_[i_[2]]:
                    
                    
                    if hasattr(self.input.loadable, "info"):
                        density_ = self.input.loadable.info['parcel'][i_[1]]['maxtempSG']
                    else:
                        density_ = self.input.loadable['parcel'][i_[1]]['maxtempSG']
                        
                    wt_ = round(i_[4],DEC_PLACE)
                    capacity_ = self.input.vessel.info['cargoTanks'][i_[2]]['capacityCubm']
                    info_ = {'parcel':i_[1], 'wt': wt_, 'SG':density_, 
                             'fillRatio': round(i_[4]/density_/capacity_,DEC_PLACE)}
                    # print(i_[2],info_)
                    if i_[2] in operation_[str(int(i_[3]))].keys():
                        operation_[str(int(i_[3]))][i_[2]].append(info_)
                        if self.input.module not in ['DISCHARGE','DISCHARGING']:
                            commingled_ = True
                    else:
                        operation_[str(int(i_[3]))][i_[2]] = [info_]
                        
            self.plans['operation'].append(operation_)
            
            # status at departure: cargo tank only 
            if hasattr(self.input.loadable, "info"):
                ship_status_dep_ = {str(pp_):{} for pp_ in range(0,self.input.loadable.info['lastVirtualPort']+1)} 
            else:
                ship_status_dep_ = {str(pp_):{} for pp_ in range(0,self.input.loadable['lastVirtualPort']+1)} 
            
            for i_ in result['ship_status']: # (1.0, 'P101', '3P', 1.0, 10000.0)
                if int(i_[0]) == (p_+1) and round(i_[4],DEC_PLACE) >= 0.01 and i_[1] in tank_cargo_[i_[2]]:
                    onboard_ = self.input.vessel.info['onboard'].get(i_[2],{}).get('wt',0.)
                    # if onboard_ > 0:
                    #     print(i_[2],i_[1],i_[4],onboard_)
                    #wt_ = round(i_[4] + onboard_ ,DEC_PLACE) 
                    wt_ = i_[4] + onboard_
                    
                    if hasattr(self.input.loadable, "info"):
                        density_ = self.input.loadable.info['parcel'][i_[1]]['maxtempSG']
                    else:
                        density_ = self.input.loadable['parcel'][i_[1]]['maxtempSG']
                    
                    
                    capacity_ = self.input.vessel.info['cargoTanks'][i_[2]]['capacityCubm']
                    vol_ = wt_/density_ 
                    
                    tcg_ = 0.
                    if i_[2] in self.input.vessel.info['tankTCG']['tcg']:
                        tcg_ = np.interp(vol_, self.input.vessel.info['tankTCG']['tcg'][i_[2]]['vol'],
                                         self.input.vessel.info['tankTCG']['tcg'][i_[2]]['tcg'])
                        
                    lcg_ = 0.
                    if i_[2] in self.input.vessel.info['tankLCG']['lcg']:
                        lcg_ = np.interp(vol_, self.input.vessel.info['tankLCG']['lcg'][i_[2]]['vol'],
                                         self.input.vessel.info['tankLCG']['lcg'][i_[2]]['lcg'])
                    
                    if onboard_ > 0:
                        vol1_ = i_[4]/density_
                        fillingRatio_ =  round(vol1_/capacity_,DEC_PLACE)
                    else:
                        fillingRatio_ =  round(vol_/capacity_,DEC_PLACE)

                    
                    if fillingRatio_ > .98:
                        print('**', i_[3], i_[2], fillingRatio_)
                    
                    tankId_ = self.input.vessel.info['tankName'][i_[2]]
                    corrUllage_ = round(self.input.vessel.info['ullage'][str(tankId_)](vol_).tolist(), 6)
                    
                    if hasattr(self.input.loadable, "info"):
                        temp_ = self.input.loadable.info['parcel'][i_[1]]['temperature']
                        api_  = self.input.loadable.info['parcel'][i_[1]]['api']
                    else:
                        temp_ = self.input.loadable['parcel'][i_[1]]['temperature']
                        api_  = self.input.loadable['parcel'][i_[1]]['api']
                    

                    
                    info_ = {'parcel':i_[1], 'wt': round(wt_,DEC_PLACE), 'SG': density_,
                             'fillRatio': fillingRatio_, 'tcg':tcg_, 'lcg':lcg_, 
                             'temperature':temp_,
                             'api':api_,
                             'corrUllage': corrUllage_,
                             'maxTankVolume':capacity_,
                             'vol': vol_}
                    
                    # print(i_[3],i_[2],info_)
                    
                    if i_[2] in ship_status_dep_[str(int(i_[3]))].keys():
                        ship_status_dep_[str(int(i_[3]))][i_[2]].append(info_)
                    else:
                        ship_status_dep_[str(int(i_[3]))][i_[2]] = [info_]
                        
            if commingled_:
                print('Commingled ship_status') 
                for k_, v_ in ship_status_dep_.items():
                    for k1_, v1_ in v_.items():
                        if len(v1_) > 1:
                            
                            if self.input.module in ['LOADABLE']:
                                parcel1_ = self.input.loadable.info['commingleCargo']['parcel1']
                                parcel2_ = self.input.loadable.info['commingleCargo']['parcel2']
                            elif self.input.module in ['LOADING']:
                                parcel1_ = self.input.loading.info['commingle']['parcel1']
                                parcel2_ = self.input.loading.info['commingle']['parcel2']

                            # parcel_ = [v1_[0]['parcel'], v1_[1]['parcel']]
                            parcel_ = [parcel1_, parcel2_]
                            onboard_ = self.input.vessel.info['onboard'].get(k1_,{}).get('wt',0.)
                            # temperature_ = self.input.loadable.info['commingleCargo']['temperature']
                            
                            wt1_ = sum([vv_['wt'] for vv_ in v1_ if vv_['parcel'] == parcel1_]) - onboard_
                            wt2_ = sum([vv_['wt'] for vv_ in v1_ if vv_['parcel'] == parcel2_]) - onboard_
                            
                            weight_ = wt1_ + wt2_ + onboard_
                            
                            capacity_ = self.input.vessel.info['cargoTanks'][k1_]['capacityCubm']
                            
                            wt__ = [wt1_,wt2_]
                            
                            if self.input.module in ['LOADABLE']:
                                api__ = [self.input.loadable.info['commingleCargo']['api1'], self.input.loadable.info['commingleCargo']['api2']]
                                temp__ = [self.input.loadable.info['commingleCargo']['t1'], self.input.loadable.info['commingleCargo']['t2']]
                            elif self.input.module in ['LOADING']:
                                api__ = [self.input.loading.info['commingle']['api1'], self.input.loading.info['commingle']['api2']]
                                temp__ = [self.input.loading.info['commingle']['t1'], self.input.loading.info['commingle']['t2']]
                       
                                
                            api_, temp_ = self._get_commingleAPI(api__, wt__, temp__)
                            
                            if self.input.module in ['LOADABLE']:
                                density_ = self.input.loadable._cal_density(round(api_,2), round(temp_,1))
                            elif self.input.module in ['LOADING']:
                                density_ = self.input.loading._cal_density(round(api_,2), round(temp_,1))
                                
                            vol_ = weight_/density_ 
                            vol1_ = wt1_/density_ 
                            vol2_ = wt2_/density_ 
                            
                            
                            if onboard_ > 0:
                                vol3_ = (wt1_ + wt2_ )/density_
                                fillingRatio_ =  round(vol3_/capacity_,DEC_PLACE)
                            else:
                                fillingRatio_ =  round(vol_/capacity_,DEC_PLACE)
                            
                            if fillingRatio_ > .98:
                                print('**', fillingRatio_)
                            
                            
                            # fillingRatio_ = round(vol_/capacity_,DEC_PLACE)

                            print(parcel1_,parcel2_, k1_, fillingRatio_, round(wt1_/(wt1_+wt2_),2), round(wt2_/(wt1_+wt2_),2), round(api_,2), round(temp_,1), density_, round(weight_,3))
                            
                            # re-run once only
                            # print(self.commingled_ratio)
                            
                            if self.input.module in ['LOADABLE']:
                                cargoweight_ = int(float(self.input.cargoweight)*10)/10
                                obj_ = [round(l_[1],1)  for l_ in result['obj'] if l_[0] == p_+1][0]
                            else:
                                cargoweight_, obj_ = 1,1

                            #if (round(fillingRatio_,3) > 0.98 or obj_ < cargoweight_)  and self.input.module in ['LOADABLE'] and self.input.mode in ['Auto'] and len(self.commingled_ratio) == 0:
                            if (round(fillingRatio_,3) > 0.98)  and self.input.module in ['LOADABLE'] and self.input.mode in ['Auto'] and len(self.commingled_ratio) == 0:

                                print('Need to regenerate commingle plans!!')
                                self.commingled_ratio = {parcel1_:round(wt1_/(wt1_+wt2_),2), 
                                                         parcel2_:round(wt2_/(wt1_+wt2_),2)}
                                self.commingled_temp = {parcel1_:self.input.loadable.info['commingleCargo']['t1'], 
                                                         parcel2_:self.input.loadable.info['commingleCargo']['t2']}
                                
                                return
                                
                                
                                
                                
                            tcg_ = 0.
                            if k1_ in self.input.vessel.info['tankTCG']['tcg']:
                                tcg_ = np.interp(vol_, self.input.vessel.info['tankTCG']['tcg'][k1_]['vol'],
                                                 self.input.vessel.info['tankTCG']['tcg'][k1_]['tcg'])
                                
                            lcg_ = 0.
                            if k1_ in self.input.vessel.info['tankLCG']['lcg']:
                                lcg_ = np.interp(vol_, self.input.vessel.info['tankLCG']['lcg'][k1_]['vol'],
                                                 self.input.vessel.info['tankLCG']['lcg'][k1_]['lcg'])
                                
                            
                            tankId_ = self.input.vessel.info['tankName'][k1_]
                            corrUllage_ = round(self.input.vessel.info['ullage'][str(tankId_)](vol_).tolist(), 6)
                            corrUllage1_ = round(self.input.vessel.info['ullage'][str(tankId_)](vol1_).tolist(), 6)
                            corrUllage2_ = round(self.input.vessel.info['ullage'][str(tankId_)](vol2_).tolist(), 6)

                                  
                            info_ = {'parcel':parcel_, 'wt': round(weight_,3), 'SG': round(density_,4),
                                     'fillRatio': fillingRatio_, 'tcg':tcg_,  'lcg':lcg_,
                                     'temperature':round(temp_,2),
                                     'api':api_,
                                     'wt1':wt1_, 'wt2':wt2_,
                                     'wt1percent':wt1_/(wt1_+wt2_), 'wt2percent':wt2_/(wt1_+wt2_),
                                     'corrUllage':corrUllage_,
                                     'maxTankVolume':capacity_,
                                     'vol':vol_, 'vol1':vol1_, 'vol2':vol2_,
                                     'corrUllage1':corrUllage1_,'corrUllage2':corrUllage2_}
                            
                            # print(info_)
                            
                            ship_status_dep_[k_][k1_] = [info_]
                            
                            # if self.input.mode in ['Auto'] and p_ == 0 and not self.full_load and (fillingRatio_ < 0.98) and abs(self.input.loadable.info['commingleCargo']['temperature'] - temp_) > 0.5:
                            #     self.rerun = True
                            #     self.input.commingle_temperature = temp_
                                # return
                            
                            # print(density_,api_)
                    
                            # print(v1_[0]['wt']/v1_[0]['SG'], v1_[1]['wt']/v1_[1]['SG'], weight_/density_)
                            
            for k_, v_ in self.input.vessel.info['onboard'].items():
                if k_ not in ['totalWeight']:
                    print(k_, 'empty with onboard', v_)
                    wt_ = round(v_['wt'], DEC_PLACE) 
                    density_ = round(v_['wt']/v_['vol'], 4)
                    capacity_ = self.input.vessel.info['cargoTanks'][k_]['capacityCubm']
                    vol_ = v_['vol']
                    
                    tcg_ = 0.
                    if k_ in self.input.vessel.info['tankTCG']['tcg']:
                        tcg_ = np.interp(wt_/density_, self.input.vessel.info['tankTCG']['tcg'][k_]['vol'],
                                         self.input.vessel.info['tankTCG']['tcg'][k_]['tcg'])
                    
                    lcg_ = 0.
                    if k_ in self.input.vessel.info['tankLCG']['lcg']:
                        lcg_ = np.interp(wt_/density_, self.input.vessel.info['tankLCG']['lcg'][k_]['vol'],
                                         self.input.vessel.info['tankLCG']['lcg'][k_]['lcg'])
                    
                    
                    
                    tankId_ = self.input.vessel.info['tankName'][k_]
                    corrUllage_ = round(self.input.vessel.info['ullage'][str(tankId_)](vol_).tolist(), 6)

                        
                    info_ = {'parcel':'onboard', 'wt': wt_, 'SG': density_,
                             'fillRatio': round(v_['vol']/capacity_,DEC_PLACE), 'tcg':tcg_, 'lcg':lcg_, 
                             'temperature': round(v_['temperature'], 2),
                             'corrUllage': corrUllage_,
                             'maxTankVolume': capacity_,
                             'vol':vol_}
                    
                    for k1_, v1_ in ship_status_dep_.items():
                        if not v1_.get(k_, []):
                            ship_status_dep_[k1_][k_] = [info_]
                    
                        
                        
                       
            # ballast status: departure/arrive for loading/discharging port       
            if hasattr(self.input.loadable, "info"):
                ballast_weight_ = {str(pp_):{} for pp_ in range(0,self.input.loadable.info['lastVirtualPort']+1)} 
                # tot_ballast_vol_ = {str(pp_):0. for pp_ in range(0,self.input.loadable.info['lastVirtualPort']+1)} 
                
            else:
                ballast_weight_ = {str(pp_):{} for pp_ in range(0,self.input.loadable['lastVirtualPort']+1)}
#                tot_ballast_vol_ = {str(pp_):0. for pp_ in range(0,self.input.loadable['lastVirtualPort']+1)} 
                
            
            if hasattr(self.input, "mode") and self.input.mode in ['FullManual']:
                
                for k_, v_ in self.input.loadable.info['ballastOperation'].items():
                    for v__ in v_:
                        tank_ = self.input.vessel.info['tankId'][int(v__['tankId'])]
                        density_ = 1.025
                        capacity_ =  self.input.vessel.info['ballastTanks'][tank_]['capacityCubm']
                        wt_ = v__['wt']
                        vol_ = wt_/density_
                        
                        tcg_ = 0.
                        if tank_ in self.input.vessel.info['tankTCG']['tcg']:
                            tcg_ = np.interp(vol_, self.input.vessel.info['tankTCG']['tcg'][tank_]['vol'],
                                              self.input.vessel.info['tankTCG']['tcg'][tank_]['tcg'])
                            
                        lcg_ = 0.
                        if tank_ in self.input.vessel.info['tankLCG']['lcg']:
                            lcg_ = np.interp(vol_, self.input.vessel.info['tankLCG']['lcg'][tank_]['vol'],
                                              self.input.vessel.info['tankLCG']['lcg'][tank_]['lcg'])
                        
                        tankId_ = v__['tankId']    
                        try:
                            corrLevel_ = self.input.vessel.info['ullage'][str(tankId_)](vol_).tolist()
                        except:
                            print('correct level not available:',i_[1], vol_)
                            corrLevel_ = 0.
                        
                        ballast_weight_[k_][tank_] = [{'wt': round(wt_,DEC_PLACE), 'SG':density_,
                                                          'fillRatio': round(v__['wt']/density_/capacity_,DEC_PLACE),
                                                          'tcg':tcg_, 'lcg':lcg_, 
                                                          'corrLevel':round(corrLevel_,3),
                                                          'maxTankVolume':capacity_,
                                                          'vol':vol_}]
                
                
            
            else:
                    
                for i_ in result['ballast_weight']: # (1.0, 'FPTL', 1.0, 5580.1)
                    if int(i_[0]) == (p_+1) and round(i_[3],DEC_PLACE) >= 1:
                        # port_ = self.input.loadable.info['virtualArrDepPort'][str(int(i_[2]))][:-1]
                        # portName_ = self.input.port.info['portOrder'][str(port_)]
                        density_ = 1.025
                        #density_ = self.input.port.info['portRotation'][portName_]['seawaterDensity']
                        capacity_ =  self.input.vessel.info['ballastTanks'][i_[1]]['capacityCubm']
                        wt_ = i_[3]
                        vol_ = wt_/density_
                        
                        
                        tcg_ = 0.
                        if i_[1] in self.input.vessel.info['tankTCG']['tcg']:
                            tcg_ = np.interp(vol_, self.input.vessel.info['tankTCG']['tcg'][i_[1]]['vol'],
                                             self.input.vessel.info['tankTCG']['tcg'][i_[1]]['tcg'])
                            
                        lcg_ = 0.
                        if i_[1] in self.input.vessel.info['tankLCG']['lcg']:
                            lcg_ = np.interp(vol_, self.input.vessel.info['tankLCG']['lcg'][i_[1]]['vol'],
                                             self.input.vessel.info['tankLCG']['lcg'][i_[1]]['lcg'])
                            
                            
                        tankId_ = self.input.vessel.info['tankName'][i_[1]]     
                        try:
                            corrLevel_ = self.input.vessel.info['ullage'][str(tankId_)](vol_).tolist()
                        except:
                            print('correct level not available:',i_[1], vol_)
                            corrLevel_ = 0.
                        
                    
                        ballast_weight_[str(int(i_[2]))][i_[1]] = [{'wt': round(wt_,DEC_PLACE), 
                                                          'SG':density_,
                                                          'fillRatio': round(i_[3]/density_/capacity_,DEC_PLACE),
                                                          'tcg':tcg_, 'lcg':lcg_,
                                                          'corrLevel':round(corrLevel_,3),
                                                          'maxTankVolume':capacity_,
                                                          'vol':vol_}]
                                                   
                        # if k_ not in [str(self.input.port.info['numPort'])+'D']:
                        #     ship_status_[k_]['other'][i_]  = [{'wt': round(v_['wt'],DEC_PLACE), 
                        #                                   'SG':round(v_['wt']/max(1.0,v_['vol']),DEC_PLACE),
                        #                                   'tcg':v_['tcg']}]
            
            
            
            
            
            self.ship_status_dep.append(ship_status_dep_)       
            self.ballast_weight.append(ballast_weight_)       
            self.commingled = commingled_
            
            
            cargo_in_tank_, max_tank_used_ = {}, 0
            # print(p_,'--------------------------------------------------------')
            
            if hasattr(self.input.loadable, "info"):
                parcel_ = self.input.loadable.info['parcel']
            else:
                parcel_ = self.input.loadable['parcel']
            
            for k_, v_ in parcel_.items():
                tanks_ = [i_  for i_,j_ in tank_cargo_.items() if k_ in j_]
                # print(k_,tanks_)
                cargo_in_tank_[k_] = tanks_
                if len(tanks_) > max_tank_used_:
                    max_tank_used_ = len(tanks_)
                    self.max_tank_parcel = k_
                    
            self.cargo_in_tank.append(cargo_in_tank_)
            
            if self.input.module in ['LOADABLE'] or (self.input.module in ['DISCHARGE'] and self.input.loadable.info['backLoadingCargo']):
            
                load_param = {'Manifolds':[1,2,3],
                         'centreTank':[],
                         'wingTank': [],
                         'slopTank': [],
                         'BottomLines': [1,2,3]
                        }
                
                loading_rate_, topping_ = {}, {}
                
                if self.input.module in ['LOADABLE']:
                    cargo_in_tank__ = cargo_in_tank_
                else:
                    # backloading
                    cargo_in_tank__ = {k_:v_ for k_, v_ in cargo_in_tank_.items() if k_ in self.input.loadable.info['backLoadingCargo']}
                    
                
                for k_, v_ in cargo_in_tank__.items():
                    load_param['centreTank'], load_param['wingTank'], load_param['slopTank'] = [], [], []
                    tank_num_ = 0
                    for t_ in v_:
                        if t_[-1] in ['C']:
                            load_param['centreTank'].append(t_)
                            tank_num_ += 1
                        elif t_ in self.input.vessel.info['slopTank']: #['SLS','SLP']:
                            load_param['slopTank'].append(t_)
                            tank_num_ += 1
                        else:
                            load_param['wingTank'].append(t_)
                            tank_num_ += 1
                    
                    if tank_num_ == 1:
                        add_ = 0.5
                    elif tank_num_ == 2:
                        add_ = 1.0
                    else:
                        add_ = 1.5
                    loading_rate_[k_] = (self._cal_max_rate(load_param), add_)
                    topping_[k_] = self._topping_seq(v_)
                    
                self.loading_rate.append(loading_rate_)
                self.topping_seq.append(topping_)
                    
                
        if self.input.module in ['LOADABLE', 'DISCHARGE']:
            # add ROB    
            other_weight_ = {str(pp_):{} for pp_ in range(0,self.input.loadable.info['lastVirtualPort']+1)} 
            for i_, j_ in self.input.vessel.info['onhand'].items():
                for k_, v_ in j_.items():
                    info_ =  [{'wt': round(v_['wt'],DEC_PLACE), 
                               'SG':round(v_['wt']/max(1.0,v_['vol']),DEC_PLACE),
                               'tcg':v_['tcg'], 'lcg':v_['lcg'], 'vol': v_['vol']}]
            
                    for k1_, v1_ in self.input.loadable.info['virtualArrDepPort'].items():
                        if v1_ == k_:
                            other_weight_[k1_][i_] =  info_
                            
            self.other_weight = other_weight_
            
        elif self.input.module in ['LOADING']:
            # initial ROB
            
            # info_ = [{'wt': wt_, 'SG':density_, "vol":vol_, 'tcg':tcg_, 'lcg':lcg_}]
            initial_ROB_ = {}
            for k_, v_ in self.input.loading.info['ROB'][0].items():
                info_ = {}
                info_['wt'] = v_[0]['quantityMT']
                info_['vol'] = v_[0]['quantityM3']
                info_['SG'] = round(v_[0]['quantityMT']/v_[0]['quantityM3'],2)
                info_['tcg'] = v_[0]['tcg']
                info_['lcg'] = v_[0]['lcg']
                
                initial_ROB_[k_] = [info_]
                
            
            # final ROB
            final_ROB_ = {}
            for k_, v_ in self.input.loading.info['ROB'][1].items():
                info_ = {}
                info_['wt'] = v_[0]['quantityMT']
                info_['vol'] = v_[0]['quantityM3']
                info_['SG'] = round(v_[0]['quantityMT']/v_[0]['quantityM3'],2)
                info_['tcg'] = v_[0]['tcg']
                info_['lcg'] = v_[0]['lcg']
                
                final_ROB_[k_] = [info_]
            
            other_weight_ = {}
            for pp_ in range(0,self.input.loadable['lastVirtualPort']+1):
                other_weight_[str(pp_)] = {}
                
                if pp_ == 0:
                    other_weight_[str(pp_)] = initial_ROB_
                else:
                    other_weight_[str(pp_)] = final_ROB_
            
           
            self.other_weight = other_weight_
            
        elif self.input.module in ['DISCHARGING']:
            # initial ROB
            
            # info_ = [{'wt': wt_, 'SG':density_, "vol":vol_, 'tcg':tcg_, 'lcg':lcg_}]
            initial_ROB_ = {}
            for k_, v_ in self.input.info['ROB'][0].items():
                info_ = {}
                info_['wt'] = v_[0]['quantityMT']
                info_['vol'] = v_[0]['quantityM3']
                info_['SG'] = round(v_[0]['quantityMT']/v_[0]['quantityM3'],2)
                info_['tcg'] = v_[0]['tcg']
                info_['lcg'] = v_[0]['lcg']
                
                initial_ROB_[k_] = [info_]
                
            
            # final ROB
            final_ROB_ = {}
            for k_, v_ in self.input.info['ROB'][1].items():
                info_ = {}
                info_['wt'] = v_[0]['quantityMT']
                info_['vol'] = v_[0]['quantityM3']
                info_['SG'] = round(v_[0]['quantityMT']/v_[0]['quantityM3'],2)
                info_['tcg'] = v_[0]['tcg']
                info_['lcg'] = v_[0]['lcg']
                
                final_ROB_[k_] = [info_]
            
            other_weight_ = {}
            for pp_ in range(0,self.input.loadable.info['lastVirtualPort']+1):
                other_weight_[str(pp_)] = {}
                
                if pp_ == 0:
                    other_weight_[str(pp_)] = initial_ROB_
                else:
                    other_weight_[str(pp_)] = final_ROB_
            
           
            self.other_weight = other_weight_
            
            
            
        self.initial_cargo_weight = {}
        if self.input.module in ['LOADABLE', 'DISCHARGE']:
            
            for  k_, v_ in self.input.loadable.info['preloadOperation'].items():
                density_ = self.input.loadable.info['parcel'][k_]['maxtempSG']
                temp_ = self.input.loadable.info['parcel'][k_]['temperature']
                api_ = self.input.loadable.info['parcel'][k_]['api']
                for k1_, v1_ in v_.items():
                    
                    
                    
                    tankId_ = self.input.vessel.info['tankName'][k1_]
                    vol_ = v1_/density_
                    capacity_ = self.input.vessel.info['cargoTanks'][k1_]['capacityCubm']
                    
#                    print(k1_,v1_, vol_/capacity_)
                    
                    tcg_data_ = self.input.vessel.info['tankTCG']['tcg'][k1_] # tcg_data
                    lcg_data_ = self.input.vessel.info['tankLCG']['lcg'][k1_] # lcg_data
                    
                    tcg_ = np.interp(vol_, tcg_data_['vol'], tcg_data_['tcg'])
                    lcg_ = np.interp(vol_, lcg_data_['vol'], lcg_data_['lcg'])
                    
                    corrUllage_ = round(self.input.vessel.info['ullage'][str(tankId_)](vol_).tolist(), 6)
                    
                    fr_ = round(vol_/self.input.vessel.info['cargoTanks'][k1_]['capacityCubm'], DEC_PLACE)
                    
                    info_ = {'parcel':k_, 'wt': round(v1_,1), 'SG': density_,
                                     'fillRatio': fr_, 'tcg':tcg_,  'lcg':lcg_,
                                     'temperature':temp_,
                                     'api':api_,
                                     'corrUllage':corrUllage_
                                     }
                    
                    self.initial_cargo_weight[k1_] = [info_]
            
            # add onboard
            for k_, v_ in self.ship_status_dep[0]['0'].items():
                self.initial_cargo_weight[k_] = v_
                
                    
                    
        elif self.input.module in ['DISCHARGING']:
                         
            for k_, v_ in self.input.info['cargo_plans'][0].items():
                
                tankId_ = self.input.vessel.info['tankName'][k_]
                
                if len(v_) == 1:
                    vol_ = v_[0]['quantityM3']
                    
                    if vol_ > 0:
                        corrUllage_ = round(self.input.vessel.info['ullage'][str(tankId_)](vol_).tolist(), 6)
                    else:
                        corrUllage_ = self.input.vessel.info['ullageEmpty'][str(tankId_)]
                        # corrUllage1_ = round(self.input.vessel.info['ullage'][str(tankId_)](vol_).tolist(), 6)
                        # print(k_, vol_, corrUllage_, corrUllage1_)
                    
                    info_ = {'parcel':v_[0]['cargo'], 'wt': round(v_[0]['quantityMT'],1), 'SG': v_[0]['SG'],
                                         'fillRatio': None, 'tcg':v_[0]['tcg'],  'lcg':v_[0]['lcg'],
                                         'temperature':v_[0]['temperature'],
                                         'api':v_[0]['api'],
                                         'corrUllage':corrUllage_
                                         }
                    
                    self.initial_cargo_weight[k_] = [info_]
                
                else:
                    exit()
                    
                
        elif self.input.module in ['LOADING']:
            
            for k_, v_ in self.input.loading.info['cargo_plans'][0].items():
                
                tankId_ = self.input.vessel.info['tankName'][k_]
                
                if len(v_) == 1:
                    vol_ = v_[0]['quantityM3']
                    corrUllage_ = round(self.input.vessel.info['ullage'][str(tankId_)](vol_).tolist(), 6)
                    
                    info_ = {'parcel':v_[0]['cargo'], 'wt': round(v_[0]['quantityMT'],1), 'SG': v_[0]['SG'],
                                         'fillRatio': None, 'tcg':v_[0]['tcg'],  'lcg':v_[0]['lcg'],
                                         'temperature':v_[0]['temperature'],
                                         'api':v_[0]['api'],
                                         'corrUllage':corrUllage_
                                         }
                    
                    self.initial_cargo_weight[k_] = [info_]
                
                else:
                    
                    parcel1_ = v_[0]['cargo']
                    parcel2_ = v_[1]['cargo']
                    parcel_ = [parcel1_, parcel2_]
                            
                    onboard_ = self.input.vessel.info['onboard'].get(k_,{}).get('wt',0.)
                    # temperature_ = self.input.loadable.info['commingleCargo']['temperature']
                    
                    wt1_ = sum([vv_['quantityMT'] for vv_ in v_ if vv_['cargo'] == parcel1_]) - onboard_
                    wt2_ = sum([vv_['quantityMT'] for vv_ in v_ if vv_['cargo'] == parcel2_]) - onboard_
                    
                    weight_ = wt1_ + wt2_ + onboard_
                    
                    capacity_ = self.input.vessel.info['cargoTanks'][k_]['capacityCubm']
                    
                    wt__ = [wt1_,wt2_]
                    
                    
                    api__ = [self.input.loading.info['commingle']['api1'], self.input.loading.info['commingle']['api2']]
                    temp__ = [self.input.loading.info['commingle']['t1'], self.input.loading.info['commingle']['t2']]
               
                        
                    api_, temp_ = self._get_commingleAPI(api__, wt__, temp__)
                    
                    density_ = self.input.loading._cal_density(round(api_,2), round(temp_,1))
                        
                    vol_ = weight_/density_ 
                    vol1_ = wt1_/density_
                    vol2_ = wt2_/density_
                    
                    fillingRatio_ = round(vol_/capacity_,DEC_PLACE)
                    print(parcel1_,parcel2_, k_, fillingRatio_, round(wt1_/(wt1_+wt2_),2), round(wt2_/(wt1_+wt2_),2), round(api_,2), round(temp_,1), density_, round(weight_,3))
                    
                    tcg_ = 0.
                    if k_ in self.input.vessel.info['tankTCG']['tcg']:
                        tcg_ = np.interp(vol_, self.input.vessel.info['tankTCG']['tcg'][k_]['vol'],
                                         self.input.vessel.info['tankTCG']['tcg'][k_]['tcg'])
                        
                    lcg_ = 0.
                    if k_ in self.input.vessel.info['tankLCG']['lcg']:
                        lcg_ = np.interp(vol_, self.input.vessel.info['tankLCG']['lcg'][k_]['vol'],
                                         self.input.vessel.info['tankLCG']['lcg'][k_]['lcg'])
                        
                    
                    tankId_ = self.input.vessel.info['tankName'][k_]
                    corrUllage_ = round(self.input.vessel.info['ullage'][str(tankId_)](vol_).tolist(), 6)
                    
                    corrUllage1_ = round(self.input.vessel.info['ullage'][str(tankId_)](vol1_).tolist(), 6)
                    corrUllage2_ = round(self.input.vessel.info['ullage'][str(tankId_)](vol2_).tolist(), 6)
                    
                          
                    info_ = {'parcel':parcel_, 'wt': round(weight_,3), 'SG': round(density_,4),
                             'fillRatio': fillingRatio_, 'tcg':tcg_,  'lcg':lcg_,
                             'temperature':round(temp_,2),
                             'api':api_,
                             'wt1':wt1_, 'wt2':wt2_,
                             'wt1percent':wt1_/(wt1_+wt2_), 'wt2percent':wt2_/(wt1_+wt2_),
                             'corrUllage':corrUllage_,
                             'maxTankVolume':capacity_,
                             'vol':vol_, 'vol1':vol1_, 'vol2':vol2_, 
                             'corrUllage1':corrUllage1_,'corrUllage2':corrUllage2_}
                    
                    self.initial_cargo_weight[k_] = [info_]
                    
        if self.input.module in ['LOADABLE']:    
            initial_ballast_weight_ = {} 
            density_ = 1.025
            init_ballast_ = ballast_weight_['0']
            
            # add ballast for first arrival port
            for i_, j_ in init_ballast_.items():
                
                capacity_ =  self.input.vessel.info['ballastTanks'][i_]['capacityCubm']
                wt_ = j_[0]['wt']
                vol_ = wt_/density_
                
                tcg_ = 0.
                if i_ in self.input.vessel.info['tankTCG']['tcg']:
                    tcg_ = np.interp(vol_, self.input.vessel.info['tankTCG']['tcg'][i_]['vol'],
                                          self.input.vessel.info['tankTCG']['tcg'][i_]['tcg'])
                
                lcg_ = 0.
                if i_ in self.input.vessel.info['tankLCG']['lcg']:
                    lcg_ = np.interp(vol_, self.input.vessel.info['tankLCG']['lcg'][i_]['vol'],
                                          self.input.vessel.info['tankLCG']['lcg'][i_]['lcg'])
                    
                tankId_ = self.input.vessel.info['tankName'][i_]     
                try:
                    corrLevel_ = self.input.vessel.info['ullage'][str(tankId_)](vol_).tolist()
                except:
                    print(i_, vol_, ': correctLevel not available!!')
                    corrLevel_ = 0.
                
                initial_ballast_weight_[i_] = [{'wt': round(wt_,DEC_PLACE),
                                                'SG':density_,
                                                'fillRatio': round(wt_/density_/capacity_,DEC_PLACE),
                                                'tcg':tcg_, 'lcg':lcg_,
                                                'corrLevel':round(corrLevel_,3),
                                                'maxTankVolume':capacity_,
                                                'vol':vol_}]
            self.initial_ballast_weight = initial_ballast_weight_
            
            
        elif self.input.module not in ['LOADING']:
                                
            initial_ballast_weight_ = {} 
            density_ = 1.025
            # add ballast for first arrival port
            for i_, j_ in self.input.vessel.info['initBallast']['wt'].items():
                
                capacity_ =  self.input.vessel.info['ballastTanks'][i_]['capacityCubm']
                wt_ = j_
                vol_ = wt_/density_
                
                tcg_ = 0.
                if i_ in self.input.vessel.info['tankTCG']['tcg']:
                    tcg_ = np.interp(vol_, self.input.vessel.info['tankTCG']['tcg'][i_]['vol'],
                                          self.input.vessel.info['tankTCG']['tcg'][i_]['tcg'])
                
                lcg_ = 0.
                if i_ in self.input.vessel.info['tankLCG']['lcg']:
                    lcg_ = np.interp(vol_, self.input.vessel.info['tankLCG']['lcg'][i_]['vol'],
                                          self.input.vessel.info['tankLCG']['lcg'][i_]['lcg'])
                    
                tankId_ = self.input.vessel.info['tankName'][i_]     
                try:
                    corrLevel_ = self.input.vessel.info['ullage'][str(tankId_)](vol_).tolist()
                except:
                    print(i_, vol_, ': correctLevel not available!!')
                    corrLevel_ = 0.
                
                initial_ballast_weight_[i_] = [{'wt': round(wt_,DEC_PLACE),
                                                'SG':density_,
                                                'fillRatio': round(j_/density_/capacity_,DEC_PLACE),
                                                'tcg':tcg_, 'lcg':lcg_,
                                                'corrLevel':round(corrLevel_,3),
                                                'maxTankVolume':capacity_,
                                                'vol':vol_}]
            self.initial_ballast_weight = initial_ballast_weight_
            
        else:
            
            self.initial_ballast_weight = {}
            for k_, v_ in self.input.loading.info['ballast'][0].items():
                info_ = {}
                info_['wt'] = v_[0]['quantityMT']
                info_['vol'] = v_[0]['quantityM3']
                info_['SG'] = 1.025
                info_['tcg'] = v_[0]['tcg']
                info_['lcg'] = v_[0]['lcg']
                
                tankId_ = self.input.vessel.info['tankName'][k_]     
                try:
                    corrLevel_ = self.input.vessel.info['ullage'][str(tankId_)](float(info_['vol'])).tolist()
                except:
                    print(k_, vol_, ': correctLevel not available!!')
                    corrLevel_ = 0.
                info_['corrLevel'] = round(corrLevel_,3)
                
                self.initial_ballast_weight[k_] = [info_]
                
                
                
            
    def _process_checking_plans(self, result):
        
        ## still in virtual port 
        for p_ in range(self.num_plans):
            ship_status_dep_ = self.ship_status_dep[p_]
            ballast_weight_ = self.ballast_weight[p_]
            
            # switch from departure only to departure/arrive for loading/discharging port
            ship_status_, cargo_status_ = {}, {}
            
            if hasattr(self.input.loadable, "info"):
                port_ = self.input.loadable.info['lastVirtualPort']
            else:
                port_ = self.input.loadable['lastVirtualPort']
                
            
            for i_ in range(0, port_+1):
                
                if i_ == port_ and self.input.module not in ['LOADING', 'DISCHARGE','DISCHARGING']:
                    break
                
                ship_status_[str(i_)] = {'cargo':{},'ballast':{},'other':{}}
                if i_ == 0:
                    ship_status_[str(i_)]['ballast'] = self.initial_ballast_weight
                    ship_status_[str(i_)]['cargo'] = self.initial_cargo_weight
                else:
                    ship_status_[str(i_)]['ballast'] = ballast_weight_[str(i_)]
                    ship_status_[str(i_)]['cargo'] = ship_status_dep_[str(i_)]
                
                ship_status_[str(i_)]['other'] = self.other_weight[str(i_)]
                
                cargo_status_[str(i_)] = {k_[1]:round(k_[3],3) for k_  in result['cargo_loaded_port'] if k_[0] == p_+1 and k_[2] == i_}
                
                
            self.plans['ship_status'].append(ship_status_)
            self.plans['cargo_status'].append(cargo_status_)
            self.plans['obj'].append(round(result['obj'][p_][1],3))
            
            ##--------------------------------------------------------------
            slop_qty_ = {}
            
            for k_, v_ in ship_status_[str(port_-1)]['cargo'].items():
                if k_ in self.input.vessel.info['slopTank']: #['SLS', 'SLP']:
                    if v_[0]['parcel'] not in slop_qty_.keys():
                        slop_qty_[v_[0]['parcel']]  = 0.
                        
                    slop_qty_[v_[0]['parcel']] += v_[0]['wt']
            self.plans['slop_qty'].append(slop_qty_)
            ##--------------------------------------------------------------
            
            if hasattr(self.input.loadable, "info") and self.input.module in ['LOADABLE'] or \
                (self.input.module in ['DISCHARGE'] and self.input.loadable.info['backLoadingCargo']):
                
                if self.input.module in ['LOADABLE']:
                    self.plans['cargo_order'].append(self.input.loadable.info['cargoOrder'])
            
            ##--------------------------------------------------------------- 
                if self.input.module in ['LOADABLE']:
                    cargo_ = cargo_status_[str(self.input.loadable.info['lastVirtualPort']-1)]
                else:
                    cargo_ = {c_: 0.0  for c_ in self.input.loadable.info['backLoadingCargo']}
                    for c_ in self.input.loadable.info['backLoadingCargo']:
                        for k_, v_ in self.input.loadable.info['operation'][c_].items():
                            if cargo_[c_] < v_:
                                cargo_[c_] = v_
                #cargo_ = {}
                #for k_, v_ in cargo_status_.items():
                #    for k__, v__ in v_.items():
                #        if v__ > 0.:
                #            cargo_[k__] = v__
                loading_hrs_ = {}
                for k_, v_ in cargo_.items():
                    loading_hrs_[k_] = (v_/self.input.loadable.info['parcel'][k_]['SG']/self.loading_rate[p_][k_][0],
                                        self.loading_rate[p_][k_][1])
                
                self.plans['loading_hrs'].append(loading_hrs_)
                                    
            
        
        self.plans['cargo_tank'] = self.cargo_in_tank
        self.plans['topping'] = self.topping_seq
        self.plans['loading_rate'] = self.loading_rate
            
            
            # if self.input.loadable.info['rotationCargo']:
            #     self.plan['constraint'].append({str(self.input.loadable.info['rotationCargo']):'ok'})
            
        
        # with open('ship_status.json', 'w') as fp:
        #     json.dump(self.plan['ship_status'], fp)            
                    
    
            
    def _get_commingleAPI(self, api, weight, temp):
        weight_api_ , weight_temp_ = 0., 0.
        
        sg60_ = [141.5/(a_+131.5) for a_ in api]
        t13_ = [(535.1911/(a_+131.5)-0.0046189)*0.042 for a_ in api]
        vol_bbls_60_ = [w_/t_ for (w_,t_) in zip(weight,t13_)]
        
        weight_sg60_ = sum([v_*s_ for (v_,s_) in zip(vol_bbls_60_,sg60_)])/sum(vol_bbls_60_)
        weight_api_ = 141.5/weight_sg60_ - 131.5
        
        weight_temp_ = sum([v_*s_ for (v_,s_) in zip(vol_bbls_60_,temp)])/sum(vol_bbls_60_)
        
        return weight_api_, weight_temp_
    
    ## for DISCHARGING  ----------------------------------------------------------------------------------
    def gen_json3(self, constraints, stability_values):
        
        self.timeStart = {}
        EVENTS = ["initialCondition", "floodSeparator", "warmPumps",
                  "initialRate", "increaseToMaxRate", "dischargingAtMaxRate", 
                  "reducedRate"]
        FINAL_EVENTS = ['Dry Check', 'Slop Discharge', 'Fresh Oil Discharge',  'Final Stripping']
        FINAL_EVENTS1 = {'Dry Check':'dryCheck', 'Slop Discharge':'slopDischarge', \
                         'Fresh Oil Discharge':'freshOilDischarge',  'Final Stripping':'finalStripping'}

        data = {}
        data['message'] = None
        data['processId'] = self.input.process_id
        data['portId'] = self.input.port_id
        data['dischargingInfoId'] = self.input.information_id
        data['hasLoadicator'] = self.input.has_loadicator
        
        data['vesselCode'] = str(self.input.vessel_id)
        data['portCode'] = self.input.port_code
        data['deadweightconstant'] = str(self.input.vessel.info['deadweightConst']['weight'])
        data['provisionalconstant'] = str(0.0)
        # self.plans['ship_status'] = []
        
        if len(self.plans['ship_status']) == 0:
            
            data['message'] = {**self.input.error, **self.plans['message']}
            data['errors'] = self._format_errors(data['message'])
            
            return data
        
        self._get_ballast_info()
        discharging_seq = Discharging_seq(self, stability_values)
        # loading_seq._get_ballast()
        # events
        data["events"] = []
        self.cow = {"topCowTankId":[], "bottomCowTankIds":[], "allCowTankIds":[]}
        # gravity_ = False
        for c__, c_ in enumerate(self.input.discharging.info['discharging_order']):
#            print(c_) 
            info_ = {}
            info_["dsCargoNominationId"] = [int(cc_[1:]) for cc_ in c_]
            info_["cargoNominationId"] = [int(self.input.discharging.info['dsCargoNominationId'][cc_][1:]) for cc_ in c_]
            info_["sequence"] = []
            # first_seq_ = False #c__ == 0
            
            info_ ["driveTank"] = []
            for t_ in self.input.discharging.seq[str(c__+1)]['info']['driveOilTank']:
                info__ = {}
                info__ ["tankShortName"] = t_
                info__ ["tankId"] = self.input.vessel.info['tankName'].get(t_,"")
                info_ ["driveTank"].append(info__)
            
            
            
            for e__, e_ in enumerate(EVENTS):
                info1_ = {"stage": e_}
                # print(e_)
                discharging_seq._stage(info1_, info_["cargoNominationId"], c__+1)
                
                if e_ == 'initialCondition' :
                    self.timeStart[c__+1] = int(info1_['timeStart'])
                # elif e_ == 'initialCondition' and (not gravity_):
                #     self.gTimeStart = -1
                    
                if e_ in ['dischargingAtMaxRate']:
                    for d__, d_ in enumerate(info_['sequence'][3:]):
#                        print('Modified:', d_['stage'])
                        assert d_['stage'] == info_['sequence'][d__+3]['stage']
                        info_['sequence'][d__+3]['deballastingRateM3_Hr'] = info1_.get('iniDeballastingRateM3_Hr', {})
                        info_['sequence'][d__+3]['ballastingRateM3_Hr'] = info1_.get('iniBallastingRateM3_Hr', {})
                        
                        info2_ = {'iniSimDeballastingRateM3_Hr': deepcopy(info1_.get('iniSimDeballastingRateM3_Hr', {})),
                                  'iniSimBallastingRateM3_Hr': deepcopy(info1_.get('iniSimBallastingRateM3_Hr', {}))}
                        
                        # if len(info2_['simIniDeballastingRateM3_Hr']) > 0:
                        for k_, v_ in info2_['iniSimDeballastingRateM3_Hr'].items():
                            info2_['iniSimDeballastingRateM3_Hr'][k_]['timeStart'] = info_['sequence'][d__+3]['timeStart']
                            info2_['iniSimDeballastingRateM3_Hr'][k_]['timeEnd'] = info_['sequence'][d__+3]['timeEnd']
                            
                        for k_, v_ in info2_['iniSimBallastingRateM3_Hr'].items():
                            info2_['iniSimBallastingRateM3_Hr'][k_]['timeStart'] = info_['sequence'][d__+3]['timeStart']
                            info2_['iniSimBallastingRateM3_Hr'][k_]['timeEnd'] = info_['sequence'][d__+3]['timeEnd']
                        
                           
                        info_['sequence'][d__+3]['simDeballastingRateM3_Hr'] = [info2_['iniSimDeballastingRateM3_Hr']]
                        info_['sequence'][d__+3]['simBallastingRateM3_Hr'] = [info2_['iniSimBallastingRateM3_Hr']]
                        
                        # return
                        # info_['sequence'][d__+1]['ballast']['BP1'],  info_['sequence'][d__+1]['ballast']['BP2']
                        # {'timeStart':, 'timeEnd':, "rateM3_Hr":, "quantityM3": }
                        self._get_ballast_pump(info_['sequence'][d__+3], [info1_['port'][0]], c__+1, delay=discharging_seq.delay)
                        
                    self._get_ballast_pump(info1_, info1_['port'] + [info1_['port'][-1]+1], c__+1, delay=discharging_seq.delay)
                    
                    
                    
                    # print(info1_.keys())
                    info1_.pop('iniSimDeballastingRateM3_Hr')
                    info1_.pop('iniSimBallastingRateM3_Hr')
                    info1_.pop('iniDeballastingRateM3_Hr')
                    info1_.pop('iniBallastingRateM3_Hr')
                    info1_.pop('iniTotDeballastingRateM3_Hr')
                    info1_.pop('iniTotBallastingRateM3_Hr')
                    
                    
                    if self.input.discharging.seq[str(c__+1)]['incMaxAndMaxDischarging']:
                        # Max1 == incToMax rate
#                        print('^^^Cleaning MaxDischarging stage')
                        list_ = ['totBallastingRateM3_Hr', 'totDeballastingRateM3_Hr', \
                                 'simDeballastingRateM3_Hr', 'simBallastingRateM3_Hr', \
                                 'simCargoDischargingRatePerTankM3_Hr', 'cargoDischargingRatePerTankM3_Hr',\
                                 'dischargePlanPortWiseDetails']
                        
                        for l_ in list_:
                            if l_ in ['dischargePlanPortWiseDetails']:
                                plan__ = info1_[l_].pop(0)
                            else:
                                info1_[l_].pop(0)
                            
                        list_ = ['ballast', 'cargo']    
                        for l_ in list_:
                            for pp_ in info1_[l_]:
                                info1_[l_][pp_].pop(0)
                                
                        plan__['time'] = str(self.input.discharging.seq[str(c__+1)]['startTime']+60+discharging_seq.delay+discharging_seq.start_time)
                        info_["sequence"][-1]['toLoadicator'] = True
                        info_["sequence"][-1]['jumpStep'] = True
                        info_["sequence"][-1]['dischargePlanPortWiseDetails'] = [plan__]
                        
                        # print(info1_)
                        
                if info1_['stage'] in ['increaseToMaxRate']:
                    self._get_tank_transfer(info1_, c__+1, delay=discharging_seq.delay+discharging_seq.start_time)
                    
                    
                if info1_['stage'] in ['dischargingAtMaxRate']:
                    self._get_tank_transfer(info1_, c__+1, freshOil=True, delay=discharging_seq.delay+discharging_seq.start_time)
                    
                if info1_['stage'] in ['COWStripping', 'dischargingAtMaxRate']:
                    self._get_COW(info1_, c__+1)
                    
                if info1_['stage'] in ['COWStripping', 'reducedRate']:
                    self._get_ballast_pump(info1_, info1_['port'], c__+1, delay=discharging_seq.start1)
                    
                
                info_["sequence"].append(info1_)
                
            if c__+1 == len(self.input.discharging.info['discharging_order']):
                e1_ = 0
                for e__, e_ in enumerate(FINAL_EVENTS):
                    
                    if e_ in self.input.discharging.seq[str(c__+1)]['info']['stages_timing']:
                        e1_ += 1
                        info1_ = {"stage": FINAL_EVENTS1[e_]}
                        discharging_seq._stage(info1_, str(c__+1), c__+1, final_event = e1_)
                        
                        if info1_['stage'] in ['finalStripping', 'freshOilDischarge', 'slopDischarge', 'dryCheck']:
                            self._get_ballast_pump(info1_, info1_['port'], c__+1, delay=discharging_seq.start1)
                        
                        info_["sequence"].append(info1_)
                    
                    
                
                
            data["events"].append(info_)
                
            
        time_end_ = data["events"][-1]["sequence"][-1]["timeEnd"]
        
        data["plans"] = {'arrival':discharging_seq.initial_plan, 'departure':discharging_seq.final_plan}
        data["plans"]['departure']["time"] = time_end_
        
        data["stages"] = discharging_seq.stages
        data["dischargingInformation"] = self.input.discharging_information
        data["dischargingInformation"]['cowPlan']['topCowTankId'] = self.cow['topCowTankId']
        data["dischargingInformation"]['cowPlan']['bottomCowTankIds'] = self.cow['bottomCowTankIds']
        data["dischargingInformation"]['cowPlan']['allCowTankIds'] = self.cow['allCowTankIds']
        data['message'] = {'limits':self.input.limits}
        
        return data
    
    def _get_ballast_pump(self, out, ports, cargo, delay = 0):
        
        start_, end_ = int(out['timeStart']), int(out['timeEnd'])
#        print('bp', out['stage'], start_, end_)
        
        if out['stage'] in ['initialRate', 'increaseToMaxRate']:
            start__ = start_
            end__ = end_
#            print('port', ports[0], start__, end__)
            port = ports[0]
            self._get_ballast_pump_info(out, port, start__, end__)
            
            
        
        elif out['stage'] in ['dischargingAtMaxRate']:
            # print('port', ports)
            last_ = int(self.input.discharging.seq[str(cargo)]['lastMaxDischarging'][14:])
            for p_ in range(1, last_+1):
                if p_ == 1:
                    start__ = start_
                    end__ = out['stageEndTime']['MaxDischarging'+str(p_)]
                elif p_ == last_:
                    start__ = out['stageEndTime']['MaxDischarging'+str(p_-1)]
                    end__ = end_
                else:
                    start__ = out['stageEndTime']['MaxDischarging'+str(p_-1)]
                    end__ =  out['stageEndTime']['MaxDischarging'+str(p_)]
                
#                print('MaxDischarging'+str(p_), 'in port ', ports[p_-1], start__, end__)
                
                port = ports[p_-1]
                self._get_ballast_pump_info(out, port, start__, end__)
                
            
        elif out['stage'] in ['reducedRate', 'COWStripping']:
            for p_ in range(1, int(self.input.discharging.seq[str(cargo)]['lastStripping'][9:])+1):
                
                if p_ == 1:
                    ss_ = self.input.discharging.seq[str(cargo)]['lastMaxDischarging']
                    local_start__ = self.input.discharging.seq[str(cargo)]['gantt'][ss_]['Time']
                else:
                    local_start__ = self.input.discharging.seq[str(cargo)]['gantt']['Stripping'+str(p_-1)]['Time']
                
                local_end__ = self.input.discharging.seq[str(cargo)]['gantt']['Stripping'+str(p_)]['Time']
                
                # start__ = local_start__ + self.input.discharging.seq[str(cargo)]['startTime'] + delay
                # end__ = local_end__ + self.input.discharging.seq[str(cargo)]['startTime'] + delay
                
                start__ = local_start__ +  delay
                end__ = local_end__ + delay
              
                
#                print('Stripping'+str(p_), 'in port ', \
#                      self.input.discharging.seq['stripToPort']['Stripping'+str(p_)+str(cargo)], \
#                         start__, end__ )
                port = self.input.discharging.seq['stripToPort']['Stripping'+str(p_)+str(cargo)]    
                self._get_ballast_pump_info(out, port, start__, end__)
                
        elif out['stage'] in ['finalStripping', 'freshOilDischarge', 'slopDischarge', 'dryCheck']:
            print(out['stage'])
            port = ports    
            start__ = int(out['timeStart'])
            end__ = int(out['timeEnd'])
            self._get_ballast_pump_info(out, port, start__, end__)
                    
    def _get_ballast_pump_info(self, out, port, start__, end__):
                    
        if 'BP1' in self.ballast_info['vol_and_rate'][port]:
            # print('BP1')
            id1_ = self.input.vessel.info['vesselPumps']['ballastPump']['BP1']['pumpId']
            rate_ = self.ballast_info['vol_and_rate'][port]['BP1']
            vol_ = rate_*(end__-start__)/60
            info_ = {'timeStart': str(start__), 'timeEnd': str(end__), \
                      "rateM3_Hr": str(round(rate_,2)), 
                      "quantityM3": str(round(vol_,2))}
#            print('BP1', info_)
            if id1_ not in out['ballast']:
                out['ballast'][id1_] = [info_]
            else:
                out['ballast'][id1_].append(info_)
                
        
        if 'BP2' in self.ballast_info['vol_and_rate'][port]:
            # print('BP2')
            id2_ = self.input.vessel.info['vesselPumps']['ballastPump']['BP2']['pumpId']
            rate_ = self.ballast_info['vol_and_rate'][port]['BP2']
            vol_ = rate_*(end__-start__)/60
            info_ = {'timeStart': str(start__), 'timeEnd': str(end__), \
                      "rateM3_Hr": str(round(rate_,2)), 
                      "quantityM3": str(round(vol_,2))}
#            print('BP2', info_)
            if id2_ not in out['ballast']:
                out['ballast'][id2_] = [info_]
            else:
                out['ballast'][id2_].append(info_)
        
        
        
    def _get_ballast_info(self, first_port = False):
        
        INDEX1 = self.input.config["gantt_chart_ballast_index"] # ballast tank
        # df_ = pd.DataFrame(index=['Time']+INDEX1+['ballastRate', 'deballastRate', 'rate', 'pump']+['BP1','BP2'])
        df_ = {}
        self.ballast_info = {}
        
        pump_ = False 
        max_rate_, max_pump_ = 0, 0
        
        rate, pump = [], {}
        for k_, v_ in self.plans['ship_status'][0].items():
            if k_ not in [0, '0']:
                df_[int(k_)] = {}
                
                if self.input.module in ['DISCHARGING']:
                    df_[int(k_)]['Time'] = self.input.discharging.seq['dischargingRate'][k_]['time']
                    time_diff_ = self.input.discharging.seq['dischargingRate'][k_]['time'][1] -\
                        self.input.discharging.seq['dischargingRate'][k_]['time'][0]
                
                elif self.input.module in ['LOADING']:
                    df_[int(k_)]['Time'] = self.input.loading.seq['loadingRate'][k_]['time']
                    time_diff_ = self.input.loading.seq['ballastLimitTime'].get(int(k_), 0.)
                    
                            
                # print(time_diff_)
                
                if time_diff_ > 0:
                    # print(k_,time_diff_)
                    deballast_, ballast_ = 0., 0.
                    for t_ in INDEX1:
                        v1_ = v_['ballast'][t_][0]['vol'] if t_ in v_['ballast'] else 0.
                        v0_ = self.plans['ship_status'][0][str(int(k_)-1)]['ballast'][t_][0]['vol'] if t_ in self.plans['ship_status'][0][str(int(k_)-1)]['ballast'] else 0.
                        
                        diff_ = v1_ - v0_
                        
                        if diff_ > 0 or diff_ < 0:
                            rate_ = diff_/time_diff_*60
                            if t_[0] in ['W', 'L', 'F']:
                                pump_ = True
                                rate__ = rate_
                            else:
                                rate__ = 0.
                        else:
                            rate_ = 0.
                            rate__ = 0.
                            
                        if rate_ > 0:
                            ballast_ += rate__
                        else:
                            deballast_ += rate__
                            
                        df_[int(k_)][t_] = rate_
                        
                    pump_num_ = 0
                    if pump_:
                        rate_ = max(ballast_,-deballast_)
                        if rate_ > 3500:
                            pump_num_ = 2
                        elif rate_ > 0.:
                            pump_num_ = 1

                    df_[int(k_)]['ballastRate'] = ballast_
                    df_[int(k_)]['deballastRate'] = deballast_
                    df_[int(k_)]['rate'] = max(ballast_,-deballast_)
                    df_[int(k_)]['pump'] = pump_num_
                    max_rate_ = max(max_rate_, df_[int(k_)]['rate'])
                    max_pump_ = max(max_pump_, pump_num_)
                    rate.append(df_[int(k_)]['rate'])
                    pump[int(k_)] = pump_num_
                    
                    # print(k_, pump_num_, df_[int(k_)]['rate'])  
                    
        
        pump_list_ = [pump.get(a_+1, 0) for a_ in range(len(df_))]
        print('ballast pump:', pump_list_)    
        ## to do
        pump_list1_ = deepcopy(pump_list_)
        done_ = False
        while not done_:
            # print(pump_list1_)
            for n__, n_ in enumerate(pump_list1_):
                if n__ in [0]:
                    pass
                elif n__ == len(pump_list1_)-1: 
                    done_ = True
                else:
                    if pump_list1_[n__-1] >= n_  >= pump_list1_[n__+1] or pump_list1_[n__-1] in [0] \
                        or (n_ >= pump_list1_[n__-1] and  n_ >= pump_list1_[n__+1]):
                        pass
                    elif pump_list1_[n__-1] > n_  and pump_list1_[n__+1] > n_:
                        pump_list1_[n__] += 1
                        break
                            
        print(pump_list1_)
        pump1 = pump_list1_
        print('ballast pump:', pump1)

        op_pump_ = {'BP1':[100,-1], 'BP2':[100,-1]}
        for c_, col_ in enumerate(df_):
            if df_[col_].get('pump', 0) > 0:
                # print(col_, rate_)
                rate_ = df_[col_]['rate']
                max_pump_ = pump1[c_]
                if max_pump_ == 1:
                    df_[col_]['BP1'] = rate_
                    if round(rate_) > 0.:
                        op_pump_['BP1'][0] = min(op_pump_['BP1'][0], col_)
                        op_pump_['BP1'][1] = max(op_pump_['BP1'][1], col_)
                        
                else:
                    df_[col_]['BP1'] = rate_/2
                    df_[col_]['BP2'] = rate_/2
                    
                    if round(rate_) > 0.:
                        op_pump_['BP1'][0] = min(op_pump_['BP1'][0], col_)
                        op_pump_['BP1'][1] = max(op_pump_['BP1'][1], col_)
                    
                        op_pump_['BP2'][0] = min(op_pump_['BP2'][0], col_)
                        op_pump_['BP2'][1] = max(op_pump_['BP2'][1], col_)
                    
        self.ballast_info['vol_and_rate'] = df_ # local time
        self.ballast_info['startStop'] = op_pump_
        print(op_pump_)
        
    
    def _get_tank_transfer(self, out, cargo_order, freshOil = False, delay = 0):

        data_ = self.input.discharging.seq[str(cargo_order)]['info']
        
        if not freshOil and data_['tankTransfer']:
#            print('tankTransfer:', data_['tankTransfer'])
            info_ = self._get_tank_transfer_info(cargo_order, 'tankTransfer', delay = delay)
            # info_['start']
            tcp_ = info_.pop('TCP')
            out["transfer"] = [info_]
            out["TCP"] = tcp_
            
        if freshOil and data_['freshOilDischarge']:
            print('FreshOil:', data_['freshOilDischarge'])
            info_ = self._get_tank_transfer_info(cargo_order, 'freshOilDischarge', delay = delay)
            # info_['start']
            tcp_ = info_.pop('TCP')
            out["transfer"] = [info_]
            out["TCP"] = tcp_

    def _get_tank_transfer_info(self, cargo_order, purpose, delay = 0):
        
#        print(purpose)
        PURPOSE = {'tankTransfer': 'Tank Transfer', 'freshOilDischarge': 'Fresh Oil Transfer'}
        purpose_ = PURPOSE[purpose]
        
        data_ = self.input.discharging.seq[str(cargo_order)]['info']
        data1_ = data_['gantt_chart_operation_end']
        data2_ = data_['gantt_chart_volume']
        data3_ = data_['fixedPumpTimes']
        
        if len(data_[purpose]) == 2:
            from_, to_ = [data_[purpose][0]], data_[purpose][1]
            
        elif len(data_[purpose]) == 3:
            from_, to_ = [data_[purpose][0], data_[purpose][1]], data_[purpose][2]
            
        fromId_ = [self.input.vessel.info['tankName'][t_] for t_ in from_]
        toId_ = self.input.vessel.info['tankName'][to_]
        
        df_ = data1_[data1_.index == to_].to_dict('split') 
        
        ind_ = [d__  for d__, d_ in enumerate(df_['data'][0]) if d_ == purpose_]
        
        start_ =  df_['columns'][ind_[0]-1]
        end_ =  df_['columns'][ind_[-1]]
        
        print(purpose, start_, end_, str(int(start_+self.timeStart[cargo_order])), str(int(end_+self.timeStart[cargo_order])))
        
        info_ = {}
        info_["fromTankShortName"] = from_
        info_["fromTankId"] = fromId_
        info_["toTankShortName"] = [to_]
        info_["toTankId"] = [toId_]
        
        info_["timeStart"] = str(int(start_+self.timeStart[cargo_order]))
        info_["timeEnd"] = str(int(end_+self.timeStart[cargo_order]))
        info_['purpose'] = 'strip' if purpose == "tankTransfer" else 'freshOil'
        parcel_ = self.input.discharging.info['tank_cargo'][from_[0]]
        info_["cargoNominationId"] = int(parcel_[1:])
        info_["dsCargoNominationId"] = int(self.input.discharging.info['cargoNominationId'][parcel_][1:])

        df_ = data2_[data2_.index == to_].to_dict('split') 
        toStartVol_ = 0. # 
        toEndInd_ = [d__ for d__, d_ in enumerate(df_['columns']) if d_ >= end_][0]
        toEndVol_ = df_['data'][0][toEndInd_]
#        print(to_, toStartVol_, toEndVol_)
        
        df_ = data2_[data2_.index == from_[0]].to_dict('split') 
        fromEndVol_ = df_['data'][0][toEndInd_]
        fromStartVol_ = fromEndVol_ + toEndVol_
#        print(from_, fromStartVol_, fromEndVol_)
                   
        density_ = self.input.discharging.info['density'][parcel_]
        fromStartWt_ = fromStartVol_*density_
        fromEndWt_ = fromEndVol_*density_
        toStartWt_ = toStartVol_*density_
        toEndWt_ = toEndVol_*density_
        
        info_['startQuantity'] = {fromId_[0]: str(round(fromStartWt_,1)), toId_:str(round(toStartWt_,1))}
        info_['endQuantity'] = {fromId_[0]:str(round(fromEndWt_,1)), toId_:str(round(toEndWt_,1))}
        if len(data_[purpose]) == 3:
            info_['startQuantity'][fromId_[1]] = str(round(fromStartWt_,1))
            info_['endQuantity'][fromId_[1]] = str(round(fromEndWt_,1))
            
        
        fromStartUll_ = self.input.vessel.info['ullage'][str(fromId_[0])](fromStartVol_).tolist()
        fromEndUll_ = self.input.vessel.info['ullage'][str(fromId_[0])](fromEndVol_).tolist()
        toStartUll_ = self.input.vessel.info['ullage'][str(toId_)](toStartVol_).tolist()
        toEndUll_ = self.input.vessel.info['ullage'][str(toId_)](toEndVol_).tolist()
        
        info_['startUllage'] = {fromId_[0]: str(round(fromStartUll_,3)), toId_:str(round(toStartUll_,3))}
        info_['endUllage'] =  {fromId_[0]:str(round(fromEndUll_,3)), toId_:str(round(toEndUll_,3))}
        if len(data_[purpose]) == 3:
            info_['startUllage'][fromId_[1]] = str(round(fromStartUll_,3))
            info_['endUllage'][fromId_[1]] = str(round(fromEndUll_,3))

#        print('tankToTank:', info_)

        local_time_start_ = int(info_['timeStart']) - self.input.discharging.seq[str(cargo_order)]['startTime'] - delay
                            
        pump_ = [k_ for k_, v_ in self.input.discharging.seq[str(cargo_order)]['pump'].items() \
                  if "TCP" in k_ and int(v_[0]) <= local_time_start_ <= int(v_[1])]# and v_[0] <= time_end__ <= v_[1] ]
            
#        print('pump used', pump_, local_time_start_)
        
        id_ = self.input.vessel.info['cargoPumpId']['TCP']['id']
        
        rate_ = round(toEndVol_/(int(info_['timeEnd'])-int(info_['timeStart']))*60,2)
        info_["TCP"] = {}
        info_["TCP"][id_] = [{"rateM3_Hr": str(rate_),
                            "quantityM3": str(toEndVol_),
                            "timeStart": info_['timeStart'],
                            "timeEnd": info_['timeEnd']}]

        return info_

    def _get_COW(self, out, cargo_order):
        
        empty_tank__ = self.input.discharging.info['stripping_tanks'][cargo_order]
        cow_tanks_ = self.input.discharging.seq[str(cargo_order)]['info']['tanksCOWed']
        tank_ = self.input.discharging.seq[str(cargo_order)]['info']['tanksDischarged']
        
        empty_tank_ = [t_ for t_ in empty_tank__ if t_ in tank_] + cow_tanks_
        
        early_cow_ = list(self.input.discharging.seq[str(cargo_order)]['info']['tanksEarlyCOWed'])
        
        if out['stage'] in ['dischargingAtMaxRate']:
            cow_tanks_ = early_cow_
            empty_tank_ = []
            tank_ = early_cow_
        else:
            cow_tanks_ = list(set(cow_tanks_)-set(early_cow_))
            tank_ = list(set(tank_)-set(early_cow_))
        
            
        print('cow:', cow_tanks_)     
        print('strip+cow:', empty_tank_)
        
        if len(cow_tanks_) == 0:
            return
        
#        print('cow:', cow_tanks_)     
#        print('strip+cow:', empty_tank_)
            
        # drive_tank_ = self.input.discharging.seq[str(cargo_order)]['info']['driveOilTank']
        data_ = self.input.discharging.seq[str(cargo_order)]['info']
        data1_ = data_['gantt_chart_operation_end']
        data2_ = data_['gantt_chart_volume']
        # min_start_, max_end_ = 100000, 0
        
        # starting_time_ = 
        for t_ in tank_:
            info_ = {'tankShortName':t_, 'tankId':self.input.vessel.info['tankName'][t_]}
            
            df_ = data1_[data1_.index == t_].to_dict('split') 
            
            strip_ =  [d__  for d__, d_ in enumerate(df_['data'][0]) if d_ == 'Strip']
            if strip_:
                start_ = df_['columns'][strip_[0]-1]
                end_ = df_['columns'][strip_[-1]]
                
                info_["timeStart"] = str(int(start_+self.timeStart[cargo_order]))
                info_["timeEnd"] = str(int(end_+self.timeStart[cargo_order]))
                
                out['stripping'].append(info_)
#                print('Stripping', t_, info_["timeStart"], info_["timeEnd"])
            
            full_cow_ = [d__  for d__, d_ in enumerate(df_['data'][0]) if d_ == 'Full COW']

            if full_cow_:
                start_ = df_['columns'][full_cow_[0]-1]
                end_ = df_['columns'][full_cow_[-1]]
                
                info_["timeStart"] = str(int(start_+self.timeStart[cargo_order]))
                info_["timeEnd"] = str(int(end_+self.timeStart[cargo_order]))
                
                out['Cleaning']['FullClean'].append(info_)
#                print('FullClean', t_, info_["timeStart"], info_["timeEnd"])
                self.cow['allCowTankIds'].append(info_['tankId'])
            
            top_cow_ = [d__  for d__, d_ in enumerate(df_['data'][0]) if d_ == 'Top COW']
            if top_cow_:
                start_ = df_['columns'][top_cow_[0]-1]
                end_ = df_['columns'][top_cow_[-1]]
                
                info_["timeStart"] = str(int(start_+self.timeStart[cargo_order]))
                info_["timeEnd"] = str(int(end_+self.timeStart[cargo_order]))
                
                out['Cleaning']['TopClean'].append(info_)
#                print('TopClean', t_, info_["timeStart"], info_["timeEnd"])
                self.cow['topCowTankId'].append(info_['tankId'])
            
            
            bottom_cow_ = [d__  for d__, d_ in enumerate(df_['data'][0]) if d_ == 'Bottom COW']
            if bottom_cow_:
                start_ = df_['columns'][bottom_cow_[0]-1]
                end_ = df_['columns'][bottom_cow_[-1]]
                
                info_["timeStart"] = str(int(start_+self.timeStart[cargo_order]))
                info_["timeEnd"] = str(int(end_+self.timeStart[cargo_order]))
                
                out['Cleaning']['BtmClean'].append(info_)
#                print('BtmClean', t_, info_["timeStart"], info_["timeEnd"])
                self.cow['bottomCowTankIds'].append(info_['tankId'])
            
            slop_discharge_ = [d_  for d__, d_ in enumerate(df_['data'][0]) if d_ in ['Dry Check', 'Slop Discharge']]
            slop_discharge__ = [d__  for d__, d_ in enumerate(df_['data'][0]) if d_ in ['Slop Discharge']]
            
            if slop_discharge_ and 'Dry Check' not in slop_discharge_:
                
                start_ = df_['columns'][slop_discharge__[0]-1]
                end_ = df_['columns'][slop_discharge__[-1]]
                
                info_["timeStart"] = str(int(start_+self.timeStart[cargo_order]))
                info_["timeEnd"] = str(int(end_+self.timeStart[cargo_order]))
#                print(t_, 'stripping only', info_["timeStart"],info_["timeEnd"])

                for k_, v_ in self.input.discharging.seq[str(cargo_order)]['pump'].items():
                    p1_ = [v__  for v__ in v_ if round(v__,3) == round(start_,3)]
                    p2_ = [v__  for v__ in v_ if round(v__,3) > round(start_,3)]
                    
                    if len(p1_) == 1 and len(p2_) >= 1:
                        pump_ = k_
                        id_ = self.input.vessel.info['cargoPumpId'][pump_]['id']
                        start1_ = p1_[0]+self.timeStart[cargo_order]
                        end1_ = p2_[0]+self.timeStart[cargo_order]
                        
                        df2_ = data2_[data2_.index == t_].to_dict('split') 
                        vol_ = df2_['data'][0][-2]
                        time_diff_ = end1_ - start1_
                        rate_ = vol_/time_diff_*60
                    
                        info___ = {}
                        info___["timeStart"] = str(int(p1_[0] + self.timeStart[cargo_order]))
                        info___["timeEnd"]   = str(int(p2_[0] + self.timeStart[cargo_order]))
                        info___["rateM3_Hr"] = str(round(rate_,2))
                        info___["quantityM3"] = str(round(vol_,2))
                        
                        if id_ in  out['cargo']:
                            out['cargo'][id_].append(info___)
                        else:
                            out['cargo'][id_] = [info___]
                        
                        break
                    
                # out['stripping'].append(info_)
#                print('Slop Discharge', t_, info_["timeStart"], info_["timeEnd"])
                
                
        if len(empty_tank_) > 0:
            # print('open TCP/STrip')
            df_ = data_['fixedPumpTimes'][data_['fixedPumpTimes'].index == 'TCP'].to_dict('split') 
            
            id_ = self.input.vessel.info['cargoPumpId']['TCP']['id']
            open_ = [d__  for d__, d_ in enumerate(df_['data'][0]) if d_ == 'open']
            close_ = [d__  for d__, d_ in enumerate(df_['data'][0]) if d_ == 'close']

            if open_ and close_:
#                print('open TCP, STED')
                start_ =  df_['columns'][open_[-1]]
                end_ =  df_['columns'][close_[-1]]
                
                
                out["TCP"][id_] = [{"rateM3_Hr": "",
                                    "quantityM3": "",
                                    "timeStart": str(int(start_+self.timeStart[cargo_order])),
                                    "timeEnd": str(int(end_+self.timeStart[cargo_order]))}]
                
                id_ = self.input.vessel.info['cargoPumpId']['STPED1']['id']
                out["STPED"][id_] = [{"rateM3_Hr": "",
                                    "quantityM3": "",
                                    "timeStart": str(int(start_+self.timeStart[cargo_order])),
                                    "timeEnd": str(int(end_+self.timeStart[cargo_order]))}]
            else:
#                print('open STP pump')
                df_ = data_['fixedPumpTimes'][data_['fixedPumpTimes'].index == 'Strip Pump'].to_dict('split') 
                
                id_ = self.input.vessel.info['cargoPumpId']['STP']['id']
                open_ = [d__  for d__, d_ in enumerate(df_['data'][0]) if d_ == 'open']
                close_ = [d__  for d__, d_ in enumerate(df_['data'][0]) if d_ == 'close']
                
                start_ =  df_['columns'][open_[0]]
                end_ =  df_['columns'][close_[0]]
                
                out["STP"][id_] = [{"rateM3_Hr": "",
                                    "quantityM3": "",
                                    "timeStart": str(int(start_+self.timeStart[cargo_order])),
                                    "timeEnd": str(int(end_+self.timeStart[cargo_order]))}]
                
            print("cowStartTime", data_['firstCOWTime'])
            out["cowStartTime"] = str(int(data_['firstCOWTime'][1]+self.timeStart[cargo_order])) if data_['firstCOWTime'][1] > 0 else None
    
    ## for LOADING ------------------------------------------------------------------------------------------
    def gen_json1(self, constraints, stability_values):
        
        
        EVENTS = ["initialCondition", "openSingleTank", "initialRate",
                  "openAllTanks", "increaseToMaxRate", "loadingAtMaxRate", 
                  "topping"]
        
        
        
        
        data = {}
        data['message'] = None
        data['processId'] = self.input.process_id
        data['portId'] = self.input.port_id
        data['loadingInfoId'] = self.input.information_id
        data['hasLoadicator'] = self.input.has_loadicator
        
        data['vesselCode'] = self.input.vessel_id
        data['portCode'] = self.input.port_code
        data['deadweightconstant'] = str(self.input.vessel.info['deadweightConst']['weight'])
        data['provisionalconstant'] = str(0.0)
        # data['user'] = self.input.user
        # data['role'] = self.input.role
        # data['hasLoadicator'] = self.input.has_loadicator
        
        if len(self.plans['ship_status']) == 0:
            
            data['message'] = {**self.input.error, **self.plans['message']}
            data['errors'] = self._format_errors(data['message'])
            
            return data
        
        loading_seq = Loading_seq(self, stability_values)
        self._get_ballast_info()
        # events
        data["events"] = []
        
        for c__, c_ in enumerate(self.input.loading.info['loading_order']):
#            print(c_)
            info_ = {}
            info_["cargoNominationId"] = int(c_[1:])
            info_["sequence"] = []
            # first_port_cargo_ = c__ == 0 and self.input.loading.first_loading_port
            # gravity_ = False
            # gravity_ = self.input.first_loading_port and first_cargo_ and (self.input.loading.max_loading_rate < 15000)
            # print('gravity:', gravity_)
            
            for e__, e_ in enumerate(EVENTS):
                info1_ = {"stage": e_}
                loading_seq._stage(info1_, c_, c__+1)
                
                if e_ in ['loadingAtMaxRate']:
                    for d__, d_ in enumerate(info_['sequence'][1:]):
                        # from open single tank ... increase to max rate
                        # start_ = int(info_['sequence'][d__+1]['timeStart'])
                        # end_ = int(info_['sequence'][d__+1]['timeEnd'])
                        # print(start_, end_, info1_['iniTime'])
                        if self.input.loading.first_loading_port and c__ == 0:
                            pass
                        else:
                            
#                            print('Modified:', d_['stage'])
                            assert d_['stage'] == info_['sequence'][d__+1]['stage']
                            info_['sequence'][d__+1]['deballastingRateM3_Hr'] = info1_.get('iniDeballastingRateM3_Hr', {})
                            info_['sequence'][d__+1]['ballastingRateM3_Hr'] = info1_.get('iniBallastingRateM3_Hr', {})
                            
                            info2_ = {'simIniDeballastingRateM3_Hr': deepcopy(info1_.get('simIniDeballastingRateM3_Hr', {})),
                                      'simIniBallastingRateM3_Hr': deepcopy(info1_.get('simIniBallastingRateM3_Hr', {}))}
                            
                            # change time to current stage
                            for k_, v_ in info2_['simIniDeballastingRateM3_Hr'].items():
                                info2_['simIniDeballastingRateM3_Hr'][k_]['timeStart'] = info_['sequence'][d__+1]['timeStart']
                                info2_['simIniDeballastingRateM3_Hr'][k_]['timeEnd'] = info_['sequence'][d__+1]['timeEnd']
                                
                            for k_, v_ in info2_['simIniBallastingRateM3_Hr'].items():
                                info2_['simIniBallastingRateM3_Hr'][k_]['timeStart'] = info_['sequence'][d__+1]['timeStart']
                                info2_['simIniBallastingRateM3_Hr'][k_]['timeEnd'] = info_['sequence'][d__+1]['timeEnd']
                                 
                            info_['sequence'][d__+1]['simDeballastingRateM3_Hr'] = [info2_['simIniDeballastingRateM3_Hr']]
                            info_['sequence'][d__+1]['simBallastingRateM3_Hr'] = [info2_['simIniBallastingRateM3_Hr']]
                            
                            # get ballast pump operating time
                            self._get_ballast_pump1(info_['sequence'][d__+1], [info1_['port'][0]], c_, delay=loading_seq.delay)
    
                    self._get_ballast_pump1(info1_, info1_['port'] + [info1_['port'][-1]+1], c_, delay=loading_seq.delay)
                   
                    # print(info1_['stageEndTime'])
                    self._get_eduction(info1_, c_)
                    
                    # self._cleanup(info1_)
                    # print(info1_.keys())
                    info1_.pop('simIniDeballastingRateM3_Hr')
                    info1_.pop('simIniBallastingRateM3_Hr')
                    info1_.pop('iniDeballastingRateM3_Hr')
                    info1_.pop('iniBallastingRateM3_Hr')
                    info1_.pop('iniTotDeballastingRateM3_Hr')
                    info1_.pop('iniTotBallastingRateM3_Hr')
                        
                info_["sequence"].append(info1_)
                        
            
            data["events"].append(info_)
            
        
        data["plans"] = {'arrival':loading_seq.initial_plan, 'departure':loading_seq.final_plan}
        data["stages"] = loading_seq.stages
        data["loadingInformation"] = self.input.loading_information
        
        data['message'] = {'limits':self.input.limits}
        
        return data
    
    
    def _get_ballast_pump1(self, out, ports, cargo, delay = 0):
        
        start_, end_ = int(out['timeStart']), int(out['timeEnd'])
#        print('bp', out['stage'], start_, end_)
        
        if out['stage'] in ['openSingleTank', 'initialRate', 'openAllTanks', 'increaseToMaxRate']:
            start__ = start_
            end__ = end_
#            print('port', ports[0], start__, end__)
            port = ports[0]
            self._get_ballast_pump_info(out, port, start__, end__)

        elif out['stage'] in ['loadingAtMaxRate']:
            # print('port', ports)
            # last_ = int(self.input.loading.seq[str(cargo)]['justBeforeTopping'][10:])
            for p__, p_ in enumerate(out['ballastIntervalPort']):
                # if p_ in out['ballastIntervalPort']:
                if p__ == 0 and self.input.first_loading_port:
                    start__ = max(out['ballastIntervalPort'][p_][0], out['ballastIntervalPort'][p_][1] - self.input.loading.seq['ballastLimitTime'][p_])
                    end__   = out['ballastIntervalPort'][p_][1] 
                else:
                    start__ = out['ballastIntervalPort'][p_][0]
                    end__   = out['ballastIntervalPort'][p_][0] + self.input.loading.seq['ballastLimitTime'][p_]
              
#                print('MaxLoading'+str(p__+1), 'in port ', p_, start__, end__, ' (start+ballastTimeGiven)', out['ballastIntervalPort'][p_][0], out['ballastIntervalPort'][p_][1])
                
                port = p_
                self._get_ballast_pump_info(out, port, start__, end__)

            out['pumpEndTime'] = {}
            for k_, v_ in self.ballast_info['startStop'].items():
                if v_[1] in ports:
                    # print(k_, 'stopped at ', v_[1])
                    time__ = out['ballastIntervalPort'][v_[1]][0]+self.input.loading.seq['ballastLimitTime'][v_[1]]
                    out['pumpEndTime'][k_] = str(time__)
                    
            print('pumpEndTime:', out['pumpEndTime'])
    
    
    def _get_eduction(self, out, cargo):
        
        if self.input.loading.seq[cargo].get('eduction',()):
            # print(self.input.loading.seq[cargo]['eduction'])
#            print(out['stageEndTime'])
            out['eduction'] = {}
            
            cur_stage_ = self.input.loading.seq[cargo]['eduction'][1]
            pre_stage_ = int(cur_stage_[10:]) - 1
            if pre_stage_ == 0:
                timeStart_ = int(out['timeStart'])
            else:
                pre_stage_ = 'MaxLoading' + str(pre_stage_)
                timeStart_ = out['stageEndTime'][pre_stage_]    
            
            timeStart_ += self.input.loading.seq[cargo]['eduction'][0]
            timeEnd_ = timeStart_ + self.input.loading.time_eduction - 60
            
            out['eduction']['timeStart'] = str(int(timeStart_))
            out['eduction']['timeEnd']   = str(int(timeEnd_))
            out['eduction']['tank'] = {self.input.vessel.info['tankName'][t_]:t_  for t_ in self.input.loading.info['eduction'] if t_ not in ['LFPT', 'FPT']}
            
            eduction_ = {}
            # for p_ in self.input.loading.eduction_pump:
            #     id_ = str(self.input.vessel.info['vesselPumps']['ballastEductor'][p_]['pumpId'])
            #     eduction_[id_] = {}
            #     eduction_[id_]['pumpName'] = p_
                
            if len(eduction_) == 0:
                id_ = str(self.input.vessel.info['vesselPumps']['ballastEductor']['Ballast Eductor 1']['pumpId'])
                eduction_[id_] = {}
                eduction_[id_]['pumpName'] = 'Ballast Eductor 1'
                
            pump_ = [p_ for p_ in out['ballast'] if p_ not in ['Gravity']]
            out['eduction']['pumpSelected'] = eduction_ #self.input.loading.eduction_pump
            out['eduction']['ballastPumpSelected'] = {str(min(pump_)): {'pumpName': self.input.vessel.info['vesselPumps']['ballastPumpId'][min(pump_)]}} #self.input.loading.eduction_pump
               
            # print(out['eduction'])
            
        
    
    ## for discharge study --------------------------------------------------------------------------------------
    def gen_json2(self, constraints, stability_values):

        data = {}
        data['message'] = None
        data['processId'] = self.input.process_id
        data['hasLoadicator'] = self.input.has_loadicator
        
        data['vesselCode'] = self.input.vessel_id
        # data['portCode'] = self.input.port_code
        data['deadweightconstant'] = str(self.input.vessel.info['deadweightConst']['weight'])
        data['provisionalconstant'] = str(0.0)
        
        if len(self.plans['ship_status']) == 0:
            data['loadablePlanDetails'] = []
            #data['message'] = self.input.error + self.plan['message']
            
            data['message'] = {**self.input.error, **self.plans['message']}
            data['errors'] = self._format_errors(data['message'])
            # data['validated'] = False if self.input.mode in ['Manual', 'FullManual'] else None
            
            return data
        
        # self.cow_tanks = []
        self.cow_tanks_remain = list(self.input.loadable.info['toCow'])
        self.strip_tanks = []
        # all loading port
        path_ = [self.input.port.info['portOrder'][str(i_+1)]  for i_ in range(self.input.port.info['numPort'])]
        # print(path_)
        data['dischargePlanDetails'] = []
        for s_ in range(len(self.plans['ship_status'])):
            plan = {}
            
            plan['caseNumber'] = int(s_+1)
            
            plan['dischargePlanPortWiseDetails'] = []
            plan['constraints'] = constraints.get(str(s_),[])
            
            for p__,p_ in enumerate(path_):
                plan_ = {}
                plan_['portId'] = int(str(self.input.port.info['portRotation'][p_]['portId'])[:-1])
                plan_['portCode'] = p_[:-1]
                plan_['portRotationId'] = int(self.input.port.info['portRotation'][p_]['portRotationId'])
                
                # arrival
                plan_['arrivalCondition'] = {"dischargeQuantityCargoDetails":[],
                                              "dischargeQuantityCommingleCargoDetails":[],
                                              "dischargePlanStowageDetails":[],
                                              "dischargePlanBallastDetails":[],
                                              "dischargePlanRoBDetails":[]}
                
                plan_['arrivalCondition']["stabilityParameters"] = stability_values[s_][self.input.loadable.info['arrDepVirtualPort'][str(p__+1)+'A']]
                
                # plan_['arrivalCondition']["dischargeQuantityCargoDetails"] = self._get_status(s_, str(p__+1)+'A', 'dTotal')
                plan_['arrivalCondition']["dischargeQuantityCargoDetails"] = []

                # get loadablePlanStowageDetails
                plan_['arrivalCondition']["dischargePlanStowageDetails"] = self._get_status(s_, str(p__+1)+'A', 'dCargoStatus')
                # get loadablePlanBallastDetails
                plan_['arrivalCondition']["dischargePlanBallastDetails"] = self._get_status(s_, str(p__+1)+'A', 'ballastStatus')
                # get loadablePlanRoBDetails
                plan_['arrivalCondition']["dischargePlanRoBDetails"] = self._get_status(s_, str(p__+1)+'A', 'robStatus')
                
                if p__ == 0:
                    self.arrival = deepcopy(plan_['arrivalCondition']["dischargePlanStowageDetails"])

                # departure
                plan_['departureCondition'] = {"dischargeQuantityCargoDetails":[],
                                              "dischargeQuantityCommingleCargoDetails":[],
                                              "dischargePlanStowageDetails":[],
                                              "dischargePlanBallastDetails":[],
                                              "dischargePlanRoBDetails":[],
                                              "loadableQuantityCargoDetails":[]}
                
                plan_['departureCondition']["stabilityParameters"] = stability_values[s_][self.input.loadable.info['arrDepVirtualPort'][str(p__+1)+'D']]
                
                plan_['departureCondition']["dischargeQuantityCargoDetails"] = self._get_status(s_, str(p__+1)+'D', 'dTotal')
                plan_['departureCondition']["loadableQuantityCargoDetails"] = self._get_status(s_, str(p__+1)+'D', 'total')
                # get loadablePlanStowageDetails
                plan_['departureCondition']["dischargePlanStowageDetails"] = self._get_status(s_, str(p__+1)+'D', 'dCargoStatus')
                # get loadablePlanBallastDetails
                plan_['departureCondition']["dischargePlanBallastDetails"] = self._get_status(s_, str(p__+1)+'D', 'ballastStatus')
                # get loadablePlanRoBDetails
                plan_['departureCondition']["dischargePlanRoBDetails"] = self._get_status(s_, str(p__+1)+'D', 'robStatus')
                # get loadableQuantityCommingleCargoDetails
                # plan_['departureCondition']["loadableQuantityCommingleCargoDetails"] = self._get_status(s_, str(p__+1)+'D', 'commingleStatus')

                plan_['cowTanks'] = []
                nonempty_tanks_ = [i_['tankShortName'] for i_ in plan_['departureCondition']["dischargePlanStowageDetails"] if float(i_['quantityMT']) > 0.] + \
                                  [i_['tankShortName'] for i_ in plan_['departureCondition']["dischargeQuantityCommingleCargoDetails"]]
                empty_tanks_ = set(self.input.vessel.info['cargoTanks'].keys()) - set(nonempty_tanks_)
                
                cow_allow_ = self.input.port.info['portRotation'][p_]['cowAllowed']
                strip_tanks_ = [] # current port 
                # cow_allow_ = False
                # print(empty_tanks_)
                for t_ in empty_tanks_:
                    if t_ not in self.strip_tanks:
                        self.strip_tanks.append(t_)
                        strip_tanks_.append(t_)
                         
                    if t_ in self.cow_tanks_remain and cow_allow_:
                        plan_['cowTanks'].append({"tankShortName": t_,
                                                  "tankId": self.input.vessel.info['tankName'][t_],
                                                  "cowType": "Full"})
                        self.cow_tanks_remain.remove(t_)
                
                discharge_rate_ = 15000 ## fixed
                num_cargo_ = len(plan_['departureCondition']["dischargeQuantityCargoDetails"])
                print("##-----------------------------------------------------")
                print("num_cargo_", num_cargo_)
                if num_cargo_ == 1:
                    discharge_rate_ = discharge_rate_*0.9
                elif num_cargo_ == 2:
                    discharge_rate_ = discharge_rate_*0.85
                else:
                    discharge_rate_ = discharge_rate_*0.8
                
                print("discharge_rate_", discharge_rate_)
                total_vol_ = 0.
                for d__, d_ in enumerate(plan_['departureCondition']["dischargeQuantityCargoDetails"]):
                    parcel_ = 'P'+ str(d_['dscargoNominationId'])
                    if float(d_['dischargeMT']) > 0:
                        density_ = self.input.loadable.info['parcel'][parcel_]['maxtempSG']
                        total_vol_ += float(d_['dischargeMT'])/density_
                        
                # time_ = total_vol_/discharge_rate_
                
                    
                empty_slop_ = True if self.input.vessel.info['slopTank'][0] in strip_tanks_ or \
                    self.input.vessel.info['slopTank'][1] in strip_tanks_ else False
                slop_qty_ = 1200. if empty_slop_ and len(strip_tanks_) > 0 else 0.
                
                print("slop_qty_", slop_qty_)
                fresh_oil_qty_ = self.input.port.info['portRotation'][p_]['freshCrudeOilQuantity'] \
                    if self.input.port.info['portRotation'][p_]['freshCrudeOil'] else 0.
                        
                fresh_oil_time_ = self.input.port.info['portRotation'][p_]['freshCrudeOilTime'] \
                    if self.input.port.info['portRotation'][p_]['freshCrudeOil'] else 0.
                
                print("freshCrude", fresh_oil_qty_, fresh_oil_time_)
                last_port_ = self.input.port.info['portOrder'][str(len(path_))] == p_      
                
                if last_port_:
                    add_time_ = 3.
                elif empty_slop_:
                    add_time_ = 1.
                else:
                    add_time_ = 0.

                print("add_time_", add_time_)   
                print("vol_", total_vol_)
                time_ = (total_vol_-slop_qty_-fresh_oil_qty_)/discharge_rate_ + add_time_ + fresh_oil_time_/60
                plan_['departureCondition']['dischargingRate'] = str(round(discharge_rate_,1))
                plan_['departureCondition']['timeRequiredForDischarging'] = str(round(time_,1))
                print('timeRequiredForDischarging', time_)
                
                for c__, c_ in enumerate(plan_['departureCondition']['dischargeQuantityCargoDetails']):
                    if float(c_['dischargeMT']) > 0:
                        print(c_['cargoAbbreviation'], c_['dischargeMT'])
                        parcel_ = 'P'+str(c_['dscargoNominationId'])
                        plan_['departureCondition']['dischargeQuantityCargoDetails'][c__]['dischargingRate'] = str(round(discharge_rate_,1))
                        density_ = self.input.loadable.info['parcel'][parcel_]['maxtempSG']
                        vol_ = float(c_['dischargeMT'])/density_
                        time_ = vol_/discharge_rate_
                        plan_['departureCondition']['dischargeQuantityCargoDetails'][c__]['timeRequiredForDischarging'] = str(round(time_,1))

                plan['dischargePlanPortWiseDetails'].append(plan_)
                
            data['dischargePlanDetails'].append(plan)
        data['message'] = {'limits':self.input.limits}
        
        if self.input.discharge_json["existingDischargePlanDetails"]:
            self._gen_json2a(data)

        if len(self.cow_tanks_remain) > 0:
            print('Non empty cow tanks:', self.cow_tanks_remain)
 
        return data
    
    
    def _gen_json2a(self, data):
        print('New port mode!!')
        
        # plan1_ =  deepcopy(data['dischargePlanDetails'][0]['dischargePlanPortWiseDetails']) # list of port
        # # real plan
        # for p__, p_ in enumerate(self.input.port.info['past_plans']):
        #     rotation_ = int(list(p_.keys())[0])
        #     info_ = {}
        #     info_['portId'] = self.input.port.info['ignore_port'][rotation_][0]
        #     info_['portCode'] = self.input.port.info['ignore_port'][rotation_][1]
        #     info_['portRotationId'] = rotation_
        #     info_['arrivalCondition'] =  {}
        #     info_['arrivalCondition']['dischargeQuantityCargoDetails'] =  []
        #     info_['arrivalCondition']['dischargeQuantityCommingleCargoDetails'] =  []
        #     info_['arrivalCondition']['dischargePlanStowageDetails'] =  p_[str(rotation_)]['arrival']['planDetails']['stowageDetails']
        #     info_['arrivalCondition']['dischargePlanBallastDetails'] =  p_[str(rotation_)]['arrival']['planDetails']['ballastDetails']
        #     info_['arrivalCondition']['dischargePlanRoBDetails'] =  p_[str(rotation_)]['arrival']['planDetails']['robDetails']
        #     info_['arrivalCondition']['stabilityParameters'] =  {}
            
        #     info_['departureCondition'] =  {}
        #     info_['departureCondition']['dischargeQuantityCargoDetails'] =  []
        #     info_['departureCondition']['dischargeQuantityCommingleCargoDetails'] =  []
        #     info_['departureCondition']['dischargePlanStowageDetails'] =  p_[str(rotation_)]['departure']['planDetails']['stowageDetails']
        #     info_['departureCondition']['dischargePlanBallastDetails'] =  p_[str(rotation_)]['departure']['planDetails']['ballastDetails']
        #     info_['departureCondition']['dischargePlanRoBDetails'] =  p_[str(rotation_)]['departure']['planDetails']['robDetails']
        #     info_['departureCondition']['stabilityParameters'] =  {}
           
            
        #     info_['cowTanks'] = []
            
        #     plan1_.insert(p__, info_)
            
        # data['realDischargePlanDetails'] = deepcopy(data['dischargePlanDetails'])
        # data['realDischargePlanDetails'][0]['dischargePlanPortWiseDetails'] = plan1_    
        
        
            
        plan2_ =  deepcopy(data['dischargePlanDetails'][0]['dischargePlanPortWiseDetails']) # list of port
        # planned plan
        for p__, p_ in enumerate(self.input.port.info['past_plans1']):
            rotation_ = int(list(p_.keys())[0])
            info_ = {}
            info_['portId'] = self.input.port.info['ignore_port'][rotation_][0]
            info_['portCode'] = self.input.port.info['ignore_port'][rotation_][1]
            info_['portRotationId'] = rotation_
            info_['arrivalCondition'] =  {}
            info_['arrivalCondition']['dischargeQuantityCargoDetails'] =  []
            info_['arrivalCondition']['dischargeQuantityCommingleCargoDetails'] =  []
            info_['arrivalCondition']['dischargePlanStowageDetails'] =  p_[str(rotation_)]['arrivalCondition']['dischargePlanStowageDetails']
            info_['arrivalCondition']['dischargePlanBallastDetails'] =  p_[str(rotation_)]['arrivalCondition']['dischargePlanBallastDetails']
            info_['arrivalCondition']['dischargePlanRoBDetails'] =  p_[str(rotation_)]['arrivalCondition']['dischargePlanRoBDetails']
            info_['arrivalCondition']['stabilityParameters'] =  {}
            
            info_['departureCondition'] =  {}
            info_['departureCondition']['dischargeQuantityCargoDetails'] =  []
            info_['departureCondition']['dischargeQuantityCommingleCargoDetails'] =  []
            info_['departureCondition']['dischargePlanStowageDetails'] =  p_[str(rotation_)]['departureCondition']['dischargePlanStowageDetails']
            info_['departureCondition']['dischargePlanBallastDetails'] =  p_[str(rotation_)]['departureCondition']['dischargePlanBallastDetails']
            info_['departureCondition']['dischargePlanRoBDetails'] =  p_[str(rotation_)]['departureCondition']['dischargePlanRoBDetails']
            info_['departureCondition']['stabilityParameters'] =  {}
           
            
            info_['cowTanks'] = []
            
            plan2_.insert(p__, info_)
       
        data['dischargePlanDetails'][0]['dischargePlanPortWiseDetails'] = plan2_    
            
            
        
    
    def gen_json(self, constraints, stability_values):
        data = {}
        data['message'] = None
        data['processId'] = self.input.process_id
        data['user'] = self.input.user
        data['role'] = self.input.role
        data['hasLoadicator'] = self.input.has_loadicator
        
        data['vesselCode'] = self.input.vessel_id
        # data['portCode'] = self.input.port_code
        
        data['errors'] = []
        
        data['validated'] = True if self.input.mode in ['Manual', 'FullManual'] else None
        data['feedbackLoop'] = self.input.feedbackLoop
        data['feedbackLoopCount'] = self.input.feedbackLoopCount
        
        
        if len(self.plans['ship_status']) == 0:
            data['loadablePlanDetails'] = None if self.input.mode in  ['Manual', 'FullManual'] else []
            #data['message'] = self.input.error + self.plan['message']
            
            data['message'] = {**self.input.error, **self.plans['message']}
            data['errors'] = self._format_errors(data['message'])
            data['validated'] = False if self.input.mode in ['Manual', 'FullManual'] else None
            
            return data
        
        data['deadweightconstant'] = str(self.input.vessel.info['deadweightConst']['weight'])
        data['provisionalconstant'] = str(0.0)
        
        
        # data['loadableStudyId'] = str(self.input.loadable_id)
        # data['vesselId'] = str(self.input.vessel_id)
        # data['voyageId'] = str(self.input.voyage_id)
        
        # all loading port
        path_ = [self.input.port.info['portOrder'][str(i_+1)]  for i_ in range(self.input.port.info['numPort'])]
        
        data['loadablePlanDetails'] = []
        for s_ in range(len(self.plans['ship_status'])):
            plan = {}
            
            if self.input.mode in ['Manual', 'FullManual']:
                plan['caseNumber'] = self.input.case_number
            else:
                plan['caseNumber'] = int(s_+1)
                port_ = self.input.loadable.info['lastVirtualPort']-1
                plan['deadfreight'] = str(0.00)
                if stability_values[s_][str(port_)]['empty']:
                    plan['deadfreight'] = str(round(float(self.input.cargoweight) - float(stability_values[s_][str(port_)]['cargo']),2))
                
            plan['loadablePlanPortWiseDetails'] = []
            plan['constraints'] = constraints.get(str(s_),[])
            # plan['stabilityParameters'] = stability_values[s_][self.input.loadable.info['arrDepVirtualPort'][str(self.input.port.info['lastLoadingPort'])+'D']]
            plan['slopQuantity'] = str(self.plans['slop_qty'][s_]) if len(self.plans['slop_qty']) > 0 else None
            
            for p__,p_ in enumerate(path_):
                plan_ = {}
                plan_['portId'] = int(str(self.input.port.info['portRotation'][p_]['portId'])[:-1])
                plan_['portCode'] = p_[:-1]
                plan_['portRotationId'] = int(self.input.port.info['portRotation'][p_]['portRotationId'])
                plan_['seaWaterTemperature'] = str(self.input.port.info['portRotation'][p_]['seaWaterTemperature'])
                plan_['ambientTemperature'] = str(self.input.port.info['portRotation'][p_]['ambientTemperature'])
                # arrival
                plan_['arrivalCondition'] = {"loadableQuantityCargoDetails":[],
                                              "loadableQuantityCommingleCargoDetails":[],
                                              "loadablePlanStowageDetails":[],
                                              "loadablePlanBallastDetails":[],
                                              "loadablePlanRoBDetails":[]}
                
                # if p_ not in [path_[0]]:
                    # print(s_,p_, 'Get arrival info')
                plan_['arrivalCondition']["loadableQuantityCargoDetails"] = self._get_status(s_, str(p__+1)+'A', 'total')
                # get loadablePlanStowageDetails
                plan_['arrivalCondition']["loadablePlanStowageDetails"] = self._get_status(s_, str(p__+1)+'A', 'cargoStatus')
                # get loadablePlanBallastDetails
                plan_['arrivalCondition']["loadablePlanBallastDetails"] = self._get_status(s_, str(p__+1)+'A', 'ballastStatus')
                # get loadablePlanRoBDetails
                plan_['arrivalCondition']["loadablePlanRoBDetails"] = self._get_status(s_, str(p__+1)+'A', 'robStatus')
                # get loadableQuantityCommingleCargoDetails
                plan_['arrivalCondition']["loadableQuantityCommingleCargoDetails"] = self._get_status(s_, str(p__+1)+'A', 'commingleStatus')
                plan_['arrivalCondition']["stabilityParameters"] = stability_values[s_][self.input.loadable.info['arrDepVirtualPort'][str(p__+1)+'A']]
                
                
                # departure
                plan_['departureCondition'] = {"loadableQuantityCargoDetails":[],
                                              "loadableQuantityCommingleCargoDetails":[],
                                              "loadablePlanStowageDetails":[],
                                              "loadablePlanBallastDetails":[],
                                              "loadablePlanRoBDetails":[]}
                
                if p_ not in [path_[-1]]:
                    # print(s_,p_,'Get departure info')
                    # get loadableQuantityCargoDetails
                    plan_['departureCondition']["loadableQuantityCargoDetails"] = self._get_status(s_, str(p__+1)+'D', 'total')
                    # get loadablePlanStowageDetails
                    plan_['departureCondition']["loadablePlanStowageDetails"] = self._get_status(s_, str(p__+1)+'D', 'cargoStatus')
                    # get loadablePlanBallastDetails
                    plan_['departureCondition']["loadablePlanBallastDetails"] = self._get_status(s_, str(p__+1)+'D', 'ballastStatus')
                    # get loadablePlanRoBDetails
                    plan_['departureCondition']["loadablePlanRoBDetails"] = self._get_status(s_, str(p__+1)+'D', 'robStatus')
                    # get loadableQuantityCommingleCargoDetails
                    plan_['departureCondition']["loadableQuantityCommingleCargoDetails"] = self._get_status(s_, str(p__+1)+'D', 'commingleStatus')
                    plan_['departureCondition']["stabilityParameters"] = stability_values[s_][self.input.loadable.info['arrDepVirtualPort'][str(p__+1)+'D']]
                
                id_ = self.input.port.info['portRotation'][p_]['portId'] 
                loadingHr_ = 0.
                for c__, c_ in enumerate(self.input.loadable.info['cargoPort'][str(id_)]):
                    cargo_id_ = int(c_[1:])
                    for u__, u_ in enumerate(plan_['departureCondition']["loadableQuantityCargoDetails"]):
                        if u_['cargoNominationId'] == cargo_id_:
                            loadingHr_ += float(u_['timeRequiredForLoading'])
                            break
                        
                plan_['timeRequiredForLoading'] = str(round(loadingHr_,2))       
                plan['loadablePlanPortWiseDetails'].append(plan_)
                
                
            # self._set_bunker(plan)
                
                
            data['loadablePlanDetails'].append(plan)
        data['message'] = {'limits':self.input.limits}
        
        if self.input.mode in ['Manual', 'FullManual']:
            data['loadablePlanDetails'] = data['loadablePlanDetails'][0]
                
      
        return data
    
    def _set_bunker(self, plan):
        
        # ['normalOp'] = {0: 359, 1: 2116, 3: 2065}
        # ['bunkering'] = {2 : {'id': 100003006 ... }}
        for k_, v_ in self.input.port.info['bunkering'].items():
            print('bunkering:', k_, v_)

    def _get_status(self,sol,port,category):
        
        # print('enter vlcc_gen.py')
        
        plan_ = []
        virtual_ = self.input.loadable.info['arrDepVirtualPort'][port]
        
        if category == 'total':
            
            if len(self.plans['cargo_status'][sol]) > 0:
            
                for k_, v_ in self.plans['cargo_status'][sol][virtual_].items():
                    if v_ > 0.:
                    # load_ = 0
                    #if virtual_ not in ['0']:
                        #arr_dep_ = self.input.loadable.info['virtualArrDepPort'][str(int(virtual_))]
                        #load_ = [self.plans['cargo_status'][sol][a_][k_] for a_, b_ in self.input.loadable.info['virtualArrDepPort'].items() if b_ == arr_dep_]
                        #load_ = round(sum(load_),1)
                        
                    
                    #if load_ > 0.:
                        info_ = {}
                        info_["cargoId"] = int(self.input.loadable.info['parcel'][k_]['cargoId'])
                        info_["cargoNominationId"] = int(k_[1:])
                        info_['cargoAbbreviation'] = self.input.loadable.info['parcel'][k_]['abbreviation']
                        info_['abbreviation'] = self.input.loadable.info['parcel'][k_]['abbreviation']
                        info_['estimatedAPI'] = str(self.input.loadable.info['parcel'][k_]['api'])
                        info_['estimatedTemp'] = str(self.input.loadable.info['parcel'][k_]['temperature'])
                        info_['loadableMT'] = str(v_)
                        info_['priority'] = int(self.input.loadable.info['parcel'][k_]['priority'])
                        info_['colorCode'] = self.input.loadable.info['parcel'][k_]['color']
                        
                        if self.input.loadable.info.get('toLoadIntend',None):
                            intend_ = self.input.loadable.info['toLoadIntend'][k_]
                            info_['orderedQuantity'] = str(round(intend_,DEC_PLACE))
                            info_['differencePercentage'] = str(round((v_-intend_)/intend_*100,2))
                        
                            info_['loadingOrder'] = int(self.plans['cargo_order'][sol][k_])
                            info_["maxTolerence"] = str(self.input.loadable.info['parcel'][k_]['minMaxTol'][1])
                            info_["minTolerence"] = str(self.input.loadable.info['parcel'][k_]['minMaxTol'][0])
                            info_['slopQuantity'] = str(self.plans['slop_qty'][sol].get(k_,0.))
                            
                        info_['toppingSequence'] = self.plans['topping'][sol][k_]
                        info_['timeRequiredForLoading'] = str(round(self.plans['loading_hrs'][sol][k_][0]+self.plans['loading_hrs'][sol][k_][1], 2))
                        info_['cargoNominationTemperature'] = str(self.input.loadable.info['parcel'][k_]['loadingTemperature'])
                        info_['loadingRateM3Hr'] = str(round(self.plans['loading_rate'][sol][k_][0]))

                        plan_.append(info_)
        
        elif category == 'dTotal':
             if len(self.plans['cargo_status'][sol]) > 0:
                 
                slop_qty_ = {} 
                if virtual_ in ['0']:
                    data_ = {}
                    
                    for k_, v_ in self.input.loadable.info['preloadOperation'].items():
                        data_[k_] = 0.
                        for k1_, v1_ in v_.items():
                            data_[k_]  += v1_
                            
                            if k1_ in self.input.vessel.info['slopTank']: #['SLS', 'SLP']:
                                if k_ not in slop_qty_.keys():
                                    slop_qty_[k_] = v1_
                                else:
                                    slop_qty_[k_] += v1_
                            
                            
                    self.plans['cargo_status'][sol][virtual_] = data_
                
                else:
                    for k_, v_ in self.plans['ship_status'][sol][virtual_]['cargo'].items(): 
                        if k_ in self.input.vessel.info['slopTank']: #['SLS', 'SLP']:
                            if v_[0]['parcel'] not in slop_qty_.keys():
                                slop_qty_[v_[0]['parcel']] = v_[0]['wt']
                            else:
                                slop_qty_[v_[0]['parcel']] += v_[0]['wt']
                        
               
                    for k_, v_ in self.plans['cargo_status'][sol][virtual_].items():
                        #print(k_, v_)
                        
                        info_ = {}
                        info_["cargoId"] = int(self.input.loadable.info['parcel'][k_]['cargoId'])
                        info_["dscargoNominationId"] = int(k_[1:])
                        if self.input.loadable.info['parcel'][k_]['cargoNominationId'][1:] not in ['None']:
                            info_['cargoNominationId'] = int(self.input.loadable.info['parcel'][k_]['cargoNominationId'][1:])
                        else:
                            info_['cargoNominationId'] = None
                            
                        info_['cargoAbbreviation'] = self.input.loadable.info['parcel'][k_]['abbreviation']
                        info_['abbreviation'] = self.input.loadable.info['parcel'][k_]['abbreviation']
                        info_['estimatedAPI'] = str(self.input.loadable.info['parcel'][k_]['api'])
                        info_['estimatedTemp'] = str(self.input.loadable.info['parcel'][k_]['temperature'])
                        
                        info_['dischargeMT'] = str(0.0)
                        disch_ = 0
                        if virtual_ not in ['0']:
                            arr_dep_ = self.input.loadable.info['virtualArrDepPort'][str(int(virtual_))]
                            disch_ = [self.plans['cargo_status'][sol][a_][k_] for a_, b_ in self.input.loadable.info['virtualArrDepPort'].items() if b_ == arr_dep_]
                            disch_ = -sum(disch_)
                            info_['dischargeMT'] = str(round(disch_,1))
                            
                        info_['priority'] = int(self.input.loadable.info['parcel'][k_]['priority'])
                        info_['colorCode'] = self.input.loadable.info['parcel'][k_]['color']
                        
                        # info_['slopQuantity'] = str(round(slop_qty_.get(k_, 0.0),1))
                        
                        info_['dischargingRate'] = str(0.0)
                        info_['timeRequiredForDischarging'] = str(0.0)
                        # info_['cowDetails'] = []
                        
                        portId_ = self.input.port.info['portOrderId'][port[:-1]]
                        
                        for a_, b_ in self.input.loadable.info['cargoPort'][portId_].items():
                            if k_ in b_:
                                info_['sequenceNum'] = str(a_)
                                break
                        
                        if float(info_['dischargeMT']) > 0.:
                            # print('cargo discharged:', info_['cargoAbbreviation'])
                            plan_.append(info_)
                                    
      
                                    
            
        elif category == 'dCargoStatus':

            full_tank_ = []
                        
            for k_,v_ in self.plans['ship_status'][sol][virtual_]['cargo'].items():
                # print(k_,v_)
                full_tank_.append(k_)
                info_ = {}
                info_['tankShortName'] = k_
                info_['quantityMT'] = str(abs(v_[0]['wt']))
                info_['quantityM3'] = str(round(abs(v_[0]['wt'])/v_[0]['SG'],2))
                
                info_['cargoAbbreviation'] = self.input.loadable.info['parcel'][v_[0]['parcel']]['abbreviation']
                info_['abbreviation'] = self.input.loadable.info['parcel'][v_[0]['parcel']]['abbreviation']
                info_['tankId'] = int(self.input.vessel.info['tankName'][k_])
                info_['fillingRatio'] = str(round(v_[0]['fillRatio']*100,2))
                info_['tankName'] = self.input.vessel.info['cargoTanks'][k_]['name']
                   
                info_['temperature'] = str(v_[0]['temperature'])
                # info_['cargoNominationTemperature'] = str(v_[0]['temperature'])
                
                info_['colorCode'] = self.input.loadable.info['parcel'][v_[0]['parcel']]['color']
                info_['api'] = str(self.input.loadable.info['parcel'][v_[0]['parcel']]['api'])
                
                info_['dscargoNominationId'] = int(v_[0]['parcel'][1:])
                if self.input.loadable.info['parcel'][v_[0]['parcel']]['cargoNominationId'][1:] not in ['None']:
                    info_['cargoNominationId'] = int(self.input.loadable.info['parcel'][v_[0]['parcel']]['cargoNominationId'][1:])
                else:
                    info_['cargoNominationId'] = None
                # info_['onboard'] = str(self.input.vessel.info['onboard'].get(k_,{}).get('wt',0.))
                
                # vol_ = abs(v_[0]['wt'])/v_[0]['SG']
                # info_['rdgUllage'] = str(round(self.input.vessel.info['ullage_func'][str(info_['tankId'])](vol_).tolist(), 2))
                
                info_['correctedUllage'] = str(round(v_[0]['corrUllage'],7))
                info_['correctionFactor'] = str(0.00 if v_[0]['correctionFactor'] == 0 else v_[0]['correctionFactor'])
                info_['rdgUllage'] = str(v_[0]['rdgUllage'])
                info_['maxTankVolume'] = str(self.input.vessel.info['cargoTanks'][k_]['capacityCubm'])
                info_['isLoadedOnTop'] = self.input.loadable.info['isLoadedOnTop'].get(int(self.input.vessel.info['tankName'][k_]),False)
                info_['isSlopTank'] = self.input.loadable.info['isSlopTank'].get(int(self.input.vessel.info['tankName'][k_]),False)
                plan_.append(info_)
                
            if port not in ['1A']:
                # print(port)
                empty_ = set(self.input.vessel.info['cargoTanks']) - set(full_tank_)
                
                for t_ in empty_:
                    # print(port, t_)
                    info_ = next((i_ for i_ in self.arrival if i_['tankShortName'] == t_), None)
                    # print(info_)
                    
                    if info_ in [None]:
                        info_ = {}
                        info_['quantityMT'] = str(0.0)
                        info_['quantityM3'] = str(0.0)
                        info_['tankShortName'] = t_
                        info_['dscargoNominationId'] = None
                        info_['cargoNominationId'] = None
                    else:
                        info_['quantityMT'] = str(0.0)
                        info_['quantityM3'] = str(0.0)
                        
                    plan_.append(info_)
                    
        elif category == 'cargoStatus':
            full_tank_ = []
                        
            for k_,v_ in self.plans['ship_status'][sol][virtual_]['cargo'].items():
                # print(k_,v_)
                full_tank_.append(k_)
                if type(v_[0]['parcel']) == str and v_[0]['parcel'] in self.input.loadable.info['parcel'].keys():
                    info_ = {}
                    info_['tankShortName'] = k_
                    info_['quantityMT'] = str(abs(v_[0]['wt']))
                    info_['quantityM3'] = str(round(abs(v_[0]['vol']),2))
                    
                    
                    info_['cargoAbbreviation'] = self.input.loadable.info['parcel'][v_[0]['parcel']]['abbreviation']
                    info_['abbreviation'] = self.input.loadable.info['parcel'][v_[0]['parcel']]['abbreviation']
                    
                    info_['tankId'] = int(self.input.vessel.info['tankName'][k_])
                    info_['fillingRatio'] = str(round(v_[0]['fillRatio']*100,2))
                    info_['tankName'] = self.input.vessel.info['cargoTanks'][k_]['name']
                    
                    
                    info_['temperature'] = str(self.input.loadable.info['parcel'][v_[0]['parcel']]['temperature'])
                    info_['cargoNominationTemperature'] = str(self.input.loadable.info['parcel'][v_[0]['parcel']]['loadingTemperature'])
                    
                    info_['colorCode'] = self.input.loadable.info['parcel'][v_[0]['parcel']]['color']
                    info_['api'] = str(self.input.loadable.info['parcel'][v_[0]['parcel']]['api'])
                    
                    info_['cargoNominationId'] = int(v_[0]['parcel'][1:])
                    info_['onboard'] = str(self.input.vessel.info['onboard'].get(k_,{}).get('wt',0.))
                    
                    # vol_ = abs(v_[0]['wt'])/v_[0]['SG']
                    # info_['rdgUllage'] = str(round(self.input.vessel.info['ullage_func'][str(info_['tankId'])](vol_).tolist(), 2))
                    
                    info_['correctedUllage'] = str(round(v_[0]['corrUllage'],7))
                    info_['correctionFactor'] = str(0.00 if v_[0]['correctionFactor'] == 0 else v_[0]['correctionFactor'])
                    info_['rdgUllage'] = str(v_[0]['rdgUllage'])
                    info_['maxTankVolume'] = str(round(v_[0]['maxTankVolume'],3))
                    info_['isSlopTank'] = self.input.vessel.info['cargoTanks'][k_].get('isSlop', False)
                    info_['isLoadedOnTop'] = True if info_['isSlopTank'] else False
                    
                    plan_.append(info_)
                    
                elif type(v_[0]['parcel']) == str:
                 	# only onboard 
                    info_ = {}
                    info_['tankShortName'] = k_
                    info_['quantityMT'] = str(abs(v_[0]['wt']))
                    info_['quantityM3'] = str(round(abs(v_[0]['vol']),2))
                    
                    info_['cargoAbbreviation'] = self.input.vessel.info['cargoTanks'][k_]['abbreviation']
                    info_['abbreviation'] = self.input.vessel.info['cargoTanks'][k_]['abbreviation']
                    
                    info_['tankId'] = int(self.input.vessel.info['tankName'][k_])
                    
                    
                    info_['fillingRatio'] = str(round(v_[0]['fillRatio']*100,2))
                    info_['tankName'] = self.input.vessel.info['cargoTanks'][k_]['name']
                    info_['temperature'] = str(v_[0]['temperature'])
                    info_['colorCode'] = self.input.vessel.info['cargoTanks'][k_]['colorCode']
                    info_['api'] = self.input.vessel.info['cargoTanks'][k_]['api']
                    
                    # vol_ = abs(v_[0]['wt'])/v_[0]['SG']
                    # info_['rdgUllage'] = str(round(self.input.vessel.info['ullage_func'][str(info_['tankId'])](vol_).tolist(), 2))
                    info_['correctedUllage'] = str(round(v_[0]['corrUllage'],7))
                    info_['correctionFactor'] = str(0.00 if v_[0]['correctionFactor'] == 0 else v_[0]['correctionFactor'])
                    info_['rdgUllage'] = str(v_[0]['rdgUllage'])
                                        
                    info_['cargoNominationId'] = ''
                    info_['onboard'] = str(self.input.vessel.info['onboard'].get(k_,{}).get('wt',0.))
                    info_['maxTankVolume'] = str(round(v_[0]['maxTankVolume'],3))
                    info_['isSlopTank'] = self.input.vessel.info['cargoTanks'][k_].get('isSlop', False)
                    info_['isLoadedOnTop'] = False
                    
                    plan_.append(info_)
                    
                # if port not in ['1A']:
                # print(port)
            empty_ = set(self.input.vessel.info['cargoTanks']) - set(full_tank_)
            
            for t_ in empty_:
                # if info_ in [None]:
                info_ = {}
                info_['quantityMT'] = str(0.0)
                info_['quantityM3'] = str(0.0)
                info_['tankShortName'] = t_
                # info_['dscargoNominationId'] = None
                info_['cargoNominationId'] = None
                
                info_['cargoAbbreviation'] = None
                info_['abbreviation'] = None
                
                info_['tankId'] = int(self.input.vessel.info['tankName'][t_])
                info_['fillingRatio'] = None
                info_['tankName'] = self.input.vessel.info['cargoTanks'][t_]['name']
                
                
                info_['temperature'] = None
                info_['cargoNominationTemperature'] = None
                
                info_['colorCode'] = None
                info_['api'] = None
                
                info_['cargoNominationId'] = None
                info_['onboard'] = None
                
                # vol_ = abs(v_[0]['wt'])/v_[0]['SG']
                # info_['rdgUllage'] = str(round(self.input.vessel.info['ullage_func'][str(info_['tankId'])](vol_).tolist(), 2))
                
                info_['correctedUllage'] = None
                info_['correctionFactor'] = None
                info_['rdgUllage'] = None
                info_['maxTankVolume'] = None
                info_['isSlopTank'] = self.input.vessel.info['cargoTanks'][t_].get('isSlop', False)
                info_['isLoadedOnTop'] = True if info_['isSlopTank'] else False
                
                plan_.append(info_)
                    
                    
        elif category == 'commingleStatus':
            
            for k_,v_ in self.plans['ship_status'][sol][virtual_]['cargo'].items():
                if type(v_[0]['parcel']) == list:
                    info_ = {}
                    
                    info_['tankShortName'] = k_
                    info_['quantity'] = str(abs(v_[0]['wt']))
                    info_['quantityM3'] = str(round(abs(v_[0]['vol']),2))
                    
                    info_['cargo1Abbreviation'] = self.input.loadable.info['parcel'][v_[0]['parcel'][0]]['abbreviation']
                    info_['cargo2Abbreviation'] = self.input.loadable.info['parcel'][v_[0]['parcel'][1]]['abbreviation']
                    info_['priority'] = int(self.input.loadable.info['commingleCargo']['priority'])
                    
                    info_['cargo1NominationId'] = int(v_[0]['parcel'][0][1:])
                    info_['cargo2NominationId'] = int(v_[0]['parcel'][1][1:])
                     
                    
                    
                    # info_['priority'] = str(self.input.loadable.info['commingleCargo']['priority'])
                    info_['cargo1Percentage'] = str(round(v_[0]['wt1percent']*100,2))
                    info_['cargo2Percentage'] = str(round(v_[0]['wt2percent']*100,2))
                    info_['cargo1MT'] = str(v_[0]['wt1'])
                    info_['cargo2MT'] = str(v_[0]['wt2'])
                    
                    info_['fillingRatio'] = str(round(v_[0]['fillRatio']*100,2))
                    info_['temp'] = str(v_[0]['temperature'])
                    
                    info_['api'] =  str(round(v_[0]['api'],2))
                    info_['tankId'] = int(self.input.vessel.info['tankName'][k_])
                    info_['tankName'] = self.input.vessel.info['cargoTanks'][k_]['name']
                    # vol_ = abs(v_[0]['wt'])/v_[0]['SG']
                    
                    info_['correctedUllage'] = str(round(v_[0]['corrUllage'],7))
                    info_['correctionFactor'] = str(0.00 if v_[0]['correctionFactor'] == 0 else v_[0]['correctionFactor'])
                    info_['rdgUllage'] = str(v_[0]['rdgUllage'])
                   
                    info_['onboard'] = str(self.input.vessel.info['onboard'].get(k_,{}).get('wt',0.))
                    #info_['slopQuantity'] = str(abs(v_[0]['wt'])) if k_ in ['SLS','SLP'] else 0.
                    info_['slopQuantity'] = str(abs(v_[0]['wt'])) if k_ in self.input.vessel.info['slopTank'] else 0.
                    info_['isSlopTank'] = self.input.vessel.info['cargoTanks'][k_].get('isSlop', False)
                    info_['isLoadedOnTop'] = True if info_['isSlopTank'] else False
                    
                    info_['colorCode'] = self.input.loadable.info['commingleCargo']['colorCode']
                    info_['maxTankVolume'] = str(round(v_[0]['maxTankVolume'],3))
                    
                    l1_ = self.plans['loading_hrs'][sol][v_[0]['parcel'][0]][0]+self.plans['loading_hrs'][sol][v_[0]['parcel'][0]][1]
                    l2_ = self.plans['loading_hrs'][sol][v_[0]['parcel'][1]][0]+self.plans['loading_hrs'][sol][v_[0]['parcel'][1]][1]
                    
                    info_['timeRequiredForLoading'] = str(round(l1_+l2_, 2))
                    
                    loading_order1_ = int(self.plans['cargo_order'][sol]['P'+str(info_['cargo1NominationId'])])
                    loading_order2_ = int(self.plans['cargo_order'][sol]['P'+str(info_['cargo2NominationId'])])
                    
                    if loading_order1_ < loading_order2_:
                        info_['toppingOffCargoId'] = info_['cargo2NominationId']
                    else:
                        info_['toppingOffCargoId'] = info_['cargo1NominationId']
                        
                            
                    plan_.append(info_)
                
        elif category == 'ballastStatus':
            
            for k_,v_ in self.plans['ship_status'][sol][virtual_]['ballast'].items():
                info_ = {}
                info_['tankShortName'] = k_
                info_['quantityMT'] = str(round(abs(v_[0]['wt']),2))
                info_['quantityM3'] = str(round(abs(v_[0]['vol']),2))
                
                info_['fillingRatio'] = str(round(v_[0]['fillRatio']*100,2))
                info_['sg'] = str(v_[0]['SG'])
                
                info_['tankId'] = int(self.input.vessel.info['tankName'][k_])
                info_['tankName'] = self.input.vessel.info['ballastTanks'][k_]['name']
                # vol_ = np.floor(abs(v_[0]['wt'])/v_[0]['SG']) # + self.input.vessel.info['onboard'].get(k_,{}).get('vol',0.)
                
                # try:
                #     ul_= self.input.vessel.info['ullage_func'][str(info_['tankId'])](vol_).tolist()
                # except:
                #     print(k_, vol_)
                #     ul_ = 0.
                info_['correctedUllage'] = str(round(v_[0]['corrLevel'],7))
                info_['correctionFactor'] = str(0.00 if v_[0]['correctionFactor'] == 0 else v_[0]['correctionFactor'])
                info_['rdgLevel'] = str(v_[0]['rdgLevel'])
                
                info_['volume'] = str(round(v_[0]['vol'],2))
                info_['maxTankVolume'] = str(round(v_[0]['maxTankVolume'],3))
                
                
                plan_.append(info_)
                
                
        elif category == 'robStatus':
            
            for k_,v_ in self.plans['ship_status'][sol][virtual_]['other'].items():
                info_ = {}
                info_['tankShortName'] = k_
                info_['quantityMT'] = str(abs(v_[0]['wt']))
                info_['quantityM3'] = str(round(abs(v_[0]['vol']),2))
                
                info_['sg'] = str(v_[0]['SG'])
                info_['tankId'] = int(self.input.vessel.info['tankName'][k_])
                info_['tankName'] =  self.input.vessel.info['tankFullName'][k_]
             
                plan_.append(info_)
        
        return plan_
        

    def _format_errors(self, message):
        errors = []
        for k_, v_ in message.items():
            errors.append({"errorHeading":k_, "errorDetails":v_})
    
        return errors
    
    # def _cal_max_rate(self, param, flow_rate):
    #     max_rate = 1000000
        
    #     components = {'manifolds':[['manifolds'], ['manifolds']],   # param, flow_rate
    #                   'drop':[['manifolds'], ['dropLines']], 
    #                   'bottom':[['bottomLines'],['bottomLines']],
    #                   'tanks':[['centreTank', 'wingTank'], ['centreTankBranch','wingTankBranch']], 
    #                   'PVvalves':[['centreTank', 'wingTank'], ['PVvalveCentreTank','PVvalveWingTank']], 
    #                   'maxVessel':[[''],['maxLoadingRate']],
    #                   'maxRiser':[[''],['maxRiser']]}
    #     rate = {}
    #     for k_, v_ in components.items():
    #         rate_ = 0
    #         for i_, j_ in zip(v_[0], v_[1]):
    #             # print(i_,j_, param.get(i_,1), flow_rate[j_])
    #             rate_ += len(param.get(i_,[1])) * flow_rate[j_]
            
    #         rate[k_] = rate_
    #         if max_rate > rate_:
    #             max_rate = rate_
            
    #     # print(rate)
        
        
    #     return max_rate
    
    
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
        
        flow_rate = self.input.vessel.info['loadingRate6']
        
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
        loading_rate_ = min(self.input.vessel.info['loadingRateVessel'], self.input.vessel.info['loadingRateRiser'])

        for k_, v_ in components.items():
            rate_ = 0
            for i_, j_ in zip(v_[0], v_[1]):
                # print(i_,j_, param.get(i_,1), flow_rate[j_])
                if j_ in ['maxLoadingRate', 'maxRiser']:
                    # print(i_, j_, flow_rate[j_])
                    rate_ += flow_rate.get(j_, loading_rate_)
                else:
                    # print(i_, j_, param[i_], flow_rate[j_])
                    if i_ == 'wingTank' :
                        rate_ += len(param[i_])*2 * flow_rate[j_]
                    else:
                        rate_ += len(param[i_]) * flow_rate[j_]
    
            
            rate[k_] = rate_
            if max_rate > rate_:
                max_rate = rate_
            
            # print('>>>', k_, rate_)
            
        # print(max_rate)
        
        
        return max_rate


            

    def _topping_seq(self, tanks):
        # fixed_order = ['SLS','SLP','5P','5C', '4P', '4C', '2P','2C', '1P','1C','3P', '3C']
        slopP = [t_ for t_ in self.input.vessel.info['slopTank'] if t_[-1] == 'P'][0]
        slopS = [t_ for t_ in self.input.vessel.info['slopTank'] if t_[-1] == 'S'][0]
        
        fixed_order = [slopS, slopP, '5P', '5C', '1P', '1C', '4P', '4C', '2P', '2C', '3P', '3C']
        # print('topping order:', fixed_order)
        order_ = ['' for o_ in fixed_order]
        
        for t_ in tanks:
            t__ = t_ #if t_ not in ['SLS'] else 'SLP'
            if t__ in fixed_order:
                i_ = fixed_order.index(t__)
                order_[i_] = t__
                
        order__ = [o_ for o_ in order_ if o_ not in ['']]
    
        # print(order__)
        
        seq = []
        for t_ in tanks:
            if t_ not in self.input.vessel.info['slopTank']: #['SLS', 'SLP']:
                t__ = t_ if t_[-1] not in ['S'] else t_[:-1]+'P'
            else:
                t__ = t_ 
            # print(t_,t__)
            seq_ = {}
            seq_['shortName'] = t_
            seq_['tankId'] = self.input.vessel.info['tankName'][t_]
            seq_['sequenceOrder'] = order__.index(t__) + 1
            
            seq.append(seq_)
            
            
        # print(seq)
        
        return seq
                    
        

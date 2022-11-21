# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 18:32:54 2021

@author: I2R
"""

import pickle
from vlcc_rotation import Check_rotations


with open('result5008.pickle', 'rb') as handle:
    data, input_param, plans = pickle.load(handle)
    
input_param.solver = 'ORTOOLS' # 'ORTOOLS', 'AMPL'
## check cargo rotation
cargo_rotate = Check_rotations(data, input_param)
cargo_rotate._check_plans(plans)

print(cargo_rotate.constraints)
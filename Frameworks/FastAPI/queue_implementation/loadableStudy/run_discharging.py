# -*- coding: utf-8 -*-
"""
Created on Thu Oct 14 21:28:31 2021

@author: phtan1
"""


import json
from uuid import uuid4

from api_discharging import gen_sequence1

## load configuration --------------------------------------------------------
with open('config.json', "r") as f_:
   config = json.load(f_)
   
   
fname = '../samples/dischargingInformationRequest_300000050b.json' # 1 single cargo

# fname = 'dischargingInformationRequest_186.json'

## to be modified in main.py --------------------------------------------
data = {}

with open(fname) as f_:
    data_ = json.load(f_)
    data['discharging'] = data_
    data['discharging']['infoId'] = data_["dischargeInformation"]["dischargeInfoId"]
    
    vessel_id_ = data['discharging']['vesselId']
        
        
with open('vessel_info'+str(vessel_id_)+'.json') as f_:    
    data['vessel'] = json.load(f_)
    
    
data['processId'] = str(uuid4())    
data['config'] = config["vessel"][str(vessel_id_)]

if __name__ == "__main__":


    result = gen_sequence1(data)
    
    with open('result.json', 'w') as f_:  
        json.dump(result, f_)
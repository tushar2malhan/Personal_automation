# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 14:38:01 2021

@author: I2R
"""
import json
import requests

# -----------------------------------------------------------------
data_ = {"id":1, "tankId":25580, "rdgUllage":"1.04" , "trim" : "3.31",
         "api" : "35",  "temp" : "60"}

data_ = {"id":1, "tankId":25581, "rdgUllage":"1.068" , "trim" : "3.31",
         "api" : "35",  "temp" : "60"}

data_ = {"id":1, "tankId":25582, "rdgUllage":"1.032" , "trim" : "3.31",
         "api" : "35",  "temp" : "60"}

data_ = {"id":1, "tankId":25583, "rdgUllage":"1.073" , "trim" : "3.31",
         "api" : "35",  "temp" : "60"}

data_ = {"id":1, "tankId":25584, "rdgUllage":"0.916" , "trim" : "3.31",
         "api" : "35",  "temp" : "60"}



fname = 'correction.json' # single dict
with open(fname, 'w') as f_:  
    json.dump(data_, f_)

# with open(fname) as f_:    
#     data = json.load(f_)



headers = {'Accept' : 'application/json', 'Content-Type' : 'application/json'}
url2 = 'http://127.0.0.1:8000/ullage_results'
rr2 = requests.get(url2, data=open(fname, 'rb'), headers=headers)
obj2 = json.loads(rr2.content.decode('utf-8'))


#{'BFOSRV': 25619, 'WB5P': 25606, 'WB5S': 25607, 'AWBP': 25608, 'AWBS': 25609, 'APT': 25610, 
#'FPTU': 25611, 'FO2P': 25614, 'FO2S': 25615, 'DOSRV1': 25624, 'DOSRV2': 25625, 'DRWT': 25636, 
#'SLS': 25596, 'WB1S': 25599, 'WB2P': 25600, 'WB2S': 25601, 'FRWT': 25637, 'DSWTP': 25638, 
#'WB3P': 25602, 'WB3S': 25603, 'WB4P': 25604, 'WB4S': 25605, 'DSWTS': 25639, '2C': 25581, 
#'1P': 25585, '1S': 25586, '2P': 25587, '2S': 25588, 'DO1S': 25622, '4P': 25591, '4S': 25592, 
#'5P': 25593, '1C': 25580, '3C': 25582, '4C': 25583, '5C': 25584, '3P': 25589, '3S': 25590, 
#'5S': 25594, 'SLP': 25595, 'FPTL': 25597, 'WB1P': 25598, 'FO1P': 25612, 'FO1S': 25613, 
#'HFOSRV': 25616, 'HFOSET': 25617, 'DO2S': 25623}        
    
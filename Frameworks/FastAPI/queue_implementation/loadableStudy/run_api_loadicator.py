# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 15:43:04 2021

@author: I2R
"""
import requests
import json


fname1 = 'loadicator_request_v66.json'
fname1 = 'loadicator_6001a.json'

fname1 = 'loadicator_6606.json'
fname1 = 'loadicator_8380.json'
fname1 = 'loadicator_0713.json'

fname1 = 'loadicator_request1025.json'

headers = {'Accept' : 'application/json', 'Content-Type' : 'application/json'}
#
url3 = 'http://127.0.0.1:8000/loadicator_results'
rr3 = requests.post(url3, data=open(fname1, 'rb'), headers=headers)
obj3 = json.loads(rr3.content.decode('utf-8'))

with open('obj3.json', 'w') as f:  
    json.dump(obj3, f)
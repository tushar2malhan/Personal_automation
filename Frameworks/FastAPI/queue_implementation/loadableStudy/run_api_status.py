# -*- coding: utf-8 -*-
"""
Created on Sat Dec  5 14:58:21 2020

@author: I2R
"""

import requests
import json

fname2 = 'serial.json'
#data2 = {'uid': '7552ed6b-7f12-4ef6-8c76-4e01e411adfb'}
#with open(fname2, 'w') as f:  
#    json.dump(data2, f)

headers = {'Accept' : 'application/json', 'Content-Type' : 'application/json'}
url2 = 'http://127.0.0.1:8000/status'
rr2 = requests.get(url2, data=open(fname2, 'rb'), headers=headers)
obj2 = json.loads(rr2.content.decode('utf-8'))


with open('obj2.json', 'w') as f:  
    json.dump(obj2, f)

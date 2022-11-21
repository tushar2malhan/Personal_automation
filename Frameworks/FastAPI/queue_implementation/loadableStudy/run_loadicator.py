# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 14:38:01 2021

@author: I2R
"""
import json
#from api_vlcc import loadicator
from api_loading import loadicator1


fname = 'loadable_pattern_loadicator_request.json' # single dict
fname = 'loadable_study_loadicator_request.json'

fname = 'loadicator-request0413.json'
fname = 'algo-request0413.json'

fname = 'loadicator_6001a.json'
fname = 'loadicator_6606.json'

fname = 'loadicator_6680.json'
fname = 'loadicator_0713.json'

fname = 'loading_loadicator_25.json'
# fname = 'loadicator_request_165.json'
fname = 'loading_information_loadicator_request_165.json'

fname = 'commingle_ullage_update_with_loadicator.json'
# fname = 'commingle_ullage_update_without_loadicator.json'


fname = 'loading_information_loadicator_request_100000223.json'

fname = 'loadicator_request1025.json'

with open(fname) as f_:    
    data = json.load(f_)

# limits = {'limits': {'draft': {'loadline': 20.943, '107327': 22.0, '107328': 22.0},
#   'operationId': {'107327': '1', '107328': '2'},
#   'id': 4468,
#   'vesselId': 1,
#   'voyageId': 115,
#   'airDraft': {'107327': 200, '107327': 200}}}


# limits = {'limits': {'draft': {'loadline': 20.943, '359': 20.0, '1': 20.0},
#   'operationId': {'359': '1', '1': '2'},
#   'id': 6861,
#   'vesselId': 1,
#   'voyageId': 2042,
#   'airDraft': {'359': 20.0, '1': 20.0}}}

# limits = {'limits': {'draft': {'loadline': 100, 'maxDraft': 30.0}, 'maxAirDraft': 33.69}}
limits = {'limits': {'draft': {'loadline': 20.943,
   '2355': 25.9175,
   '2116': 32.9175,
   '736': 32.9175,
   'maxDraft': 32.9175},
  'operationId': {'2355': '1', '2116': '1', '736': '2'},
  'seawaterDensity': {'2355': 1.025, '2116': 1.025, '359': 1.025},
  'tide': {'2355': 1.025, '2116': 1.025, '359': 1.025},
  'id': 8857,
  'vesselId': 1,
  'voyageId': 2265,
  'airDraft': {'2355': 44.0, '2116': 45.41, '504': 55.0},
  'sfbm': 0.95,
  'feedback': {'feedbackLoop': False, 'feedbackLoopCount': 0},
  'maxAirDraft': 32.9175}}

# limits = {'limits': {'draft': {'loadline': 100, 'maxDraft': 16.2}, 'maxAirDraft': 26.0}}


 
if __name__ == "__main__":
    result = loadicator1(data, limits)
    
    with open('result_loadicator.json', 'w') as f_:  
        json.dump(result, f_)
        
        
        
        
        
        
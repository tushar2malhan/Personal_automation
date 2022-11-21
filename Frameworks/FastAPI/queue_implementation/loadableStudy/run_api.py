# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 17:21:13 2020

@author: I2R
"""

import requests
import json


#fname1 = 'out.json'
#data1 = {'mean':50, 'variance':100}
#with open(fname1, 'w') as f:  
#    json.dump(data1, f)


fname1 = 'loadableStudy_4618.json' # 2 cargo at 1st port; 2 ports; zero ballast not possible at discharge port
fname1 = 'loadableStudy_4614.json' # api too high; max draft too low
fname1 = 'loadableStudy_4614a.json' # fixed; 2 cargo at 1st port; 2 ports;

fname = 'loadableStudy_4826.json' # non-zero ballast at last loading port

# fname1 = 'result66c2.json' # manual mode corresponding zero ballast at discharge
# fname1 = 'result23c2.json' # manual mode corresponding zero ballast at discharge

fname1 = 'loadableStudy70rob2.json' #  non-zero ballast 20sec full load
# fname1 = 'result70rob2.json' # manual mode corresponding; use with generate_manual_plan


# fname1 = 'loadablePattern_request_2885.json' # manual


fname1 = 'loadableStudy_5572.json' # single cargo
# fname1 = 'loadableStudy_5574.json' # 
# fname1 = 'loadableStudy_5575.json' #
# fname1 = 'loadableStudy_5576.json' # Draft error
# fname1 = 'loadableStudy_5577.json' # Draft error
# fname1 = 'loadableStudy_5578.json' # Port rotation error
# fname1 = 'loadableStudy_5579.json' # 

fname1 = 'loadablePattern_request_2911.json'
fname1 = 'loadableStudy_6164.json'
fname1 = 'loadableStudy_6287.json'
fname1 = 'loadableStudy_6318.json'

fname1 = 'request0422a.json' # infeasible
# fname1 = 'request0421.json' # deballast limit relax
fname1 = 'loadableStudy_6540.json'

fname1 = 'loadablePattern_request_3325.json'
fname1 = 'loadableStudy_6606.json'

fname1 = 'loadablestudy_6676.json'

fname1 = 'loadablestudy_6849.json' # max draft error
# fname1 = 'loadablestudy_6854.json' # port ordering error




fname1 = 'loadableStudy_8066.json' # sea water density different between arrival and departure port same set of ballast tanks might not be possible
fname1 = 'pattern_validate.json'
fname1 = 'loadablePattern_request_3654a.json' # commingle
fname1 = 'loadablePattern_request_3984.json' # 1 cargo loaded at 2 port

fname1 = 'ballast_edit_request_0611.json'

fname1 = 'loadableStudy_8095.json'
fname1 = 'loadableStudy_8380.json'

fname1 = 'loadableStudy_0713.json'

#fname1 = 'pattern_validate_0713.json' # fully manual mode
#fname1 = 'loading_information_40c.json'
#
#fname = 'loading_information_request_144v4.json'
#fname = 'loading_loadicator_25.json'


# fname1 = 'loadableStudy_10155.json'
# fname1 = 'loadableStudy_10129.json'
#fname1 = 'loading_information_request_167.json'
#
#fname1 = 'dischargeStudy_25b.json' # fully discharge
#fname1 = 'all_rules.json'
fname1 = 'loadingDSS-4061.json'
fname1 = 'loading_info_165.json'

fname1 = 'loadableStudy_100000351.json'


fname1 = 'loadable_study_200000021.json' # ATLANTIC PIONEER

headers = {'Accept' : 'application/json', 'Content-Type' : 'application/json'}
#
url1 = 'http://127.0.0.1:8000/new_loadable'
rr1 = requests.post(url1, data=open(fname1, 'rb'), headers=headers)
obj1 = json.loads(rr1.content.decode('utf-8'))

with open('obj1.json', 'w') as f:  
    json.dump(obj1, f)

fname2 = 'serial.json'
data2 = {'processId': obj1['processId']}
with open(fname2, 'w') as f:  
    json.dump(data2, f)






# uvicorn main:app --reload --host 0.0.0.0 --port:8000
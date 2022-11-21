# -*- coding: utf-8 -*-
"""
Created on Sun Dec  6 12:24:27 2020

@author: I2R

Testing loadable module 
"""
import json
from uuid import uuid4

from api_vlcc import gen_allocation

# import sys
# sys.stdout = open('log.txt', 'w')



# fname = 'loadableStudy_4614.json' # api too high; max draft too low
# fname = 'loadableStudy_4614a.json' # fixed; 2 cargo at 1st port; 2 ports;

# fname = 'loadableStudy_4557.json' # api too high; max draft too low
# fname = 'loadableStudy_4557a.json' # fixed




# fname = 'loadableStudy_4826.json' # non-zero ballast at last loading port

# fname = 'loadableStudy_4601.json' # unload 210k total load;

fname = 'loadableStudy70rob2.json' #  non-zero ballast 20sec full load
# fname = 'loadableStudy66c2.json'  # rotation at 2nd port; load more if non-zero ballast
# 
fname = 'loadableStudy26c2.json' # commingle 4C:0 onboard 90sec deballastPercent = 1

# 
# fname = 'loadableStudy_4601.json' # partial load 200k 40% cargo deballast disable
# fname = 'loadableStudy_5009.json'

# fname = 'loadableStudy_5233.json' # infeasible

# fname = 'result26c2.json' # manual mode corresponding; use with generate_manual_plan

# fname = 'pattern_validate_request.json'

# fname = 'loadablePattern_request_1418.json' # np port rotation
# fname = 'loadablePattern_request_2742.json' # discharge port first
# fname = 'loadablePattern_request_2885.json' # manual

# fname = 'loadableStudy_5572.json' # single cargo
# fname = 'loadableStudy_5574.json' # 
# fname = 'loadableStudy_5575.json' #
# fname = 'loadableStudy_5576.json' # Draft error
# fname = 'loadableStudy_5577.json' # Draft error
# fname = 'loadableStudy_5578.json' # Port rotation error
# fname = 'loadableStudy_5579.json' # 

# fname = 'loadablePattern_request_2251.json' # missing cargoNorminationId
# fname = 'loadableStudy_6066.json'


# fname = 'loadableStudy_5426.json'
# fname = 'loadablePattern_request_2251.json'

# fname = 'loadablePattern_request_2911.json'
# fname = 'loadableStudy_6165.json'

# fname = 'loadableStudy_6164.json'
# fname = 'loadableStudy_6318.json' # missing maxDraft at port 2
# fname = 'loadableStudy_6159.json' # missing maxDraft 

# fname = 'request0421.json' # deballast limit relax
# fname = 'request0422b.json' # max draft error

# fname = 'request0422a.json' # infeasible
# fname = 'loadableStudy_6540.json'

# fname = 'loadablePattern_request_3314.json' # manual 1 dec place wt in tank
# fname = 'request_commingle0429a.json'

# fname = 'request_commingle0429c.json' # 2 commingle cargo



# fname = 'loadableStudy_6572.json'
# fname = 'loadablePattern_request_3325.json'



# fname = 'loadableStudy_6671.json' # loadable json
# fname = 'loadablePattern_request_3546.json'

# fname = 'loadablestudy_6711.json'
# fname = 'loadablestudy_6799.json'

# fname = 'loadablestudy_6849.json' # max draft error
# fname = 'loadablestudy_6854.json' # port order error

# fname = 'loadable_study_2cargos.json'
# fname = 'loadableStudy_4618.json' # 2 cargo at 1st port; 2 ports; Port 2 and 3 cannot share same ballast tank; zero ballast not possible at discharge port; 
# fname = 'loadableStudy66c2.json'  # rotation at 2nd port; load more if non-zero ballast
# fname = 'loadableStudy23c2.json' # rotation not required

##------------
# fname = 'request0422a.json' # infeasible

# fname = 'loadablestudy_6849.json' # max draft error
# fname = 'loadableStudy26c2.json' # commingle 4C:0 onboard 90sec deballastPercent = 1

# 

# fname = 'loadablePattern_request_3995.json'
# fname = 'discharge_port_error.json' # bulking
## fname = 'loadablePattern_request_3654.json' # manual commingle
# fname = 'loadableStudy_8016a.json' # API error

# fname = 'pattern_validate.json'

# fname = '7588-loadablestudy.json' # fix draft error duplication 
fname = '7872-loadablestudy.json' # 2 port 2 cargo
# fname = '7967-loadablestudy.json' # fix loading hrs

# fname = 'pattern_validate.json'
# fname = 'loadablePattern_request_3995.json' # manual
# fname = 'Loadablepatternrequest-4439.json' # loosen 98% vol, symmetric tank
# fname = 'loadablePattern_request_3654a.json' # commingle
# fname = 'loadablePattern_request_3984.json' # 1 cargo loaded at 2 port manual


# fname = 'loadableStudy_7410.json'
# fname = 'loadableStudy_8066.json' # sea water density different between arrival and departure port same set of ballast tanks might not be possible

# UAT
# fname = 'loadableStudy_8073.json'
# fname = 'loadableStudy_8080.json'
# fname = 'loadableStudy_8154.json'
# fname = 'loadableStudy_8095.json'
# fname = 'loadableStudy_8219a.json' # cargoToBeDischargeFirstId should be cargoNominationId 

# fname = 'loadablePattern_request_4900.json' # failed 98% volume > .98005
# fname = 'loadableStudy_8254.json'

# fname = 'loadableStudy_8252.json' # infeasible
# fname = 'loadableStudy_8247.json' # infeasible
# fname = 'loadableStudy_8251.json' # infeasbible

# fname = 'loadableStudy_8285.json' # loadicator results mismatched
# fname = 'loadableStudy_8018.json' # commingle section error
# fname = 'loadableStudy_8288.json'
# fname = 'loadableStudy_8302.json'

# fname = 'loadableStudy_8310a.json' # infeasbile
# fname = 'loadableStudy_8311.json' # infeasbile

# fname = 'pattern_edit_request0615.json'

# fname = 'ballast_edit_request_0611.json' # fully manual

# fname = 'loadableStudy_8327.json' # commingle error
# fname = 'loadableStudy_8328b.json' # priority

# fname = 'loadableStudy_8380.json'

# fname = 'loadableStudy_9220.json'

# fname = 'loadableStudy_8441a.json' #first port bunkering
# fname = 'loadableStudy_9254.json' #first port bunkering 

# fname = 'loadableStudy_8481.json' # missing port
# fname = 'loadableStudy_9283.json' # missing port
# fname = 'loadableStudy_9316.json'
# fname = 'loadableStudy_9220a.json'

# fname = 'loadableStudy_8486a.json' # "totalQuantity": "287702.5000",
# fname = 'loadableStudy_8487.json' # "totalQuantity": "287702.5000",


# fname = 'loadableStudy_8520.json'
# fname = 'loadableStudy_9660.json'

fname = 'pattern_validate_0713.json' # fully manual mode

# fname = 'loadableStudy_9486.json'
# fname = 'loadableStudy_9450.json'
# fname = 'loadableStudy_9664.json'
#fname = 'loadableStudy_9483.json'

#fname = 'loadableStudy_0718.json'

# fname = 'loadableStudy_6436.json'     # min tank 3 cargos 3 ports
# fname = 'loadableStudy_10242.json' # min tank 3 cargos 2 ports

fname = 'loadableStudy_10155.json'
# fname = 'loadableStudy_10129.json' # infeasbible 

fname = 'loadableStudy_8593.json' # Bunkering port as the first port 
fname = 'loadableStudy_8594.json' # Bunkering port in between two loading ports 
fname = 'loadableStudy_8595.json' # Bunkering port after last loading ports

# fname = 'loadableStudy_8621.json' # 3 cargos 3 ports

# fname = 'loadableStudy_7872.json' # 2 port 2 cargos each port

# fname = 'dischargeStudy_25a.json'
# fname = 'dischargeStudy_25b.json' # fully discharge


# fname = 'loadableStudy_10880.json'
# fname = 'loadableStudy_10881.json'
# fname = 'loadableStudy_10882.json'

# fname = 'ls_1.json' # ATLANTIC PIONEER
# fname = 'loadable_study_200000021.json' # ATLANTIC PIONEER
fname = 'all_rules.json'
fname = 'all_rules_updated.json'

# fname = 'discharge_study_111.json'

fname = '../samples/DS ALGO request with Cow history.json'
fname = 'loadablePattern_request_300002034.json'

#fname = 'error_request_json.json'

## load configuration --------------------------------------------------------
with open('config.json', "r") as f_:
   config = json.load(f_)
   
## to be modified in main.py --------------------------------------------
with open(fname) as f_:
    data_ = json.load(f_)

data = {}
data['module'] = data_.get('module', 'LOADABLE')

if data['module'] in ['LOADABLE']:
    # print('LOADABLE MODULE')
    if data_.get('loadableStudy', []):
        # manual mode
        data['loadable'] = data_['loadableStudy']
        data['loadablePlanPortWiseDetails'] = data_['loadablePlanPortWiseDetails']
        data['caseNumber'] = data_.get('caseNumber', None)
        data['loadable']['loadablePatternId'] = data_.get('loadablePatternId',111)
    else:
        # auto mode
        data['loadable'] = data_
        
    vessel_id_ = data['loadable']['vesselId']
        
elif data['module'] in ['DISCHARGE']:
    # print('DISCHARGE MODULE')
    data['discharge'] = data_ 
    
    vessel_id_ = data['discharge']['vesselId']
    
    

        
        
with open('vessel_info'+str(vessel_id_)+'.json') as f_:    
    data['vessel'] = json.load(f_)

data['processId'] = str(uuid4())
data['ballastEdited'] = data_.get('ballastEdited',False)
data['config'] = config["vessel"][str(vessel_id_)]
data['config']["solver"] = "ORTOOLS" #config["solver"]


if __name__ == "__main__":

    result = gen_allocation(data)
    
    with open('result.json', 'w') as f_:  
        json.dump(result, f_)



## %logstart -o
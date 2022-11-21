# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 15:06:16 2020

@author: phtan1
"""
import numpy as np
import pandas as pd
from pathlib import Path
import pickle
import pwlf
import matplotlib.pyplot as plt
import json
from scipy.interpolate import interp1d, interp2d
plt.style.use('seaborn-whitegrid')



class Vessel:
    def __init__(self, inputs, loading = False):
        
        vessel_json = inputs.vessel_json['vessel']
        
        vessel_info_ = {}
        
        vessel_info_['hasLoadicator'] = vessel_json['vessel'].get('hasLoadicator', False)
        # vessel_info_['banBallast'] = ['UFPT']   ## config
        vessel_info_['banBallast'] = inputs.config['ban_ballast']   
        
        if hasattr(inputs, 'loadable'):
            vessel_info_['banCargo'] = {k_: v_['banTank'] for k_,v_ in inputs.loadable.info['parcel'].items()}
        else:
            vessel_info_['banCargo'] = {}
        vessel_info_['slopTank'] = []
        
        ## 
        loadingRate_ = vessel_json.get('selectableParameter', [])
        if len(loadingRate_) == 0:
            loadingRate_ = [{'name': 'Manifolds', 'values': [{'type': 1, 'value': '1140.0000'}, {'type': 6, 'value': '6841.0000'}, {'type': 7, 'value': '7981.0000'}, {'type': 12, 'value': '13681.0000'}]}, {'name': 'DropLines', 'values': [{'type': 1, 'value': '1140.0000'}, {'type': 6, 'value': '6841.0000'}, {'type': 7, 'value': '7981.0000'}, {'type': 12, 'value': '13681.0000'}]}, {'name': 'BottomLines', 'values': [{'type': 1, 'value': '1534.0000'}, {'type': 6, 'value': '9205.0000'}, {'type': 7, 'value': '10739.0000'}, {'type': 12, 'value': '18409.0000'}]}, {'name': 'WingTankBranchLine', 'values': [{'type': 1, 'value': '659.0000'}, {'type': 6, 'value': '3950.0000'}, {'type': 7, 'value': '3950.0000'}, {'type': 12, 'value': '3950.0000'}]}, {'name': 'CentreTankBranchLine', 'values': [{'type': 1, 'value': '965.0000'}, {'type': 6, 'value': '5790.0000'}, {'type': 7, 'value': '5790.0000'}, {'type': 12, 'value': '5790.0000'}]}, {'name': 'PVValveWingTank', 'values': [{'type': 1, 'value': '7050.0000'}, {'type': 6, 'value': '7050.0000'}, {'type': 7, 'value': '7050.0000'}, {'type': 12, 'value': '7050.0000'}]}, {'name': 'PVValveCentreTank', 'values': [{'type': 1, 'value': '12000.0000'}, {'type': 6, 'value': '12000.0000'}, {'type': 7, 'value': '12000.0000'}, {'type': 12, 'value': '12000.0000'}]}, {'name': 'SlopTankBranchLine', 'values': [{'type': 1, 'value': '573.0000'}, {'type': 6, 'value': '3435.0000'}, {'type': 7, 'value': '3950.0000'}, {'type': 12, 'value': '3950.0000'}]}]
               
        vessel_info_['loadingRate6'] = {l_['name']: [float(l__['value']) for l__ in l_['values'] if l__['type'] == 6][0]   for l_ in loadingRate_}
        vessel_info_['loadingRate1'] = {l_['name']: [float(l__['value']) for l__ in l_['values'] if l__['type'] == 1][0]   for l_ in loadingRate_}
        
        vessel_info_['loadingRateVessel'] = float(vessel_json['vessel'].get('maxLoadRate', 20500))
        vessel_info_['loadingRateRiser'] = float(vessel_json['vessel'].get('mastRiser', 20500))
        
        
        ##***
        if vessel_json['vessel']['name'] == 'KAZUSA':
            vessel_info_['loadingRate6']['SlopTankBranchLine'] = 1292
            vessel_info_['constLCGTanks'] = ['2C', '2P',  '2S',  '4P',  '4S',  '1C',  '3C',  '4C',  '3P', '3S']
        elif vessel_json['vessel']['name'] == 'ATLANTIC PIONEER':
            vessel_info_['loadingRate6']['SlopTankBranchLine'] = 2372
            
        ##***
        
        
        ## 
        vessel_info_['name'] = vessel_json['vessel']['name'].replace(" ", "")
        
        ##
        vessel_info_['lightweight'] = {}
        vessel_info_['lightweight']['weight'] = float(vessel_json['vessel']['lightweight'])
        vessel_info_['lightweight']['lcg'] = float(vessel_json['vessel']['lcg'])
        vessel_info_['lightweight']['vcg'] = vessel_json['vessel'].get('vcg', 15.34)
        vessel_info_['lightweight']['tcg'] = vessel_json['vessel'].get('tcg', 0.)
        ##
        vessel_info_['deadweightConst'] = {}
        vessel_info_['deadweightConst']['weight'] = float(vessel_json['vessel']['deadweightConstant'])
        vessel_info_['deadweightConst']['lcg'] = float(vessel_json['vessel']['deadweightConstantLcg'])
        vessel_info_['deadweightConst']['vcg'] = vessel_json['vessel'].get('deadweightConstantVcg',15.55)
        vessel_info_['deadweightConst']['tcg'] = vessel_json['vessel']['deadweightConstantTcg'] 
        ##
        vessel_info_['draftCondition'] = {}
        if inputs.module in ['LOADABLE']:
            condition_ = next(i_ for i_ in vessel_json['vesselDraftCondition'] if i_.get("draftConditionId")  == inputs.loadline_id and i_.get("draftExtreme")  == inputs.draft_mark)
            vessel_info_['draftCondition']['deadweight'] = float(condition_['deadWeight'])
            vessel_info_['draftCondition']['draftExtreme'] = float(condition_['draftExtreme'])
            vessel_info_['draftCondition']['displacement'] = float(condition_['displacement'])
        
        ##
        vessel_info_['height'] = float(vessel_json['vessel']['keelToMastHeight'])
        vessel_info_['depth'] = float(vessel_json['vessel']['depthMolded'])
        vessel_info_['manifoldHeight'] = float(vessel_json['vessel'].get('heightOfManifoldAboveDeck', 2.05)) # default Kazusa 
        
        
        ## tanks
        vessel_info_['cargoTankNames'], vessel_info_['ballastTankNames'], vessel_info_['otherTankNames'] = [], [], []
        vessel_info_['cargoTanks'], vessel_info_['ballastTanks']  = {}, {}
        vessel_info_['fuelTanks'], vessel_info_['dieselTanks'], vessel_info_['freshWaterTanks']  = {}, {}, {}
        categoryid_ = {1:'cargoTanks', 2:'ballastTanks', 3:'freshWaterTanks', 5:'fuelTanks', 6:'dieselTanks'}
        vessel_info_['tankId'], vessel_info_['tankName'], vessel_info_['category'] = {}, {}, {}
        vessel_info_['tankFullName'] = {}
        for t_ in vessel_json['vesselTanks']:
            if t_['categoryId'] in categoryid_.keys():
                
                vessel_info_[categoryid_[t_['categoryId']]][t_['shortName']] = {'lcg': float(t_['lcg']), 'vcg': float(t_['vcg']), 
                                                                                     'tcg': t_['tcg'], 
                                                                                     'capacityCubm': t_['fullCapcityCubm'],
                                                                                     'slopTank': t_['slopTank'],
                                                                                     'tankId': t_['id'],
                                                                                     'name':t_['name'],
                                                                                     'inLoadicator':t_['isLoadicatorUsing']
                                                                                   }
                if t_['isLoadicatorUsing']:
                    vessel_info_['tankId'][t_['id']] = t_['shortName'] 
                    vessel_info_['tankName'][t_['shortName']] = t_['id'] 
                    vessel_info_['category'][t_['shortName']] = categoryid_[t_['categoryId']]
                    
                    vessel_info_['tankFullName'][t_['shortName']] = t_['name']
                    
                    if t_['categoryId'] == 1:
                        vessel_info_['cargoTankNames'].append(t_['shortName'])
                    elif t_['categoryId'] == 2:
                        vessel_info_['ballastTankNames'].append(t_['shortName'])
                    else:
                        vessel_info_['otherTankNames'].append(t_['shortName'])
                    
                if t_['slopTank'] and (t_['categoryId'] == 1):
                    print(t_['shortName'], t_['slopTank'])
                if t_['slopTank'] and t_['categoryId'] in [1]:
                    vessel_info_['slopTank'].append(t_['shortName'])
                    
                
                    
                    
        
        
                
#                print(t_['shortName'],t_['name'])
                
        ##
        # vessel_info_['ullage'] = {}
        # for d_ in vessel_json['ullageDetails']:
        #     # print(d_['id'])
        #     if str(d_['tankId']) not in vessel_info_['ullage']:
        #         vessel_info_['ullage'][str(d_['tankId'])] = {'id': [d_['id']], 'depth':[float(d_['ullageDepth'])], 'vol':[float(d_['evenKeelCapacityCubm'])]}
        #     else:
        #         vessel_info_['ullage'][str(d_['tankId'])] ['depth'].append(float(d_['ullageDepth']))
        #         vessel_info_['ullage'][str(d_['tankId'])] ['vol'].append(float(d_['evenKeelCapacityCubm']))
        #         # vessel_info_['ullage'][str(d_['tankId'])] ['id'].append(d_['id'])
        
        ## linear approx ullage
        self._get_ullage_func(vessel_info_, {k_:v_ for k_,v_ in vessel_json.items() if k_ in ['ullageDetails','ullageTrimCorrections']})    
        vessel_info_['ullage30cm'] = {}
        for k_,v_ in vessel_info_['ballastTanks'].items():
            k1_ = str(vessel_info_['tankName'][k_])
            if k_ not in vessel_info_['banBallast']:
                vessel_info_['ullage30cm'][k_] = round(float(vessel_info_['ullageInvFunc'][k1_](0.3))*1.025,3)
                
        vessel_info_['ullage16mVol'] = {}
        for k_ in vessel_info_['slopTank']: #['SLP', 'SLS']:
            k1_ = str(vessel_info_['tankName'][k_])
            vessel_info_['ullage16mVol'][k_] = round(float(vessel_info_['ullageInvFunc'][k1_](16)),3)
            
        vessel_info_['sounding2mVol'] = {} # sounding 2m 
        for k_ in vessel_info_['cargoTanks']:
            k1_ = str(vessel_info_['tankName'][k_])
            u1_ = vessel_info_['ullageEmpty'][k1_] - 2
            vessel_info_['sounding2mVol'][k_] = round(float(vessel_info_['ullageInvFunc'][k1_](u1_)),3)
            ## to 3m for High vapor vargo

        vessel_info_['sounding3mVol'] = {} # sounding 3m 
        for k_ in vessel_info_['cargoTanks']:
            k1_ = str(vessel_info_['tankName'][k_])
            u1_ = vessel_info_['ullageEmpty'][k1_] - 3
            vessel_info_['sounding3mVol'][k_] = round(float(vessel_info_['ullageInvFunc'][k1_](u1_)),3)
        
            
        vessel_info_['sounding4mVol'] = {} # sounding 4m 
        for k_ in vessel_info_['cargoTanks']:
            k1_ = str(vessel_info_['tankName'][k_])
            u1_ = vessel_info_['ullageEmpty'][k1_] - 4
            vessel_info_['sounding4mVol'][k_] = round(float(vessel_info_['ullageInvFunc'][k1_](u1_)),3)
       
        
        vessel_info_['sounding30cmVol'] = {} # sounding 30cm 
        for k_ in vessel_info_['cargoTanks']:
            k1_ = str(vessel_info_['tankName'][k_])
            u1_ = vessel_info_['ullageEmpty'][k1_] - 0.3
            vessel_info_['sounding30cmVol'][k_] = round(float(vessel_info_['ullageInvFunc'][k1_](u1_)),3)
            
            
        vessel_info_['vol30percent'] = {} # sounding 30cm 
        for k_ in vessel_info_['slopTank']:
            k1_ = str(vessel_info_['tankName'][k_])
            vessel_info_['vol30percent'][k_] = round(vessel_info_['cargoTanks'][k_]['capacityCubm']*0.3,2)

         
        
        # self._get_ullage_corr(vessel_info_, vessel_json['ullageTrimCorrections'])
        
        ## 
        vessel_info_['hydrostatic'] = {}
        # vessel_info_['hydrostatic']['draft'], vessel_info_['hydrostatic']['displacement'] = [], []
        # vessel_info_['hydrostatic']['lcf'], vessel_info_['hydrostatic']['mtc'], vessel_info_['hydrostatic']['lcb'], vessel_info_['hydrostatic']['tkm'] = [], [], [], []
        
        
        df_ = pd.DataFrame(vessel_json['hydrostaticDatas'], dtype=float)
        df_ = df_.sort_values(by="draft", ascending=True)
        vessel_info_['hydrostatic']['draft'] = df_['draft'].to_numpy()
        vessel_info_['hydrostatic']['displacement'] = df_['displacement'].to_numpy()
        vessel_info_['hydrostatic']['lcf'] = df_['lcf'].to_numpy()
        vessel_info_['hydrostatic']['mtc'] = df_['mtc'].to_numpy()
        vessel_info_['hydrostatic']['lcb'] = df_['lcb'].to_numpy()
        vessel_info_['hydrostatic']['tkm'] = df_['tkm'].to_numpy()
        
        
        
        
        ## pw linear approx LCB x disp
        self._get_lcb_parameters(vessel_info_)    
       
        ##
        tcg_details_, lcg_details_ = {}, {}
        
        df_ = pd.DataFrame(vessel_json['vesselTankTCGs'], dtype=float)
        tank_record_ = df_['tankId'].unique()
        for t_ in tank_record_:
            tank_name_ = vessel_info_['tankId'].get(int(t_),None)
            if tank_name_:
                if tank_name_ in vessel_info_['cargoTanks']:
                    type_ = 'cargo'
                elif tank_name_ in vessel_info_['ballastTanks']:
                    type_ = 'ballast'
                else:
                    type_ = 'other'
                    
                df__ = df_.loc[df_['tankId'] == t_]
                df__ = df__.sort_values(by="capacity", ascending=True)
                
                tcg_details_[tank_name_], lcg_details_[tank_name_] = {'type':type_}, {'type':type_}
                tcg_details_[tank_name_]['tcg'] = df__['tcg'].to_numpy()
                tcg_details_[tank_name_]['vol'] = df__['capacity'].to_numpy()
                
                lcg_details_[tank_name_]['lcg'] = df__['lcg'].to_numpy()
                lcg_details_[tank_name_]['vol'] = df__['capacity'].to_numpy()
                
                
        ## pw linear approx TCG x weight
        vessel_info_['tankTCG'] = {}
        vessel_info_['tankTCG']['tcg'] = tcg_details_
        self._get_tcg_parameters(vessel_info_, tcg_details_)   
        
        ##
        vessel_info_['tankLCG'] = {}
        vessel_info_['tankLCG']['lcg'] = lcg_details_
        self._get_lcg_parameters(vessel_info_, lcg_details_)  
        
        
        for k_, v_ in vessel_info_['cargoTanks'].items():
            vol_ = 0.98*v_['capacityCubm']
            lcg_data_ = lcg_details_[k_]
            lcg_ = np.interp(vol_, lcg_data_['vol'], lcg_data_['lcg'])
            # print(k_, lcg_, v_['lcg'])
            vessel_info_['cargoTanks'][k_]['lcg'] = lcg_
            
        # vessel_info_['cargoTanks']['SLP']['lcg'] = 106.6
        ##
        vessel_info_['KTM'] = vessel_json['vessel']['keelToMastHeight']
        vessel_info_['LPP'] = float(vessel_json['vessel']['lengthBetweenPerpendiculars'])
        
        ## BM and SF
        vessel_info_['SSTable'] = pd.DataFrame(vessel_json['bmandSF']['shearingForceType1'], dtype=np.float)
        vessel_info_['SBTable'] = pd.DataFrame(vessel_json['bmandSF']['bendingMomentType1'], dtype=np.float)
        vessel_info_['frames'] = []
        vessel_info_['tankGroupLCG'], vessel_info_['tankGroup']  = {}, {}
        vessel_info_['SFlimits'], vessel_info_['BMlimits'] = {}, {}
        vessel_info_['locations'], vessel_info_['alpha'], vessel_info_['BWCorr'],  vessel_info_['C4'] = [], [], [], []
        vessel_info_['centerTank'], vessel_info_['wingTank'], vessel_info_['ballastTankBSF'] = [], [], []
        vessel_info_['BSFlimits'] = {}
        vessel_info_['distStation'] = {}
        
        for d_ in vessel_json['bmandSF']['calculationSheetTankGroup']:
            vessel_info_['frames'].append(d_['frameNumber'])
            vessel_info_['tankGroupLCG'][str(d_['tankGroup'])] = float(d_['lcg'])
            vessel_info_['tankGroup'][str(d_['tankGroup'])] = {}
        
        for d_ in vessel_json['bmandSF']['calculationSheet']:
            info_ = {'wr': float(d_['weightRatio'])/100, 'lcg': float(d_['lcg'])}
            tank_ = vessel_info_['tankId'][d_['tankId']]
            vessel_info_['tankGroup'][str(d_['tankGroup'])][tank_] = info_
            
        
        for d_ in vessel_json['bmandSF']['minMaxValuesForBMAndSfs']:
            vessel_info_['SFlimits'][str(int(float(d_['frameNumber'])))] = [float(d_['minSf']), float(d_['maxSf'])]
            vessel_info_['BMlimits'][str(int(float(d_['frameNumber'])))] = [float(d_['minBm']), float(d_['maxBm'])]
            
        ## max BM 
        for d_ in vessel_json['bmandSF']['stationValues']:
            xx_ = str(int(float(d_['frameNumberFrom']))) +'-'+str(int(float((d_['frameNumberTo']))))
            vessel_info_['distStation'][xx_] = d_['distance']
            
        
        ## BSF
        for d_ in vessel_json['bmandSF']['innerBulkHeadValues']:
#            print(d_)
            if '' not in (d_['foreAlpha'], d_['aftAlpha']):
                vessel_info_['locations'].append(str(int(float(d_['frameNumber']))) + 'f')
                vessel_info_['locations'].append(str(int(float(d_['frameNumber']))) + 'a')
                vessel_info_['alpha'].append(float(d_['aftAlpha']))
                vessel_info_['alpha'].append(float(d_['foreAlpha']))
                vessel_info_['BWCorr'].append(float(d_['aftBWCorrection']))
                vessel_info_['BWCorr'].append(float(d_['foreBWCorrection']))
                vessel_info_['C4'].append(float(d_['aftC4']))
                vessel_info_['C4'].append(float(d_['foreC4']))
                
                center_tanks_  = [vessel_info_['tankId'][int(t_)] for t_ in str(d_['aftCenterCargoTankId']).split(',')]
                wing_tanks_    = [vessel_info_['tankId'][int(t_)] for t_ in str(d_['aftWingTankIds']).split(',')]
                ballast_tanks_ = [vessel_info_['tankId'][int(t_)] for t_ in str(d_['aftBallstTanks']).split(',')]
                
                vessel_info_['centerTank'].append({'tanks':center_tanks_,'C1':float(d_['aftC1'])})
                vessel_info_['wingTank'].append({'tanks':wing_tanks_,'C2':float(d_['aftC2'])})
                vessel_info_['ballastTankBSF'].append({'tanks':ballast_tanks_,'C3':float(d_['aftC3'])})
                
                center_tanks_  = [vessel_info_['tankId'][int(t_)] for t_ in str(d_['foreCenterCargoTankId']).split(',')]
                wing_tanks_    = [vessel_info_['tankId'][int(t_)] for t_ in str(d_['foreWingTankIds']).split(',')]
                ballast_tanks_ = [vessel_info_['tankId'][int(t_)] for t_ in str(d_['foreBallstTanks']).split(',')]
                
                vessel_info_['centerTank'].append({'tanks':center_tanks_,'C1':float(d_['foreC1'])})
                vessel_info_['wingTank'].append({'tanks':wing_tanks_,'C2':float(d_['foreC2'])})
                vessel_info_['ballastTankBSF'].append({'tanks':ballast_tanks_,'C3':float(d_['foreC3'])})
                
                vessel_info_['BSFlimits'][str(int(float(d_['frameNumber']))) + 'f'] = [float(d_['foreMinAllowence'])*1000, float(d_['foreMaxAllowence'])*1000]
                vessel_info_['BSFlimits'][str(int(float(d_['frameNumber']))) + 'a'] = [float(d_['aftMinFlAllowence'])*1000, float(d_['aftMaxFlAllowence'])*1000]
    
                
            elif d_['aftAlpha'] == '':
                vessel_info_['locations'].append(str(int(float(d_['frameNumber']))) + 'f')
                vessel_info_['alpha'].append(float(d_['foreAlpha']))
                vessel_info_['BWCorr'].append(float(d_['foreBWCorrection']))
                vessel_info_['C4'].append(float(d_['foreC4']))
                
                center_tanks_  = [vessel_info_['tankId'][int(t_)] for t_ in str(d_['foreCenterCargoTankId']).split(',')]
                wing_tanks_    = [vessel_info_['tankId'][int(t_)] for t_ in str(d_['foreWingTankIds']).split(',')]
                ballast_tanks_ = [vessel_info_['tankId'][int(t_)] for t_ in str(d_['foreBallstTanks']).split(',')]
                
                vessel_info_['centerTank'].append({'tanks':center_tanks_,'C1':float(d_['foreC1'])})
                vessel_info_['wingTank'].append({'tanks':wing_tanks_,'C2':float(d_['foreC2'])})
                vessel_info_['ballastTankBSF'].append({'tanks':ballast_tanks_,'C3':float(d_['foreC3'])})
                
                vessel_info_['BSFlimits'][str(int(float(d_['frameNumber']))) + 'f'] = [float(d_['foreMinAllowence'])*1000, float(d_['foreMaxAllowence'])*1000]
                

            elif d_['foreAlpha'] == '':
                vessel_info_['locations'].append(str(int(float(d_['frameNumber']))) + 'a')
                vessel_info_['alpha'].append(float(d_['aftAlpha']))
                vessel_info_['BWCorr'].append(float(d_['aftBWCorrection']))
                vessel_info_['C4'].append(float(d_['aftC4']))
                
                center_tanks_  = [vessel_info_['tankId'][int(t_)] for t_ in str(d_['aftCenterCargoTankId']).split(',')]
                wing_tanks_    = [vessel_info_['tankId'][int(t_)] for t_ in str(d_['aftWingTankIds']).split(',')]
                ballast_tanks_ = [vessel_info_['tankId'][int(t_)] for t_ in str(d_['aftBallstTanks']).split(',')]
                
                vessel_info_['centerTank'].append({'tanks':center_tanks_,'C1':float(d_['aftC1'])})
                vessel_info_['wingTank'].append({'tanks':wing_tanks_,'C2':float(d_['aftC2'])})
                vessel_info_['ballastTankBSF'].append({'tanks':ballast_tanks_,'C3':float(d_['aftC3'])})
                
                vessel_info_['BSFlimits'][str(int(float(d_['frameNumber']))) + 'a'] = [float(d_['aftMinFlAllowence'])*1000, float(d_['aftMaxFlAllowence'])*1000]
                
            else: 
                print('Error!!')
        
        
        if inputs.module in ['LOADING', 'DISCHARGING']:
            ## pump data to add other later
            vessel_info_['pumpTypes'] = {}
            for d_ in vessel_json.get('pumpTypes', []):
                if d_['name'] == 'Ballast Pump':
                    vessel_info_['pumpTypes']['ballastPump'] = d_['id']
                elif d_['name'] == 'Ballast Eductor':
                    vessel_info_['pumpTypes']['ballastEductor'] = d_['id']
                 
            vessel_info_['vesselPumps'] = {}
            vessel_info_['vesselPumps']['ballastEductorId'] = {}
            vessel_info_['vesselPumps']['ballastPumpId'] = {}
            for d_ in vessel_json.get('vesselPumps', []):
                if d_['pumpTypeId'] == vessel_info_['pumpTypes']['ballastPump']:
                    
                    if 'ballastPump' not in vessel_info_['vesselPumps']:
                        vessel_info_['vesselPumps']['ballastPump'] = {}
                    
                    vessel_info_['vesselPumps']['ballastPump'][d_['pumpName']] = {k_:v_ for k_, v_ in d_.items() if k_ not in ['pumpName']}
                    vessel_info_['vesselPumps']['ballastPumpId'][d_['pumpId']] = d_['pumpName']
                    
                elif d_['pumpTypeId'] == vessel_info_['pumpTypes']['ballastEductor']:
                    
                    if 'ballastEductor' not in vessel_info_['vesselPumps']:
                        vessel_info_['vesselPumps']['ballastEductor'] = {}
                    
                    vessel_info_['vesselPumps']['ballastEductor'][d_['pumpName']] = {k_:v_ for k_, v_ in d_.items() if k_ not in ['pumpName']}
                    vessel_info_['vesselPumps']['ballastEductorId'][d_['pumpId']] = d_['pumpName']
                    
            
            vessel_info_['cargoPump'], vessel_info_['tankCargoPump'] = {}, {}
            if vessel_json.get('vesselPumpTankMappings', []):
                for l_ in vessel_json['vesselPumpTankMappings']:
                    
                    pump_ = l_['vesselPump']['pumpName']
                    vessel_info_['cargoPump'][pump_] = []
                    for l__ in l_['vesselPump']['vesselTanks']:
                        vessel_info_['cargoPump'][pump_].append(l__['shortName'])
                        vessel_info_['tankCargoPump'][l__['shortName']] = pump_
                        
            cargo_pumps_ = ['COP1','COP2','COP3','TCP', 'STP', 'STPED1', 'STPED2']
            vessel_info_['cargoPumpId'] = {}
            for p_ in vessel_json.get('vesselPumps', []):
                if p_['pumpCode'] in cargo_pumps_:
                    vessel_info_['cargoPumpId'][p_['pumpCode']] = {'id':p_['pumpId']}
                    
            if len(vessel_info_['cargoPumpId']) != len(cargo_pumps_):
                inputs.error['Cargo Pump Error'] = ["Missing cargo pumps!!"]
                    
           
        self.info = vessel_info_     
        
        if not Path(vessel_info_['name']+'.pickle').is_file():
            with open(vessel_info_['name']  +'.pickle', 'wb') as fp_:
                pickle.dump(vessel_info_, fp_)    
            
            
        
        
        
    def _get_onboard(self, inputs, loading = False): 
        onboard_json = inputs.vessel_json['onBoard']
        self.info['onboard'] = {} # leftover
        self.info['onboard']['totalWeight'] = 0. # leftover
        
        self.info['notOnTop'] = []
        
        if hasattr(inputs, 'loadable'):
            ave_sg_ = np.mean(inputs.loadable.info['sg'])
        else:
            ave_sg_ = 1.0
        
        for o__, o_ in enumerate(onboard_json):
            tank_ = self.info['tankId'][o_['tankId']]
            # port_order_ = '1A'
            
            # print(o_)
            wt_ = float(o_['plannedArrivalWeight']) if o_['plannedArrivalWeight'] not in [None] else 0.
            # vol1_ = float(o_['volume']) if o_['volume'] not in [None] else 0.
            if wt_ > 0. :
                
                # api_, temp_ = float(o_['api']), float(o_['temperature'])
                # density_ = inputs.loadable._cal_density(api_, temp_)
                    
                # vol1_ = wt_/density_
                
                vol_ = float(o_['volume'])
                
                if tank_ not in self.info['onboard'].keys():
                    self.info['onboard'][tank_] = {}
                    
                # vol_ =  max(vol1_, wt_/ave_sg_)
                self.info['onboard'][tank_]= {'vol': vol_, 'wt': wt_, 'temperature': float(o_['temperature'])}
                self.info['onboard']['totalWeight'] += wt_
                self.info['cargoTanks'][tank_]['api'] = o_.get('api',None)
                self.info['cargoTanks'][tank_]['colorCode'] = o_.get('colorCode',None)
                self.info['cargoTanks'][tank_]['sg'] = wt_/vol_
                self.info['cargoTanks'][tank_]['abbreviation'] = o_['abbreviation']
                self.info['cargoTanks'][tank_]['isSlop'] = o_['isSlopTank']
 
                
                # inputs.loadOnTop = False
                if (not inputs.loadOnTop) and self.info['cargoTanks'][tank_]['isSlop']:
                    
                    self.info['notOnTop'].append(tank_)
                    
                    for k_,v_ in inputs.loadable.info['parcel'].items():
                        self.info['banCargo'][k_].append(tank_)
                    # fixed tcg
                    tcg_data_ = self.info['tankTCG']['tcg'][tank_] # tcg_data
                    tcg_ = np.interp(vol_, tcg_data_['vol'], tcg_data_['tcg'])
                    self.info['cargoTanks'][tank_]['tcg'] = tcg_
                    # fixed lcg
                    
                    ## remove from pw-linear
                    self.info['tankTCG']['tcg_pw'].pop(tank_,None)
                    # self.info['tankTCG']['tcg_pw'].pop('1P',None)
                    
        if inputs.module in ['LOADABLE']:
            ## balllast -------------------------------------------------
            ## config
            
            # if inputs.config['loadableConfig'].get('initBallastTanksAmt',[]):
            #     ratio_ = inputs.config['loadableConfig']['initBallastTanksAmt']['amt']
            #     init_ballast_ = {}
            #     for t_ in inputs.config['loadableConfig']['initBallastTanksAmt']['tanks']:
            #         if t_[-1] in ["W"]:
            #             t1_, t2_ = 'WB'+t_[0]+'P', 'WB'+t_[0]+'S'
            #             init_ballast_[t1_] = round(self.info['ballastTanks'][t1_]['capacityCubm']*ratio_*1.025,2)
            #             init_ballast_[t2_] = round(self.info['ballastTanks'][t2_]['capacityCubm']*ratio_*1.025,2)
                        
            #         else:
            #             init_ballast_[t_] = round(self.info['ballastTanks'][t_]['capacityCubm']*ratio_*1.025,2)
                        
                
            # else:
            init_ballast_ = inputs.config['initial_ballast']
            
            
            self.info['initBallast'] = {'wt': init_ballast_,
                                        'dec':[t_ for t_ in self.info['ballastTanks'] if t_ not in self.info['banBallast']],
                                        'inc':[]}
            
            
            self.info['finalBallast'] = {}
            ## ballast requirements
            loading_port_ = [int(inputs.loadable.info['arrDepVirtualPort'][str(i_)+'D']) for i_ in range(1,inputs.port.info['numPort'])]
            # self.info['loadingNotLast'] = loading_port_[:-1]
            self.info['loading'] = loading_port_
            # self.info['depArr'] = loading_port_
            if len(inputs.loadable.info.get('rotationVirtual',[]))> 0:
                #self.info['rotationVirtual'] = [inputs.loadable.info['rotationVirtual'][0]-1] + inputs.loadable.info['rotationVirtual']
                self.info['rotationVirtual'] = [[l_[0]-1]+l_ for l_ in inputs.loadable.info['rotationVirtual']] 
            else:
                self.info['rotationVirtual'] = []  
            ## cargo tank requirements
            ## config all wing tank + slot tank
            # tanks_ = ['SLS', '1P', '1S', '2P', '2S', '4P', '4S', '5P', '3P', '3S', '5S']
            tanks_ = inputs.config['tanks_max_cargo']
            capacity_ = sum([0.98*v_['capacityCubm']  for k_,v_ in self.info['cargoTanks'].items() if k_ in tanks_])
            
            asym_ = True
            self.info['maxCargo'] = []
            if len(inputs.loadable.info['toLoadIntend']) > 1 and inputs.mode in ['Auto']:
                for k_,v_ in inputs.loadable.info['toLoadIntend'].items():
                    vol_need_ = v_/inputs.loadable.info['parcel'][k_]['SG']
                    if (vol_need_ > .99*capacity_):
                        asym_ = False
                        self.info['maxCargo'].append(k_)
            
            ## config ------
            slopP = [t_ for t_ in inputs.vessel.info['slopTank'] if t_[-1] == 'P'][0]
            slopS = [t_ for t_ in inputs.vessel.info['slopTank'] if t_[-1] == 'S'][0]
            self.info['notSym'] = [(slopP, slopS)]
            # self.info['notSym'] = [] #[inputs.config['diff_cargo_slops']]
            if asym_ and inputs.mode in ['Auto']:
                #self.info['notSym'] += [('1P','1C'), ('2P','2C'), ('3P','3C'), ('4P','4C'), ('5P','5C')]
                
                if inputs.loadable.info['numParcel'] == 2 and inputs.loadable.info['commingleCargo']:
                    
                    self.info['notSym'] += [('1P','1C'), ('3P','3C'), ('5P','5C')]
                else:
                    self.info['notSym'] += inputs.config['diff_cargo_tanks']
                
                
    def _set_preloaded(self, inputs): 
        
        if inputs.loadable.info['initialBallast']:
            self.info['initBallast'] = {'wt':{}, 'dec':[], 'inc':[]}
            
            for k_, v_ in inputs.loadable.info['initialBallast'].items():
                tank_ = self.info['tankId'][k_]
                self.info['initBallast']['wt'][tank_] = v_
            
            ## config for discharging 
            self.info['initBallast']['inc'] = ['WB1P','WB1S','WB2P','WB2S','WB3P','WB3S','WB4P','WB4S','WB5P','WB5S']
            
        else:
            self.info['initBallast'] = {'wt':{}, 'dec':[], 'inc':[]}
            
            for k_, v_ in inputs.vessel.info['ballastTanks'].items():
                if k_ not in inputs.vessel.info['banBallast']:
                    # tank_ = v_['tankId']
                    self.info['initBallast']['wt'][k_] = 0.
            
            ## config for discharging 
            self.info['initBallast']['inc'] = ['WB1P','WB1S','WB2P','WB2S','WB3P','WB3S','WB4P','WB4S','WB5P','WB5S']
        
            
        if  inputs.loadable.info['preloadOperation']:
            info_, wt_ = {}, 0.
            for k_, v_ in inputs.loadable.info['preloadOperation'].items():
                info_[k_] = {}
                for k1_, v1_ in v_.items():
                    tank_ = self.info['tankId'][k1_]
                    info_[k_][tank_] = v1_
                    density_ = inputs.loadable.info['parcel'][k_]['maxtempSG']
                    vol_ = v1_/density_
                    capacity_ = self.info['cargoTanks'][tank_]['capacityCubm']
                    if round(vol_/capacity_,3) > 0.98:
                        print(tank_, round(vol_/capacity_,3))
                        if 'Preloading Error' not in inputs.error.keys():
                            inputs.error['Preloading Error'] = ['Fill ratio exceeded in tank ' +  tank_ + '!!']
                        else:
                            inputs.error['Preloading Error'].append('Fill ratio exceeded in tank ' +  tank_ + '!!')
                    wt_ += v1_
                    
            inputs.loadable.info['preloadOperation'] = info_
            inputs.loadable.info['preloadAmt'] = wt_
            
            for k_, v_ in inputs.loadable.info['preloadOperation'].items():
                if self.info['slopTank'][0] in v_.keys():
                    inputs.loadable.info['inSlop'][k_].append(self.info['slopTank'][0])
                if self.info['slopTank'][1] in v_.keys():
                    inputs.loadable.info['inSlop'][k_].append(self.info['slopTank'][1])

        
    def _get_onhand(self, inputs): 
        # ## virtual ports ## config
        # DENSITY = {'DSWP':1.0, 'DWP':1.0, 'FWS':1.0, 'DSWS':1.0,
        #            'FO2P':0.98, 'FO2S':0.98, 'FO1P':0.98, 'FO1S':0.98, 'BFOSV':0.98, 'FOST':0.98, 'FOSV':0.98,
        #            'DO1S':0.88,  'DO2S':0.88, 'DOSV1':0.88, 'DOSV2':0.88}
        
        # ROB_CHANGE = 200 ## config
        
        DENSITY = inputs.config['rob_density'] # default density of ROB
        ROB_CHANGE = inputs.config['rob_change'] # change in ROB which required adjusting ballast b/w departure and arrival
        portId_ = []
        for p_ in range(len(inputs.port.info['portOrderId'])):
            id_ = inputs.port.info['portOrderId'][str(p_+1)]
            rot_id_ = inputs.port.info['portRotationId1'][id_]
            portId_.append(str(rot_id_))
            
            
        onhand_json = inputs.vessel_json['onHand']
        self.info['onhand'] = {} # ROB
        self.info['onhand1'] = {} # ROB
        self.info['initialROBweight'] = 0.
        for o__, o_ in enumerate(onhand_json):
            tank_ = self.info['tankId'].get(o_['tankId'],None)
            # print(tank_, o_['portId'])
            if o_.get('portRotationId', None) in [None]:
                if inputs.port.info['portRotationId1'].get(str(o_['portId']) + '1', None) not in [None]:
                    o_['portRotationId'] = inputs.port.info['portRotationId1'][str(o_['portId']) + '1']
                elif inputs.port.info['portRotationId1'].get(str(o_['portId']) + '2', None) not in [None]:
                    o_['portRotationId'] = inputs.port.info['portRotationId1'][str(o_['portId']) + '2']
                else:
                    o_['portRotationId'] = inputs.port.info['portRotationId1'][str(o_['portId']) + '3']
                    
            
            if tank_ and str(o_['portRotationId']) in portId_:
                port_order_  = [q__ +1 for q__, q_ in enumerate(portId_) if q_ == str(o_['portRotationId'])]
                tcg_data_ = self.info['tankTCG']['tcg'][tank_] # tcg_data
                lcg_data_ = self.info['tankLCG']['lcg'][tank_] # lcg_data
                
                if tank_ not in self.info['onhand'].keys():
                    self.info['onhand'][tank_] = {}
                    
                for port_order__ in port_order_:    
                    if str(port_order__)+'A' not in self.info['onhand1'].keys():
                        self.info['onhand1'][str(port_order__)+'A'] = {}
                    
                    if str(port_order__)+'D' not in self.info['onhand1'].keys():
                        self.info['onhand1'][str(port_order__)+'D'] = {}
                    
                # print(o_)
                wt_ = float(o_['arrivalQuantity']) if o_['arrivalQuantity'] not in [None] else 0.
                vol_ = wt_/DENSITY[tank_]
                # vol_ = float(o_['arrivalVolume']) if o_['arrivalVolume'] not in [None] else 0.
                
                # print(vol_)
                if wt_ > 0:
                    tcg_ = np.interp(vol_, tcg_data_['vol'], tcg_data_['tcg'])
                    lcg_ = np.interp(vol_, lcg_data_['vol'], lcg_data_['lcg'])
                    
                    for port_order__ in port_order_:    
                        self.info['onhand'][tank_][str(port_order__)+'A'] = {'wt': wt_, 'vol': vol_, 'tcg':tcg_, 'lcg':lcg_}
                        self.info['onhand1'][str(port_order__)+'A'][tank_] = wt_
                        
                        if port_order__ == 1:
                            self.info['initialROBweight'] += wt_
                            
                    
                wt_ = float(o_['departureQuantity']) if o_['departureQuantity'] not in [None] else 0.
                vol_ = wt_/DENSITY[tank_]
                # vol_ = float(o_['departureVolume']) if o_['arrivalVolume'] not in [None] else 0.
                # print(vol_)
                if wt_ > 0:
                    tcg_ = np.interp(vol_, tcg_data_['vol'], tcg_data_['tcg'])
                    lcg_ = np.interp(vol_, lcg_data_['vol'], lcg_data_['lcg'])
                    
                    for port_order__ in port_order_:    
                        self.info['onhand'][tank_][str(port_order__)+'D'] = {'wt': wt_, 'vol': vol_,'tcg':tcg_, 'lcg':lcg_}
                        self.info['onhand1'][str(port_order__)+'D'][tank_] = wt_
                
        self.info['sameROB'] = []
        self.info['changeROB'] = {}
        self.info['draftRestriction'] = []
        for p_ in range(1,inputs.port.info['numPort']):
            p1_, p2_ = str(p_)+'D', str(p_+1)+'A'
            # port1_, port2_ = inputs.port.info['portOrder'][p1_[:-1]], inputs.port.info['portOrder'][p2_[:-1]]
            wt1_ = sum([v_ for k_,v_ in self.info['onhand1'].get(p1_,{}).items()])
            wt2_ = sum([v_ for k_,v_ in self.info['onhand1'].get(p2_,{}).items()])
            
            self.info['changeROB'][(inputs.loadable.info['arrDepVirtualPort'][p1_],inputs.loadable.info['arrDepVirtualPort'][p2_])] = wt1_-wt2_
            p3_ = inputs.port.info['portOrderId'][str(p_+1)]
            if (abs(wt1_-wt2_) <= ROB_CHANGE) and (inputs.port.info['maxDraft'][p3_] >= 19.8):
            # if (self.info['onhand1'].get(p1_,{}) == self.info['onhand1'].get(p2_,{})) and (inputs.port.info['portRotation'][port1_]['seawaterDensity'] == inputs.port.info['portRotation'][port2_]['seawaterDensity']):
                q1_ = inputs.loadable.info['arrDepVirtualPort'][p1_]
                q2_ = inputs.loadable.info['arrDepVirtualPort'][p2_]
                s1_ = inputs.loadable.info['seawaterDensity'][q1_]
                s2_ = inputs.loadable.info['seawaterDensity'][q2_]
                
                print('sameROB:', p1_, p2_, inputs.loadable.info['arrDepVirtualPort'][p1_], inputs.loadable.info['arrDepVirtualPort'][p2_])
                if s1_ == s2_:
                    self.info['sameROB'].append((inputs.loadable.info['arrDepVirtualPort'][p1_],inputs.loadable.info['arrDepVirtualPort'][p2_]))
                else:
                    print('Diff seawater density:', s1_, s2_)
                    
            if inputs.port.info['maxDraft'][p3_] <= 19.8:
                self.info['draftRestriction'].append((inputs.loadable.info['arrDepVirtualPort'][p1_],inputs.loadable.info['arrDepVirtualPort'][p2_]))
                
        # print(self.info['onhand'])      
    
    def _get_lcg_parameters(self, vessel_info_, lcg_details_):
        
        if not Path(vessel_info_['name']+'_lcg_pw.pickle').is_file():
            npw_ = 10
            parameters_ = {'npw':npw_}
            for k_, v_ in lcg_details_.items():
                
                
                if k_ not in vessel_info_['banBallast'] and  v_['type'] in ['ballast'] and abs(v_['lcg'][-1]-v_['lcg'][2]) > 0.1:
                #if k_ not in vessel_info_['banBallast'] and  v_['type'] in ['ballast','cargo'] and abs(v_['lcg'][-1]-v_['lcg'][2]) > 0.1:
                    print(k_, v_['lcg'][-1], v_['lcg'][0], v_['lcg'][1] ,v_['lcg'][2])
                    
                    lcg_weight_ = np.array(v_['vol'])*1.0 # density == 1 
                    lcg_mom_ = lcg_weight_ * np.array(v_['lcg'])/1000
                    
                    my_pwlf = pwlf.PiecewiseLinFit(lcg_weight_, lcg_mom_)
                    # fit the data for four line segments
                    breaks = my_pwlf.fit(npw_)
                    slopes = my_pwlf.calc_slopes()
                    intercepts = my_pwlf.intercepts
                    
                    ## predict for the determined points
                    xHat = np.linspace(min(v_['vol']), max(v_['vol']), num=1000)*1.0
                    yHat = np.zeros(len(xHat))
                    
                    for i__,i_ in enumerate(xHat):
                        
                        m_ = np.where(i_ <= breaks[1:])[0][0]
                        yHat[i__] = slopes[m_]*i_ + intercepts[m_]
                        
#                    yy = np.interp(xHat,tcgVolumes_,tcgValues_)
#                    mse = np.abs(yy-yHat)
                    
                    parameters_[k_] = {'slopes':slopes.tolist(), 'breaks':breaks[1:].tolist(), 'intercepts':intercepts.tolist()}
            
                    fig = plt.figure()
                    ax = plt.axes()
                    ax.plot(v_['vol'], lcg_mom_,'o')
                    ax.plot(xHat, yHat, '-')
                    ax.set_title(vessel_info_['name'] + ' Tank: ' + k_)
                    ax.set_xlabel("volume")
                    ax.set_ylabel("LCGMoment")
                    fig_name = vessel_info_['name'] + '_Tank_LCG_'+ k_
                    fig.savefig(fig_name + '.png')
                    plt.close(fig)
                        
                    print(k_ + ': LCG approximation done!!')
                    # with open(k_  +'_lcg_pw.pickle', 'wb') as fp_:
                    #     pickle.dump(parameters_, fp_)   
                        
                else:
                    
                    print(k_ + ': LCG approximation not needed!!')
                    # print(k_, v_['lcg'][-1], v_['lcg'][0], v_['lcg'][1] ,v_['lcg'][2])
            
            vessel_info_['tankLCG']['lcg_pw'] = parameters_
            with open(vessel_info_['name']  +'_lcg_pw.pickle', 'wb') as fp_:
                pickle.dump(parameters_, fp_)     
                
        else:
            
            with open(vessel_info_['name']  +'_lcg_pw.pickle', 'rb') as fp_:
                vessel_info_['tankLCG']['lcg_pw'] = pickle.load(fp_)
            
    
    def _get_tcg_parameters(self, vessel_info_, tcg_details_):
        
        # with open('tcg_data.json', 'w') as f_:  
        #     json.dump({'data':tcg_details_}, f_)

        
        if not Path(vessel_info_['name']+'_pw.pickle').is_file():
            npw_ = 10
            parameters_ = {'npw':npw_}
            
            for k_, v_ in tcg_details_.items():
                if v_['type'] in ['ballast','cargo'] and abs(v_['tcg'][-1]-v_['tcg'][2]) > 0.1:
                    
                    tcg_weight_ = np.array(v_['vol']) # density == 1 
                    tcg_mom_ = tcg_weight_ * np.array(v_['tcg'])
                    
                    my_pwlf = pwlf.PiecewiseLinFit(v_['vol'], tcg_mom_)
                    # fit the data for four line segments
                    breaks = my_pwlf.fit(npw_)
                    slopes = my_pwlf.calc_slopes()
                    intercepts = my_pwlf.intercepts
                    
                    ## predict for the determined points
                    xHat = np.linspace(min(v_['vol']), max(v_['vol']), num=1000)
                    yHat = np.zeros(len(xHat))
                    
                    for i__,i_ in enumerate(xHat):
                        
                        m_ = np.where(i_ <= breaks[1:])[0][0]
                        yHat[i__] = slopes[m_]*i_ + intercepts[m_]
                        
#                    yy = np.interp(xHat,tcgVolumes_,tcgValues_)
#                    mse = np.abs(yy-yHat)
                    
                    parameters_[k_] = {'slopes':slopes.tolist(), 'breaks':breaks[1:].tolist(), 'intercepts':intercepts.tolist()}
            
                    fig = plt.figure()
                    ax = plt.axes()
                    ax.plot(v_['vol'], tcg_mom_,'o')
                    ax.plot(xHat, yHat, '-')
                    ax.set_title(vessel_info_['name'] + ' Tank: ' + k_)
                    ax.set_xlabel("volume")
                    ax.set_ylabel("TCGMoment")
                    fig_name = vessel_info_['name'] + '_Tank_TCG_'+ k_
                    fig.savefig(fig_name + '.png')
                    plt.close(fig)
                        
                    print(k_ + ': TCG approximation done!!')
                else:
                    
                    print(k_ + ': TCG approximation not needed!!')
            
            vessel_info_['tankTCG']['tcg_pw'] = parameters_
            with open(vessel_info_['name']  +'_pw.pickle', 'wb') as fp_:
                pickle.dump(parameters_, fp_)     
                
        else:
            
            with open(vessel_info_['name']  +'_pw.pickle', 'rb') as fp_:
                vessel_info_['tankTCG']['tcg_pw'] = pickle.load(fp_)
    
    def _get_lcb_parameters(self, vessel_info_):
        
        if not Path(vessel_info_['name']+'_trim.pickle').is_file():
            npw_ = 10
            parameters_ = {'npw':npw_}
            
            # lower_draft_, upper_draft_ = 6, 22
            # lower_ind_ = np.where(vessel_info_['hydrostatic']['draft'] == lower_draft_)[0][0]
            # upper_ind_ = np.where(vessel_info_['hydrostatic']['draft'] == upper_draft_)[0][0]
            
            draft_ = vessel_info_['hydrostatic']['draft']
            lcb_   = vessel_info_['hydrostatic']['lcb']
            disp_  = vessel_info_['hydrostatic']['displacement']
            mtc_   = vessel_info_['hydrostatic']['mtc']
            
            with open(vessel_info_['name']  + '_hydro_data.json', 'w') as f_:  
                json.dump({'draft':draft_.tolist(), 'lcb':lcb_.tolist(), 'disp':disp_.tolist(), 'mtc':mtc_.tolist() }, f_)

            
            # draft_ = vessel_info_['hydrostatic']['draft'][lower_ind_:upper_ind_]
            # lcb_   = vessel_info_['hydrostatic']['lcb'][lower_ind_:upper_ind_]
            # disp_  = vessel_info_['hydrostatic']['displacement'][lower_ind_:upper_ind_]
            # mtc_   = vessel_info_['hydrostatic']['mtc'][lower_ind_:upper_ind_]
                      
            ## LCB x disp ------------------------------------------------------------------------
            disp_lcb_ = lcb_ * disp_
            my_pwlf = pwlf.PiecewiseLinFit(disp_, disp_lcb_)
            # fit the data for four line segments
            breaks = my_pwlf.fit(npw_)
            slopes = my_pwlf.calc_slopes()
            intercepts = my_pwlf.intercepts
            
            ## predict for the determined points
            xHat = np.linspace(min(disp_), max(disp_), num=5000)
            yHat = np.zeros(len(xHat))
            
            for i__,i_ in enumerate(xHat):
                m_ = np.where(i_ <= breaks[1:])[0][0]
                yHat[i__] = slopes[m_]*i_ + intercepts[m_]
                
#                    yy = np.interp(xHat,tcgVolumes_,tcgValues_)
#                    mse = np.abs(yy-yHat)
            
            parameters_['lcb'] = {'slopes':slopes.tolist(), 'breaks':breaks[1:].tolist(), 'intercepts':intercepts.tolist()}
    
            fig = plt.figure()
            ax = plt.axes()
            ax.plot(disp_, disp_lcb_,'x')
            ax.plot(xHat, yHat, '-')
            ax.set_title('LCB')
            ax.set_xlabel("disp")
            ax.set_ylabel("Disp x LCB")
            fig.savefig(vessel_info_['name']  + '_LCB.png')
            plt.close(fig)
            
            print('LCB approximation done!!')
            
            ## MTC --------------------------------------------------------------
            my_pwlf = pwlf.PiecewiseLinFit(disp_, mtc_)
            # fit the data for four line segments
            breaks = my_pwlf.fit(npw_)
            slopes = my_pwlf.calc_slopes()
            intercepts = my_pwlf.intercepts
            
            ## predict for the determined points
            xHat = np.linspace(min(disp_), max(disp_), num=5000)
            yHat = np.zeros(len(xHat))
            
            for i__,i_ in enumerate(xHat):
                m_ = np.where(i_ <= breaks[1:])[0][0]
                yHat[i__] = slopes[m_]*i_ + intercepts[m_]
                
#                    yy = np.interp(xHat,tcgVolumes_,tcgValues_)
#                    mse = np.abs(yy-yHat)
            
            parameters_['mtc'] = {'slopes':slopes.tolist(), 'breaks':breaks[1:].tolist(), 'intercepts':intercepts.tolist()}
    
            fig = plt.figure()
            ax = plt.axes()
            ax.plot(disp_, mtc_ ,'x')
            ax.plot(xHat, yHat, '-')
            ax.set_title('MTC')
            ax.set_xlabel("disp")
            ax.set_ylabel("MTC")
            fig.savefig(vessel_info_['name']  + '_MTC.png')
            plt.close(fig)
            
            print('MTC approximation done!!')
            
            ## Draft --------------------------------------------------------------
          
            my_pwlf = pwlf.PiecewiseLinFit(disp_, draft_)
            # fit the data for four line segments
            breaks = my_pwlf.fit(npw_)
            slopes = my_pwlf.calc_slopes()
            intercepts = my_pwlf.intercepts
            
            ## predict for the determined points
            xHat = np.linspace(min(disp_), max(disp_), num=5000)
            yHat = np.zeros(len(xHat))
            
            for i__,i_ in enumerate(xHat):
                m_ = np.where(i_ <= breaks[1:])[0][0]
                yHat[i__] = slopes[m_]*i_ + intercepts[m_]
                
#                    yy = np.interp(xHat,tcgVolumes_,tcgValues_)
#                    mse = np.abs(yy-yHat)
            
            parameters_['draft'] = {'slopes':slopes.tolist(), 'breaks':breaks[1:].tolist(), 'intercepts':intercepts.tolist()}
    
            fig = plt.figure()
            ax = plt.axes()
            ax.plot(disp_, draft_,'x')
            ax.plot(xHat, yHat, '-')
            ax.set_title('Draft')
            ax.set_xlabel("disp")
            ax.set_ylabel("Draft")
            fig.savefig(vessel_info_['name']  + '_Draft.png')
            plt.close(fig)
            
            print('Draft approximation done!!')
            
            vessel_info_['lcb_mtc'] = parameters_
            with open(vessel_info_['name']  +'_trim.pickle', 'wb') as fp_:
                pickle.dump(parameters_, fp_)     
                
        else:
            
            with open(vessel_info_['name']  +'_trim.pickle', 'rb') as fp_:
                vessel_info_['lcb_mtc'] = pickle.load(fp_)
                        
    def _get_ullage_func(self, vessel_info_, ullage_data):
        
        # with open('ullage_data.json', 'w') as f_:  
        #     json.dump({'data':vessel_info_['ullage']}, f_)
        
        if not Path(vessel_info_['name'] +'_ullage.pickle').is_file():
            
            
            ullageDetails = pd.DataFrame(ullage_data['ullageDetails'], dtype=np.float)
            ullageTrimCorrections = pd.DataFrame(ullage_data['ullageTrimCorrections'], dtype=np.float)
            ullageTrimCorrections.drop(columns=['trimM2', 'trimM3', 'trimM4', 'trimM5'], inplace=True)
            
            ullage_func = {}
            ullage_inv_func = {}
            ullage_corr = {}
            ullage_data = {}
            ullage_empty = {}
            
            
            for k_, v_ in vessel_info_['tankName'].items():
                
                print(k_,v_)
                
                ullage_ = ullageDetails[ullageDetails['tankId'] == v_]
                ullage_ = ullage_.sort_values(by='ullageDepth')
                
                ullage_corr_ = ullageTrimCorrections[ullageTrimCorrections['tankId'] == v_]
                ullage_corr_ = ullage_corr_.sort_values(by='ullageDepth')
                
                yy_ = []
                if k_ in vessel_info_['ballastTanks']:
                    yy_ = ullage_['soundDepth'].astype('float')
                elif k_ in vessel_info_['cargoTanks']:
                    yy_ = ullage_['ullageDepth'].astype('float')
                
                if len(yy_) >  0:
                    
                    ullage_func[str(v_)] = interp1d(ullage_['evenKeelCapacityCubm'], yy_)
                    ullage_inv_func[str(v_)] = interp1d(yy_, ullage_['evenKeelCapacityCubm'])
                    ullage_corr[str(v_)] = ullage_corr_.values.tolist()
                    ullage_data[str(v_)] = ullage_.values.tolist()
                    ullage_empty[str(v_)] = float(ullage_func[str(v_)](ullage_['evenKeelCapacityCubm'].min()))
                    
                    
                else:
                    print(k_,v_, 'is empty or not needed!!')
            
            vessel_info_['ullage']  = ullage_func
            vessel_info_['ullageCorr']  = ullage_corr
            vessel_info_['ullageInvFunc']  = ullage_inv_func
            vessel_info_['ullageEmpty']  = ullage_empty
            
            
            
            with open(vessel_info_['name']  +'_ullage.pickle', 'wb') as fp_:
                pickle.dump([ullage_func, ullage_corr, ullage_inv_func, ullage_empty], fp_)     
                
        else:
            
            with open(vessel_info_['name']  +'_ullage.pickle', 'rb') as fp_:
                vessel_info_['ullage'], vessel_info_['ullageCorr'], vessel_info_['ullageInvFunc'], vessel_info_['ullageEmpty'] = pickle.load(fp_)
            
    # def _get_ullage_corr(self, vessel_info_, ullageCorrDetails):
        
    #     # with open('ullage_data.json', 'w') as f_:  
    #     #     json.dump({'data':vessel_info_['ullage']}, f_)
        
    #     if not Path(vessel_info_['name']+'_ullage_corr.pickle').is_file():
            
    #         vessel_info_['ullageCorr'] = {}
            
    #         for d_ in ullageCorrDetails: #vessel_json['ullageDetails']:
    #             # print(d_['id'])
    #             if str(d_['tankId']) not in vessel_info_['ullageCorr']:
    #                 vessel_info_['ullageCorr'][str(d_['tankId'])] = {'depth':[float(d_['ullageDepth'])], 'corr':[[float(d_['trimM1']),float(d_['trim0']), float(d_['trim1']),
    #                                                                                                           float(d_['trim2']),float(d_['trim3']),float(d_['trim4']),
    #                                                                                                           float(d_['trim5']),float(d_['trim6'])]]}
    #             else:
    #                 vessel_info_['ullageCorr'][str(d_['tankId'])] ['depth'].append(float(d_['ullageDepth']))
    #                 vessel_info_['ullageCorr'][str(d_['tankId'])] ['corr'].append([float(d_['trimM1']),float(d_['trim0']), float(d_['trim1']),
    #                                                                                float(d_['trim2']),float(d_['trim3']),float(d_['trim4']),
    #                                                                                float(d_['trim5']),float(d_['trim6'])])
    #                 # vessel_info_['ullage'][str(d_['tankId'])] ['id'].append(d_['id'])
        
    #         func_ = {}
    #         for k_, v_ in vessel_info_['ullageCorr'].items():
                
    #             xx_, yy_, zz_ = [], [], []
    #             for a_, b_ in zip(v_['depth'], v_['corr']):
    #                 xx_ += [a_ for i_ in range(8)]
    #                 yy_ += [-1, 0, 1, 2, 3, 4, 5, 6]
    #                 zz_ += b_
                
    #             func_[k_] = interp2d(xx_, yy_, zz_)
            
    #         vessel_info_['ullage_corr'] = func_
            
    #         with open(vessel_info_['name']  +'_ullage_corr.pickle', 'wb') as fp_:
    #             pickle.dump(func_, fp_)     
                
    #     else:
            
    #         with open(vessel_info_['name']  +'_ullage_corr.pickle', 'rb') as fp_:
    #             vessel_info_['ullage_func_corr'] = pickle.load(fp_)
    
    
 
            
            
# {'WB5P': 25606, 'WB5S': 25607, 'AWBP': 25608, 'AWBS': 25609, 'APT': 25610, 'FO2P': 25614, 
#'FO2S': 25615, 'SLS': 25596, 'WB1S': 25599, 'WB2P': 25600, 'WB2S': 25601, 'WB3P': 25602, 'WB3S': 25603, 
#'WB4P': 25604, 'WB4S': 25605, '2C': 25581, '1P': 25585, '1S': 25586, '2P': 25587, '2S': 25588, 'DO1S': 25622, 
#'4P': 25591, '4S': 25592, '5P': 25593, '1C': 25580, '3C': 25582, '4C': 25583, '5C': 25584, '3P': 25589, '3S': 25590, 
#'5S': 25594, 'SLP': 25595, 'WB1P': 25598, 'FO1P': 25612, 'FO1S': 25613, 'DO2S': 25623, 'FOST': 25617, 
#'BFOSV': 25619, 'DOSV1': 25624, 'LFPT': 25597, 'UFPT': 25611, 'FOSV': 25616, 'DOSV2': 25625, 'DWP': 25636, 
#'FWS': 25637, 'DSWP': 25638, 'DSWS': 25639}
    
        
        
        
        
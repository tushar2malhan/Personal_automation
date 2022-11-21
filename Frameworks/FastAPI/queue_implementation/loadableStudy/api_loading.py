# -*- coding: utf-8 -*-
"""
Created on Wed Jul 14 16:50:44 2021

@author: I2R
"""

from loading_init import Process_input
from vlcc_gen import Generate_plan 
from vlcc_check import Check_plans
from vlcc_valves import Generate_valves
from valveSequence import Constants, ValveFilters, ValveOperations, ValveSequencing, ValveConversion
import numpy as np
# import json

import pickle

def gen_sequence(data: dict) -> dict:
    
    if not data['vessel']:
        return {'message': 'Vessel details not available!!'}
    
    out = loading(data)
    
    return out


def loading(data: dict) -> dict:
    out = {}
    
    params = Process_input(data)
    params.prepare_data()
    params.write_ampl(IIS = False)
    
    # input("Press Enter to continue...")
    if not params.error:
        # collect plan from AMPL
        done_ = False 
        time_left_eduction = 0
        while not done_:
            gen_output = Generate_plan(params)
            gen_output.IIS = False if time_left_eduction < 30 else True
            gen_output.run(num_plans=1)
            
            if time_left_eduction <= 20 and len(gen_output.plans['ship_status']) == 0:
                time_left_eduction += 10
                IIS = False if time_left_eduction < 30 else True
                print('time_left_eduction:', time_left_eduction)
                params.loading._get_ballast_requirements(time_left_eduction = time_left_eduction)
                params.get_param()
                params.write_ampl(IIS = IIS)
                
            else:
                done_ = True
                
    else:
        gen_output = Generate_plan(params)
        gen_output.run(num_plans=1)
            
    
    #with open('result.pickle', 'wb') as fp_:
    #    pickle.dump(gen_output, fp_)  
    
    # with open('result.pickle', 'rb') as fp_:
    #     gen_output = pickle.load(fp_)
    
    ## check and modify plans    
    plan_check = Check_plans(params, reballast = True)
    plan_check._check_plans(gen_output)
   
      
    # gen json  
    out = gen_output.gen_json1({}, plan_check.stability_values)

    # Valve
    if params.error:
       print('Error while processing input. Skipping valve module.')
       return out
    elif len(gen_output.plans.get('ship_status', [])) == 0:
        print('Infeasible Solution. Skipping valve module.')
        return out
    elif params.vessel_id == 2:
        print('Valves module not ready for Atlantic Pioneer')
        return out
    else:
        # valve_params = Generate_valves(params, out, gen_output)  ## get parameters for valve module
        # valve_params.prepOperation()
        # valve_out = valve_params.integrateValves()

        # Cargo & Ballast Valves
        constants = Constants()
        vfilter = ValveFilters(constants)
        voperation = ValveOperations(vfilter, data, constants)
        voperation.getManifoldParameters(out)
        valve_time = ValveSequencing(out, voperation, constants.LOADING_OPS, constants)
        # Conversion
        valve_conversion = ValveConversion(out, constants)
        if hasattr(valve_time, 'load_valves'):
            valve_conversion.convertValves(valve_time.load_valves, 'cargoValves')
        if hasattr(valve_time, 'deballast_valves'):
            valve_conversion.convertValves(valve_time.deballast_valves, 'ballastValves')
        return valve_conversion.json #valve_out




def loadicator1(data, limits, stability = []):
    
    if data['module'] == 'LOADING':
    
        out = {"processId": data["processId"], 
               "loadingInformationId": data["loadingInformationId"],  
                'vesselId': data["vesselId"],
                'portId': data["portId"],
               "loadicatorResults":[]}
        
    elif data['module'] == 'DISCHARGING':
    
        out = {"processId": data["processId"], 
               "dischargingInformationId": data["dischargingInformationId"],  
                'vesselId': data["vesselId"],
                'portId': data["portId"],
               "loadicatorResults":[]}
      # print(limits)
    
    if data['stages'] in [None, []]:
        
        print('Need to calculate the stability!!')
        params = Get_info(data, limits)
        ship_status, cargo_tank = params._get_status()
        
        output = lambda: None
        setattr(output, 'plans', {})
        output.plans['ship_status'] = ship_status
        output.plans['cargo_tank'] = cargo_tank
                
        plan_check = Check_plans(params, reballast = False)
        plan_check._check_plans(output)

        
        for s__, s_ in enumerate(plan_check.stability_values): 
            u_ = s_['0']
            
            # ['forwardDraft', 'meanDraft', 'afterDraft', 
            # 'trim', 'heel', 'airDraft', 'freeboard', 
            # 'manifoldHeight', 'bendinMoment', 'shearForce']
            
            info_ = {}
            info_["calculatedDraftFwdPlanned"] = u_["forwardDraft"]
            info_["calculatedDraftMidPlanned"] = u_["meanDraft"]
            info_["calculatedDraftAftPlanned"] = u_["afterDraft"]
            info_["calculatedTrimPlanned"] = u_["trim"]
            info_["blindSector"] = None
            info_["list"] = u_["heel"]
            info_['airDraft'] = u_['airDraft']
            info_['deflection'] = u_.get("deflection", None) 
            info_['freeboard'] = u_.get("freeboard", None) 
            info_['manifoldHeight'] = u_.get("manifoldHeight", None) 
            info_["SF"] = u_["bendinMoment"]
            info_['BM'] = u_["shearForce"]
            info_['errorDetails'] = []
            info_['gomValue'] = None
            info_["SFFrameNumber"] = None
            info_['BMFrameNumber'] = None
            info_['UKC'] = u_.get("UKC", None)
            info_['displacement'] = u_.get("displacement", None)
            
            
            if info_['deflection'] in [None, ""]:
                sag_ = 0.
            else:
                sag_ = float(u_.get('deflection', 0.))/4000
                
            mid_ship_draft_ = float(u_["meanDraft"]) + sag_
            info_['judgement'] = []
            
            # UKC
            if info_['UKC'] and float(info_['UKC']) < limits['limits'].get('underKeelClearance', 0):
                info_['judgement'].append('Failed UKC check ('+ "{:.2f}".format(float(info_['UKC'])) +'m)!')
                print('Failed UKC check ('+ "{:.2f}".format(float(info_['UKC'])) +'m)!')
             
            
            # trim
            if abs(float(u_["trim"])) > limits['limits'].get('maxTrim',3):
                info_['judgement'].append('Failed trim check ('+ "{:.2f}".format(float(u_["trim"])) +'m)!')
                print('Failed trim check')
               
            # list
            if u_["heel"] not in [None and ""] and abs(float(u_["heel"])) >= 0.5:
                info_['judgement'].append('Failed list check ('+ "{:.1f}".format(float(u_["heel"])) +')!')
                print('Failed list check')
                
            
            # max permissible draft
            max_draft_ = max([float(u_["forwardDraft"]), float(u_["afterDraft"])]) 
            if str(data['portId']) in limits['limits']['draft']:
                limit_draft_ = limits['limits']['draft'][str(data['portId'])]
                limit_air_draft_ = limits['limits']['airDraft'][str(data['portId'])]
            
            else:
                limit_draft_ = limits['limits']['draft']['maxDraft']
                limit_air_draft_ = limits['limits']['maxAirDraft']
            
                
            if limit_draft_ < max_draft_:
                info_['judgement'].append('Failed max permissible draft check ('+ "{:.2f}".format(max_draft_) +'m)!')
                print('Failed max permissible draft check')
            # loadline 
            if limits['limits']['draft']['loadline'] < max_draft_:
                info_['judgement'].append('Failed loadline check ('+ "{:.2f}".format(max_draft_) +'m)!')
                print('Failed loadline check')
            # airDraft
            if limit_air_draft_ < float(info_['airDraft']) :
                info_['judgement'].append('Failed airdraft check ('+ "{:.2f}".format(float(info_['airDraft'])) +'m)!')
                print('Failed airdraft check')

            
            
            # SF
            if abs(float(u_["shearForce"])) > 100:
                
                if abs(float(u_["shearForce"])) == 10000:
                    info_['judgement'].append('Failed SF check (None)!')
                    info_["SF"]  = None
                else:
                    info_['judgement'].append('Failed SF check ('+ "{:.0f}".format(float(u_["shearForce"])) +')!')
                    print('Failed SF check')
                
            # BM
            if abs(float(u_["bendinMoment"])) > 100:
                if abs(float(u_["bendinMoment"])) == 10000:
                    info_['judgement'].append('Failed BM check (None)!')
                    info_["BM"]  = None
                    print('Failed BM check')
                else:
                    info_['judgement'].append('Failed BM check ('+ "{:.0f}".format(float(u_["bendinMoment"])) +')!')
                    print('Failed BM check')

            out["loadicatorResults"].append(info_)
        
        
        
    else:
        # 
        for s__, s_ in enumerate(data['stages']):
            u_, v_, w_  = s_['ldTrim'], s_['ldStrength'], s_['ldIntactStability']
            info_ = {}
            info_['time'] = int(float(s_.get('time',0)))
            
            info_["calculatedDraftFwdPlanned"] = u_["foreDraftValue"]
            info_["calculatedDraftMidPlanned"] = u_["meanDraftValue"]
            info_["calculatedDraftAftPlanned"] = u_["aftDraftValue"]
            info_["calculatedTrimPlanned"] = u_["trimValue"]
            info_["blindSector"] = None
            info_["list"] = str(u_["heelValue"])
            info_['airDraft'] = u_['airDraftValue']
            info_['deflection'] = u_.get("deflection", None) 
            info_['gomValue'] = w_.get("bigintialGomValue", None)
            info_["SF"] = v_["shearingForcePersentValue"]
            info_['BM'] = v_["bendingMomentPersentValue"]
            info_["SFFrameNumber"] = v_.get("sfFrameNumber", None)
            info_['BMFrameNumber'] = v_.get("bendingMomentPersentFrameNumber", None)
            
            info_['UKC'] = stability[s__]['UKC'] if stability else None
            info_['displacement'] = u_.get("displacementValue", None)
            # print('SFFN:', info_["SFFrameNumber"], 'BMFN:', info_['BMFrameNumber'])
            
            info_['errorDetails'] = []
            if u_["errorDetails"] not in [""]:
                info_['errorDetails'].append(u_["errorDetails"])
            if v_["errorDetails"] not in [""]:
                info_['errorDetails'].append(v_["errorDetails"])
            if w_["errorDetails"] not in [""]:
                info_['errorDetails'].append(w_["errorDetails"])
           
            if info_['deflection'] in [None, ""]:
                sag_ = 0.
            else:
                sag_ = float(u_.get('deflection', 0.))/4000
                
            mid_ship_draft_ = float(u_["meanDraftValue"]) + sag_
            info_['judgement'] = []
            
            # UKC
            if info_['UKC'] and float(info_['UKC']) < limits['limits'].get('underKeelClearance', 0):
                info_['judgement'].append('Failed UKC check ('+ "{:.2f}".format(float(info_['UKC'])) +'m)!')
                print('Failed UKC check ('+ "{:.2f}".format(float(info_['UKC'])) +'m)!')
                
            
            # trim
            if abs(float(u_["trimValue"])) > limits['limits'].get('maxTrim',3):
                info_['judgement'].append('Failed trim check ('+ "{:.2f}".format(float(u_["trimValue"])) +'m)!')
                print('Failed trim check ('+ "{:.2f}".format(float(u_["trimValue"])) +'m)!')
                
            # list
            if u_["heelValue"] not in [None and ""] and abs(float(u_["heelValue"])) >= 0.5:
                info_['judgement'].append('Failed list check ('+ "{:.1f}".format(float(u_["heelValue"])) +')!')
                print('Failed list check ('+ "{:.1f}".format(float(u_["heelValue"])) +')!')
                
            
            # max permissible draft
            max_draft_ = max([float(u_["foreDraftValue"]), float(u_["aftDraftValue"])]) 
            if str(data['portId']) in limits['limits']['draft']:
                limit_draft_ = limits['limits']['draft'][str(data['portId'])]
                limit_air_draft_ = limits['limits']['airDraft'][str(data['portId'])]
            
            else:
                limit_draft_ = limits['limits']['draft']['maxDraft']
                limit_air_draft_ = limits['limits']['maxAirDraft']
            
            
            if limit_draft_ < max_draft_:
                info_['judgement'].append('Failed max permissible draft check ('+ "{:.2f}".format(max_draft_) +'m)!')
                print('Failed max permissible draft check ('+ "{:.2f}".format(max_draft_) +'m)!')
            
            # loadline 
            if limits['limits']['draft']['loadline'] < max_draft_:
                info_['judgement'].append('Failed loadline check ('+ "{:.2f}".format(max_draft_) +'m)!')
                print('Failed loadline check ('+ "{:.2f}".format(max_draft_) +'m)!')
                
            # airDraft
            if limit_air_draft_ < float(info_['airDraft']) :
                info_['judgement'].append('Failed airdraft check ('+ "{:.2f}".format(float(info_['airDraft'])) +'m)!')
                print('Failed airdraft check ('+ "{:.2f}".format(float(info_['airDraft'])) +'m)!')
            
            # SF
            if abs(float(v_["shearingForcePersentValue"])) > 100:
                info_['judgement'].append('Failed SF check ('+ "{:.1f}".format(float(v_["shearingForcePersentValue"])) +')!')
                print(s__, 'Failed SF check ('+ "{:.1f}".format(float(v_["shearingForcePersentValue"])) +')!')
                # fail_SF_  = True
            # BM
            if abs(float(v_["bendingMomentPersentValue"])) > 100:
                info_['judgement'].append('Failed BM check ('+ "{:.1f}".format(float(v_["bendingMomentPersentValue"])) +')!')
                print(s__, 'Failed BM check ('+ "{:.1f}".format(float(v_["bendingMomentPersentValue"])) +')!')
                # fail_BM_ = True
                        
            out["loadicatorResults"].append(info_)
        
    
    
    
    return out

class Get_info(object):
    def __init__(self, data, limits):
        self.data = data
        # ['portRotation', 'portOrder', 'idPortOrder', 'portOrderId', 'firstPortBunker', 'lastLoadingPort', 
        # 'numPort', 'operationId', 'maxDraft', 'maxAirDraft', 'ambientTemperature']
        self.port = lambda: None
        setattr(self.port, 'info', {})
        self.port.info['id'] = data['portId']
        self.port.info['tide'] = limits['limits']['tide'][str(self.port.info['id'])]
        self.port.info['portDepth'] = data.get('portDepth', 99)
        
        # ['parcel', 'sg', 'maxPriority', 'priority', 'cargoPort', 'cargoRotation', 'rotationCheck', 
        # 'virtualPort', 'arrDepVirtualPort', 'virtualArrDepPort', 'lastVirtualPort', 'rotationVirtual', 
        # 'rotationCargo', 'seawaterDensity', 'commingleCargo', 'operation', 'toLoad', 'toLoadIntend', 
        # 'toLoadMin', 'toLoadPort', 'toLoadMinPort', 'cargoOrder', 'toLoadPort1', 'numParcel', 'manualOperation', 
        # 'preloadOperation', 'ballastOperation', 'fixedBallastPort']
       
        self.loadable = lambda: None
        setattr(self.loadable, 'info', {})
        self.loadable.info['seawaterDensity'] = {}
        self.loadable.info['seawaterDensity']['0'] = limits['limits']['seawaterDensity'][str(self.port.info['id'])]
        
        
        # ['hasLoadicator', 'banBallast', 'banCargo', 'slopTank', 'loadingRate6', 'loadingRate1', 
        # 'loadingRateVessel', 'loadingRateRiser', 'name', 'lightweight', 'deadweightConst',
        # 'draftCondition', 'height', 'depth', 'manifoldHeight', 'cargoTankNames', 'ballastTankNames',
        # 'otherTankNames', 'cargoTanks', 'ballastTanks', 'fuelTanks', 'dieselTanks', 'freshWaterTanks',
        # 'tankId', 'tankName', 'category', 'tankFullName', 'ullage', 'ullageCorr', 'ullageInvFunc', 
        # 'ullageEmpty', 'ullage30cm', 'hydrostatic', 'lcb_mtc', 'tankTCG', 'tankLCG', 'KTM', 'LPP', 
        # 'SSTable', 'SBTable', 'frames', 'tankGroupLCG', 'tankGroup', 'SFlimits', 'BMlimits', 'locations', 
        # 'alpha', 'BWCorr', 'C4', 'centerTank', 'wingTank', 'ballastTankBSF', 'BSFlimits', 'distStation', 
        # 'onhand', 'onhand1', 'sameROB', 'onboard', 'initBallast', 'finalBallast', 'loading', 'rotationVirtual',
        # 'maxCargo', 'notSym']

        self.vessel = lambda: None
        setattr(self.vessel, 'info', {})
        if data['vesselId'] in [1, "1"]:
            
            with open('KAZUSA.pickle', 'rb') as fp_:
                self.vessel.info = pickle.load(fp_)
                
        elif data['vesselId'] in [2, "2"]:
            
            with open('ATLANTICPIONEER.pickle', 'rb') as fp_:
                self.vessel.info = pickle.load(fp_)

        self.error = {}
        self.module = "ULLAGE"
        self.vessel_id = data['vesselId']
        self.tide_info = None
        
    def _get_status(self):
        ship_status, cargo_tank = [{"0":{"cargo": {}, "ballast": {}, "other": {}}}], [{}]
        
        for k_, v_ in self.data['planDetails'].items():
            
            if k_ in ['stowageDetails']:
                for l_ in v_:
                    
                    if l_['quantity'] > 0. :
                        cargo_ = 'P' + str(l_['cargoNominationXId'])
                        wt_  = l_['quantity']
                        
                        tankId_ = l_['tankXId']
                        tankName_ = self.vessel.info['tankId'][tankId_]
                        capacity_ = self.vessel.info['cargoTanks'][tankName_]['capacityCubm']
                        # print(tankName_)
                        
                        if cargo_ not in cargo_tank[0]:
                            cargo_tank[0][cargo_] = [tankName_]
                        else:
                            cargo_tank[0][cargo_].append(tankName_)
                            
                        
                        api_ = l_['api']
                        temp_ = l_['temperature']
                        density_ = self._cal_density(api_, temp_)
                        vol_ = wt_/density_ 
                        
                        fillingRatio_ = round(vol_/capacity_,3)
                        tcg_ = 0.
                        if tankName_ in self.vessel.info['tankTCG']['tcg']:
                            tcg_ = np.interp(vol_, self.vessel.info['tankTCG']['tcg'][tankName_]['vol'],
                                             self.vessel.info['tankTCG']['tcg'][tankName_]['tcg'])
                            
                        lcg_ = 0.
                        if tankName_ in self.vessel.info['tankLCG']['lcg']:
                            lcg_ = np.interp(vol_, self.vessel.info['tankLCG']['lcg'][tankName_]['vol'],
                                             self.vessel.info['tankLCG']['lcg'][tankName_]['lcg'])
                        
                        corrUllage_ = round(self.vessel.info['ullage'][str(tankId_)](vol_).tolist(), 6)
                        
                        info_ = {"parcel": cargo_,
                                "wt": wt_,
                                "SG": density_,
                                "fillRatio": fillingRatio_,
                                "tcg": tcg_,
                                "lcg": lcg_,
                                "temperature": temp_,
                                "api": api_,
                                "corrUllage": corrUllage_,
                                "maxTankVolume": capacity_,
                                "vol": vol_}
                        
                        ship_status[0]["0"]["cargo"][tankName_] = [info_]
                    
                    
                
                
            elif k_ in ['commingleDetails']:
                for l_ in v_:
                    
                    cargo1_ = 'P' + str(l_['cargoNomination1Id'])
                    cargo2_ = 'P' + str(l_['cargoNomination2Id'])
                    
                    wt_  = l_['quantityMT']
                        
                    tankId_ = l_['tankId']
                    tankName_ = self.vessel.info['tankId'][tankId_]
                    capacity_ = self.vessel.info['cargoTanks'][tankName_]['capacityCubm']
                    
                    if cargo1_ not in cargo_tank[0]:
                        cargo_tank[0][cargo1_] = [tankName_]
                    else:
                        cargo_tank[0][cargo1_].append(tankName_)
                        
                    if cargo2_ not in cargo_tank[0]:
                        cargo_tank[0][cargo2_] = [tankName_]
                    else:
                        cargo_tank[0][cargo2_].append(tankName_)
                            
                    
                    api_ = l_['api']
                    temp_ = l_['temperature']
                    density_ = self._cal_density(api_, temp_)
                    vol_ = wt_/density_ 
                    
                    fillingRatio_ = round(vol_/capacity_,3)
                    tcg_ = 0.
                    if tankName_ in self.vessel.info['tankTCG']['tcg']:
                        tcg_ = np.interp(vol_, self.vessel.info['tankTCG']['tcg'][tankName_]['vol'],
                                         self.vessel.info['tankTCG']['tcg'][tankName_]['tcg'])
                        
                    lcg_ = 0.
                    if tankName_ in self.vessel.info['tankLCG']['lcg']:
                        lcg_ = np.interp(vol_, self.vessel.info['tankLCG']['lcg'][tankName_]['vol'],
                                         self.vessel.info['tankLCG']['lcg'][tankName_]['lcg'])
                    
                    corrUllage_ = round(self.vessel.info['ullage'][str(tankId_)](vol_).tolist(), 6) 
                    
                    info_ = {
                        "parcel": [cargo1_, cargo2_],
                        "wt": wt_,
                        "SG": density_,
                        "fillRatio": fillingRatio_,
                        "tcg": tcg_,
                        "lcg": lcg_,
                        "temperature": temp_,
                        "api": api_,
                        "wt1": None,
                        "wt2": None,
                        "wt1percent": None,
                        "wt2percent": None,
                        "corrUllage": corrUllage_,
                        "maxTankVolume": capacity_,
                        "vol": vol_}
                    
                    ship_status[0]["0"]["cargo"][tankName_] = [info_]
                
            elif k_ in ['ballastDetails']:
                for l_ in v_:
                    
                    if l_['quantity'] > 0. :
                        
                        tankId_ = l_['tankXId'] 
                        
                        tank_ = self.vessel.info['tankId'][int(tankId_)]
                        density_ = 1.025
                        capacity_ =  self.vessel.info['ballastTanks'][tank_]['capacityCubm']
                        wt_ = l_['quantity']
                        vol_ = wt_/density_
                        
                        fillingRatio_ = round(vol_/capacity_,3)
                        
                        tcg_ = 0.
                        if tank_ in self.vessel.info['tankTCG']['tcg']:
                            tcg_ = np.interp(vol_, self.vessel.info['tankTCG']['tcg'][tank_]['vol'],
                                              self.vessel.info['tankTCG']['tcg'][tank_]['tcg'])
                            
                        lcg_ = 0.
                        if tank_ in self.vessel.info['tankLCG']['lcg']:
                            lcg_ = np.interp(vol_, self.vessel.info['tankLCG']['lcg'][tank_]['vol'],
                                              self.vessel.info['tankLCG']['lcg'][tank_]['lcg'])
                        
                           
                        try:
                            corrLevel_ = self.vessel.info['ullage'][str(tankId_)](vol_).tolist()
                        except:
                            print('correct level not available:',tank_, vol_)
                            corrLevel_ = 0.
                        
                        info_ = {"wt": wt_,
                            "SG": density_,
                            "fillRatio": fillingRatio_,
                            "tcg": tcg_,
                            "lcg": lcg_,
                            "corrLevel": corrLevel_,
                            "maxTankVolume": capacity_,
                            "vol": vol_}
                        
                        ship_status[0]["0"]["ballast"][tank_] = [info_]
            
            elif k_ in ['robDetails']:
                for l_ in v_:
                    
                    if l_['quantity'] > 0. :
                        
                        tankId_ = l_['tankXId'] 
                        
                        tank_ = self.vessel.info['tankId'][int(tankId_)]
                        density_ = l_['density']
                        wt_ = l_['quantity']
                        vol_ = wt_/density_
                        
                        tcg_ = 0.
                        if tank_ in self.vessel.info['tankTCG']['tcg']:
                            tcg_ = np.interp(vol_, self.vessel.info['tankTCG']['tcg'][tank_]['vol'],
                                              self.vessel.info['tankTCG']['tcg'][tank_]['tcg'])
                            
                        lcg_ = 0.
                        if tank_ in self.vessel.info['tankLCG']['lcg']:
                            lcg_ = np.interp(vol_, self.vessel.info['tankLCG']['lcg'][tank_]['vol'],
                                              self.vessel.info['tankLCG']['lcg'][tank_]['lcg'])
                        
                        
                        info_ = {"wt": wt_,
                                "SG": density_,
                                "tcg": tcg_,
                                "lcg": lcg_,
                                "vol": vol_}
                        
                        ship_status[0]["0"]["other"][tank_] = [info_]
                    
            
        
        
        return ship_status, cargo_tank
        
        
            
    def _cal_density(self, api, temperature_F):
        
        
        ## https://www.myseatime.com/blog/detail/cargo-calculations-on-tankers-astm-tables
    
        a60 = 341.0957/(141360.198/(api+131.5))**2
        dt = temperature_F-60
        vcf_ = np.exp(-a60*dt*(1+0.8*a60*dt))
        t13_ = (535.1911/(api+131.5)-0.0046189)*0.42/10
        density = t13_*vcf_*6.2898
        
    
        return round(density,6)
    
        
        
        
        
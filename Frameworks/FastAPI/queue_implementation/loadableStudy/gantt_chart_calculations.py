#!/usr/bin/env python
# coding: utf-8

# In[135]:


import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from scipy.interpolate import interp1d
import gantt_chart_operations as ops


# initial stage volume and time calculation
def initial_stage(no_of_tanks, start_time, config):
    tank_specific_rate = config["INITIAL_RATE"] / no_of_tanks
    volume_initial = (tank_specific_rate * config['INITIAL_TIME']) / 60
    initial_stage_time = start_time + config['INITIAL_TIME']
    return volume_initial, initial_stage_time


# inc to max stage volume and time calculation
def inc_to_max_stage(inc_to_max_rate, no_of_tanks, initial_stage_time, config):
    tank_specific_rate = inc_to_max_rate / no_of_tanks
    volume_discharged = (tank_specific_rate * config['INC_TIME']) / 60
    inc_max_time = initial_stage_time + config['INC_TIME']
    return volume_discharged, inc_max_time


# decreasing rates stage for partial discharge volume and time calculation
def dec_stage(dec_rate, no_of_tanks, config):
    tank_specific_rate = dec_rate / no_of_tanks

    volume_discharged = tank_specific_rate * config['DEC_TIME'] / 60
    return volume_discharged


# reduced rates stage for partial discharge volume and time calculation
def reduced_stage(no_of_tanks, config):
    tank_specific_rate = config["REDUCED_RATE"] / no_of_tanks
    volume_discharged = tank_specific_rate * config['INC_TIME'] / 60
    return volume_discharged


# concert weight to volume of cargo
def _cal_density(api, temperature_F):
    ## https://www.myseatime.com/blog/detail/cargo-calculations-on-tankers-astm-tables
    a60 = 341.0957 / (141360.198 / (api + 131.5)) ** 2
    dt = temperature_F - 60
    vcf_ = np.exp(-a60 * dt * (1 + 0.8 * a60 * dt))
    t13_ = (535.1911 / (api + 131.5) - 0.0046189) * 0.42 / 10
    density = t13_ * vcf_ * 6.2898

    return round(density, 6)


def getVolumeOfCargo(weight, density):
    vol = weight / density
    return vol


# UPDATE TANK PARAMETER FOR DISCHARGE AND OPERATIONS

# complete discharge of tank from certain amount to 0
def updateCompleteDischargeParam(param_dict):
    param_dict['complete_discharge'] = True
    return param_dict


# stripping of tank when tank is completely discharged (compulsory after complete discharge)
def updateStrippingParam(param_dict, cell_value, config):
    param_dict['cow_strip_duration'] = config['STRIP_TIME']
    param_dict['complete_discharge'] = True
    if 'Strip -p' in cell_value: # if strip -p mentioned in operation, means stripping to be done by strip pump
        param_dict['StripPump'] = 'Strip Pump'
    return param_dict


# decide cow time and type
def decideCOWTime(tank, config):
    cow_type = 'Full'
    if len(config["MANUAL_COW"]) > 0:  # manual cow, top/full/bottom cow specified
        if config["MANUAL_COW"][tank]['cowType'] == 'Top':
            cow_type = 'Top'
            cow_time = config['TOP_COW_TIME'] + config['STRIP_TIME']
        elif config["MANUAL_COW"][tank]['cowType'] == 'Bottom':
            cow_type = 'Bottom'
            cow_time = config['BOTTOM_COW_TIME'] + config['STRIP_TIME']
        elif config["MANUAL_COW"][tank]['cowType'] == 'Full':
            cow_time = config['FULL_COW_TIME'] + config['STRIP_TIME']
    else: # auto cow, full cow for all except when we have to cow more than 6 tanks and cannot reuse cargo for COW
        if (tank in config['BOTTOM_COW_TANKS']) & (tank not in config['heavyWeatherTank']):
            cow_time = config['BOTTOM_COW_TIME'] + config['STRIP_TIME']
            cow_type = 'Bottom'
        else:
            cow_time = config['FULL_COW_TIME'] + config['STRIP_TIME']
    return cow_time, cow_type


# update cow paramters (type and time) for tanks with COW
def updateCOWParam(param_dict, tank, config):
    cow_time, cow_type = decideCOWTime(tank, config) # cow + stripping after cow
    param_dict['cow_strip_duration'] += cow_time
    #     param_dict['complete_discharge'] = True
    param_dict['COWType'] = cow_type # full/top/bottom
    return param_dict


# initialise tank parameters
def initialiseParamDictForTank(tank, prev_value, cell_value, cargo, config):
    param_dict = {}

    if cargo != 'null':
        if cargo not in prev_value:
            start_volume = prev_value[list(prev_value.keys())[0]]['volume']
        else:
            start_volume = prev_value[cargo]['volume']

        end_volume = cell_value[cargo]['volume']
        param_dict['tank'] = tank
        param_dict['cargo'] = cargo
        param_dict['api'] = config["CARGO_DETAILS"][cargo]['api']
        param_dict['temperature'] = config["CARGO_DETAILS"][cargo]['temperature']
        param_dict['high_vapour'] = config["CARGO_DETAILS"][cargo]['isHrvpCargo']
        param_dict['condensate'] = config["CARGO_DETAILS"][cargo]['isCondensateCargo']
        param_dict['initial_volume'] = start_volume

        param_dict['end_volume'] = end_volume
        param_dict['cow_strip_duration'] = 0
    else:
        start_volume = prev_value[list(prev_value.keys())[0]]['volume']
        end_volume = cell_value[cargo]['volume']
        param_dict['tank'] = tank
        param_dict['cargo'] = cargo
        param_dict['api'] = np.nan
        param_dict['temperature'] = np.nan
        param_dict['high_vapour'] = False
        param_dict['condensate'] = False
        param_dict['initial_volume'] = start_volume

        param_dict['end_volume'] = 0
        param_dict['cow_strip_duration'] = 0

    # cow / strip
    param_dict['COWTime'] = np.nan
    param_dict['COWType'] = np.nan
    param_dict['StripTime'] = np.nan
    param_dict['StripPump'] = 'TCP'
    param_dict['complete_discharge'] = False

    # early COW
    param_dict['earlyCOW'] = False
    param_dict['earlyCOWDuration'] = np.nan
    param_dict['earlyCOWTime'] = np.nan
    param_dict['earlyCOWType'] = np.nan

    # slop discharge
    param_dict['slopDischarge'] = False
    param_dict['slopPartialDischarge'] = False

    # load on top
    param_dict['loadOnTopDischarge'] = False
    param_dict['tankTransferAmt'] = False
    param_dict['tankTransferStartTime'] = np.nan

    # tank transfer
    param_dict['tankTransfer'] = False
    param_dict['tankTransferAmt'] = False
    param_dict['tankTransferStartTime'] = np.nan

    # fresh oil
    param_dict['freshOil'] = False
    param_dict['freshOilAmt'] = False
    param_dict['freshOilStartTime'] = np.nan
    param_dict['restricted'] = False
    return param_dict


# # update parameter if there is slop discharge
# def updateSlopDischarge(param_dict, tank, config):
#     param_dict['slopDischarge'] = True
#     if param_dict['end_volume'] == 0:
#         param_dict['end_volume'] = config['cargoTank30Capacity'][tank]
#     #     param_dict['complete_discharge'] = True
#     return param_dict
def updateearlySlopDischarge(param_dict, tank, config):
    param_dict['earlySlopDischarge'] = True
#     if param_dict['end_volume'] == 0:
#         param_dict['end_volume'] = config['cargoTank30Capacity'][tank]
    #     param_dict['complete_discharge'] = True
    return param_dict

# update tank if there is partial discharge of slop (use afterwards for calculations)
def updateSlopPartialDischarge(param_dict, tank, config):
    param_dict['slopPartialDischarge'] = True
    param_dict['complete_discharge'] = True
    if param_dict['end_volume'] == 0: # end volume for partial discharge is 30% of tank capacity
        param_dict['end_volume'] = config['cargoTank30Capacity'][tank]
    return param_dict


# update tank parameters (amount, duration, type) if there is tank transfer
def updateTankTransfer(param_dict, tank, ops, shift_ops, config):
    param_dict['complete_discharge'] = True
    if 'TTT' in ops:
        if 'dest' in ops:  # tank to transfer cargo into (so this tank's volume should increase)
            param_dict['restricted'] = True
            param_dict['end_volume'] = float(config['cargoTank30Capacity'][tank])
            param_dict['tankTransfer'] = True
            param_dict['tankTransferAmt'] = float(
                config['cargoTank30Capacity'][config['DRIVE_OIL_TANK'][config['CURRENT_STAGE']][0]])
            param_dict['tankTransferStartTime'] = config['WARM_PUMP_TIME'] + config['AIR_PURGE_TIME'] + config[
                'FLOOD_SEP_TIME'] + config['TANK_TRANSFER_DELAY']
        else: # tank to transfer cargo from  (so this tank's volume should drop)
            param_dict['tankTransfer'] = True
            param_dict['tankTransferAmt'] = -float(
                config['cargoTank30Capacity'][config['DRIVE_OIL_TANK'][config['CURRENT_STAGE']][0]])
            if not tank.endswith('C'):
                param_dict['tankTransferAmt'] = param_dict['tankTransferAmt'] / 2
            param_dict['tankTransferStartTime'] = config['WARM_PUMP_TIME'] + config['AIR_PURGE_TIME'] + config[
                'FLOOD_SEP_TIME'] + config['TANK_TRANSFER_DELAY']

    elif 'FO' in ops:
        if param_dict['cargo'] == 'null': # cargo information
            cargo = config['CURRENT_CD'][0]
            param_dict['cargo'] = cargo
            param_dict['api'] = config["CARGO_DETAILS"][cargo]['api']
            param_dict['temperature'] = config["CARGO_DETAILS"][cargo]['temperature']
            param_dict['high_vapour'] = config["CARGO_DETAILS"][cargo]['isHrvpCargo']
            param_dict['condensate'] = config["CARGO_DETAILS"][cargo]['isCondensateCargo']

        density = _cal_density(param_dict['api'], param_dict['temperature'])
        vol = getVolumeOfCargo(config['FRESH_OIL_MT'], density)
        if 'dest' in ops:  # tank to transfer cargo into (so this tank's volume should increase)
            param_dict['restricted'] = True
            param_dict['end_volume'] = vol
            param_dict['freshOil'] = True
            param_dict['freshOilAmt'] = vol
            param_dict['freshOilStartTime'] = config['WARM_PUMP_TIME'] + config['AIR_PURGE_TIME'] + config[
                'FLOOD_SEP_TIME'] + config['TANK_TRANSFER_TIME'] + config['TANK_TRANSFER_DELAY']
            if shift_ops:  # shift back fresh oil transfer to do COW of that tank first if COW allocated
                param_dict['earlyCOW'] = True
                param_dict['earlyCOWTime'] = config['WARM_PUMP_TIME'] + config['AIR_PURGE_TIME'] + config[
                    'FLOOD_SEP_TIME'] + config['TANK_TRANSFER_TIME']
                param_dict['earlyCOWDuration'] = config['FULL_COW_TIME'] + config['STRIP_TIME']
                param_dict['freshOilStartTime'] = param_dict['freshOilStartTime'] + param_dict['earlyCOWDuration']
                param_dict['earlyCOWType'] = 'Full'
        else: # tank to transfer cargo from  (so this tank's volume should drop)
            param_dict['freshOil'] = True
            param_dict['freshOilAmt'] = -vol
            if not tank.endswith('C'):
                param_dict['freshOilAmt'] = param_dict['freshOilAmt'] / 2
            param_dict['freshOilStartTime'] = config['WARM_PUMP_TIME'] + config['AIR_PURGE_TIME'] + config[
                'FLOOD_SEP_TIME'] + config['TANK_TRANSFER_TIME'] + config['TANK_TRANSFER_DELAY']
            if shift_ops:  # shift back fresh oil transfer to do COW of that tank first if COW allocated
                param_dict['freshOilStartTime'] = param_dict['freshOilStartTime'] + config['FULL_COW_TIME'] + config[
                    'STRIP_TIME']

    return param_dict


# get tank parameters depending on dataframe of operations
def getTankOperationSpecificParam(df_input, column, cow_restriction_stages, config):
    column = df_input.columns[column]
    prev_col = df_input.columns[int(column) - 1]
    partial_items = []
    complete_cow = []
    empty_items = []
    cow_tanks = []
    early_slop = []
    for j in range(len(df_input.index)):
        item = df_input.index[j]
        cell_value = json.loads(df_input.loc[item][column])
        prev_value = json.loads(df_input.loc[item, prev_col])
        for cargo in cell_value.keys():

            param_dict = initialiseParamDictForTank(item, prev_value, cell_value, cargo, config)
            shift_ops = False
            # Discharge
            if 'PD' in cell_value[cargo]['operation']:
                if item in config["SLOP_TANK"]:
                    param_dict = updateSlopPartialDischarge(param_dict, item, config)
                else:
                    partial_items.append(param_dict)

            if 'CD' in cell_value[cargo]['operation']:
                param_dict = updateCompleteDischargeParam(param_dict)

            # Strip/COW
            if ('Strip' in cell_value[cargo]['operation']) or ('Strip -p' in cell_value[cargo]['operation']):
                param_dict = updateStrippingParam(param_dict, cell_value[cargo]['operation'], config)

            if ('COW' in cell_value[cargo]['operation']) & (column not in cow_restriction_stages):
                cow_tanks.append(item)
                shift_ops = True
                param_dict = updateCOWParam(param_dict, item, config)

            # Slop discharge
            if 'SD-COW' in cell_value[cargo]['operation']:
                param_dict = updateSlopPartialDischarge(param_dict, item, config)
            
            if 'eSD' in cell_value[cargo]['operation']:
                param_dict = updateearlySlopDischarge(param_dict, item, config)
                early_slop.append(param_dict)
            # tank transfer
            if 'TTT' in cell_value[cargo]['operation']:
                param_dict = updateTankTransfer(param_dict, item, 'TTT_dest', False, config)
            elif 'FO' in cell_value[cargo]['operation']:
                param_dict = updateTankTransfer(param_dict, item, 'FO_dest', shift_ops, config)

        if param_dict['complete_discharge'] | pd.notna(param_dict['COWType']):
            complete_cow.append(param_dict)
        elif param_dict not in partial_items and param_dict not in early_slop:
            empty_items.append(param_dict)

    return complete_cow, partial_items, empty_items, cow_tanks,early_slop


# MAIN CALCULATION


# calculate all volume during initial stages (air purge, flood separator, warm pumps, initial rate, inc to max)
def initial_calculation(item, df_initial, no_of_tanks, stages_timing, config):
    start_time = 0
    initial_volume = item['initial_volume']
    diff_volume = initial_volume - item['end_volume']

    # air purge
    if config['AIR_PURGE_TIME'] > 0:
        air_purge_time = start_time + config['AIR_PURGE_TIME']
        volume_air_purge = initial_volume
        stages_timing['Air Purge'] = [start_time, air_purge_time]
    else:
        volume_air_purge = initial_volume
        air_purge_time = start_time

    # flood separator
    volume_flood_sep, flood_sep_time = initial_volume, air_purge_time + config['FLOOD_SEP_TIME']
    stages_timing['Flood Separator'] = [air_purge_time, flood_sep_time]

    # Warm pumps
    volume_warm_pump, warm_pump_time = initial_volume, flood_sep_time + config['WARM_PUMP_TIME']
    stages_timing['Warming Pumps'] = [flood_sep_time, warm_pump_time]

    # initial rate
    volume_initial, initial_stage_time = initial_stage(no_of_tanks, warm_pump_time, config)
    end_volume_initial = initial_volume - volume_initial
    stages_timing['Initial Rate'] = [warm_pump_time, initial_stage_time]

    if item['restricted'] | (diff_volume <= 0):
        volume_flood_sep = initial_volume
        end_volume_initial = initial_volume

    if item['tankTransfer']:
        transfer_end_time = item['tankTransferStartTime'] + config['TANK_TRANSFER_TIME']
        if initial_stage_time >= transfer_end_time:
            end_volume_initial = end_volume_initial + item['tankTransferAmt']  # negative accounted for
    #             item['tankTransfer'] = False
    if item['freshOil']:
        transfer_end_time = item['freshOilStartTime'] + config['TANK_TRANSFER_TIME']
        if initial_stage_time >= transfer_end_time:
            end_volume_initial = end_volume_initial + item['freshOilAmt']  # negative accounted for
    #             item['freshOil'] = False

    # inc to max
    inc_to_max_rate = (config["INITIAL_RATE"] + config["MAX_RATE"][config['CURRENT_STAGE'] - 1]) / 2
    volume_inc, inc_max_time = inc_to_max_stage(inc_to_max_rate, no_of_tanks, initial_stage_time, config)
    end_volume_inc_to_max = end_volume_initial - volume_inc
    stages_timing['Increase to Max Rate'] = [initial_stage_time, inc_max_time]

    if item['restricted'] | (diff_volume <= 0):
        end_volume_inc_to_max = initial_volume

    if item['tankTransfer']:
        transfer_end_time = item['tankTransferStartTime'] + config['TANK_TRANSFER_TIME']
        if inc_max_time >= transfer_end_time:
            end_volume_inc_to_max = end_volume_inc_to_max + item['tankTransferAmt']  # negative accounted for
    #             item['tankTransfer'] = False
    elif item['freshOil']:
        transfer_end_time = item['freshOilStartTime'] + config['TANK_TRANSFER_TIME']
        if inc_max_time >= transfer_end_time:
            end_volume_inc_to_max = end_volume_inc_to_max + item['freshOilAmt']  # negative accounted for
    #             item['freshOil'] = False

    df_initial.loc[item['tank'], air_purge_time] = volume_air_purge
    df_initial.loc[item['tank'], flood_sep_time] = volume_flood_sep
    df_initial.loc[item['tank'], warm_pump_time] = volume_warm_pump
    df_initial.loc[item['tank'], initial_stage_time] = end_volume_initial
    df_initial.loc[item['tank'], inc_max_time] = end_volume_inc_to_max

    df_initial = correctionForSmallDischargeVolume(df_initial, item)

    return df_initial, stages_timing, item


# set time to start cow for each tank and volume of tank during the COW/Stripping stage
def cow_initial(complete_cow, partial_items, config):
    temp_cow = pd.DataFrame()
    cow_tanks = []
    tank_record = []

    # when there are partial discharge and complete discharge,
    # need to add additional 2 sub stages before cow of first tank with decreasing rate before actual cow can start
    if len(partial_items) > 0:
        for index, ele in enumerate(partial_items):  # for each partial discharge tank
            item = ele['tank']
            temp_cow.loc[item, 0] = np.nan
            temp_cow.loc[item, config['DEC_TIME']] = np.nan  # first decreasing rate sub stage
            temp_cow.loc[item, config['DEC_TIME'] + config['INC_TIME']] = ele[
                'end_volume']  # second decreasing rate sub stage

        for index, ele in enumerate(complete_cow):  # for each complete discharge tank
            if not ele['slopPartialDischarge']:
                item = ele['tank']
                temp_cow.loc[item, 0] = np.nan
                temp_cow.loc[item, config['DEC_TIME']] = np.nan  # first decreasing rate sub stage
                temp_cow.loc[item, config['DEC_TIME'] + config['INC_TIME']] = np.nan  # second decreasing rate sub stage
            else:  # slop partial discharge, slop volume cannot change as its used as drive oil tank
                item = ele['tank']
                temp_cow.loc[item, 0] = ele['end_volume']
                temp_cow.loc[item, config['DEC_TIME']] = ele['end_volume']  # first decreasing rate sub stage
                temp_cow.loc[item, config['DEC_TIME'] + config['INC_TIME']] = ele[
                    'end_volume']  # second decreasing rate sub stage

        cow_time = config['DEC_TIME'] + config['INC_TIME']
    else:
        for index, ele in enumerate(complete_cow):
            item = ele['tank']
            if not (ele['slopPartialDischarge'] | ele['restricted']):
                temp_cow.loc[item, 0] = np.nan
            else:  # slop partial discharge, slop volume cannot change as its used as drive oil tank
                temp_cow.loc[item, 0] = ele['end_volume']
        cow_time = 0

    # set time to start for tanks to COW
    for index, ele in enumerate(complete_cow):

        # Wing tanks
        if ele['tank'].endswith('P') & (not ele['slopPartialDischarge']) & (not ele['restricted']):
            end_cow_time = cow_time + ele['cow_strip_duration']
            # Wing P tanks
            if ele['initial_volume'] > 0:
                temp_cow.loc[ele['tank'], cow_time] = config["cow_strip_vol"][ele['tank']]  # strip volume
            else:
                temp_cow.loc[ele['tank'], cow_time] = 0  # end of cow strip 0
            temp_cow.loc[ele['tank'], end_cow_time] = 0  # end of cow strip 0

            # Wing S tanks
            other_wing_tank = ele['tank'][:-1] + 'S'
            if other_wing_tank not in config["SLOP_TANK"]:
                if ele['initial_volume'] > 0:
                    temp_cow.loc[other_wing_tank, cow_time] = config["cow_strip_vol"][other_wing_tank]  # strip volume
                else:
                    temp_cow.loc[other_wing_tank, cow_time] = 0  # end of cow strip 0
                temp_cow.loc[other_wing_tank, end_cow_time] = 0  # end of cow strip 0
                cow_tanks.append((ele['tank'], other_wing_tank))
                tank_record += [ele['tank'], other_wing_tank]
            cow_time = end_cow_time

        # Center tanks
        elif ele['tank'].endswith('C') & (not ele['slopPartialDischarge']) & (not ele['restricted']):
            if ele['initial_volume'] > 0:
                temp_cow.loc[ele['tank'], cow_time] = config["cow_strip_vol"][ele['tank']]
            else:
                temp_cow.loc[ele['tank'], cow_time] = 0  # end of cow strip 0
            temp_cow.loc[ele['tank'], cow_time + ele['cow_strip_duration']] = 0
            cow_time += ele['cow_strip_duration']
            cow_tanks.append(ele['tank'])
            tank_record += [ele['tank']]

        # Other tanks to be COWed (e.g. slop tanks)
        elif (ele['cow_strip_duration'] > 0) & (ele['tank'] not in tank_record) & (not ele['slopPartialDischarge']) & (
                not ele['restricted']):
            if ele['initial_volume'] > 0:
                temp_cow.loc[ele['tank'], cow_time] = config["cow_strip_vol"][ele['tank']]
            else:
                temp_cow.loc[ele['tank'], cow_time] = 0  # end of cow strip 0
            temp_cow.loc[ele['tank'], cow_time + ele['cow_strip_duration']] = 0
            cow_tanks.append(ele['tank'])
            tank_record += [ele['tank']]
            cow_time += ele['cow_strip_duration']

    temp_cow = temp_cow[sorted(temp_cow.columns)]
    return temp_cow, cow_tanks


# depending on number of tanks to cow, calculate rates for each substage (each substage is the COW of a set of tanks)
def sub_cow_rates(temp_cow, config,partial_discharge_check):
    #stagescount = temp_cow.isna().sum(axis=1).max()

    #if stagescount > 0:
        #stages_to_get_rate = np.arange(1, stagescount)
        #stages_known_rate = {0: config["MAX_RATE"][config['CURRENT_STAGE'] - 1], stagescount: config["REDUCED_RATE"]}
        #stages_rates = np.interp(stages_to_get_rate, list(stages_known_rate.keys()),
                                 #list(stages_known_rate.values())).tolist()
        #stages_rates.append(config["REDUCED_RATE"])
        #stages_rates.append(0)
    #else:
        #stages_rates = [0]
    stages_rates = []
    for i in range(len(temp_cow.columns)):
        tanks = []
        final_list = []
        col_name = temp_cow.columns[i]
        for j in range(len(temp_cow.index)):
            item = temp_cow.index[j]
            #print(item)
            cell_value = temp_cow.loc[item,col_name]
            cell_value = float(cell_value)
            if partial_discharge_check or item in ['SLP','SLS']:
                pass
            elif (cell_value != config['cow_strip_vol'][item]) and (cell_value !=0.0):
                tanks.append(item)

            else :
                pass
        #print(tanks)  
        for tank in tanks:
            if tank.endswith('P'):
                tank = tank[:-1] +'W'
                final_list.append(tank)
            elif tank.endswith('S'):
                pass
            else:
                final_list.append(tank)
        if temp_cow[col_name].isna().sum() >0 and i == 0 and partial_discharge_check:
            stages_rates.append(config["MAX_RATE"][config['CURRENT_STAGE'] - 1])
        elif temp_cow[col_name].isna().sum() >0 and i == 1 and partial_discharge_check:
            stages_rates.append(config["MAX_RATE"][config['CURRENT_STAGE'] - 1]-3000) 
        elif temp_cow[col_name].isna().sum() ==1 and partial_discharge_check:
            stages_rates.append(2550)      

        elif len(final_list) ==1:
            stages_rates.append(2550)
        elif len(final_list) ==2:
            stages_rates.append(5100)
        elif len(final_list)>=3:
            stages_rates.append(config["MAX_RATE"][config['CURRENT_STAGE'] - 1])

    stages_rates.append(0)
    return stages_rates


# set volume of tanks for other restricted tanks (TT, FO) tanks that cannot be discharged
def backFillStaggeredCOW(complete_cow, temp_cow):
    for item in complete_cow:
        tank = item['tank']
        if item['restricted'] | item['slopPartialDischarge']:
            temp_cow.loc[tank, :] = item['end_volume']
        # elif item['initial_volume'] == 0:
        #     temp_cow.loc[tank, :] = 0
    temp_cow = temp_cow.ffill(axis=1)
    return temp_cow


# precalculate when each tank will COW
def preCalculateCOWGanttChart(partial_items, complete_cow, config):
    partial_discharge_check = len(partial_items) > 0

    temp_cow, cow_tanks = cow_initial(complete_cow, partial_items, config) # set time for substages and cow/stripping of tanks

    temp_cow = backFillStaggeredCOW(complete_cow, temp_cow) # fill up volume for tanks which cannot be discharged

    cow_rates = sub_cow_rates(temp_cow, config,partial_discharge_check) # calculate discharge rate for each sub stage

    tanks_available = list(temp_cow.iloc[:, :].isna().sum()) # for ech substage get the no. of tanks to be discharged

    stage_specific_tank_rate = []

    for i in range(len(cow_rates)): # get rate of each tank for each sub stage
        if (cow_rates[i] > 0) & (tanks_available[i] > 0):
            tank_rate = cow_rates[i] / tanks_available[i]
        else:
            tank_rate = 0
        stage_specific_tank_rate.append(tank_rate)

    return temp_cow, stage_specific_tank_rate


# calculate all volume during end stages when there is only partial discharge (decrease rate, reduced rate)
def partial_only_calculation(item, df_end, no_of_tanks, start_time, stages_timing, config):
    end_dec_time = start_time + config['DEC_TIME']
    end_reduced_time = end_dec_time + config['INC_TIME']

    # reduced rate
    end_volume = item['end_volume']
    volume_reduced_stage = reduced_stage(no_of_tanks, config)
    end_reduced_stage = end_volume + volume_reduced_stage
    stages_timing['Reduced Rate'] = [start_time, end_reduced_time]

    # decreasing rate
    dec_rate = (config["MAX_RATE"][config['CURRENT_STAGE'] - 1] + config["REDUCED_RATE"]) / 2

    volume_decreased_stage = dec_stage(dec_rate, no_of_tanks, config)
    end_dec_stage = end_reduced_stage + volume_decreased_stage

    if item['restricted']:
        end_dec_stage = item['end_volume']
        end_reduced_stage = item['end_volume']

    df_end.loc[item['tank'], start_time] = end_dec_stage
    df_end.loc[item['tank'], end_dec_time] = end_reduced_stage
    df_end.loc[item['tank'], end_reduced_time] = end_volume
    return df_end, stages_timing


# calculate all volume for end stage when there are tanks with complete discharge (COW/Strpping stage)
def partial_complete_calculation(item, df_end, stage_specific_tank_rate, stages_timing, config):
    tank = item['tank']
    to_fill = df_end.loc[tank]
    end_volume = df_end.loc[tank, to_fill.first_valid_index()]
    prev_volume = end_volume

    if (df_end.loc[tank, 0] == config["cow_strip_vol"][tank]) | (df_end.loc[tank, 0] == item['initial_volume']):
        if (item['cow_strip_duration'] > config['STRIP_TIME']) & pd.isna(item['COWTime']):
            item['COWTime'] = 0
        elif (item['cow_strip_duration'] == config['STRIP_TIME']) & pd.isna(item['StripTime']):
            item['StripTime'] = 0

    for idx in range(len(stage_specific_tank_rate) - 1, -1, -1):
        start_time = list(df_end.columns)[idx]
        end_time = list(df_end.columns)[idx + 1]
        duration = float(end_time) - float(start_time)

        if pd.isna(df_end.loc[tank, start_time]):
            start_volume = prev_volume + (stage_specific_tank_rate[idx] * duration / 60)
            df_end.loc[tank, start_time] = start_volume
            prev_volume = start_volume

            if (item['cow_strip_duration'] > config['STRIP_TIME']) & pd.isna(item['COWTime']):
                item['COWTime'] = end_time
            elif (item['cow_strip_duration'] == config['STRIP_TIME']) & pd.isna(item['StripTime']):
                item['StripTime'] = end_time

    stages_timing['COW/Stripping'] = [0, list(df_end.columns)[-1]]

    return df_end, stages_timing, item


# calculation of initial and end stages for partial discharge
def partial_discharge(item, df_initial, df_end, no_of_tanks, stages_timing, config):
    df_initial, stages_timing, item = initial_calculation(item, df_initial, no_of_tanks, stages_timing, config)
    df_end, stages_timing = partial_only_calculation(item, df_end, no_of_tanks, 0, stages_timing, config)

    return df_initial, df_end, stages_timing, item


# calculation of initial and end stages for complete discharge
def partial_complete_discharge(item, df_initial, df_end, no_of_tanks, stage_tank_rates, stages_timing, config):
    df_initial, stages_timing, item = initial_calculation(item, df_initial, no_of_tanks, stages_timing, config)
    df_end, stages_timing, item = partial_complete_calculation(item, df_end, stage_tank_rates, stages_timing, config)

    return df_initial, df_end, stages_timing, item


# calculation of all intermediate snapshots for max stage
def max_stage(info, df_initial, df_middle, tank_max_rate, max_time_minutes, stages_timing, config):
    tank = info['tank']

    last_initial_time = list(df_initial.columns)[-1]
    last_initial_volume = df_initial.loc[tank, last_initial_time]  # time, end of initial stages
    initial_max_time_minutes = df_initial.columns[-1] + max_time_minutes  # time, end of max stage

    extra_transfer_amt = 0
    total_transfer_amt = 0
    end_time = np.nan
    if info['tankTransfer']: # calculate amount to be reduced from tank due to tank transfer
        total_transfer_amt += info['tankTransferAmt']
        if info['tankTransferStartTime'] > last_initial_time:
            extra_transfer_amt = info['tankTransferAmt']
            end_time = info['tankTransferStartTime'] + config['TANK_TRANSFER_TIME']
    if info['freshOil']: # calculate amount to be reduced from tank due to fresh oil transder
        total_transfer_amt += info['freshOilAmt']
        if info['freshOilStartTime'] > last_initial_time:
            extra_transfer_amt += info['freshOilAmt']
            end_time = info['freshOilStartTime'] + config['TANK_TRANSFER_TIME']

    current_time = config['INTERVAL_MINUTES'] # first intermediate timestamp to be generated to be interval calculated
    if current_time <= last_initial_time:
        current_time += config['INTERVAL_MINUTES']
    idx = 0
    while current_time < initial_max_time_minutes: # calculate volume for intermediate timestamp within max rate stage
        time_interval = current_time - last_initial_time # current duration in max rate stage until current timestamp
        volume_discharged = time_interval * tank_max_rate / 60 # volume discharge until current timestamp
        if (idx == 0) & (pd.notna(end_time)):
            volume_discharged += extra_transfer_amt
        df_middle.loc[tank, current_time] = last_initial_volume - volume_discharged # volume at current timestamp
        current_time += config['INTERVAL_MINUTES'] # current time
        idx += 1
    if info['restricted']:
        df_middle.loc[tank, :] = total_transfer_amt
    stages_timing['Max Rate Discharging'] = [last_initial_time, initial_max_time_minutes]
    return df_middle, stages_timing


# for tank transfer or fresh oil get the highest volume tank as source tank to transfer to slops
def getHighestVolumeTank(all_tanks, slop, config):
    slop_info = [t for t in all_tanks if t['tank'] == slop][0]
    slop_cargo = [slop_info['cargo']]
    if slop_cargo == ['null']:
        slop_cargo = [item['cargo'] for item in all_tanks if
                      (not item['restricted']) & (not item['slopPartialDischarge'])]

    cargo_tank, highest_volume = [], 0
    for info in all_tanks:
        tank = info['tank']
        cargo = str(info['cargo'])
        v = info['initial_volume']
        dischargedCargoVolume = config["cargoTankCapacity"][tank] * 0.98 - (config['cop_close_vol'][tank] * 1.05 / 2)

        if (tank not in config["SLOP_TANK"]) & (v >= highest_volume) & (
                cargo in slop_cargo)& (v < dischargedCargoVolume) &(tank != slop):
            if tank.endswith('P'):
                cargo_tank = [tank[:-1] + 'S', tank]
            elif tank.endswith('S'):
                cargo_tank = [tank[:-1] + 'P', tank]
            else:
                cargo_tank = [tank]
            highest_volume = v
    return cargo_tank


# identify any special operation (tank transfer, fresh oil, slop discharge, early slop discharge) in particular stage
def identifyOperations(df, column, config):
    ops = {'TTT': [], 'FO': [], 'SD': [], 'COW': [], 'eSD': [], 'CD': []}
    for tank in df.index:
        info = json.loads(df.loc[tank, column])
        c = list(info.keys())[0]
        for i in info[c]["operation"]:
            if i in ops:
                if i == 'COW':
                    if tank.endswith('P'):
                        ops[i].append((tank, tank[:-1] + 'S'))
                    elif tank.endswith('C'):
                        ops[i].append(tank)
                elif i == 'CD':
                    ops[i].append(c)
                elif i == 'eSD':
                    ops[i].append(tank)
                else:
                    ops[i].append(tank)
        if (tank in config['SLOP_TANK']) & (tank not in ops['SD']):
            if (info[c]['volume'] == 0.0) & ('PD' in info[c]['operation']):
                ops['SD'].append(tank)
    return ops


# identify if duration of current discharge able to accomadate number of intermediate snapshots requested
def identifyIntermediateStages(total_time, stage, config):
    if config['INTERVAL'] == 'stages':
        config["INTERVAL_HOUR"] = np.floor(total_time / (config['INTERVAL_STAGES']+1))
        if config["INTERVAL_HOUR"] < 1:
            config['ERROR'].append(
                f'Discharge time for current Stage {stage} too short to accomadate {config["INTERVAL_STAGES"]} stages. Total discharge time is approximately {round(total_time, 2)} hrs with max discharge rate {config["MAX_RATE"][stage - 1]}m3/hr.')
    else:
        if total_time * 1.01 <= config["INTERVAL_HOUR"]:
            config['ERROR'].append(
                f'Discharge time for current Stage {stage} too short to accomadate {config["INTERVAL_HOUR"]}hrs interval. Total discharge time is approximately {round(total_time, 2)} hrs with max discharge rate {config["MAX_RATE"][stage - 1]}m3/hr.')

    config["INTERVAL_MINUTES"] = config["INTERVAL_HOUR"] * 60
    return config


# correction of volume if volume at end of initial stages is lower than volume at start of end stages
def correctionForPossibleLoading(df_initial, df_end, param_dict):
    last_initial_time = list(df_initial.columns)[-1]

    for t in df_initial.index:
        if (not param_dict[t]['restricted']) & (not param_dict[t]['slopPartialDischarge']):
            last_initial_volume = df_initial.loc[t, last_initial_time]
            for col in df_end.columns:
                end_volume = df_end.loc[t, col]
                diff = last_initial_volume - end_volume
                if diff < -0.001:  # it shd be negative
                    df_end.loc[t, col] = last_initial_volume

    return df_initial, df_end


# Correction of volume when very little cargo is discharged and discharging end before end of initial stages
def correctionForSmallDischargeVolume(df_initial, item):
    t = item['tank']
    if (not item['restricted']) & (not item['slopPartialDischarge']):
        planned_end_volume = item['end_volume']
        timings = list(df_initial.columns)[::-1]
        for col in timings:
            if df_initial.loc[t, col] < planned_end_volume:
                df_initial.loc[t, col] = planned_end_volume
    return df_initial


# main calcuation to get events and volume at current port
def ganttChartCalculation(config, df_input, cow_restriction, early_top_cow):
    result_dict = {i: {} for i in range(1, len(df_input.columns))}

    for column in range(1, len(df_input.columns)):

        print(column)
        config['CURRENT_STAGE'] = int(column)
        ops = identifyOperations(df_input, int(column), config)
        config['CURRENT_CD'] = ops['CD']

        # Initialise output for current stage
        df_initial = pd.DataFrame()
        df_end = pd.DataFrame()
        df_middle = pd.DataFrame()
        df_final = pd.DataFrame()
        stages_timing = {}
        firstCOWTime = 10e9
        firstCOWTank = np.nan
        tanks_cowed = []
        tanks_stripped = []
        earlyCOW_tanks = {}
        tanksDischarged = []
        earlyCOW = {'TCP': []}
        strip_pump = {'TCP': [], 'Strip Pump': []}
        transfer_pump = {'TCP': []}
        fresh_oil_pump = {'TCP': []}
        earlySlopDischarge = {'COP':[]}
        pumps = {'strip': strip_pump, 'transfer': transfer_pump, 'fresh oil': fresh_oil_pump, 'earlyCOW': earlyCOW,'earlySlopDischarge':earlySlopDischarge}
        df_events = pd.DataFrame(index=config["TANKS"])
        freshOilDischarge = []
        freshOilStorageTank = []
        tankTransfer = []
        slopDischarge = ops['SD']
        earlySlopDischarge = ops['eSD']
        updated_param_dict = {}
        drive_oil_tank = []

        # For each tank, find operation specific parameters (PD, CD, COW etc.)
        bottomCOW = config['BOTTOM_COW_TANKS']  # have to replace
        complete_cow, partial_items, empty_items, cow_tanks,early_slop = getTankOperationSpecificParam(df_input, column,
                                                                                            cow_restriction, config)
        complete_cow = sorted(complete_cow, key=lambda x: x['tank'])

        no_of_tanks = len(partial_items) + len(complete_cow)
        all_tanks = partial_items + complete_cow

        fails_restriction = True
        get_debottoming_time = False
        earliest_debottom_tanks = []
        earliest_debottom_time = 9999999
        if no_of_tanks > 0:
            while fails_restriction:
                df_initial = pd.DataFrame()
                df_end = pd.DataFrame()
                df_middle = pd.DataFrame()
                df_final = pd.DataFrame()

                # get special operations like fresh oil, tank transfer, early COW
                if len(ops['TTT']) > 0:
                    slop_tank = ops['TTT'][0] # tank transfer destination tank (slop tanks) given
                    slop_tank_info = [(idx, t) for idx, t in enumerate(all_tanks) if t['tank'] == slop_tank]

                    if len(earliest_debottom_tanks) == 0:  # no need to debottom tanks (1m) before transferring to tank transfer destination tank
                        tanks = getHighestVolumeTank(all_tanks, slop_tank, config) # get tank with highest volume to be the tank transfer source tank
                    else: # need to debottom tanks, so delay tank transfer until debottoming of 1m is done
                        tanks = earliest_debottom_tanks # get tank which debottom/discharge 1m of tank the earliest to be tank transfer source tank
                        config['TANK_TRANSFER_DELAY'] = earliest_debottom_time
                        slop_idx = slop_tank_info[0][0]
                        slop_dict = slop_tank_info[0][1]
                        slop_updated = updateTankTransfer(slop_dict, slop_tank, 'TTT_dest', False, config)
                        all_tanks[slop_idx] = slop_updated # tank transfer destination tank to include delay
                    if len(tanks) == 0:
                        get_debottoming_time = True
                    else:
                        for tank in tanks:
                            param_dict = [t for t in all_tanks if t['tank'] == tank][0]
                            idx = all_tanks.index(param_dict)
                            updated = updateTankTransfer(param_dict, tank, 'TTT', False, config) # update tank transfer source tank
                            all_tanks[idx] = updated
                        get_debottoming_time = False

                if len(ops['FO']) > 0:
                    slop_tank = ops['FO'][0]
                    slop_tank_info = [(idx, t) for idx, t in enumerate(all_tanks) if t['tank'] == slop_tank]
                    shift_ops = slop_tank_info[0][1]['earlyCOW'] # if cow needs to be done before fresh oil transfer

                    if len(earliest_debottom_tanks) == 0:  # no need to debottom tanks (1m) before transferring to tank transfer destination tank
                        tanks = getHighestVolumeTank(all_tanks, slop_tank, config) # get tank with highest volume to be the tank transfer source tank
                    else: # need to debottom tanks, so delay tank transfer until debottoming of 1m is done
                        tanks = earliest_debottom_tanks # get tank which debottom/discharge 1m of tank the earliest to be tank transfer source tank
                        config['TANK_TRANSFER_DELAY'] = earliest_debottom_time
                        slop_idx = slop_tank_info[0][0]
                        slop_dict = slop_tank_info[0][1]
                        updated = updateTankTransfer(slop_dict, slop_tank, 'FO_dest', False, config)
                        all_tanks[slop_idx] = updated
                    if len(tanks) == 0:
                        get_debottoming_time = True
                    else:
                        for tank in tanks:
                            param_dict = [t for t in all_tanks if t['tank'] == tank][0]
                            idx = all_tanks.index(param_dict)
                            updated = updateTankTransfer(param_dict, tank, 'FO', shift_ops, config) # update tank transfer source tank
                            all_tanks[idx] = updated
                        get_debottoming_time = False

                if column in early_top_cow:
                    tanks = list(early_top_cow[column].keys()) # tanks which require early top cow
                    param_dicts = [t for t in all_tanks if t['tank'] in tanks]
                    for v in param_dicts: # update tank parameter information
                        idx = all_tanks.index(v)
                        tank = v['tank']
                        v['cow_strip_duration'] = config['FULL_COW_TIME'] + config['STRIP_TIME']
                        v['COWType'] = 'Full'
                        v['earlyCOW'] = True
                        v['earlyCOWTime'] = early_top_cow[column][tank]
                        v['earlyCOWDuration'] = config['TOP_COW_TIME']
                        v['earlyCOWType'] = 'Top'
                        all_tanks[idx] = v

                # Compute volume and timing of initial(initial, inc to max) and end(reduced rate or cow/stripping) stages
                real_complete_cow = [i for i in complete_cow if (not i['restricted']) & (not i['slopPartialDischarge'])]

                if len(real_complete_cow) == 0:
                    for item in all_tanks:
                        df_initial, df_end, stages_timing, item = partial_discharge(item, df_initial, df_end,
                                                                                    no_of_tanks,
                                                                                    stages_timing, config)
                        updated_param_dict[item['tank']] = item
                else:
                    temp_cow, stage_specific_tank_rate = preCalculateCOWGanttChart(partial_items, complete_cow, config)

                    for item in all_tanks:
                        df_initial, df_end, stages_timing, item = partial_complete_discharge(item, df_initial, temp_cow,
                                                                                             no_of_tanks,
                                                                                             stage_specific_tank_rate,
                                                                                             stages_timing, config)
                        updated_param_dict[item['tank']] = item

                # Correction for df_end > df_initial
                df_initial, df_end = correctionForPossibleLoading(df_initial, df_end, updated_param_dict)

                # Calculate time required for max rate
                volume_max_discharge_tank = {}
                for tank, info in updated_param_dict.items():
                    if not info['restricted']:
                        to_discharge = df_initial.iloc[:, -1][tank] - df_end.iloc[:, 0][tank]
                        volume_max_discharge_tank[tank] = to_discharge
                        if info['tankTransferAmt'] > 0:
                            if info['tankTransferStartTime'] > list(df_initial.index)[-1]:
                                volume_max_discharge_tank[tank] -= info['tankTransferAmt']
                            elif info['freshOilStartTime'] > list(df_initial.index)[-1]:
                                volume_max_discharge_tank[tank] -= info['freshOilAmt']
                    else:
                        volume_max_discharge_tank[tank] = 0

                volume_max_discharge_stage = sum(list(volume_max_discharge_tank.values()))
                max_time = volume_max_discharge_stage / config["MAX_RATE"][config['CURRENT_STAGE'] - 1]

                # Calculate no. of intermediate stages
                total_time = (df_initial.columns[-1] + df_end.columns[-1] + max_time * 60) / 60
                config = identifyIntermediateStages(total_time, column, config)

                fails_restriction = get_debottoming_time
                # Calculate max rate volume and timing
                if config['INTERVAL_MINUTES'] > 59:
                    for tank, info in updated_param_dict.items():
                        tank_max_rate = volume_max_discharge_tank[tank] / max_time # rate of tank during max rate stage
                        df_middle, stages_timing = max_stage(info, df_initial, df_middle, tank_max_rate, max_time * 60,
                                                             stages_timing, config) # volume of tank during max rate stage

                    timestamps_needed = list(range(0, int(np.floor(total_time * 60)), int(config["INTERVAL_MINUTES"])))

                    # update timing
                    for s in stages_timing:
                        if s in ['Reduced Rate', 'COW/Stripping']:
                            stages_timing[s] = [i + df_initial.columns[-1] + max_time * 60 for i in stages_timing[s]]
                    df_end.columns = [i + df_initial.columns[-1] + max_time * 60 for i in df_end.columns]

                    df_final = pd.concat([df_initial, df_middle, df_end], axis=1)

                    if get_debottoming_time:
                        earliest_debottom_tanks = []
                        earliest_debottom_time = 9999999
                        slop_tank = ops['FO'][0]
                        for t in df_final.index:
                            if all(x ==0 for x in df_final.loc[t, :].values):
                                pass
                            elif t ==slop_tank:
                                pass
                            else:
                                if ( not updated_param_dict[t]['slopPartialDischarge']):#(not updated_param_dict[t]['restricted']) & 
                                    debottom_vol = config["cargoTankCapacity"][t] * 0.98 - (
                                            config['cop_close_vol'][t] * 1.05 / 2)
                                    vol = df_final.loc[t, :].values
                                    time = list(df_final.columns)
                                    time_vol_func = interp1d(vol, time)
                                    debottom_time = time_vol_func(debottom_vol)
                                    if debottom_time < earliest_debottom_time:
                                        earliest_debottom_tanks.append(t)
                                        earliest_debottom_time = debottom_time
                                    if not earliest_debottom_tanks[0].endswith('C'):
                                        tank_no = earliest_debottom_tanks[0][:-1]
                                        earliest_debottom_tanks = [tank_no + 'P', tank_no + 'S']

            if len(config['ERROR']) == 0:
                for i in df_final.columns:
                    df_events.loc[:, i] = np.nan
                tanksDischarged = list(updated_param_dict.keys())
                for item in empty_items:
                    updated_param_dict[item['tank']] = item

                # Get events and pump time:
                for tank, info in updated_param_dict.items():
                    tt_time = info['tankTransferStartTime']
                    fo_time = info['freshOilStartTime']
                    cow_time = info['COWTime']
                    early_cow_time = info['earlyCOWTime']
                    strip_time = info['StripTime']

                    if pd.notna(tt_time):
                        tankTransfer.append(tank)
                        tt_end_time = tt_time + config['TANK_TRANSFER_TIME']
                        timings = [i for i in df_events.columns if (i > tt_time) & (i <= tt_end_time)]
                        if tt_end_time not in timings:
                            timings += [tt_end_time]
                        df_events.loc[tank, timings] = 'Tank Transfer'
                        pumps['transfer']['TCP'].append(tt_time)

                    if pd.notna(fo_time):
                        freshOilDischarge.append(tank)
                        if updated_param_dict[tank]['freshOilAmt'] > 0:
                            freshOilStorageTank.append(tank)
                        fo_end_time = fo_time + config['TANK_TRANSFER_TIME']
                        timings = [i for i in df_events.columns if (i > fo_time) & (i <= fo_end_time)]
                        if fo_end_time not in timings:
                            timings += [fo_end_time]
                        df_events.loc[tank, timings] = 'Fresh Oil Transfer'
                        pumps['fresh oil']['TCP'].append(fo_time)

                    if pd.notna(early_cow_time):
                        new_cow_time = info['earlyCOWTime']
                        new_cow_end_time = new_cow_time + info['earlyCOWDuration']
                        pumps['earlyCOW']['TCP'].append((new_cow_time, new_cow_end_time))
                        timings = [i for i in df_events.columns if (i > new_cow_time) & (i <= new_cow_end_time)]
                        if new_cow_end_time not in timings:
                            timings += [new_cow_end_time]
                        df_events.loc[tank, timings] = f"{info['earlyCOWType']} COW"
                        earlyCOW_tanks[tank] = new_cow_time

                    if pd.notna(cow_time):
                        new_cow_end_time = cow_time + info['cow_strip_duration'] + df_initial.columns[
                            -1] + max_time * 60
                        new_cow_start_time = cow_time + df_initial.columns[-1] + max_time * 60
                        # print(new_cow_time, firstCOWTime)
                        if new_cow_start_time < firstCOWTime:
                            # print(tank, new_cow_time, firstCOWTime, firstCOWTank)
                            firstCOWTime = new_cow_start_time
                            firstCOWTank = tank

                        pumps['strip']['TCP'] += [new_cow_start_time, new_cow_end_time]

                        timings = [i for i in df_events.columns if (i > new_cow_start_time) & (i <= new_cow_end_time)]
                        if new_cow_end_time not in timings:
                            timings += [new_cow_end_time]
                        df_events.loc[tank, timings[-1]] = f"{info['COWType']} COW"
                        tanks_cowed.append(tank)

                    if pd.notna(strip_time):
                        new_strip_end_time = strip_time + info['cow_strip_duration'] + df_initial.columns[
                            -1] + max_time * 60
                        new_strip_start_time = strip_time + df_initial.columns[-1] + max_time * 60
                        pumps['strip'][info['StripPump']] += [new_strip_start_time, new_strip_end_time]
                        timings = [i for i in df_events.columns if
                                   (i > new_strip_start_time) & (i <= new_strip_end_time)]
                        if new_strip_end_time not in timings:
                            timings += [new_strip_end_time]
                        df_events.loc[tank, timings] = 'Strip'
                        tanks_stripped.append(tank)

                    if 'Air Purge' in stages_timing:
                        for t in df_events.index:
                            time = stages_timing['Air Purge'][1]
                            df_events.loc[t, time] = 'Air Purge'
                    if 'Warming Pumps' in stages_timing:
                        for t in df_events.index:
                            time = stages_timing['Warming Pumps'][1]
                            df_events.loc[t, time] = 'Warming Pumps'

                if firstCOWTime == 10e9:
                    firstCOWTime = np.nan

                for item in empty_items:
                    df_final.loc[item['tank'], :] = item['initial_volume']
                df_final = df_final[sorted(df_final.columns)]
                # timestamps_missing = [t for t in timestamps_needed if float(t) not in list(df_final.columns)]
                # print(timestamps_missing)
                # for tank in df_final.index:
                #     vol = df_final.loc[tank, :].to_list()
                #     time = list(df_final.columns)
                #     time_vol_func = np.vectorize(interp1d(time, vol))
                #     for t in timestamps_missing:
                #         vol_timestamps = float(time_vol_func(t))
                #         print(tank, t, vol_timestamps)
                #         if vol_timestamps < config['cow_strip_vol'][tank]:
                #             vol_timestamps = 0
                #         df_final.loc[tank, t] = vol_timestamps
                # df_final = df_final[sorted(df_final.columns)]

                drive_oil_tank = []
                if int(column) in config['DRIVE_OIL_TANK']:
                    drive_oil_tank = config['DRIVE_OIL_TANK'][int(column)]

            result_dict[int(column)]['fixedPumpTimes'] = pumps
            result_dict[int(column)]['gantt_chart_volume'] = df_final
            result_dict[int(column)]['gantt_chart_operation_end'] = df_events[sorted(df_events.columns)]
            result_dict[int(column)]['stages_timing'] = stages_timing
            result_dict[int(column)]['firstCOWTime'] = [firstCOWTank, firstCOWTime]
            result_dict[int(column)]['tanksCOWed'] = tanks_cowed
            result_dict[int(column)]['tanksStripped'] = tanks_stripped
            result_dict[int(column)]['tanksDischarged'] = tanksDischarged
            result_dict[int(column)]['slopDischarge'] = slopDischarge
            result_dict[int(column)]['freshOilDischarge'] = freshOilDischarge
            result_dict[int(column)]['freshOilStorageTank'] = freshOilStorageTank
            result_dict[int(column)]['tankTransfer'] = tankTransfer
            result_dict[int(column)]['tanksEarlyCOWed'] = earlyCOW_tanks
            result_dict[int(column)]['driveOilTank'] = drive_oil_tank
            result_dict[int(column)]['earlySlopDischarge'] = earlySlopDischarge
        elif len(early_slop)>0:
            print(early_slop[0])
            start_time = 0.0
            df_final = pd.DataFrame()
            slop_discharging_rate = 7000
            volume = early_slop[0]['initial_volume']
            time_taken = (volume/slop_discharging_rate)*60
            df_final.loc[early_slop[0]['tank'],start_time] = volume
            tanksDischarged.append(early_slop[0]['tank'])
            end_time = start_time + time_taken
            pumps['earlySlopDischarge']['COP'] =[start_time,end_time]
            df_final.loc[early_slop[0]['tank'],end_time] = 0.0
            for item in empty_items:
                df_final.loc[item['tank'], :] = item['initial_volume']
            df_final = df_final[sorted(df_final.columns)]
            print(df_final)
            result_dict[int(column)]['fixedPumpTimes'] = pumps
            result_dict[int(column)]['gantt_chart_volume'] = df_final
            result_dict[int(column)]['gantt_chart_operation_end'] = df_events[sorted(df_events.columns)]
            result_dict[int(column)]['stages_timing'] = stages_timing
            result_dict[int(column)]['firstCOWTime'] = [firstCOWTank, firstCOWTime]
            result_dict[int(column)]['tanksCOWed'] = tanks_cowed
            result_dict[int(column)]['tanksStripped'] = tanks_stripped
            result_dict[int(column)]['tanksDischarged'] = tanksDischarged
            result_dict[int(column)]['slopDischarge'] = slopDischarge
            result_dict[int(column)]['freshOilDischarge'] = freshOilDischarge
            result_dict[int(column)]['freshOilStorageTank'] = freshOilStorageTank
            result_dict[int(column)]['tankTransfer'] = tankTransfer
            result_dict[int(column)]['tanksEarlyCOWed'] = earlyCOW_tanks
            result_dict[int(column)]['driveOilTank'] = drive_oil_tank
            #result_dict[int(column)]['stripPumpTanks'] = strip_pump_tanks
            result_dict[int(column)]['earlySlopDischarge'] = earlySlopDischarge
        
        else:
            config['ERROR'].append(f'No cargo is being discharged at stage {column}.')
            break

    return result_dict


# get time at which tank reaches 4m sounding. To identify when it is possible to do top cow for each tank
def getSounding4MTime(gantt_chart, tank_transfer, early_cow, fresh_oil, config):
    top_cow_time = {}
    for t in gantt_chart.index:
        start_time = config['WARM_PUMP_TIME'] + config['AIR_PURGE_TIME'] + config['FLOOD_SEP_TIME']
        if tank_transfer:
            start_time += config['TANK_TRANSFER_TIME']
        if early_cow:
            start_time += config['FULL_COW_TIME'] + config['STRIP_TIME']
        if fresh_oil:
            start_time += config['TANK_TRANSFER_TIME']
        time = list(gantt_chart.loc[t, :].index)
        vol = gantt_chart.loc[t, :].to_list()
        partial_volume = config["cop_close_vol"][t] * 1.5

        if partial_volume > max(vol):
            partial_volume = max(vol)
        elif partial_volume < min(vol):
            partial_volume = min(vol)
        vol_time_func = interp1d(vol, time)
        time_partial = float(vol_time_func(partial_volume))
        top_cow_time[t] = time_partial
    return top_cow_time


# so if there is early cow of slop tank then fresh oil transfer to that slop tank, 
# check if early cow satisfies daylight if not cancel all and cannot do fresh oil
# early cow occurs immediately when the discharging starts so if it is still after sunset then there is no choice

# so if there is no early cow of slop tank then fresh oil transfer,
# choose cow tanks which is earliest to reach 4m sounding , and record down tank and time to reach 4m sounding
# after that rerun gantt chart generation and early cow of that tank at that time

def dayLightRestrictionCalculation(result_dict, config):
    cow_restriction = []
    early_top_cow_restriction = {}
    if config["dayLightRestriction"]:
        stage_start_datetime = datetime.combine(config["start_date"], config["start_time"])
        for stage in result_dict:

            stages_timing = result_dict[stage]['stages_timing']
            inc_rate_to_max_time = stages_timing['Increase to Max Rate'][0]
            firstCOWTime = result_dict[stage]['firstCOWTime'][1]
            firstCOWTank = result_dict[stage]['firstCOWTime'][0]
            cow_tanks = result_dict[stage]['tanksCOWed']
            early_cow_tanks = result_dict[stage]['tanksEarlyCOWed']
            gantt = result_dict[stage]['gantt_chart_volume']

            if ('COW/Stripping' in stages_timing) & pd.notna(firstCOWTime):
                if len(early_cow_tanks) > 0:
                    # get time at which early cow (cow before cows/stripping stage starts) starts
                    earlyCOWTime = min(list(early_cow_tanks.values()))
                    cow_start_datetime = (stage_start_datetime + timedelta(
                        minutes=earlyCOWTime))
                    top_cow_start_datetime = cow_start_datetime # top cow can only start when early cow starts
                else:
                    # get time at which first cow starts
                    cow_start_datetime = (stage_start_datetime + timedelta(
                        minutes=firstCOWTime))

                    tank_transfer = len(result_dict[stage]['tankTransfer']) > 0
                    fresh_oil = len(result_dict[stage]['freshOilDischarge']) > 0
                    early_cow = len(early_cow_tanks) > 0

                    # get first tank to reach 4m sounding/ volume to allow top cow
                    top_cow_time = getSounding4MTime(gantt, tank_transfer, early_cow,
                                                     fresh_oil, config)
                    fastest_tank = firstCOWTank
                    fastest_time = top_cow_time[firstCOWTank]
                    for tank, time in top_cow_time.items():
                        if (time > inc_rate_to_max_time) & (time < fastest_time) & (tank in cow_tanks):
                            fastest_time = time
                            fastest_tank = tank

                    if fastest_tank.endswith('P'):
                        other_tank = fastest_tank[:-1] + 'S'
                    elif fastest_tank.endswith('S'):
                        other_tank = fastest_tank[:-1] + 'P'
                    else:
                        other_tank = fastest_tank

                    top_cow_tank_time = max(top_cow_time[fastest_tank], top_cow_time[other_tank])
                    top_cow_start_datetime = (stage_start_datetime + timedelta(
                        minutes=top_cow_tank_time))

                if (cow_start_datetime.time() >= config["sunset_time"]) & (cow_start_datetime.time() <= config["sunrise_time"]): # night time
                    if (top_cow_start_datetime.time() < config["sunset_time"]) & (top_cow_start_datetime.time() > config["sunrise_time"]):
                        early_top_cow_restriction[stage] = {}
                        early_top_cow_restriction[stage][firstCOWTank] = top_cow_tank_time
                        early_top_cow_restriction[stage][other_tank] = top_cow_tank_time
                        config["WARNING"].append(
                            f'Top COW of {firstCOWTank, other_tank} done early at stage {stage}. Estimated time of Top COW at {top_cow_start_datetime}')
                    else:
                        cow_restriction.append(stage)
                        tanks_not_cowed = ','.join(cow_tanks)
                        config["WARNING"].append(
                            f'Tanks planned for COW {tanks_not_cowed} at stage {stage} cannot be done due to daylight restriction. Estimated start time of first set of tanks {cow_start_datetime}')
            print(stage_start_datetime, config['stage_delay'][stage-1], list(gantt.columns)[-1])
            stage_start_datetime = (stage_start_datetime + timedelta(minutes=config['stage_delay'][stage-1])
                                     + timedelta(minutes=list(gantt.columns)[-1]))
    return early_top_cow_restriction, cow_restriction


# calculate how many COP to use and which COP to use for discharging
def findCOPToUse(tanks_discharged, config):
    tank_pump_mapping = {}
    for p, tanks in config["TANK_PUMP"].items():
        for t in tanks:
            tank_pump_mapping[t] = p

    pumps_selected = list(config["PUMPS_USED"].keys())
    rated_capacity = config["PUMPS_USED"][pumps_selected[0]] *(60/100)
    if all(x in ['SLP','SLS'] for x in tanks_discharged):
        print('here')
        pumps_needed = int(
        np.ceil(7000 / rated_capacity))
    else:
        pumps_needed = int(
            np.ceil(config["MAX_RATE"][config['CURRENT_STAGE'] - 1] / rated_capacity))
    if pumps_needed>3:
        pumps_needed = 3
    unique, counts = np.unique([tank_pump_mapping[i] for i in tanks_discharged], return_counts=True)
    pump_line_used = dict(zip(unique, counts))
    pump_recom = []
    for i in range(pumps_needed):
        p = max(pump_line_used, key=pump_line_used.get)
        pump_recom.append(p)
        pump_line_used[p] = -1

    if pumps_needed == len(pumps_selected):
        return pumps_selected
    else:
        return pump_recom


# calcualte the opening and closing of all pumps for discharge
def pumpTimeCalculation(result_dict, config):
    for s in result_dict:

        pump_df = pd.DataFrame(index=['COP1', 'COP2', 'COP3', 'TCP', 'Strip Pump'],
                               columns=result_dict[s]['gantt_chart_volume'].columns)
        empty_tank_time = {}
        partial_tank_time = {}
        if 'Max Rate Discharging' in result_dict[s]['stages_timing']:
            max_discharge_time = result_dict[s]['stages_timing']['Max Rate Discharging'][0]
        gantt = result_dict[s]['gantt_chart_volume']
        tanksDischarged = result_dict[s]['tanksDischarged']
        for t in tanksDischarged:
            time = list(gantt.loc[t, :].index)
            vol = gantt.loc[t, :].to_list()

            vol_diff = vol[0] - vol[-1]
            if vol_diff > 10.0:  # substantial difference in volume
                min_vol = min(vol)
                if min_vol == 0.0:
                    idx = vol.index(min_vol) - 1
                else:
                    idx = vol.index(min_vol)
                empty_tank_time[t] = time[idx]

        pumps_used = findCOPToUse(list(empty_tank_time.keys()), config)
        if all(x in ['SLP','SLS'] for x in tanksDischarged):
            pumps = result_dict[s]['fixedPumpTimes']
            p = pumps_used[0]
            pump_df.loc[p, pumps['earlySlopDischarge']['COP'][0]] = 'open'
            pump_df.loc[p, pumps['earlySlopDischarge']['COP'][1]] = 'close'
        else:
            for t in empty_tank_time:
                time = list(result_dict[s]['gantt_chart_volume'].loc[t, max_discharge_time:empty_tank_time[t]].index)
                vol = result_dict[s]['gantt_chart_volume'].loc[t, max_discharge_time:empty_tank_time[t]].to_list()

                partial_volume = config["cop_close_vol"][t]
                if partial_volume < min(vol):
                    partial_volume = min(vol)
                if partial_volume > max(vol):
                    partial_volume = max(vol)
                if len(vol) >= 2:
                    vol_time_func = interp1d(vol, time)
                    time_partial = float(vol_time_func(partial_volume))
                    partial_tank_time[t] = time_partial
                elif len(vol) == 1:
                    partial_tank_time[t] = time[0]

            # find COP end time
            pump_close_order = {}
            for p in pumps_used:

                direct_tank_time = {t: empty_tank_time[t] for t in config["TANK_PUMP"][p] if t in empty_tank_time}
                indirect_tank_time = {v: partial_tank_time[v] for v in partial_tank_time if v not in direct_tank_time}

                indirect_tank_limit = 0
                if len(direct_tank_time) > 0:
                    indirect_tank_limit = max(list(direct_tank_time.values()))

                indirect_tank_timing = [i for i in indirect_tank_time.values() if i > indirect_tank_limit]
                if len(indirect_tank_timing) > 0:
                    cop_end_time = min(indirect_tank_timing)
                else:
                    cop_end_time = indirect_tank_limit
                #if p ==pumps_used[0]:
                    #pump_df.loc[p, 0] = 'open'
                #else:
                    #pump_start = result_dict[s]['stages_timing']['Initial Rate'][1]
                pump_df.loc[p, 0] = 'open'
                #pump_df.loc[p, cop_end_time] = 'close'
                if 'Reduced Rate' in result_dict[s]['stages_timing']:
                    if len(direct_tank_time)>0:
                        last_time = result_dict[s]['stages_timing']['Reduced Rate'][1]
                        pump_close_order[p] = last_time
                    else:
                         middle_time = result_dict[s]['stages_timing']['Reduced Rate'][1]-5.0
                         if middle_time not in pump_close_order.values():
                                #middle_time = result_dict[s]['stages_timing']['Reduced Rate'][1]-5.0
                                pump_close_order[p] = middle_time
                         else:  
                                first_time = result_dict[s]['stages_timing']['Reduced Rate'][1]-10.0
                                pump_close_order[p] = first_time
                else:
                    pump_df.loc[p, cop_end_time] = 'close'
                for pump in pump_close_order.keys():
                    
                    pump_df.loc[pump, pump_close_order[pump]] = 'close'

            # TCP/Strip Pump

            # transfer pump
            pumps = result_dict[s]['fixedPumpTimes']
            if len(result_dict[s]['tankTransfer']) > 0:
                start_time = pumps['transfer']['TCP'][0]
                end_time = start_time + config['TANK_TRANSFER_TIME']

                pump_df.loc['TCP', start_time] = 'open'
                pump_df.loc['TCP', end_time] = 'close'

            # early COW

            for times in pumps['earlyCOW']['TCP']:
                start_time, end_time = times
                if start_time in pump_df.columns:
                    if pd.isna(pump_df.loc['TCP', start_time]):
                        pump_df.loc['TCP', start_time] = 'open'
                    else:
                        pump_df.loc['TCP', start_time] = np.nan
                else:
                    pump_df.loc['TCP', start_time] = 'open'
                pump_df.loc['TCP', end_time] = 'close'

            # fresh oil pump
            if len(result_dict[s]['freshOilDischarge']) > 0:
                start_time = pumps['fresh oil']['TCP'][0]
                end_time = start_time + config['TANK_TRANSFER_TIME']

                pump_df.loc['TCP', start_time] = 'open'
                if start_time in pump_df.columns:
                    if pd.isna(pump_df.loc['TCP', start_time]):
                        pump_df.loc['TCP', start_time] = 'open'
                    else:
                        pump_df.loc['TCP', start_time] = np.nan
                else:
                    pump_df.loc['TCP', start_time] = 'open'
                pump_df.loc['TCP', end_time] = 'close'

            # COW/Stripping
            if 'COW/Stripping' in result_dict[s]['stages_timing']:
                if len(pumps['strip']['TCP']) > 0:
                    start_time = min(pumps['strip']['TCP'])
                    end_time = max(pumps['strip']['TCP'])
                    pump_df.loc['TCP', start_time] = 'open'
                    pump_df.loc['TCP', end_time] = 'close'
                elif len(pumps['strip']['Strip Pump']) > 0:
                    start_time = min(pumps['strip']['Strip Pump'])
                    end_time = max(pumps['strip']['Strip Pump'])
                    pump_df.loc['Strip Pump', start_time] = 'open'
                    pump_df.loc['Strip Pump', end_time] = 'close'

        #         pump_df = pd.DataFrame(pump_time)
        pump_df = pump_df[sorted(pump_df.columns)]
        result_dict[s]['fixedPumpTimes'] = pump_df

    return result_dict


# add post discharge stages for last parcel to be discharged at port
def addFinalStages(stage_result_dict, config,stage):
    tanksCowed = stage_result_dict['tanksCOWed']
    tanksSTRIPed = stage_result_dict['tanksStripped']
    slopDischargeTanks = stage_result_dict['slopDischarge']
    freshOilDischargeTanks = stage_result_dict['freshOilStorageTank']
    stages_timing = stage_result_dict['stages_timing']
    gantt_chart_volume = stage_result_dict['gantt_chart_volume']
    gantt_chart_ops = stage_result_dict['gantt_chart_operation_end']
    discharge_end_time = list(gantt_chart_volume.columns)[-1]
    #discharge_end_volume = gantt_chart_volume.loc[:, discharge_end_time].values
   
    if len(slopDischargeTanks) == 2 and len(config['TWO_DRIVE_OIL_INFO'][stage]['SLP TANKS'])>0:
        slop_tank_mid = config['TWO_DRIVE_OIL_INFO'][stage]['SLP TANKS'][-1]
        slopDischargeTanks = [stage_result_dict['slopDischarge'][1]]
        cop = config["SLOP_TANK_PUMP"]['SLP']
        gantt_chart_volume_transposed = stage_result_dict['gantt_chart_volume'].T
        index = gantt_chart_volume_transposed.index
        if isinstance(slop_tank_mid, list):
            slop_tank_mid = slop_tank_mid[-1]
        else:
            pass
        condition = gantt_chart_volume_transposed[slop_tank_mid] == 0
        indices = index[condition]
        indices_list = indices.tolist()
        cow_end_time = indices_list[0]
        slop_discharge_time = cow_end_time + config['SLOP_DISCHARGE']
        gantt_chart_volume[slop_discharge_time] = gantt_chart_volume[cow_end_time] - (((gantt_chart_volume[cow_end_time]-gantt_chart_volume[indices_list[1]])/90)*60)
        gantt_chart_volume[slop_discharge_time] = gantt_chart_volume[slop_discharge_time].apply(lambda x: x if x > 100 else 0)
        gantt_chart_volume = gantt_chart_volume[sorted(gantt_chart_volume.columns)]
        gantt_chart_volume.loc['SLP', slop_discharge_time:] = 0
        gantt_chart_ops.loc['SLP', slop_discharge_time] = 'Slop Discharge'
        pump_df = stage_result_dict['fixedPumpTimes']
        pump_df_transposed = pump_df.T
        index_pump = pump_df_transposed.index
        condition = pump_df_transposed[cop] == 'close'
        indices_pump = index_pump[condition]
        indices_pump_list = indices_pump.tolist()
        pump_close_time = indices_pump_list[0]
        if pump_close_time>cow_end_time:
            pass
        else:
            stage_result_dict['fixedPumpTimes'].loc[cop, cow_end_time] = 'open'
            stage_result_dict['fixedPumpTimes'].loc[cop, cow_end_time + (config['SLOP_DISCHARGE_MID'] / 2)] = 'close'
    # dry check
    if len(tanksCowed)>0 or len(tanksSTRIPed)>0:
        discharge_end_volume = gantt_chart_volume.loc[:, discharge_end_time].values
        dry_check_time = discharge_end_time + config['DRY_CHECK']
        gantt_chart_ops.loc[:, dry_check_time] = 'Dry Check'
        gantt_chart_volume.loc[:, dry_check_time] = discharge_end_volume
        stages_timing['Dry Check'] = [discharge_end_time, dry_check_time]

    # slop discharge
    if len(slopDischargeTanks) > 0:
        cop = [config["SLOP_TANK_PUMP"][i] for i in slopDischargeTanks]
        slop_discharge_time = dry_check_time + config['SLOP_DISCHARGE']
        gantt_chart_ops.loc[slopDischargeTanks, slop_discharge_time] = 'Slop Discharge'  # end time
        gantt_chart_volume.loc[:, slop_discharge_time] = gantt_chart_volume.loc[:, dry_check_time]
        gantt_chart_volume.loc[slopDischargeTanks, slop_discharge_time] = 0
        stages_timing['Slop Discharge'] = [dry_check_time, slop_discharge_time]
        stage_result_dict['fixedPumpTimes'].loc[cop, dry_check_time] = 'open'
        stage_result_dict['fixedPumpTimes'].loc[cop, dry_check_time + (config['SLOP_DISCHARGE_MID'] / 2)] = 'close'
    else:
        slop_discharge_time = discharge_end_time

    # fresh oil discharge  
    if len(freshOilDischargeTanks) > 0:
        cop = [config["SLOP_TANK_PUMP"][i] for i in freshOilDischargeTanks]
        fresh_oil_time = slop_discharge_time + config['FRESH_OIL']
        gantt_chart_ops.loc[freshOilDischargeTanks, fresh_oil_time] = 'Fresh Oil Discharge'  # end time
        gantt_chart_volume.loc[:, fresh_oil_time] = gantt_chart_volume.loc[:, slop_discharge_time]
        gantt_chart_volume.loc[freshOilDischargeTanks, fresh_oil_time] = 0
        stages_timing['Fresh Oil Discharge'] = [slop_discharge_time, fresh_oil_time]
        stage_result_dict['fixedPumpTimes'].loc[cop, slop_discharge_time] = 'open'
        stage_result_dict['fixedPumpTimes'].loc[cop, fresh_oil_time] = 'close'
    else:
        fresh_oil_time = slop_discharge_time

    # final stripping

    final_stripping_time = fresh_oil_time + config['FINAL_STRIPPING']
    gantt_chart_ops.loc[:, final_stripping_time] = 'Final Stripping'
    gantt_chart_volume.loc[:, final_stripping_time] = gantt_chart_volume.loc[:, fresh_oil_time]
    stages_timing['Final Stripping'] = [fresh_oil_time, final_stripping_time]
    stage_result_dict['fixedPumpTimes'].loc['Strip Pump', fresh_oil_time] = 'open'
    stage_result_dict['fixedPumpTimes'].loc['Strip Pump', final_stripping_time] = 'close'
    stage_result_dict['gantt_chart_volume'] = gantt_chart_volume
    gantt_chart_ops = gantt_chart_ops[sorted(gantt_chart_ops.columns)]
    stage_result_dict['gantt_chart_operation_end'] = gantt_chart_ops
    return stage_result_dict


# add post discharge stages for intermediate stages at port
def addSlopDischargeMid(stage_result_dict, config):
    slopDischargeTanks = stage_result_dict['slopDischarge']
    gantt_chart_volume = stage_result_dict['gantt_chart_volume']
    if len(slopDischargeTanks) > 0:
        for tank in slopDischargeTanks:
            cop = config["SLOP_TANK_PUMP"][tank]
            stages_timing = stage_result_dict['stages_timing']
            gantt_chart_ops = stage_result_dict['gantt_chart_operation_end']
            discharge_end_time = list(gantt_chart_volume.columns)[-1]
            discharge_end_volume = gantt_chart_volume.loc[:, discharge_end_time].values

            # slop discharge
            slop_discharge_time = discharge_end_time + config['SLOP_DISCHARGE_MID']
            gantt_chart_volume.loc[:, slop_discharge_time] = discharge_end_volume
            gantt_chart_volume.loc[tank, slop_discharge_time] = 0
            gantt_chart_ops.loc[tank, slop_discharge_time] = 'Slop Discharge'  # end time
            stages_timing['Slop Discharge'] = [discharge_end_time, slop_discharge_time]
            stage_result_dict['fixedPumpTimes'].loc[cop, discharge_end_time] = 'open'
            stage_result_dict['fixedPumpTimes'].loc[
                cop, discharge_end_time + (config['SLOP_DISCHARGE_MID'] / 2)] = 'close'

    return stage_result_dict


# add intermediate timing (empty columns with no events) for events ddataframe
def addEmptyColumns(df_pump, df_event):
    columns = df_pump.columns
    for col in columns:
        if col not in df_event.columns:
            df_event.loc[:, col] = np.nan
    df_event = df_event[sorted(df_event.columns)]
    return df_event


# add post discharge stage for all stages in port
def addPostDischargeStages(result_dict, config):
    total_stages = len(result_dict)
    for stage in result_dict:

        if stage == total_stages:
            result_dict[stage] = addFinalStages(result_dict[stage], config,stage)
        else:
            result_dict[stage] = addSlopDischargeMid(result_dict[stage], config)
    return result_dict


# extract inputs and configurations needed to calculate discharging gantt chart at port
def defineCalculationsConfigParameters(data, output_data):
    config = {}
    config['CURRENT_STAGE'] = 0

    # operations output
    config['COW_TANKS'] = output_data['cowed_Tanks']
    config['DRIVE_OIL_TANK'] = output_data['Drive_Oil']
    config['BOTTOM_COW_TANKS'] = output_data['bottom_Cow']
    config['TWO_DRIVE_OIL_INFO'] = output_data['Two_drive_oil_info']
    
    # TIMING
    config['stage_delay'] = data["delays"]
    config['WARM_PUMP_TIME'] = 15
    config['FLOOD_SEP_TIME'] = 2
    config['AIR_PURGE_TIME'] = 2 if data["airPurge"] else 0
    config['INITIAL_TIME'] = 20
    config['INC_TIME'] = 15
    config['FULL_COW_TIME'] = float(data['cowDuration']['full'])
    config['TOP_COW_TIME'] = float(data['cowDuration']['top'])
    config['BOTTOM_COW_TIME'] = float(data['cowDuration']['bottom'])
    config['STRIP_TIME'] = 20
    config['DEC_TIME'] = 10

    config['DRY_CHECK'] = data["dryCheckDuration"]
    config['SLOP_DISCHARGE'] = data["slopDischargeDuration"]
    config['FRESH_OIL'] = data["freshOilDuration"]
    config['SLOP_DISCHARGE_MID'] = data["slopDischargeDuration"]
    config['FINAL_STRIPPING'] = data["finalStrippingDuration"]
    config['TANK_TRANSFER_TIME'] = 30
    config['TANK_TRANSFER_DELAY'] = 0

    # Rates
    config['INITIAL_RATE'] = data['initialRate']
    config['MAX_RATE'] = data['maxRate']
    # config['MAX_RATE'][2] = config['MAX_RATE'][2] / 3.3
    # config['MAX_RATE'][4] = config['MAX_RATE'][4] / 2
    config['REDUCED_RATE'] = data['initialRate']

    # Interval
    config['INTERVAL'] = data['ganttChartIntermediateInterval']['indicator']
    config['INTERVAL_HOUR'] = int(data['ganttChartIntermediateInterval']['value'])
    config['INTERVAL_STAGES'] = int(data['ganttChartIntermediateInterval']['value'])
    config["INTERVAL_MINUTES"] = np.nan

    # CARGO
    config['CARGO_DETAILS'] = data['cargoDetails']

    # COW
    config['MANUAL_COW'] = data['manualCOW']
    config['cow_strip_vol'] = data['30cmSounding']

    # OPERATIONS
    # day light restriction
    config['dayLightRestriction'] = data['dayLightCOW']
    config['start_date'] = datetime.strptime(data['startDate'], "%Y-%m-%d")
    config['start_time'] = datetime.strptime(data['startTime'], "%H:%M").time()
    config['sunset_time'] = datetime.strptime(data['sunset'], "%H:%M").time()
    config['sunrise_time'] = datetime.strptime(data['sunrise'], "%H:%M").time()
    # fresh oil
    config['freshOil'] = data['haveFreshOil']
    config['FRESH_OIL_MT'] = data['freshOilAmt']
    # tanks
    config['heavyWeatherTank'] = data['heavyWeatherTank']
    config['TANKS'] = data["cargoTanks"]
    config['SLOP_TANK'] = data["slopTanks"]
    config['SLOP_TANK_AMT'] = data['cargoTank30Capacity'][config["SLOP_TANK"][0]]
    config['cargoTank30Capacity'] = data['cargoTank30Capacity']
    config["cargoTankCapacity"] = data["cargoTankCapacity"]

    # tank pump mapping
    config['SLOP_TANK_PUMP'] = data['slopTankPumpMapping']
    config['TANK_PUMP'] = data['pumpTankMapping']
    config['cop_close_vol'] = data['2mSounding']
    config['PUMPS_USED'] = data['pumpsSelected']

    # load on top discharge
    config['loadOnTopTanksDischarge'] = data['loadOnTopTanksDischarge']

    config['ERROR'] = []
    config['WARNING'] = []
    return config


# Create discharge gantt chart including daylight restriction (early top cow/cancellation of cow) and post discharge stages
def calculations(df_input, data, output_data):
    config = defineCalculationsConfigParameters(data, output_data)

    result_dict = ganttChartCalculation(config, df_input, [], {})

    if len(config["ERROR"]) == 0:
        # day light restriction
        early_top_cow_restriction, cow_restriction = dayLightRestrictionCalculation(result_dict, config)
        result_dict = ganttChartCalculation(config, df_input, cow_restriction, early_top_cow_restriction)

        # add post discharge stages
        result_dict = pumpTimeCalculation(result_dict, config)
        result_dict = addPostDischargeStages(result_dict, config)
    else:
        result_dict = {}

    return result_dict, config['WARNING'], config['ERROR']

# data = {}
#
# with open(f'../../loadableStudy/sample.json') as f_:
#     data = json.load(f_)
#
# df_operations, output_data = ops.generate_discharge_operations(data)
# df_operations = df_operations.sort_index()
#
# print(output_data)
#
# result_dict, WARNING, ERROR = calculations(df_operations, data, output_data)
#
# print(result_dict.keys())
# print(ERROR)
# print(WARNING)

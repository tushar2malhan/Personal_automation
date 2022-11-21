#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import json
import collections
import re

#To create operation dataframe with cow deferred to last stage
def defered_cow_df(sample_defered,cow_campactible_dict):
    non_cow_cargo_tanks = []
    for i in range(len(sample_defered.columns)-1):
        if i==0:
            pass
        else:
            col_name = sample_defered.columns[i]
            for j in range(len(sample_defered.index)):
                item = sample_defered.index[j]
                slp_initial = json.loads(sample_defered.loc['SLP'][i])
                key_slp = list(slp_initial.keys())[0]
                sls_initial = json.loads(sample_defered.loc['SLS'][i])
                key_sls = list(sls_initial.keys())[0]
                if item in ['SLP','SLS']:
                    pass
                else:
                    cell_value = json.loads(sample_defered.loc[item][i])
                    key_cell_value = list(cell_value.keys())[0]
                    if (any(x in slp_initial[key_slp]['operation'] for x  in  ['SD','PD','TTT']) or any(x in sls_initial[key_sls]['operation'] for x  in  ['SD','PD','TTT'])) and (key_slp in cow_campactible_dict[key_cell_value] or key_sls in cow_campactible_dict[key_cell_value]):
                        pass
                    else:
                        if 'COW' in cell_value[key_cell_value]['operation']:
                            cell_value[key_cell_value]['operation'].remove('COW')
                            sample_defered.loc[item,col_name] = json.dumps(cell_value)
                            non_cow_cargo_tanks.append(item)
                        else:
                            pass
                        
    column = len(sample_defered.columns)-1    
    for elem in non_cow_cargo_tanks:
        cell_value = json.loads(sample_defered.loc[elem][column])
        key = list(cell_value.keys())[0]
        cell_value[key]['operation'] = []
        cell_value[key]['operation'].append('COW')
        sample_defered.loc[elem][column] = json.dumps(cell_value)                    
    return sample_defered            

def greedy_df(sample,tanks_to_be_cowed):#to create operations dataframe with cow done immediately
    tanks_discharged_current_port= []
    for i in range(len(sample.columns)-1):
        col_name = sample.columns[i]
        next_col = sample.columns[i+1]
        for j in range(len(sample.index)):
            item = sample.index[j]
            if item in ['SLP','SLS']:
                pass
            else:
                cell_value = json.loads(sample.loc[item][i])
                next_value = json.loads(sample.loc[item][i+1])
                for cargo in cell_value.keys():   
                    
                    if (cell_value[cargo]['volume']>next_value[cargo]['volume']) and (next_value[cargo]['volume']!=0):
                        next_value[cargo]['operation'] = []
                        next_value[cargo]['operation'].append('PD') 
                        sample.loc[item][i+1] = json.dumps(next_value)
                        tanks_discharged_current_port.append(item)
                    elif (next_value[cargo]['volume']==0) and (cell_value[cargo]['volume']>0):
                        if item in tanks_to_be_cowed:
                                next_value[cargo]['operation'] = []
                                next_value[cargo]['operation'].append('CD')
                                next_value[cargo]['operation'].append('Strip')
                                next_value[cargo]['operation'].append('COW')
                                sample.loc[item][i+1] = json.dumps(next_value)
                                tanks_discharged_current_port.append(item)
                        else:
                            next_value[cargo]['operation'] = []
                            next_value[cargo]['operation'].append('CD')
                            next_value[cargo]['operation'].append('Strip')
                            sample.loc[item][i+1] = json.dumps(next_value)
                            tanks_discharged_current_port.append(item)
                    else:
                        next_value[cargo]['operation'] = []
                        next_value[cargo]['operation'].append('NA')
                        sample.loc[item][i+1] = json.dumps(next_value)                   
    return sample ,tanks_discharged_current_port   

def cargo_operations_future(i,stop_number,sample_df):#to determine cargo discharged in futere stages
    cargos = []
    next_number = i+1
    for elem in range(next_number,stop_number):
        col_ = sample_df.columns[elem]
        for j in range(len(sample_df.index)):
            item = sample_df.index[j]
            if item in ['SLP','SLS']:
                pass
            else:
                cell_value = json.loads(sample_df.loc[item,col_])
                #print(cell_value)
                for cargo in cell_value.keys():
                    for elem in cell_value[cargo]['operation']:
                        if elem in 'Strip':
                            cargos.append(cargo)
                        else:
                            pass
   
    future_cargos = list(set(cargos))
    return future_cargos   

def cargo_operations(col_name,sample):#to create a dict with cargos with respective operations
    operations_list = []
    operation_dict = {}
    #print(col_name)
    for j in range(len(sample.index)):
        item = sample.index[j]
        if item not in ['SLP','SLS']:
            cell_value = json.loads(sample.loc[item,col_name])
            for cargo in cell_value.keys():
                for elem in cell_value[cargo]['operation']:
                    operations_list.append(elem)
                    if elem in ['COW','Strip','PD']:
                        if cargo in operation_dict:
                            operation_dict[cargo].append(elem)
                        else:    
                            operation_dict[cargo] = []
                            operation_dict[cargo].append(elem)
    #print(operations_list)
    return operations_list,operation_dict

   

def cargo_tanks(col_name,cargo_name,sample,tanks_to_be_cowed ):#To create a list of cargo tanks to count for slop -cow operations
    cargo_tanks =[]
    respective_tank = None
    for j in range(len(sample.index)):
        combined_tanks = []
        item = sample.index[j]
        cell_value = json.loads(sample.loc[item,col_name])
        for cargo in cell_value.keys():
            if cargo ==cargo_name and item in tanks_to_be_cowed and 'COW' in cell_value[cargo]['operation']:
                if item.endswith('P'):
                    combined_tanks.append(item)
                    start_letter = item[0]
                    for tank in range(j+1,len(sample.index)):
                        tank_item = sample.index[tank]
                        if tank_item[0] == start_letter and tank_item[1] =='S':
                            respective_tank = tank_item
                            combined_tanks.append(tank_item)
                    cargo_tanks.append(combined_tanks)        
                elif item == respective_tank:
                    pass
                else:
                     cargo_tanks.append(item)
                
                   
    return cargo_tanks

def cargo_slop_operations(col_name,sample):
    operations_slop_list = []
    operation_slop_dict = {}
    for j in range(len(sample.index)):
        item = sample.index[j]
        if item not in ['SLP','SLS']:
            cell_value = json.loads(sample.loc[item,col_name])
            for cargo in cell_value.keys():
                for elem in cell_value[cargo]['operation']:
                    operations_slop_list.append(elem)
                    if elem in ['COW']:
                        if cargo in operation_slop_dict:
                            operation_slop_dict[cargo].append(elem)
                        else:    
                            operation_slop_dict[cargo] = []
                            operation_slop_dict[cargo].append(elem)
        #print(operations_list)
    return operations_slop_list,operation_slop_dict

def slop_cow_operations(sample,cow_campactible_dict,tanks_notcowed_previous_port):#To update dataframe with cow operations for slop tanks and remaining tanks not discharged at current port
    cow_remaining_tanks =[]
    for element in tanks_notcowed_previous_port:
        for i in range(len(sample.columns)):
                if i==0:
                    pass
                else:
                    col_name = sample.columns[i]
                    cell_value_SLP = json.loads(sample.loc['SLP',col_name])
                    key_slp = list(cell_value_SLP.keys())[0]
                    cell_value_SLS = json.loads(sample.loc['SLS',col_name])
                    key_sls = list(cell_value_SLS.keys())[0]
                    if any(x in cell_value_SLP[key_slp]['operation']for x in  ['SD','PD','TTT']):
                        if element not in ['SLP','SLS']:
                            cell_value = json.loads(sample.loc[element,col_name])
                            cargo = list(cell_value.keys())[0]
                            if key_slp in cow_campactible_dict[cargo] and element not in cow_remaining_tanks and cell_value[cargo]['volume']==0:
                                cell_value[cargo]['operation'].append('COW')
                                cow_remaining_tanks.append(element)
                            else:
                                pass  
                        elif cell_value_SLS[key_sls]['volume'] == 0 and 'SLS' not in cow_remaining_tanks and not any(x in cell_value_SLS[key_sls]['operation'] for x  in  ['SD','PD','TTT']):
                            cow_remaining_tanks.append('SLS')
                            cell_value_SLS[key_sls]['operation'].append('COW')
                            sample.loc['SLS'][col_name]= json.dumps(cell_value_SLS)
                        else:
                            pass
                    elif any(x in cell_value_SLS[key_sls]['operation']for x in  ['SD','PD','TTT']):
                        if element not in ['SLP','SLS']:
                            #print(element)
                            cell_value = json.loads(sample.loc[element,col_name])
                            cargo = list(cell_value.keys())[0]
                            if key_sls in cow_campactible_dict[cargo] and element not in cow_remaining_tanks and cell_value[cargo]['volume']==0:
                                cell_value[cargo]['operation'].append('COW')
                                cow_remaining_tanks.append(element)
                            else:
                                pass
                        elif cell_value_SLP[key_slp]['volume'] == 0 and 'SLP' not in cow_remaining_tanks and  not any(x in cell_value_SLP[key_slp]['operation']for x in  ['SD','PD','TTT']):
                            cow_remaining_tanks.append('SLP')  
                            cell_value_SLP[key_slp]['operation'].append('COW')
                            sample.loc['SLP'][col_name]= json.dumps(cell_value_SLP)
                        else:
                            pass
                    else:
                        pass
    return cow_remaining_tanks   

def strip_pump(sample_df,Strip_not_done):#to update dataframe with strip-p if stripping is done with stripper pump for respective cargos
    for i in range(len(sample_df.columns)):
        if i==0:
            pass
        else:
            col_name = sample_df.columns[i]
            for j in range(len(sample_df.index)):
                item = sample_df.index[j]
                cell_value = json.loads(sample_df.loc[item,col_name])
                key_ = list(cell_value.keys())[0]
                if key_ in Strip_not_done:
                    cell_value[key_]['operation'] = [word.replace('Strip','Strip -p')for word in cell_value[key_]['operation']]
                    sample_df.loc[item,col_name] = json.dumps(cell_value)
                else:
                    pass
    return sample_df 

def cow_count(sample,cargo_api_dict,tanks_to_be_cowed,cow_campactible_dict):#to create a dict ofcount of cow tanks washed with slop tanks in each stage
    count_dict = {}
    non_cow_tanks = []
    cow_tanks = []
    two_drive_oil_info = {} 
    for i in range(len(sample.columns)):
        slp_tanks = []
        sls_tanks = []
        count_slp = 0
        count_sls = 0
        if i ==0:
            #print(i)
            pass
        else:
            col_name = sample.columns[i]
            prev_col = sample.columns[i-1]
            operations_slop_list,operation_slop_dict = cargo_slop_operations(col_name,sample)
            if 'COW' in operations_slop_list:
                cargo_cow_list = [k for k, v in operation_slop_dict.items() if 'COW' in v]
                for element in cargo_cow_list:
                    tanks =  cargo_tanks(col_name,element,sample,tanks_to_be_cowed )
                    SLP = json.loads(sample.loc['SLP',col_name])
                    SLS = json.loads(sample.loc['SLS',col_name])
                    slp_cargo = list(SLP.keys())[0]
                    sls_cargo = list(SLS.keys())[0]
                    if (slp_cargo in cow_campactible_dict[element]) and ( 'SD' in SLP[slp_cargo]['operation'] or 'PD' in SLP[slp_cargo]['operation']) and (sls_cargo in cow_campactible_dict[element]) and ('SD' in SLS[sls_cargo]['operation']or 'PD' in SLS[sls_cargo]['operation']):
                        if count_slp>=4:
                            count_sls = count_sls+len(tanks)
                        else:
                            first_half = int(len(tanks)/2)
                            for elem in range(0,first_half):
                                slp_tanks.append(tanks[elem])
                            count_slp = count_slp+first_half
                            count_sls = count_sls +(len(tanks)-first_half)
                            for elem in range(first_half,len(tanks)):
                                sls_tanks.append(tanks[elem])
                            two_drive_oil_info[col_name] = {}    
                            two_drive_oil_info[col_name]['SLP TANKS'] = slp_tanks
                            two_drive_oil_info[col_name]['SLS TANKS'] = sls_tanks
                        cow_tanks.extend(tanks)    
                    elif slp_cargo in cow_campactible_dict[element] and any(x in SLP[slp_cargo]['operation']for x in  ['SD','PD','TTT']):
                        count_slp = count_slp+len(tanks)
                        cow_tanks.extend(tanks)
                    elif sls_cargo in cow_campactible_dict[element] and any(x in SLS[sls_cargo]['operation'] for x in ['SD','PD','TTT']):
                        count_sls = count_sls+len(tanks) 
                        cow_tanks.extend(tanks)
                    else:
                        for tank in tanks:
                            non_cow_tanks.append(tank)
                    count_dict[col_name] = {}
                    count_dict[col_name]['SLP'] = count_slp
                    count_dict[col_name]['SLS'] = count_sls
    return count_dict,non_cow_tanks,cow_tanks,two_drive_oil_info

def slop_count(count_dict,sample):#to update count dict with count of slop tanks that are cowed in respective stages
    for i in range(len(sample.columns)):
        count_slp = 0
        count_sls = 0
        if i ==0:
            #print(i)
            pass
        else:
            col_name = sample.columns[i]
            SLP = json.loads(sample.loc['SLP',col_name])
            SLS = json.loads(sample.loc['SLS',col_name])
            slp_cargo = list(SLP.keys())[0]
            sls_cargo = list(SLS.keys())[0]
            if 'COW' in SLP[slp_cargo]['operation']:
                if col_name in count_dict:
                    count_dict[col_name]['SLS'] +=1
                else:
                    count_dict[col_name] = {}
                    count_dict[col_name]['SLS'] =1
                    count_dict[col_name]['SLP'] =0
            elif 'COW' in SLS[sls_cargo]['operation']:
                if col_name in count_dict:
                    count_dict[col_name]['SLP'] +=1
                else:
                    count_dict[col_name] = {}
                    count_dict[col_name]['SLP'] =1 
                    count_dict[col_name]['SLS'] =0
    return count_dict 

def remove_cow(sample,non_CowTanks):#to remove cow operation in operatuions dataframe if cow cannot be done
    for i in range(len(sample.columns)):
        if i==0:
            pass
        else:
            col_name = sample.columns[i]
            for j in range(len(sample.index)):
                item = sample.index[j]
                if item in non_CowTanks:
                    cell_value = json.loads(sample.loc[item][col_name])
                    if 'COW' in cell_value[list(cell_value.keys())[0]]['operation']:
                        cell_value[list(cell_value.keys())[0]]['operation'].remove('COW')
                    else:
                        pass
                    sample.loc[item][col_name] = json.dumps(cell_value)

def flatten(l):
    for el in l:
        if isinstance(el, collections.abc.Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el  
            
def fresh_oil_cargo(col_name,sample_df):#to identify cargo which is discharging at last stage
    for j in range(len(sample_df.index)):
        item = sample_df.index[j]
        if item not in ['SLP','SLS']:
            cell_value = json.loads(sample_df.loc[item][col_name])
            key_ = list(cell_value.keys())[0]
            if any(x in cell_value[key_]['operation']for x in  ['CD','PD']):
                return key_
                break
                
def cargo_tank_FO(col_name,sample_df):#to identify cargo tanks to pu FO if slop tanks not available
    tank = []
    for j in range(len(sample_df.index)):
        item = sample_df.index[j]
        if item not in ['SLS','SLP']:
            cell_value = json.loads(sample_df.loc[item][col_name])
            key_value = list(cell_value.keys())[0]
            if cell_value[key_value]['volume']==0:
                tank.append(item)
            else:
                pass
    tank.sort(key=lambda test_string : list(
    map(int, re.findall(r'\d+', test_string)))[0])
    #print(tank)
    return tank  

def fresh_Oil(sample_df,count_dict,Fresh_Oil):#to update operations dataframe with FO
    
    for i in range(len(sample_df.columns)):
        if i == len(sample_df.columns)-1 and Fresh_Oil:
            col_name = sample_df.columns[i]
            for j in range(len(sample_df.index)):
                item = sample_df.index[j]
                if item in ['SLP','SLS']:
                    cell_value = json.loads(sample_df.loc[item][col_name])
                    key_value = list(cell_value.keys())[0]
                    if 'SD' not in cell_value[key_value]['operation'] and cell_value[key_value]['volume']==0:
                        key_ = fresh_oil_cargo(col_name,sample_df)
                        #cell_value = {}
                        cell_value[key_] = cell_value.pop(key_value)
                        cell_value[key_]['operation'].append('FO')
                        sample_df.loc[item][col_name] = json.dumps(cell_value)
                        break
                    elif 'COW' in  cell_value[key_value]['operation'] and cell_value[key_value]['volume']==0:
                        key_ = fresh_oil_cargo(col_name,sample_df)
                        cell_value[key_] = cell_value.po(key_value)
                        cell_value[key_]['operation'].append('FO')
                        sample_df.loc[item][col_name] = json.dumps(cell_value)
                        break
                    else:        
                        tank = cargo_tank_FO(col_name,sample_df)
                        #item = tank[0]
                        cell_value = json.loads(sample_df.loc[tank[::-1][0]][col_name])
                        key_value = list(cell_value.keys())[0]
                        key_ = fresh_oil_cargo(col_name,sample_df)
                        cell_value[key_] = cell_value.pop(key_value)
                        cell_value[key_]['operation'].append('FO')
                        sample_df.loc[tank[::-1][0]][col_name] = json.dumps(cell_value)
                        break
                
                    
def drive_tank_info(col_name,df_operations):
    #print(sample_df)
    flag = False
    for j in range(len(df_operations.index)):
        #print(j)
        item = df_operations.index[j]
        #if item not in ['SLP','SLS']:
        #print(item)
        cell_value = json.loads(df_operations.loc[item][col_name])
        key_value = list(cell_value.keys())[0] 
        #print(cell_value)
        if 'CD' in cell_value[key_value]['operation'] or 'COW' in cell_value[key_value]['operation']:
            flag = True
            break

        else:
            flag = False
    return flag  

def tanks_washed_future(count_dict,col_name,slop):   
    Found = False
    for name in count_dict.keys():
        if name>col_name: 
            if count_dict[name][slop] >0:
                Found = True
                key = name
                dict_ = count_dict[key][slop]
                break
            else:
                pass
                
    if Found:
        return dict_,key
    else:
        return 0,0

def tank_limit_count(tank_limit,tanks_washed_now,count_slop,cell_state,key_slop,sample_df,count_dict,col_name,i,slop_tank):
    bottom_cow = []
    tanks_washed_next,slop_key_next = tanks_washed_future(count_dict,col_name,slop_tank)
    
    current_limit = tank_limit-tanks_washed_now-count_slop
    
    if current_limit< tanks_washed_next and tanks_washed_next<=tank_limit and tanks_washed_now<=tank_limit:
        
        if 'SD' in cell_state[key_slop]['operation']:
            #print(cell_state)
            count_slop = 0
        else:
            if i+1<=len(sample_df.columns)-1:
                cell_state[key_slop]['operation'].append('SD')
                cell_state[key_slop]['volume']=0

                next_state_slop = json.loads(sample_df.loc[slop_tank,slop_key_next])
                next_key_slop = list(next_state_slop.keys())[0] 
                sample_df.loc[slop_tank][col_name] = json.dumps(cell_state)

                next_state_slop[next_key_slop]['operation'].append('TTT')
                next_col = sample_df.columns[i+1]
                sample_df.loc[slop_tank][next_col] = json.dumps(next_state_slop)
                count_slop=0
    elif current_limit<= tanks_washed_next and tanks_washed_now>tank_limit: #tanks_washed_SLP_next>tank_limit
        
        
        for j in range(len(sample_df.index)):
            item = sample_df.index[j]
            cell_value = json.loads(sample_df.loc[item,col_name])
            #print(cell_value)
            if 'COW' in cell_value[list(cell_value.keys())[0]]['operation']:
                bottom_cow.append(item)
            else:
                pass
    elif current_limit>=tanks_washed_next:
        count_slop = count_slop+tanks_washed_now
    
    return bottom_cow,count_slop     
    
def slop_tanks_cow(count_dict,sample_df):#to update operations dataframe with cow limit considering count of tanks washed with slop tanks in each stage
    count_slp = 0
    count_sls = 0
    tank_limit = 6
    bottom_cow_tanks = []
    for i in range(len(sample_df.columns)):
        if i ==0:
            pass
        else:
            col_name = sample_df.columns[i]
            #next_col = sample_df.columns[i+1]
            if i in list(count_dict.keys()):
                tanks_washed_SLP = count_dict[col_name]['SLP']
                tanks_washed_SLS = count_dict[col_name]['SLS']
                cell_state_SLP = json.loads(sample_df.loc['SLP',col_name])
                key_SLP = list(cell_state_SLP.keys())[0] 
                cell_state_SLS = json.loads(sample_df.loc['SLS',col_name])
                key_SLS = list(cell_state_SLS.keys())[0] 
                if tanks_washed_SLP>0:  
                    
                    bottom_cow_tanks,count_slp = tank_limit_count(tank_limit,tanks_washed_SLP,count_slp,cell_state_SLP,key_SLP,sample_df,count_dict,col_name,i,slop_tank = 'SLP')
                    
                elif tanks_washed_SLS>0:
                    
                    bottom_cow_tanks,count_sls = tank_limit_count(tank_limit,tanks_washed_SLS,count_sls,cell_state_SLS,key_SLS,sample_df,count_dict,col_name,i,slop_tank = 'SLS')  
                
                elif tanks_washed_SLP>0 and tanks_washed_SLS>0:
                    
                    bottom_cow_tankslp,count_slp = tank_limit_count(tank_limit,tanks_washed_SLP,count_slp,cell_state_SLP,key_SLP,sample_df,count_dict,col_name,i,slop_tank = 'SLP')
                    
                    bottom_cow_tanksls,count_sls = tank_limit_count(tank_limit,tanks_washed_SLS,count_sls,cell_state_SLS,key_SLS,sample_df,count_dict,col_name,i,slop_tank = 'SLS')  
                    bottom_cow_tanks = bottom_cow_tankslp +bottom_cow_tanksls
    return bottom_cow_tanks   

def driveOilInfo(df_operations):#To obtain drive oil information from each stage
    drive_oil_info={}
    for i in range(len(df_operations.columns)): 
        #print(i)
        if i==0:
            pass
        else:
            col_name = df_operations.columns[i]
            drive_tank_flag = drive_tank_info(col_name,df_operations)
            #print(drive_tank_flag)
            for j in range(len(df_operations.index)):
                item = df_operations.index[j]
                if item in ['SLS','SLP']:
                    cell_value = json.loads(df_operations.loc[item][col_name])
                    key_value = list(cell_value.keys())[0] 
                    #print(drive_tank_flag)
                    if(drive_tank_flag) and any(x in cell_value[key_value]['operation']for x in  ['SD','PD','TTT']):
                        if col_name in drive_oil_info:
                            drive_oil_info[col_name].append(item)
                        else:
                            drive_oil_info[col_name]=[]
                            drive_oil_info[col_name].append(item)

    return drive_oil_info  

def input_dataframe(cargo_data,df_input):#func to create input dataframe from input json
    i =0
    for stage in cargo_data:
        for tank in stage.keys():
            #print(stage[tank])
            cargo = stage[tank][0]['cargo']
            volume = round(stage[tank][0]['quantityM3'],2)
            cell_value = {}
            cell_value[cargo] = {}
            cell_value[cargo]['volume'] = volume
            df_input.loc[tank][i] = json.dumps(cell_value)
        i+=1
    df_input = df_input.dropna(axis=1)    
    return df_input
#func to update operations dataframe from greedy cow and defered cow whichever gives the most cowed tanks
def generate_cow(Strip_not_done,df_operations,cow_campactible_dict,tanks_notcowed_previous_port,sample_defered,cargo_api_dict,tanks_to_be_cowed):
    if len(Strip_not_done)>0:
        df_operations = strip_pump(df_operations,Strip_not_done)
    else:
        pass
    cow_remaining_tanks = slop_cow_operations(df_operations,cow_campactible_dict,tanks_notcowed_previous_port)
    count_dict,non_cow_tanks,cow_tanks,two_drive_oil_info = cow_count(df_operations,cargo_api_dict,tanks_to_be_cowed,cow_campactible_dict)
    count_dict = slop_count(count_dict,df_operations)
    if len(non_cow_tanks)>0:
        df_operations = sample_defered
        if len(Strip_not_done)>0:
            df_operations = strip_pump(df_operations,Strip_not_done)
        else:
            pass
        cow_remaining_tanks = slop_cow_operations(df_operations,cow_campactible_dict,tanks_notcowed_previous_port)
        count_dict,non_cow_tanks,cow_tanks,two_drive_oil_info = cow_count(df_operations,cargo_api_dict,tanks_to_be_cowed,cow_campactible_dict)
        count_dict = slop_count(count_dict,df_operations)
    return df_operations,non_cow_tanks,count_dict,cow_tanks,cow_remaining_tanks,two_drive_oil_info

def comingledCargos(data):
    comingled_cargo = []
    for cargo in data['cargoDetails'].keys():
        if data['cargoDetails'][cargo]['isCommingled']:
            comingled_cargo.append(cargo)
        else:
            pass
    return comingled_cargo        


def generate_discharge_operations(data):#main func
    cargo_api_dict = {}
    output_data = {}
    manualCOW = data['manualCOW']
    topCow = []
    bottomCow = []
    for tank,item in manualCOW.items():
        if item['cowType'] == 'Top':
            topCow.append(tank)
        elif item['cowType'] == 'Bottom':
            bottomCow.append(tank)
        else:
            pass
    for cargo in data['cargoDetails'].keys():
        cargo_api_dict[cargo] = data['cargoDetails'][cargo]['api']
    volume_dict = data['cargoTank30Capacity'] 
    cow_campactible_dict = data['cargo_compatibility']
    tanks_to_be_cowed = data['tanks_to_cow_at_port']
    Fresh_Oil = data['haveFreshOil']
    comingled_cargo = comingledCargos(data)
    slop_cargo_reuse =  data['driveOilTankCOWLimit']
    index = list(data['tankCondition'][0].keys())
    columns = [*range(0,len(data),1)]
    df_input=pd.DataFrame(columns = columns,index = index)
    df_input = input_dataframe(data['tankCondition'],df_input)
    df_operations,tanks_discharged_current_port = greedy_df(df_input,tanks_to_be_cowed)
    tanks_notcowed_previous_port = [elem for elem in tanks_to_be_cowed if elem not in tanks_discharged_current_port]
    df_operations,Strip_not_done =  strip_Operation(df_operations,volume_dict,comingled_cargo,cow_campactible_dict)
    sample_defered_ = df_operations.copy()
    sample_defered = defered_cow_df(sample_defered_,cow_campactible_dict)
    df_operations,non_cow_tanks,count_dict,cow_tanks,cow_remaining_tanks,two_drive_oil_info = generate_cow(Strip_not_done,df_operations,cow_campactible_dict,tanks_notcowed_previous_port,sample_defered,cargo_api_dict,tanks_to_be_cowed)
    non_CowTanks = list(flatten(non_cow_tanks))
    remove_cow(df_operations,non_CowTanks) 
    cow_tanks.extend(cow_remaining_tanks)
    fresh_Oil(df_operations,count_dict,Fresh_Oil)
    drive_oil_info = driveOilInfo(df_operations)
    if not slop_cargo_reuse:
        bottom_cow = slop_tanks_cow(count_dict,df_operations)
    else:
        bottom_cow = []
    if len(bottomCow)>0:
        for element in bottomCow:
            bottom_cow.append(element)    
    output_data['cowed_Tanks'] = cow_tanks
    output_data['bottom_Cow'] = bottom_cow
    output_data['top_cow'] = topCow
    output_data['Drive_Oil'] = drive_oil_info
    output_data['Two_drive_oil_info'] = two_drive_oil_info
    return df_operations,output_data


# In[130]:


def strip_Operation(sample_df,volume_dict,comingled_cargo,cow_campactible_dict):#func to update operations dataframe considering stripping 
    Strip_done = []
    Strip_not_done = []
    dischargeSlopFirst = True
    sls_position_fixed = False
    slp_position_fixed = False
    for i in range(len(sample_df.columns)):
        if i ==0:
            pass
        else:
            col_name = sample_df.columns[i]
            prev_col = sample_df.columns[i-1]
            operations_list,operation_dict = cargo_operations(col_name,sample_df)
            #print(operation_dict)
            stop_number = len(sample_df.columns)
            future_cargos = cargo_operations_future(i,stop_number,sample_df)
            cell_value_slp = json.loads(sample_df.loc['SLP',col_name])
            prev_value_slp = json.loads(sample_df.loc['SLP',prev_col])
            cell_value_sls = json.loads(sample_df.loc['SLS',col_name]) 
            key_slp = list(prev_value_slp.keys())[0]
            prev_value_sls = json.loads(sample_df.loc['SLS',prev_col])
            key_sls = list(prev_value_sls.keys())[0] 
            SLP_end_state = json.loads(sample_df.loc['SLP'][len(sample_df.columns)-1 ])
            SLS_end_state = json.loads(sample_df.loc['SLS'][len(sample_df.columns)-1 ])
            slp_end_cargo = list(SLP_end_state.keys())[0]
            sls_end_cargo = list(SLS_end_state.keys())[0]
            cargo_name_list_PD = [k for k, v in operation_dict.items() if 'PD' in v]
            slp_pd = False
            sls_pd = False
            slp_present = False
            sls_present = False
            if 'Strip' in operations_list:
                SLS_end_state_fixed = False
                SLP_end_state_fixed = False
                sls_fixed= False
                slp_fixed = False
                slp_state = False
                sls_state = False
                cargo_name_list = [k for k, v in operation_dict.items() if 'Strip' in v]
                #print(cargo_name_list)
                for element in cargo_name_list:
                    if element == key_slp and prev_value_slp[key_slp]['volume']>0 and prev_value_slp[key_slp]['volume'] != SLP_end_state[slp_end_cargo]['volume']or (element in comingled_cargo and key_slp in cow_campactible_dict[element]):
                        if slp_state:
                            pass
                        elif element not in future_cargos and element not in list(SLP_end_state.keys()):
                            cell_value_slp = prev_value_slp
                            cell_value_slp[key_slp]['volume'] = 0
                            cell_value_slp[key_slp]['operation'] =[]
                            cell_value_slp[key_slp]['operation'].append('SD')
                        elif element not in future_cargos and element in list(SLP_end_state.keys()):
                            if cell_value_slp == SLP_end_state:
                                slp_fixed = True
                                if SLP_end_state[slp_end_cargo]['volume'] == 0:
                                    cell_value_slp[slp_end_cargo]['operation'] =[]
                                    cell_value_slp[slp_end_cargo]['operation'].append('SD')
                                    if prev_value_slp[slp_end_cargo]['volume']>volume_dict['SLP']:
                                        cell_value_slp[slp_end_cargo]['operation'].append('PD')
                                    else:
                                        pass
                                else:
                                    cell_value_slp = SLP_end_state
                                    if cell_value_slp[slp_end_cargo]['volume']<prev_value_slp[element]['volume']:
                                        cell_value_slp[slp_end_cargo]['operation'] =[]
                                        cell_value_slp[slp_end_cargo]['operation'].append('PD')
                                    else:
                                        cell_value_slp[slp_end_cargo]['operation'] =[]
                                        Strip_not_done.append(element)
                            else:
                                if SLP_end_state[slp_end_cargo]['volume'] ==0:
                                    slp_fixed = True
                                    cell_value_slp = {}
                                    cell_value_slp[key_slp]={}
                                    cell_value_slp[key_slp]['volume'] = 0
                                    cell_value_slp[key_slp]['operation'] =[]
                                    cell_value_slp[key_slp]['operation'].append('SD')
                                    if prev_value_slp[key_slp]['volume']>volume_dict['SLP']:
                                        cell_value_slp[key_slp]['operation'].append('PD')    
                                    else:
                                        pass
                                else:  
                                    cell_value_slp = {}
                                    cell_value_slp[key_slp]={}
                                    cell_value_slp[key_slp]['volume'] = SLP_end_state[slp_end_cargo]['volume']  
                                    cell_value_slp[key_slp]['operation'] =[]
                                    cell_value_slp[key_slp]['operation'].append('SD')

                        elif element in future_cargos and element in list(SLP_end_state.keys()):
                            cell_value_slp = prev_value_slp
                            if cell_value_slp[key_slp]['volume']==volume_dict['SLP']:
                                pass
                            else:
                                cell_value_slp[key_slp]['volume']=volume_dict['SLP']
                                cell_value_slp[key_slp]['operation'] =[]
                                cell_value_slp[key_slp]['operation'].append('PD')
                                slp_position_fixed = True
                        
                           
                        slp_state = True    
                        sample_df.loc['SLP',col_name] = json.dumps(cell_value_slp)
                        
                        if key_sls == key_slp:
                            if SLS_end_state[list(SLS_end_state.keys())[0]]['volume'] ==0 and prev_value_sls[key_sls]['volume']>volume_dict['SLS']:
                                cell_value_sls = prev_value_sls
                                cell_value_sls[key_sls]['volume'] = 0
                                cell_value_sls[key_sls]['operation'] = []
                                cell_value_sls[key_sls]['operation'].append('PD')
                                cell_value_sls[key_sls]['operation'].append('SD')
                                
                            else:
                                cell_value_sls = prev_value_sls
                                cell_value_sls[key_sls]['volume'] = 0
                                cell_value_sls[key_sls]['operation'] = []
                                cell_value_sls[key_sls]['operation'].append('SD')
                        elif cell_value_sls == SLS_end_state: 
                            if key_sls not in future_cargos: 
                                cell_value_sls = SLS_end_state
                                cell_value_sls[sls_end_cargo]['operation']=[]
                            else:
                                cell_value_sls = prev_value_sls
                                cell_value_sls[key_sls]['operation']=[]
                        else:   
                            if SLS_end_state_fixed or sls_position_fixed or sls_fixed:
                                pass
                            else:
                                if 'operation' in prev_value_sls[key_sls]:
                                    if 'SD' in prev_value_sls[key_sls]['operation']:    
                                        cell_value_sls = {}
                                        cell_value_sls[key_sls] = {}
                                        cell_value_sls[key_sls]['volume'] =prev_value_sls[key_sls]['volume']
                                        cell_value_sls[key_sls]['operation']=[]
                                    else:
                                        cell_value_sls = prev_value_sls
                                        cell_value_sls[key_sls]['operation']=[]        
                                else:
                                    cell_value_sls = prev_value_sls
                                    cell_value_sls[key_sls]['operation']=[]  
                        sample_df.loc['SLS',col_name] = json.dumps(cell_value_sls)
                        Strip_done.append(element)
                    elif element == key_sls and prev_value_sls[key_sls]['volume']>0 and  prev_value_sls[key_sls]['volume'] != SLS_end_state[sls_end_cargo]['volume']or (element in comingled_cargo and key_sls in cow_campactible_dict[element]):
                        if sls_state:
                            pass
                        elif element not in future_cargos and element not in list(SLS_end_state.keys()):
                            cell_value_sls = prev_value_sls
                            cell_value_sls[key_sls]['operation'] =[]
                            cell_value_sls[key_sls]['volume'] = 0
                            cell_value_sls[key_sls]['operation'].append('SD')
                        elif element not in future_cargos and element in list(SLS_end_state.keys()):
                            if cell_value_sls == SLS_end_state:
                                sls_fixed = True 
                                if SLS_end_state[sls_end_cargo]['volume'] == 0:
                                    cell_value_sls[sls_end_cargo]['operation'] =[]
                                    cell_value_sls[sls_end_cargo]['operation'].append('SD')
                                    if prev_value_sls[sls_end_cargo]['volume']>volume_dict['SLS']:
                                        cell_value_sls[sls_end_cargo]['operation'].append('PD')
                                    else:
                                        pass    
                                else:
                                    cell_value_sls = SLS_end_state
                                    if cell_value_sls[sls_end_cargo]['volume']<prev_value_sls[element]['volume']:
                                        cell_value_sls[sls_end_cargo]['operation'] =[]
                                        cell_value_sls[sls_end_cargo]['operation'].append('PD')
                                    else:
                                        cell_value_sls[sls_end_cargo]['operation'] =[]
                                        Strip_not_done.append(element)

                            else:
                                if SLS_end_state[sls_end_cargo]['volume'] ==0:
                                    sls_fixed = True
                                    cell_value_sls = {}
                                    cell_value_sls[key_sls]={}
                                    cell_value_sls[key_sls]['volume'] = 0
                                    cell_value_sls[key_sls]['operation'] =[]
                                    cell_value_sls[key_sls]['operation'].append('SD')
                                    if prev_value_sls[key_sls]['volume']>volume_dict['SLS']:
                                        cell_value_sls[key_sls]['operation'].append('PD')    
                                    else:
                                        pass
                                else:  
                                    cell_value_sls = {}
                                    cell_value_sls[key_sls]={}
                                    cell_value_sls[key_sls]['volume'] = SLS_end_state[sls_end_cargo]['volume']  

                                    cell_value_sls[key_sls]['operation'] =[]
                                    cell_value_sls[key_sls]['operation'].append('SD')
                        elif element in future_cargos and element in list(SLS_end_state.keys()):
                            cell_value_sls = prev_value_sls
                            if cell_value_sls[key_sls]['volume']==volume_dict['SLS']:
                                pass
                            else:
                                cell_value_sls[key_sls]['volume']=volume_dict['SLS']
                                cell_value_sls[key_sls]['operation'] =[]
                                cell_value_sls[key_sls]['operation'].append('PD')
                                sls_position_fixed = True 
                        
                            
                        sls_state = True    
                        Strip_done.append(element)
                        
                        if key_sls == key_slp:
                            if SLP_end_state[list(SLP_end_state.keys())[0]]['volume'] ==0 and prev_value_slp[key_slp]['volume']>volume_dict['SLP']:
                                cell_value_slp = prev_value_slp
                                cell_value_slp[key_slp]['volume'] = 0
                                cell_value_slp[key_slp]['operation'] = []
                                cell_value_slp[key_slp]['operation'].append('PD')
                                cell_value_slp[key_slp]['operation'].append('SD')
                                
                            else:
                                cell_value_slp = prev_value_slp
                                cell_value_slp[key_slp]['volume'] = 0
                                cell_value_slp[key_slp]['operation'] = []
                                cell_value_slp[key_slp]['operation'].append('SD')
                        elif cell_value_slp == SLP_end_state:
                            if key_slp not in future_cargos: 
                                cell_value_slp = SLP_end_state
                                cell_value_slp[slp_end_cargo]['operation']=[]
                            else:
                                cell_value_slp = prev_value_slp
                                cell_value_slp[key_slp]['operation']=[]
                        else: 
                            if SLP_end_state_fixed or slp_position_fixed or slp_fixed:
                                    pass
                            else:
                                if 'operation' in prev_value_slp[key_slp]:
                                    if 'SD' in prev_value_slp[key_slp]['operation']:
                                        cell_value_slp = {}
                                        cell_value_slp[key_slp] ={} 
                                        cell_value_slp[key_slp]['volume'] =prev_value_slp[key_slp]['volume']
                                        cell_value_slp[key_slp]['operation'] = []
                                    else:
                                        cell_value_slp = prev_value_slp
                                        cell_value_slp[key_slp]['operation']=[]

                                else:
                                    cell_value_slp = prev_value_slp
                                    cell_value_slp[key_slp]['operation']=[]
                        sample_df.loc['SLP',col_name] = json.dumps(cell_value_slp)
                        sample_df.loc['SLS',col_name] = json.dumps(cell_value_sls)
                    elif prev_value_slp[key_slp]['volume']==0:
                        if SLP_end_state_fixed:
                            pass
                        elif  i == len(sample_df.columns)-1 and SLP_end_state[slp_end_cargo]['volume']==0:
                            SLP_end_state_fixed = True
                            cell_value_slp = {}
                            cell_value_slp[element]={}
                            cell_value_slp[element]['volume'] =0
                            cell_value_slp[element]['operation'] =[]
                            cell_value_slp[element]['operation'].append('TTT')
                            cell_value_slp[element]['operation'].append('SD')
                        else:
                            cell_value_slp = {}
                            cell_value_slp[element] = {}
                            cell_value_slp[element]['volume'] = volume_dict['SLP']
                            cell_value_slp[element]['operation'] =[]
                            cell_value_slp[element]['operation'].append('TTT')
                            slp_position_fixed = True
                            if element not in future_cargos and SLP_end_state[list(SLP_end_state.keys())[0]]['volume']==0:
                                cell_value_slp[element]['volume'] = 0
                                cell_value_slp[element]['operation'].append('SD')
                        cell_value_sls = {}
                        cell_value_sls[key_sls]={}
                        cell_value_sls[key_sls]['volume']=prev_value_sls[key_sls]['volume']
                        cell_value_sls[key_sls]['operation'] = []
                        sample_df.loc['SLP',col_name] = json.dumps(cell_value_slp)
                        sample_df.loc['SLS',col_name] = json.dumps(cell_value_sls)
                        Strip_done.append(element)
                    elif prev_value_sls[key_sls]['volume']==0:
                        if SLS_end_state_fixed:
                            pass
                        elif i == len(sample_df.columns)-1 and SLS_end_state[sls_end_cargo]['volume']==0:
                            SLS_end_state_fixed = True
                            cell_value_sls = {}
                            cell_value_sls[element]={}
                            cell_value_sls[element]['volume']=0
                            cell_value_sls[element]['operation'] =[]
                            cell_value_sls[element]['operation'].append('TTT')
                            cell_value_sls[element]['operation'].append('SD')
                        else:
                            cell_value_sls = {}
                            cell_value_sls[element] = {}
                            cell_value_sls[element]['volume'] = volume_dict['SLS']
                            cell_value_sls[element]['operation'] =[]
                            cell_value_sls[element]['operation'].append('TTT')
                            sls_position_fixed = True
                            if element not in future_cargos and SLS_end_state[list(SLS_end_state.keys())[0]]['volume']==0:
                                cell_value_sls[element]['volume']=0
                                cell_value_sls[element]['operation'].append('SD')
                        cell_value_slp = {}
                        cell_value_slp[key_slp]={}
                        cell_value_slp[key_slp]['volume']=prev_value_slp[key_slp]['volume']
                        cell_value_slp[key_slp]['operation'] = []
                        sample_df.loc['SLP',col_name] = json.dumps(cell_value_slp)
                        sample_df.loc['SLS',col_name] = json.dumps(cell_value_sls)
                        Strip_done.append(element)
                    else:
                        Strip_not_done.append(element)
                        
                        if sls_fixed or slp_fixed:
                            pass
                        else:
                            cell_value_slp = prev_value_slp
                            cell_value_slp[key_slp]['operation']=[]
                            sample_df.loc['SLP',col_name] = json.dumps(cell_value_slp)
                            cell_value_sls = prev_value_sls
                            cell_value_sls[key_sls]['operation']=[]
                            sample_df.loc['SLS',col_name] = json.dumps(cell_value_sls)               
            
            elif dischargeSlopFirst  and all(x==operations_list[0] for x in operations_list):
                if cell_value_slp[key_slp]['volume']<prev_value_slp[key_slp]['volume']:
                    cell_value_slp[key_slp]['operation']=[]
                    cell_value_slp[key_slp]['operation'].append('eSD')
                    cell_value_sls[key_sls]['operation'] = []
                    sample_df.loc['SLP',col_name] = json.dumps(cell_value_slp)
                    sample_df.loc['SLS',col_name] = json.dumps(cell_value_sls) 
                elif cell_value_sls[key_sls]['volume']<prev_value_sls[key_sls]['volume']:
                    cell_value_sls[key_sls]['operation']=[]
                    cell_value_sls[key_sls]['operation'].append('eSD')
                    cell_value_slp[key_slp]['operation'] = []
                    sample_df.loc['SLS',col_name] = json.dumps(cell_value_sls)  
                    sample_df.loc['SLP',col_name] = json.dumps(cell_value_slp)
            
            else:
                if len(cargo_name_list_PD)==0:
                    cell_value_slp = {}
                    cell_value_slp[key_slp] = {}
                    cell_value_slp[key_slp]['volume'] = prev_value_slp[key_slp]['volume']
                    cell_value_slp[key_slp]['operation']=[]
                    sample_df.loc['SLP',col_name] = json.dumps(cell_value_slp)
                    cell_value_sls = {}
                    cell_value_sls[key_sls] = {}
                    cell_value_sls[key_sls]['volume'] = prev_value_sls[key_sls]['volume']
                    cell_value_sls[key_sls]['operation']=[]
                    sample_df.loc['SLS',col_name] = json.dumps(cell_value_sls)
                else:
                    for element in cargo_name_list_PD: 
                        if element == key_slp: 
                            slp_present = True
                            if element not in future_cargos:
                                if prev_value_slp[key_slp]['volume'] == SLP_end_state[slp_end_cargo]['volume']:
                                    cell_value_slp = {}
                                    cell_value_slp[key_slp]={}
                                    cell_value_slp[key_slp]['volume'] = SLP_end_state[slp_end_cargo]['volume']
                                    cell_value_slp[key_slp]['operation']=[]
                                else: 
                                    cell_value_slp = {}
                                    cell_value_slp[key_slp]={}
                                    cell_value_slp[key_slp]['volume'] = SLP_end_state[slp_end_cargo]['volume']
                                    cell_value_slp[key_slp]['operation']=[]
                                    cell_value_slp[key_slp]['operation'].append('PD')
                                    slp_pd= True
                                cell_value_sls[key_sls]['operation']=[]   
                            else:
                                #cell_value_slp = {}
                                #cell_value_slp[key_slp]={}
                                if prev_value_slp[key_slp]['volume'] >cell_value_slp[key_slp]['volume']:
                                    #cell_value_slp[key_slp]['volume'] = volume_dict['SLP']
                                    cell_value_slp[key_slp]['operation']=[]
                                    cell_value_slp[key_slp]['operation'].append('PD')
                                    slp_pd = True
                                else:    
                                    cell_value_slp[key_slp]['volume'] = prev_value_slp[key_slp]['volume']
                                    cell_value_slp[key_slp]['operation']=[]
                                cell_value_sls = {}
                                cell_value_sls[key_sls]={}
                                cell_value_sls[key_sls]['volume'] = prev_value_sls[key_sls]['volume']
                                cell_value_sls[key_sls]['operation']=[]
                        if element == key_sls:
                            sls_present = True
                            if element not in future_cargos:
                                if prev_value_sls[key_sls]['volume'] == SLS_end_state[sls_end_cargo]['volume']:
                                    cell_value_sls = {}
                                    cell_value_sls[key_sls]={} 
                                    cell_value_sls[key_sls]['volume'] = SLS_end_state[sls_end_cargo]['volume']
                                    cell_value_sls[key_sls]['operation']=[]
                                else:    
                                    cell_value_sls = {}
                                    cell_value_sls[key_sls]={}   
                                    cell_value_sls[key_sls]['volume'] = SLS_end_state[sls_end_cargo]['volume']
                                    cell_value_sls[key_sls]['operation']=[]
                                    cell_value_sls[key_sls]['operation'].append('PD')
                                    sls_pd = True
                                if slp_pd:
                                    pass
                                else:
                                    cell_value_slp[key_slp]['operation']=[]
                            else:
                                if slp_pd:
                                    pass
                                else:
                                    cell_value_slp = {}
                                    cell_value_slp[key_slp]={}
                                    cell_value_slp[key_slp]['volume'] = prev_value_slp[key_slp]['volume']
                                    cell_value_slp[key_slp]['operation']=[]
                                #cell_value_sls = {}
                                #cell_value_sls[key_sls]={}
                                if prev_value_sls[key_sls]['volume'] >cell_value_sls[key_sls]['volume']:
                                    #cell_value_sls[key_sls]['volume'] = volume_dict['SLS']
                                    cell_value_sls[key_sls]['operation']=[]
                                    cell_value_sls[key_sls]['operation'].append('PD')
                                    sls_pd = True
                                else:    
                                    cell_value_sls[key_sls]['volume'] = prev_value_sls[key_sls]['volume']
                                    cell_value_sls[key_sls]['operation']=[]
                        if not slp_present and not sls_present:
                            cell_value_slp = prev_value_slp
                            cell_value_slp[key_slp]['operation']=[]
                            cell_value_sls = prev_value_sls
                            cell_value_sls[key_sls]['operation']=[]
                        sample_df.loc['SLP',col_name] = json.dumps(cell_value_slp)
                        sample_df.loc['SLS',col_name] = json.dumps(cell_value_sls)
            
    return sample_df,Strip_not_done


# In[131]:


# data = {}
# with open('sample2'+'.json','r') as f_:
#         data = json.load(f_)
# df_operations, output_data = generate_discharge_operations(data)







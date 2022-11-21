# -*- coding: utf-8 -*-
"""
Created on Mon Apr 19 11:02:04 2021

@author: I2R
"""
import numpy as np
import pandas as pd

def cal_density(api, temperature_F):
    
    ## https://www.myseatime.com/blog/detail/cargo-calculations-on-tankers-astm-tables
    
    a60 = 341.0957/(141360.198/(api+131.5))**2
    dt = temperature_F-60
    vcf_ = np.exp(-a60*dt*(1+0.8*a60*dt))
    t13_ = (535.1911/(api+131.5)-0.0046189)*0.42/10
    density = t13_*vcf_*6.2898
    
    return round(density,6) 

def get_correction(tank, ullage, trim, ullageCorr):
        
       
        # out = 0
        data = ullageCorr[tank]
        data = pd.DataFrame(data,  dtype=np.float, columns=[ 'id', 'tankId', 'ullageDepth', 'trimM1', 'trim0', 'trim1', 'trim2', 'trim3', 'trim4', 'trim5', 'trim6'])
       
        # print(tank, ullage , trim)
        ullage_range = data['ullageDepth'].to_numpy()
        if trim < -1 or trim > 6 or ullage < (ullage_range.min()+0.001) or ullage > (ullage_range.max()-0.001):
            # return {'minRange':ullage_range.min(), 'maxRange':ullage_range.max()}
            return 0.
        
        a_ = np.where(data['ullageDepth'] <= ullage)[0][-1]     
         # b_ = np.where(data['ullageDepth'] >= ullage)[0][0]
        
        trim_range = np.array([-1,0,1,2,3,4,5,6])
        a__ = np.where(trim_range <= trim)[0][-1]     
         # b__ = np.where(trim_range >= trim)[0][0]
        
         # ullage x trim
        data_ = data.iloc[a_:a_+2,a__+3:a__+5].to_numpy()
        x_ = ullage_range[a_:a_+2]
        y_ = trim_range[a__:a__+2]
        
        z1_ = [(ullage-x_[0])*(data_[1][0]-data_[0][0])/(x_[1]-x_[0]) + data_[0][0], 
                (ullage-x_[0])*(data_[1][1]-data_[0][1])/(x_[1]-x_[0]) +  data_[0][1]]
        
        
        out = (trim-y_[0])*(z1_[1]-z1_[0])/(y_[1]-y_[0]) + z1_[0]
        
       #  print(x_,y_,data_)
        
        
        
        return out

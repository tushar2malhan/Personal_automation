# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 16:33:14 2020

@author: I2R
"""

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import uvicorn
#from typing import Dict, List
import asyncio
from concurrent.futures.process import ProcessPoolExecutor
from http import HTTPStatus
import databases, sqlalchemy, datetime
from fastapi import BackgroundTasks
from uuid import uuid4
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List
import json
from api_vlcc import gen_allocation, loadicator
from api_loading import gen_sequence, loadicator1
from api_discharging import gen_sequence1
from vlcc_ullage import get_correction, cal_density
import pickle
import numpy as np
import httpx
from loguru import logger
from fastapi import Request
from fastapi.responses import JSONResponse
import sys, traceback
import requests
from fastapi_utils.tasks import repeat_every

# loading config file from app --------------------------------------------------------
import configparser
config_file = configparser.ConfigParser()
os.chdir('..')
config_file.read('app\CONFIG.INI') if sys.platform.startswith('win') \
else config_file.read('app/CONFIG.INI')                       
os.chdir('loadableStudy')

## load configuration --------------------------------------------------------
with open('config.json', "r") as f_:
   config = json.load(f_)
   
# with open('KAZUSA_ullage.pickle', 'rb') as fp_:
#    # vessel_info['ullage_func'] = pickle.load(fp_)
#    _, ullageCorr, ullageInv, _ = pickle.load(fp_)
   


## Postgres Database --------------------------------------------------------
#DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:5432/postgres"
DATABASE_URL = config['url']['database']
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "pyuser",
    metadata,
    sqlalchemy.Column("id"          ,sqlalchemy.String,primary_key=True),
    sqlalchemy.Column("log_file"    ,sqlalchemy.String),
    sqlalchemy.Column("message"     ,sqlalchemy.JSON),
    sqlalchemy.Column("status"      ,sqlalchemy.String),
    sqlalchemy.Column("timestamp"   ,sqlalchemy.String),
    )


accesLogs = sqlalchemy.Table(
    "pyaccesslog",
    metadata,
    sqlalchemy.Column("id"          ,sqlalchemy.String,primary_key=True),
    sqlalchemy.Column("ip_address"      ,sqlalchemy.String),
    sqlalchemy.Column("path"      ,sqlalchemy.String),
    sqlalchemy.Column("timestamp"   ,sqlalchemy.String),
    )

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)

app = FastAPI()
logger.add(config['log']['fileName'], rotation=config['log']['rotation'], backtrace=True, diagnose=True)

class DbList(BaseModel):
    id: str
    log_file: str
    message: dict
    status: str
    timestamp: str

class DbDelete(BaseModel):
    id: str = Field(..., example="Enter the id")



@app.middleware("http")
async def log_request(request: Request, call_next):
    client_host = request.client.host
    path = request.url.path
    gID = str(uuid4())
    gDate = str(datetime.datetime.now())
    data = gDate + " --> " + client_host + " accessed " + path
    with open("vlcc_access_log.log", 'a') as f:
        print(data, file=f)

    return await call_next(request)

@app.middleware("http")
async def errors_handling(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        return JSONResponse(status_code=500, content={'error': str(exc)})


async def get_vessel_details(url, gID, vesselId):
    try:
        async with httpx.AsyncClient(verify=False) as client:
            resp_ = await client.get(url)
#            resp_.raise_for_status()
            if resp_.status_code == httpx.codes.OK:
                response_json = resp_.json()
            else:
                resp_.raise_for_status()
    except httpx.HTTPError as err:
        # print(f"HTTP Exception: {err}")
        # print('>>>> get vessel FILE')
        logger.info(gID + ": " + f"HTTP Exception - {err}")
        logger.info(gID + ": Get vessel FILE")
        with open('vessel_info'+vesselId+'.json') as json_file: 
            response_json = json.load(json_file) 
            
    return response_json


async def post_response(url, payload, gID):
    try:
        async with httpx.AsyncClient() as client:
            resp_ = await client.post(url, json=payload)
            resp_.raise_for_status()
            # print(url,resp_)
            # logger.info(gID + ": "+ resp_)
    except httpx.HTTPError  as err:
        # print(f"HTTP Exception: {err}")
        logger.info(gID + ": "+ f"HTTP Exception - {err}")
        pass

async def run_in_process(fn, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(app.state.executor, fn, *args)  # wait and return result


async def start_cpu_bound_task(uid: str, data: dict) -> None:

    errorUrl = None
    print("data['module']", data['module'])
    try:
        if data['module'] in ['LOADABLE']:
            errorUrl = config['url']['LOADABLE']['loadable-patterns'].format(vesselId=data['loadable']['vesselId'],
                                                                        voyageId=data['loadable']['voyageId'],
                                                                        loadableStudyId=data['loadable']['id'])
#            print(errorUrl)
        if data['module'] in ['LOADING']:
            errorUrl = config['url']['LOADING']['loading-patterns'].format(vesselId=data['loading']['vesselId'],
                                                                        voyageId=data['loading']['voyageId'],
                                                                        infoId=data['loading']['infoId'])
        if data['module'] in ['DISCHARGE']:
            errorUrl = config['url']['DISCHARGE']['discharge-patterns'].format(vesselId=data['discharge']['vesselId'],
                                                                        voyageId=data['discharge']['voyageId'],
                                                                        dischargeStudyId=data['discharge']['id'])        
            
        if data['module'] in ['DISCHARGING']:
            errorUrl = config['url']['DISCHARGING']['discharging-patterns'].format(vesselId=data['discharging']['vesselId'],
                                                                        voyageId=data['discharging']['voyageId'],
                                                                        infoId=data['discharging']['infoId'])
#    print(uid,type(uid))
        if data['module'] in ['LOADABLE', 'DISCHARGE']:
            result = await run_in_process(gen_allocation, data)
        elif data['module'] in ['LOADING']:
            result = await run_in_process(gen_sequence, data)
        elif data['module'] in ['DISCHARGING']:
            result = await run_in_process(gen_sequence1, data)
            
            
        gDate = str(datetime.datetime.now())
        query = users.update().\
            where(users.c.id == uid).\
            values(
                message = result,
                status = '5',
                timestamp = gDate
                )
        await database.execute(query)
        
        
        ## send feedback
        # print('>>>> Update feedback to Thinkpalm')
        
        # print(result.get('validated', None))
        
        if data['module'] in ['LOADABLE']:
            logger.info(uid + ": Loadable study completed")
        
            if result.get('validated', None) in [None]:
                logger.info(uid + ": Update status")
                status_url_ = config['url']['LOADABLE']['loadable-study-status'].format(vesselId=data['loadable']['vesselId'],
                                                                        voyageId=data['loadable']['voyageId'],
                                                                        loadableStudyId=data['loadable']['id'])
                # print(status_url_)
                await post_response(status_url_, {"processId" : uid, "loadableStudyStatusId" : 5}, uid)
            
                result_url_ = config['url']['LOADABLE']['loadable-patterns'].format(vesselId=data['loadable']['vesselId'],
                                                                        voyageId=data['loadable']['voyageId'],
                                                                        loadableStudyId=data['loadable']['id'])
            else:
                result_url_ = config['url']['LOADABLE']['validate-patterns'].format(vesselId=data['loadable']['vesselId'],
                                                                        voyageId=data['loadable']['voyageId'],
                                                                        loadableStudyId=data['loadable']['id'],
                                                                        loadablePatternId=data['loadable']['loadablePatternId'])
        elif data['module'] in ['LOADING']:
            logger.info(uid + ": Loading sequence completed")
            
            status_url_ = config['url']['LOADING']['loading-status'].format(vesselId=data['loading']['vesselId'],
                                                                        voyageId=data['loading']['voyageId'],
                                                                        infoId=data['loading']['infoId'])
            result_url_ = config['url']['LOADING']['loading-patterns'].format(vesselId=data['loading']['vesselId'],
                                                                        voyageId=data['loading']['voyageId'],
                                                                        infoId=data['loading']['infoId'])
            
            await post_response(status_url_, {"processId" : uid, "loadingInfoStatusId" : 4}, uid)
            # print(status_url_)
            # print(result_url_)
            
        elif data['module'] in ['DISCHARGE']:
            logger.info(uid + ": Discharge study completed")
            
            status_url_ = config['url']['DISCHARGE']['discharge-status'].format(vesselId=data['discharge']['vesselId'],
                                                                        voyageId=data['discharge']['voyageId'],
                                                                        dischargeStudyId=data['discharge']['id'])
            result_url_ = config['url']['DISCHARGE']['discharge-patterns'].format(vesselId=data['discharge']['vesselId'],
                                                                        voyageId=data['discharge']['voyageId'],
                                                                        dischargeStudyId=data['discharge']['id'])
            
            await post_response(status_url_, {"processId" : uid, "loadableStudyStatusId" : 5}, uid)
            
            
        elif data['module'] in ['DISCHARGING']:
            logger.info(uid + ": Discharging sequence completed")
            
            status_url_ = config['url']['DISCHARGING']['discharging-status'].format(vesselId=data['discharging']['vesselId'],
                                                                        voyageId=data['discharging']['voyageId'],
                                                                        infoId=data['discharging']['infoId'])
            result_url_ = config['url']['DISCHARGING']['discharging-patterns'].format(vesselId=data['discharging']['vesselId'],
                                                                        voyageId=data['discharging']['voyageId'],
                                                                        infoId=data['discharging']['infoId'])
            
            await post_response(status_url_, {"processId" : uid, "dischargingInfoStatusId" : 4}, uid)
            
            
        # print(result_url_)
        logger.info(uid + ": Upload result")
        
        # if data['module'] in ['LOADABLE', 'LOADING']:
            # print(result)
        await post_response(result_url_, result, uid)
        
    except Exception as err:
#        print(err)
        r_ = traceback.format_exc()
        r_ = r_.replace("\n", " ")
        r_ = r_.replace('"','')
        
        result = {"processId" : uid, "errors": [{"errorHeading": "ALGO Internal Server Error", "errorDetails": [r_, uid]}]}
        result = json.loads(json.dumps(result))

        #print("the res ",result)


        gDate = str(datetime.datetime.now())
        query = users.update().\
            where(users.c.id == uid).\
            values(
                message = result,
                status = '5',
                timestamp = gDate
                )
        await database.execute(query)
        
        if errorUrl not in [None]:
            await post_response(errorUrl, result, uid)

        
def get_data(data, gID):
    
    data_ = {}
    
    data_['module'] = data.get('module', 'LOADABLE')
    
    if data_['module'] in ['LOADABLE']:
    
        if data.get('loadableStudy', []):
            print('manual/fullManual mode!!!')
            # manual mode
            data_['loadable'] = data['loadableStudy']
            data_['loadablePlanPortWiseDetails'] = data['loadablePlanPortWiseDetails']
            data_['caseNumber'] = data.get('caseNumber', None)
            data_['loadable']['loadablePatternId'] = data.get('loadablePatternId',111111)
            data_['ballastEdited'] = data.get('ballastEdited',False)
        else:
            print('auto mode!!!')
            data_['loadable'] = data
            
        vessel_id_ = data_['loadable']['vesselId']
            
    elif data_['module'] in ['LOADING']:
        data_['loading'] = data
        data_['loading']['infoId'] = data["loadingInformation"]["loadingInfoId"]
        
        vessel_id_ = data_['loading']['vesselId']
        
    elif data_['module'] in ['DISCHARGE']:
        # print('DISCHARGE MODULE')
        data_['discharge'] = data
        vessel_id_ = data_['discharge']['vesselId']
        
    elif data_['module'] in ['DISCHARGING']:
        # print('DISCHARGE MODULE')
        data_['discharging'] = data
        data_['discharging']['infoId'] = data["dischargeInformation"]["dischargeInfoId"]
        vessel_id_ = data_['discharging']['vesselId']
    
        
    data_['vessel'] = None
    data_['processId'] = gID
    data_['config'] = config["vessel"][str(vessel_id_)]
    data_['config']["solver"] = config["solver"]
    
    print('module', data_['module'], data_['config']["solver"], vessel_id_)

    return data_


@app.post("/run_algo", status_code=HTTPStatus.ACCEPTED)
async def algo( request: Request, background_tasks:BackgroundTasks):

    dict_data =  await request.json()
    new_data = dict_data['data']
    gID  = dict_data['process_id']
    data_ = get_data(new_data, gID)
    # data_ =  get_data(data, gID)
    # print(data_.keys())
    # data_['ballastEdited'] = True

    # print('>>>> get vessel API')
    logger.info(gID + ": Get vessel API")

    if data_['module'] in ['LOADABLE']:
        vesselId_ = data_['loadable']['vesselId']
    elif data_['module'] in ['LOADING']:
        vesselId_ = data_['loading']['vesselId']
    elif data_['module'] in ['DISCHARGE']:
        vesselId_ = data_['discharge']['vesselId']
    elif data_['module'] in ['DISCHARGING']:
        vesselId_ = data_['discharging']['vesselId']

    print(vesselId_)
        
    vessel_url_ = config['url']['vessel-details'].format(vesselId=vesselId_)
    print(vessel_url_)
    data_['vessel'] = await get_vessel_details(vessel_url_, gID, str(vesselId_))
        
    # print('>>>> add new loadable')

    if data_['module'] in ['LOADABLE']:
        logger.info(gID + ": Add new loadable")
    elif data_['module'] in ['LOADING']:
        logger.info(gID + ": Add new loading")
    elif data_['module'] in ['DISCHARGE']:
        logger.info(gID + ": Add new discharge")
    elif data_['module'] in ['DISCHARGING']:
        logger.info(gID + ": Add new discharging")
        
        # print('No action taken!!', data_['module'])
    background_tasks.add_task(start_cpu_bound_task, gID, data_)


@app.post("/new_loadable", status_code=HTTPStatus.ACCEPTED)
async def task_handler(data: dict):

    from app.database import session
    from app.main_app_ import post_queue_details
    gID = post_queue_details(data, session)
    
#    data_saved = create_data(user_in)
    gDate = str(datetime.datetime.now())
    query = users.insert().values(
        id = gID,
        log_file = "stowage",
        message = None,
        status = "4",
        timestamp = gDate
        )
    await database.execute(query)

    ## send feedback
    # print('>>>> send feedback to Thinkpalm')
    # status_url_ = config['url']['loadable-study-status'].format(vesselId=data['vesselId'],voyageId=data['voyageId'],loadableStudyId=data['id'])
    # # print(status_url_)
    # await post_response(status_url_, {"processId" : gID, "loadableStudyStatusId" : 4})
    
    return {'processId': gID,  'status': '4', 'result': None}

@app.on_event("startup")
@repeat_every(seconds = int(config_file['time_limit'].get('repeat_scheduler_seconds')))
def process_queue() :
    ''' revoking the new model request
    to run_algo API '''
    from app.scheduler import execute_queue
    from app.database import session
    from app.get_operations import get_process_id_status

    new_data = execute_queue(session)
    if new_data.get('body'):
        print('\n\n[*]\trun_algo API called \n')
        data_ = {'data':new_data.get('body') , 'process_id':new_data.get('process_id') }
        detail = get_process_id_status(data_.get('process_id') )
        result = session.execute(detail).fetchone()
        url = f"http://localhost:8080/run_algo"
        req = requests.post(url , json=data_) if result[3] != \
        config_file['section_status'].get('success_status') and \
        result[3] != config_file['section_status'].get('fail_status')\
        else None
        print(req.status_code)
    else:
        print('\nNo new module yet\n ')

@app.get("/status")
async def status_handler(userId: dict):
    query = users.select().where(users.c.id == userId['processId'])
    # out = {'processId': userId['processId'], 'status':None, 'result': None}
    # out['status'] = await database.fetch_val(query,column=3)
    out = await database.fetch_val(query,column=2)
    
#    print(isinstance(out, str) )
    if isinstance(out, str):
        out_ = {'processId': userId['processId'], 'message':None}
        err_ = {'errorHeading': 'Python Error',
                 'errorDetails': [out]}
        out_['errors'] = [err_]
        out = out_
    
    return out

@app.post("/loadicator_results", status_code=HTTPStatus.ACCEPTED)
async def loadicator_handler(data: dict, background_tasks: BackgroundTasks):
    
#    print('loadicator_results')
    if data.get('loadableStudyProcessId', None):
        process_id_ = data['loadableStudyProcessId']
        
    elif data.get("dischargeStudyProcessId", None):
        if 'planDetails' in data.keys():
            process_id_ = data["dischargeStudyProcessId"]
        else:
            process_id_ = data["processId"]
    else:
        process_id_ = data['processId']
    print(process_id_)
        
    
    query = users.select().where(users.c.id == process_id_)
#    print(query)
    # out = {'processId': data['processId'], 'status':None, 'result': None}
    #out['status'] = await database.fetch_val(query,column=3)
    result = await database.fetch_val(query,column=2)
    
    print(result['message'])
    limits = result['message']
    stability = result.get('stages', [])
    
    module_ = data.get('module', 'LOADABLE')
    
    print(module_)
    
    if module_ in ['DISCHARGE']:    
        print('DISCHARGE')
        out = loadicator(data, limits)
    
    elif module_ in ['LOADABLE']:    
        out = loadicator(data, limits)
        # # print('>>>Send loadicator results')
        # logger.info(data["processId"] + ": Upload loadicator result")
        
        if out.get('feedbackLoop', True) and int(out.get('feedbackLoopCount', 5)) <= 5:
            print('feedbackloop started!!')
            gID = data['processId']
            # print(gID)
            loadable_study_data = data["loadableStudy"]
            loadable_study_data['feedbackLoopCount'] = out['feedbackLoopCount']
            loadable_study_data['feedbackLoop'] = out['feedbackLoop']
            loadable_study_data['feedbackLoopBMSF'] = out['sfbmFac']
            
            print('RERUN sfbmFac', out['sfbmFac'])
            
            data_ =  get_data(loadable_study_data, gID)
            
            logger.info(gID + ": Get vessel API")
            vessel_url_ = config['url']['vessel-details'].format(vesselId=data_['loadable']['vesselId'])
            data_['vessel'] = await get_vessel_details(vessel_url_, gID)
                
            # print('>>>> add new loadable')
            logger.info(gID + ": Add feedbackloadable")
            background_tasks.add_task(start_cpu_bound_task, gID, data_)
            
    elif module_ in ['LOADING', 'DISCHARGING']:    
        out = loadicator1(data, limits, stability=stability)
#        print(limits)
        
    return out

@app.post("/ullage_results/")
async def ullage_handler(data: dict):
    
    if data['vesselId'] in ["1",1]:
        with open('KAZUSA.pickle', 'rb') as fp_:
            # vessel_info['ullage_func'] = pickle.load(fp_)
            vessel_details = pickle.load(fp_)
            
    elif data['vesselId'] in ["2",2]:
        with open('ATLANTICPIONEER.pickle', 'rb') as fp_:
            # vessel_info['ullage_func'] = pickle.load(fp_)
            vessel_details = pickle.load(fp_)
    
    
    ullageCorr, ullageInv = vessel_details['ullageCorr'], vessel_details['ullageInvFunc']
           
    tankId = data['tankId']
    cf = get_correction(str(tankId), float(data["rdgUllage"]), float(data["trim"]), ullageCorr)
    if type(cf) not in [dict]:
        corr_ullage =  float(data["rdgUllage"]) + cf/100 
        vol = ullageInv[str(tankId)](corr_ullage) 
        density = data.get('sg', None)
        if density in [None,""]:
            density = cal_density(float(data["api"]), float(data["temp"]))
        else:
            density = float(density)
        wt = density*vol 
        
        tank_ = vessel_details['tankId'][int(tankId)]
        print(tank_)
        if tank_ in vessel_details['cargoTanks'].keys():
            capacity_ = vessel_details['cargoTanks'][tank_]['capacityCubm']
        elif tank_ in vessel_details['ballastTanks'].keys():
            capacity_ = vessel_details['ballastTanks'][tank_]['capacityCubm']        
        
        fr = vol/capacity_*100
        
        return {"id":data["id"], "correctionFactor": str(round(cf/100,3)), "correctedUllage": str(round(corr_ullage,6)),
                "obsM3": str(np.round(vol,2)), "quantityMt": str(round(wt,1)), "fillingRatio":str(round(fr,2)) }
        
    else:
        
        return {**{"id":data["id"], "correctionFactor": "", "correctedUllage": "", "obsM3": "", 
            "quantityMt": "", 'fillingRatio':""}, **cf}
    
     
    

@app.get("/users/{userId}", response_model=DbList)
async def find_user_by_id(userId: str):
    query = users.select().where(users.c.id == userId)
    return await database.fetch_one(query)

@app.delete("/users/{userId}")
async def delete_user(userId: str):
    query = users.delete().where(users.c.id == userId)
    await database.execute(query)
    
    return{
        "status": True,
        "message": "This user has been deleted successfully."
        }



@app.on_event("startup")
async def startup_event():
    app.state.executor = ProcessPoolExecutor()

@app.on_event("shutdown")
async def on_shutdown():
    app.state.executor.shutdown()

@app.on_event("startup")
async def startup():
    await database.connect()
    
@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    
@app.get("/db/", response_model=List[DbList])
async def find_all_db_list():
    query = users.select()
    return await database.fetch_all(query)



if __name__ == '__main__':
     uvicorn.run(app, host='0.0.0.0', port=8000)
    
# uvicorn main:app --reload --host 0.0.0.0 --port:8000

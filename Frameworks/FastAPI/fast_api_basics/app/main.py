'''
[*] Created  on Tuesday 21/6/22  17:15:00

@author: Tushar Malhan
'''
import configparser

from fastapi import FastAPI
from fastapi import Depends, FastAPI, HTTPException
from fastapi.exceptions import HTTPException
from fastapi_utils.tasks import repeat_every

import app.models as models
from app.post_data import create_queue
from app.scheduler import startup_event
import app.schema as schema
from .database import SessionLocal, engine


app = FastAPI(Debug = True)
config = configparser.ConfigParser()
config.read(r'app/CONFIG.INI')

models.Base.metadata.create_all(bind=engine) 


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get('/')
def intro():
    return  'Welcome to FastAPI docker container'


@app.post('/post')
def post_queue_details(body : schema.QueueDetailsSchema, db: SessionLocal = Depends(get_db)):
    ''' post json details'''
    if not body.input_json or body.input_json.get('module') is  None:
        raise HTTPException(status_code=404, detail="Module Name not found")
    create_queue(db, body)
    return {'message': f'Module {create_queue.process}  has  successfully\
    been recieved in the queue\
    Here is the uuid id - {create_queue.process_id}'}


@app.on_event("startup")
@repeat_every(seconds = int(config['time_limit'].get('repeat_scheduler_seconds')))
def repeat_task() -> None:
    ''' repeated task
    to check the status of
    each process in the queue '''
    print('Start up Event - Scheduler')
    startup_event( SessionLocal())

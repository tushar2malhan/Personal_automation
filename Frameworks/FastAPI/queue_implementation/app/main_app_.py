'''
[*] Created  on Tuesday 21/6/22  17:15:00

@author: Tushar Malhan
'''

import os
import sys
from fastapi import FastAPI, Depends, HTTPException
import configparser
from sqlalchemy.orm import Session
from fastapi_utils.session import FastAPISessionMaker
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.conf import modules
from app.database import engine, SessionLocal, DATABASE_URL
from app.get_operations import informAlgoStatus
import app.models as models
from app.post_data import create_queue

config = configparser.ConfigParser()
os.chdir('..')
config.read('app\CONFIG.INI') if sys.platform.startswith('win')\
else config.read('app/CONFIG.INI')
os.chdir('loadableStudy')

models.Base.metadata.create_all(bind = engine)
sessionmaker = FastAPISessionMaker(DATABASE_URL)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def post_queue_details(body : dict, database: Session = Depends(get_db) ):
    ''' 
    post json details in queue header table
    and call the ALGO API for the new queue
    '''
    if not body or body.get('module') is  None:
        raise HTTPException(status_code=404, detail="Module Name not found")
    create_queue(database,body)
    process_name = body.get('module')
    vesselId = body.get('vesselId')
    voyageId = body.get('voyageId') 
    info_Id = create_queue.info_id
    info_type = modules[process_name]['info_type']
    info_number = modules[process_name]['info_number']
    informAlgoStatus(process_name, vesselId,
    voyageId, info_Id, create_queue.process_id,
    info_type, info_number)

    print( f'Module {create_queue.process}  has  successfully\
    been recieved in the queue\
    Here is the uuid id - {create_queue.process_id}' )
    return create_queue.process_id


''' db get operations '''

import json
import re
import requests
from sqlalchemy.orm import Session
from app.conf import modules
import app.models as models
from app.database import session


def get_latest_header(database: Session):
    ''' get latest queue details '''
    single_detail = database.query(models.QueueHeader).\
                    order_by(models.QueueHeader.id.desc()).\
                    first()
    return single_detail if single_detail else None


def get_proces_queue(database: Session, status: str = None):
    ''' get single process queue ''' 
    detail = database.query(models.QueueHeader).\
            join(models.QueueDetail, models.QueueHeader.id == models.QueueDetail.queue_id).\
            filter(models.QueueHeader.status == status).\
            limit(1).first() if status else None
    return detail 

def get_process_id_status(process_id:str):
    ''' 
    Confirms status of the in_progress 
    query
    '''
    detail = session.query(models.QueueHeader).\
        filter(models.QueueHeader.process_id == process_id)\
        if process_id else None 
    return detail

def informAlgoStatus(process_name, vesselId, voyageId, info_Id,
    process_id, info_type, info_number):
    ''' 
    Call ALGO API
    '''
    path = modules[process_name]['url'] 
    patn = re.sub(r"[\([{})\]]", "", path)
    url = patn.replace('vesselId',str(vesselId)).\
    replace('voyageId',str(voyageId)).\
    replace(modules[process_name]['info_name'],str(info_Id))
    data_ = {'processId': process_id, info_type:info_number }
    response = requests.post(url, data = json.dumps(data_), 
    headers = {"Content-Type": "application/json; charset=utf-8"})
    print('\n\t\n[*] API -> \t',response.text,response.status_code)
    print(data_)
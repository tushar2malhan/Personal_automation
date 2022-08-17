''' json data response '''
import configparser
from datetime import datetime
import imp
import uuid
from sqlalchemy.orm import Session
import app.models as models
from app.get_operations import get_latest_header
import json

config = configparser.ConfigParser()
config.read(r'app/CONFIG.INI')

def create_queue(database, body):
    ''' json data validation '''

    print(body)
    create_queue.process =  body.input_json.get('module')
    print('module name is: ', create_queue.process)
    create_queue.process_id = str(uuid.uuid4()).replace('-','')
    new_header = models.QueueHeader(
        process_id = create_queue.process_id,
        process = create_queue.process,
        status = config['section_status'].get('new_status'),
        created_time = datetime.now())
    database.add(new_header)
    database.commit()
    new_details = models.QueueDetail(
        queue_id = get_latest_header(database).id,
        input_json = json.dumps(body.input_json))
    database.add(new_details)
    database.commit()
    return body 

''' json data response '''
import configparser
from datetime import datetime
import uuid
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.conf import modules
import app.models as models
from app.get_operations import get_latest_header
config = configparser.ConfigParser()
os.chdir('..')
config.read('app\CONFIG.INI') if sys.platform.startswith('win')\
else config.read('app/CONFIG.INI')
os.chdir('loadableStudy')

def create_queue(database, body):
    ''' json data validation '''
    create_queue.process =  body.get('module')
    print('\nModule name is: ', create_queue.process)
    create_queue.process_id = str(uuid.uuid4()).replace('-','')
    create_queue.info_id = eval(modules[create_queue.process].get('query'))
    new_header = models.QueueHeader(
        process_id = create_queue.process_id,
        process = create_queue.process,
        status = config['section_status'].get('new_status'),
        created_time = datetime.now(),
        start_time = datetime.now(),
        vesselId = body.get('vesselId'),
        voyageId = body.get('voyageId'),
        infoId = create_queue.info_id )
    database.add(new_header)
    database.commit()
    new_details = models.QueueDetail(
        queue_id = get_latest_header(database).id,
        input_json = body)
    database.add(new_details)
    database.commit()
    return body 

''' Scheduler tasks '''

import os 
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import configparser
from datetime import datetime, timezone, timedelta
from app.conf import modules
from app.get_operations import  get_proces_queue, informAlgoStatus
from sqlalchemy.orm import Session

config = configparser.ConfigParser()
os.chdir('..')
config.read('app\CONFIG.INI') if sys.platform.startswith('win')\
else config.read('app/CONFIG.INI')
os.chdir('loadableStudy')

def execute_queue(database: Session) -> None:
    '''  
        Startup Event Scheduler 
    '''

    new_queue = get_proces_queue(database, status = config['section_status'].get('new_status') )
    in_progress_queue = get_proces_queue(database, config['section_status'].get('in_process_status'))
    if in_progress_queue:
        from loadableStudy.main import users
        query = users.select().where(users.c.id == in_progress_queue.process_id)
        result = database.execute(query).fetchone() 
        date_now = datetime.now().replace(tzinfo=timezone.utc).timestamp()
        expiry_time = (in_progress_queue.created_time+timedelta
        (minutes = int(config['time_limit'].get('expiry_time_minutes'))))\
        .replace(tzinfo=timezone.utc).timestamp()
        if date_now >= expiry_time:
            in_progress_queue.status = config['section_status'].get('fail_status')
            in_progress_queue.last_modified_time = in_progress_queue.created_time
            in_progress_queue.end_time = in_progress_queue.created_time+timedelta(minutes=60)
            in_progress_queue.remarks = config['section_status'].get('time_out_status')
            database.commit()
            print('Algo crashed, module', in_progress_queue.process , f'failed\
            Cpdss here is the uuid id of it {in_progress_queue.process_id}')
            return 'Algo crashed, module', in_progress_queue.process , f'failed\
            Cpdss here is the uuid id of it {in_progress_queue.process_id}'
        elif not result[2].get('errors'):
            in_progress_queue.status = config['section_status'].get('success_status')
            in_progress_queue.end_time = datetime.now()
            in_progress_queue.last_modified_time = datetime.now()
            in_progress_queue.remarks = config['section_status'].get('success_status')
            database.commit()
        else:
            process_name = in_progress_queue.process
            voyageId = in_progress_queue.voyageId
            vesselId = in_progress_queue.vesselId
            info_Id = in_progress_queue.infoId
            info_type = modules[in_progress_queue.process]['info_type']
            info_number = modules[in_progress_queue.process]['info_number']
    
            informAlgoStatus(process_name, vesselId, voyageId, info_Id,
            in_progress_queue.process_id, info_type, info_number)

            print( f'\n\nProcess {in_progress_queue.process} is in process,\
            kindly wait {abs(int(date_now-expiry_time))} seconds,\
            to complete the module \t\tHere is the uuid id of it {in_progress_queue.process_id} \n\n')
    else:
        if new_queue:
            new_queue_data = { "body" : new_queue.queue_details[0].input_json,
            "process_id": new_queue.process_id}
            new_queue.status = config['section_status'].get('in_process_status')
            database.commit()
            print(f'\nInvoking the {new_queue.process} module ,\
                Kindly wait , we will scehdule it\
                Cpdss here is the uuid id of it {new_queue.process_id}')
            return new_queue_data
    return {'Response':"No New Module Yet"}


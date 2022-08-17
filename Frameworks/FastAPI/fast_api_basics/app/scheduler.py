''' Scheduler tasks '''
import sys 
sys.path.append(r'C:\Users\tushar.m\Desktop\project')  
import configparser
from datetime import datetime, timezone, timedelta
from app.get_operations import  get_proces_queue

config = configparser.ConfigParser()
config.read(r'app/CONFIG.INI')


def startup_event(database) -> None:
    ''' Automatic Startup Event'''
    in_progress_queue = get_proces_queue(database, config['section_status'].get('in_process_status')) 
    if in_progress_queue:
        date_now = datetime.now().replace(tzinfo=timezone.utc).timestamp()
        expiry_time = (in_progress_queue.created_time+timedelta
        (minutes = int(config['time_limit'].get('expiry_time_minutes'))))\
        .replace(tzinfo=timezone.utc).timestamp()
        if date_now >= expiry_time:
            in_progress_queue.status = config['section_status'].get('fail_status')
            in_progress_queue.start_time = in_progress_queue.created_time
            in_progress_queue.last_modified_time = in_progress_queue.created_time
            in_progress_queue.end_time = in_progress_queue.created_time+timedelta(minutes=60)
            in_progress_queue.remarks = config['section_status'].get('time_out_status')
            database.commit()
            print('Algo crashed, module', in_progress_queue.process , f'failed\
            Cpdss here is the uuid id of it {in_progress_queue.process_id}')
            return 'Algo crashed, module', in_progress_queue.process , f'failed\
            Cpdss here is the uuid id of it {in_progress_queue.process_id}'
        else:
            print( f'\n\nProcess {in_progress_queue.process} is in process,\
            kindly wait {abs(int(date_now-expiry_time))} seconds,\
            to complete the module \t\tHere is the uuid id of it {in_progress_queue.process_id} \n\n')
    else:
        new_queue = get_proces_queue(database, status = config['section_status'].get('new_status') )
        new_queue.status = config['section_status'].get('in_process_status')
        database.commit()
        print('Type of process does new queue belongs too ! is \t ', new_queue.process)
        print(f'Invoking the {new_queue.process} module ,\
            Kindly wait , we will scehdule it\
            Cpdss here is the uuid id of it {new_queue.process_id}')
        return f'Invoking the {new_queue.process} module ,\
            Kindly wait , we will scehdule it\
            Cpdss here is the uuid id of it {new_queue.process_id}'
    return 'No module to invoke Yet'


''' db get operations '''
import app.models as models

def get_latest_header(database):
    ''' get latest queue details '''
    single_detail = database.query(models.QueueHeader).\
                    order_by(models.QueueHeader.id.desc()).\
                    first()
    return single_detail if single_detail else None

def get_proces_queue(database, status: str = None):
    ''' get single process queue '''
    detail = database.query(models.QueueHeader).\
            join(models.QueueDetail, models.QueueHeader.id == models.QueueDetail.queue_id).\
            filter(models.QueueHeader.status == status).\
            limit(1).first() if status else \
            database.query(models.QueueHeader).all()
    return detail if detail else None
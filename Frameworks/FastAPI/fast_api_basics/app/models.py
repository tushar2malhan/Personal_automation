''' models creation = QueueHeader, QueueDetail '''

import json
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from app.database import Base


class QueueHeader(Base):
    ''' queue header table '''
    
    __tablename__ = 'queue_header'

    id  = Column(BigInteger, primary_key=True,  autoincrement = True)
    process_id = Column(String, nullable=False)
    process = Column(String, nullable=False)
    status = Column(String, nullable=False)
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    created_time = Column(DateTime(timezone=True))
    last_modified_time = Column(DateTime(timezone=True))
    remarks = Column(String)
    queue_details = relationship('QueueDetail', backref='queue_header',passive_deletes=True)


    def serialize(self):
        ''' serialize the object '''
        return [self.id, self.process_id, self.process, self.start_time]


class QueueDetail(Base):
    ''' queue detail table '''
    __tablename__ = 'queue_detail'

    id  = Column(BigInteger, primary_key=True, autoincrement = True)
    queue_id = Column(BigInteger, ForeignKey('queue_header.id', ondelete='CASCADE'))
    input_json = Column(String)

    def serialize(self):
        ''' serialize the queue detail '''
        return [self.id, self.queue_id, self.input_json]

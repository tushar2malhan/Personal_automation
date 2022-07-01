import datetime as dt
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

import database as _database


class Contact(_database.Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, index=True, unique=True)
    phone_number = Column(String, index=True, unique=True)
    date_created = Column(DateTime, default=dt.datetime.utcnow)

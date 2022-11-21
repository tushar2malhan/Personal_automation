from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.environ.get("DATABASE_URL")
# DATABASE_URL='postgres+psycopg2://cpdssuser:9VC6D1C0B1eyatg7BeIa0MN4d9@cpdssdbqa.chdo37r0lkuo.ap-southeast-1.rds.amazonaws.com:5432/cpdss_ml_db'
engine = create_engine(
    DATABASE_URL  # ,connect_args={"check_same_thread": False} #SQLITE: check same thread
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

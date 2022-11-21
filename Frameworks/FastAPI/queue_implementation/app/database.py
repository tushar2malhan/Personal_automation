''' DATABASE  connection '''
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# DATABASE_URL = os.getenv('DATABASE_URL')
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/postgres"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()
Base = declarative_base()
''' DATABASE  connection '''
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/postgres"

# engine = create_engine(
#     DATABASE_URL, 
##       connect_args={"check_same_thread": False    # if connecting with local host , uncomment it
# } 
##       For connection with db use:
##       DATABASE_URL = 'postgres+psycopg2://cpdssuser:url'
##       DATABASE_URL = f"postgresql://postgres:admin@localhost:5432/postgres"  
#     |>| DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
##       SQL lite     = "sqlite:///./sql_app.db"  
# )

SQLALCHEMY_DATABASE_URI = "postgresql://postgres:admin@localhost:5432/postgres"

engine = create_engine(
    SQLALCHEMY_DATABASE_URI
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

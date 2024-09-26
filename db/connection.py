from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

uri = "sqlite:///db/main.db"
Base = declarative_base()
engine = create_engine(uri,echo=False)
Session = sessionmaker(bind=engine) 





    
    
        
# (c) Raif Sarcich, GPLv3, 2012

# Database mechanics

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, Unicode, PickleType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# engine = create_engine('sqlite:///:memory:', echo=True)
engine = create_engine('sqlite:////tmp/pieberry/pieberry.db', echo=False)
SQLABase = declarative_base(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

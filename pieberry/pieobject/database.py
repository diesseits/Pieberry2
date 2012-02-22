# (c) Raif Sarcich, GPLv3, 2012

# Database mechanics
# from pieconfig.paths import DBDIR

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, Unicode, PickleType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

def create_piedb_engine(rootpath):
    engine = create_engine('sqlite:///%s/pieberry.db' % rootpath, echo=False, 
                       poolclass=NullPool)
    SQLABase = declarative_base(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

global engine

# engine = create_engine('sqlite:///:memory:', echo=True)

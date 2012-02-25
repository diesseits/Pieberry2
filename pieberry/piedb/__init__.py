# (c) Raif Sarcich, GPLv3, 2012

# Database mechanics
# from pieconfig.paths import DBDIR

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool


def create_piedb_engine(rootpath):
    global SQLABase
    global engine
    global Session
    global session
    engine = create_engine('sqlite:///%s/pieberry.db' % rootpath, echo=False, 
                       poolclass=NullPool)
    SQLABase = declarative_base(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

def close_piedb_engine():
    session.expire_all()
    session.close()
    Session.close_all()
    engine.dispose()

# def del_all():

# engine = create_engine('sqlite:///:memory:', echo=True)

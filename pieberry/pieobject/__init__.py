#GPLv3 Raif Sarcich 2011

import sqlalchemy
import datetime
from pprint import pprint, pformat
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, Unicode, PickleType
from sqlalchemy.ext.declarative import declarative_base

from pieobject.tags import TagHandler
from pieobject.biblio import BiblioHandler

engine = create_engine('sqlite:///:memory:', echo=True)
SQLABase = declarative_base()

class PieObject(SQLABase, TagHandler, BiblioHandler):
    __tablename__ = 'pieobjects'
    
    id = Column(Integer, primary_key=True)
    title = Column(Unicode)
    author = Column(Unicode)
    date = Column(DateTime)
    tags = Column(PickleType)

    BibData_Key = Column(Unicode)
    BibData_Type = Column(Unicode(length=20))
    BibData_Fields = Column(PickleType)

    WebData_Url = Column(Unicode)
    WebData_PageUrl = Column(Unicode)
    WebData_LinkText = Column(Unicode)

    FileData_FileName = Column(Unicode)
    FileData_Root = Column(Unicode)

    def __init__(self, title='', author='', date=datetime.datetime.today()):
        self.title = title
        self.author = author
        self.date = date
        self.tags = []

    def __repr__(self):
        return "<PieObject %s - %s. (%s)>\n%s" % (self.Title()[:10], self.Author(), str(self.ReferDate()), pformat(self.BibData_Fields))

    def Title(self):
        return self.title

    def Author(self):
        return self.author

    def GetId(self):
        return self.id

    def ReferDate(self):
        return self.date

    def Url(self):
        return self.WebData_Url


#GPLv3 Raif Sarcich 2011

import sqlalchemy
import datetime
from pprint import pprint, pformat
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, Unicode, PickleType
from sqlalchemy.ext.declarative import declarative_base

from pieobject.tags import TagHandler
from pieobject.biblio import BiblioHandler
from pieobject.objectstore import PieObjectStore

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

        #aspects
        self.aspects = {
            'onweb': False,
            'cached': False,
            'saved': False,
            'stored': False
            }

    def __repr__(self):
        return "<PieObject %s - %s. (%s)>\n%s" % (self.Title()[:10], self.Author(), str(self.ReferDate()), pformat(self.BibData_Fields))

    def Title(self):
        return self.title

    def Author(self):
        return self.author

    def GetId(self):
        return self.id

    def ReferDate(self):
        '''The most salient date for this document'''
        return self.date

    def Url(self):
        return self.WebData_Url

    def has_aspect(self, t):
        if not t in self.aspects.keys():
            raise KeyError, 'Unknown type of aspect'
        return self.aspects[t]

    def add_aspect_onweb(self, url, pageurl, linktext='', defaultauthor=''):
        '''Add information gleaned from the document being on the web
        (in-situ)'''
        assert type(url) in (str, unicode)
        assert type(pageurl) in (str, unicode)
        assert type(linktext) in (str, unicode)
        self.WebData_Url = url
        self.WebData_PageUrl = pageurl
        self.WebData_LinkText = linktext
        self.title = linktext
        self.author = defaultauthor
        self.aspects['onweb']=True

    def add_aspect_cached_from_web(self, temp_location):
        '''Add information pertaining to the downloading and temporary
        caching of this object'''
        self.aspects['cached'] = True

    def add_aspect_cached_from_desktop(self, temp_location):
        '''Add information pertaining to the temporary caching of this
        object'''
        self.aspects['cached'] = True

    def add_aspect_stored(self):
        '''Add information pertaining to the storage of this item in
        the system'''
        self.aspects['stored'] = True
        self.aspects['cached'] = False

    def add_aspect_saved(self):
        '''Add information pertaining to the saving of this item into the
        database'''
        self.aspects['saved'] = True
        
    def set_session(self, sess):
        '''Mark a session flag for this object'''
        self.session = sess

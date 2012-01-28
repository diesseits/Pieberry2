#GPLv3 Raif Sarcich 2011

import sqlalchemy
import datetime
import os, os.path
from pprint import pprint, pformat
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, Unicode, PickleType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from pieobject.tags import TagHandler
from pieobject.biblio import BiblioHandler
from pieobject.objectstore import PieObjectStore
from pieobject.diagnostic import *
from pieconfig.paths import ROOT_MAP


engine = create_engine('sqlite:///:memory:', echo=True)
SQLABase = declarative_base()
Session = sessionmaker(bind=engine)

class PieObject(SQLABase, TagHandler, BiblioHandler):
    __tablename__ = 'pieobjects'

    # Fundamental fields
    id = Column(Integer, primary_key=True)
    title = Column(Unicode)
    author = Column(Unicode)
    date = Column(DateTime)
    tags = Column(PickleType)
    collection = Column(Unicode) # i.e. 'category_phrase'
    corpauthor = Column(Unicode)

    BibData_Key = Column(Unicode)
    BibData_Type = Column(Unicode(length=20))
    BibData_Fields = Column(PickleType)

    WebData_Url = Column(Unicode)
    WebData_PageUrl = Column(Unicode)
    WebData_LinkText = Column(Unicode)
    WebData_DateDownloaded = Column(DateTime)

    FileData_FileName = Column(Unicode)
    FileData_Root = Column(Unicode)
    FileData_Folder = Column(PickleType)
    FileData_FileType = Column(Unicode(length=6))
    FileData_DateCreated = Column(DateTime)
    FileData_DateModified = Column(DateTime)

    def __init__(self, title='', author='', date=datetime.datetime.today(),
                 fileloc=None):
        self.title = title
        self.author = author
        self.date = date
        self.tags = []
        self.filemetadata = {}

        if fileloc:
            self.set_file(fileloc)
            self.set_file_type(fileloc)

        #aspects
        self.aspects = {
            'onweb': False,
            'ondesktop': False,
            'cached': False,
            'saved': False,
            'stored': False,
            'failed_dl': False
            }

    def __repr__(self):
        return "<PieObject %s - %s. (%s)>\n%s" % (self.Title()[:10], self.Author(), str(self.ReferDate()), pformat(self.BibData_Fields))

    def __getattr__(self, name):
        if name == 'FileData_FullPath': 
            if not (self.has_aspect('stored') or self.has_aspect('cached') or self.has_aspect('ondesktop')):
                return None
            pathlist = [ROOT_MAP[self.FileData_Root],] + self.FileData_Folder + [self.FileData_FileName,]
            return os.path.join(*pathlist)
        elif name == 'FileData_ContainingFolder':
            if not (self.has_aspect('stored') or self.has_aspect('cached')):
                return None
            pathlist = [ROOT_MAP[self.FileData_Root],] + self.FileData_Folder
            return os.path.join(*pathlist)
        else:
            raise AttributeError

    def Title(self):
        return self.title

    def Author(self, favour_corporate=False):
        if favour_corporate and self.corpauthor:
            return self.corpauthor
        else:
            return self.author

    def GetId(self):
        return self.id

    def ReferDate(self):
        '''The most salient date for this document'''
        return self.date

    def Url(self):
        return self.WebData_Url

    def Collection(self):
        return self.collection

    def has_aspect(self, t):
        if not t in self.aspects.keys():
            raise KeyError, 'Unknown type of aspect'
        return self.aspects[t]

    def remove_aspect(self, t):
        if not t in self.aspects.keys():
            raise KeyError, 'Unknown type of aspect'
        if not self.aspects[t] == True:
            raise ValueError, 'Object does not have aspect: %s' % t
        self.aspects[t] == False

    def add_aspect_ondesktop(self, fn):
        self.set_file(fn)
        self.set_file_type(fn)
        self.aspects['ondesktop'] = True

    def add_aspect_onweb(self, url, pageurl, linktext='', defaultauthor='', 
                         category_phrase='', author_is_corporate=False):
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
        if author_is_corporate: self.corpauthor = defaultauthor
        self.collection = category_phrase
        self.aspects['onweb']=True

    def add_aspect_cached_from_web(self, temp_location):
        '''Add information pertaining to the downloading and temporary
        caching of this object'''
        self.aspects['cached'] = True
        self.set_file(temp_location)
        self.set_file_type()
        self.date = datetime.datetime.today()
        self.WebData_DateDownloaded = self.date

    def add_aspect_cached_from_desktop(self, temp_location):
        '''Add information pertaining to the temporary caching of this
        object'''
        self.aspects['cached'] = True
        self.set_file(temp_location)
        self.date = datetime.datetime.today()
 
    def add_aspect_failed_download(self):
        '''Flag this as a failed download'''
        self.aspects['failed_dl'] = True

    def add_aspect_stored(self, final_fn=None):
        '''Add information pertaining to the storage of this item in
        the system'''
        if not final_fn == self.FileData_FullPath:
            self.set_file(final_fn) #set filename if specified and different 
        self.aspects['stored'] = True
        self.aspects['cached'] = False

    def flag_aspect_stored(self):
        '''Variant of add_aspect_stored for use in search queries'''
        self.aspects['stored'] = True
        self.aspects['cached'] = False

    def add_aspect_saved(self):
        '''Add information pertaining to the saving of this item into the
        database'''
        self.aspects['saved'] = True
        
    def set_session(self, sess):
        '''Mark a session flag for this object'''
        self.session = sess

    def set_file(self, loc):
        '''Set all kinds of data associated with this being a local file.
        Should have full absolute path given to it.'''
        if not os.path.exists(loc):
            raise IOError, 'Trying to set file data for non existant file'
        self.FileData_FileName = os.path.basename(loc)
        diry = os.path.dirname(loc)
        fdroot = None
        for key, pdir in ROOT_MAP.items():
            # print 'Testing if', diry[:len(pdir)], '==', pdir
            if diry[:len(pdir)] == pdir:
                fdroot = key
                self.FileData_Root = key
                self.FileData_Folder = diry[len(pdir):].split(os.sep)
                break
        if not fdroot: raise Exception, 'File stored outside pieberry domain'

    def set_file_type(self, ft=None):
        '''Set the type of file, drawing on mime information or specified type'''
        if not ft:
            self.FileData_FileType = determine_file_type(self.FileData_FullPath)
        else:
            self.FileData_FileType = ft


#GPLv3 Raif Sarcich 2011

import datetime
import os, os.path
from pprint import pprint, pformat
from sqlalchemy import Column, Integer, String, DateTime, Unicode, PickleType, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

from pieobject.database import *
from pieobject.tags import TagHandler, PieTag, pieobject_tags
from pieobject.biblio import BiblioHandler
from pieobject.objectstore import PieObjectStore
from pieobject.diagnostic import *
from pieobject.folder import FOLDER_LOOKUP, PieFolder, recommend_folder
from pieobject.website import PieWebsite, referable_website, validify_domain
from pieconfig import PIE_CONFIG
from pieconfig.paths import ROOT_MAP
from pieconfig.schemas import bibtexfields, bibtexmap

class PieObject(SQLABase, TagHandler, BiblioHandler):
    __tablename__ = 'pieobjects'

    # Fundamental fields
    id = Column(Integer, primary_key=True)
    title = Column(Unicode)
    author = Column(Unicode)
    date = Column(DateTime)
    # tags = Column(PickleType)

    collection = Column(Unicode) # i.e. 'category_phrase'
    corpauthor = Column(Unicode)
    aspects = Column(PickleType)
    filemetadata = Column(PickleType)

    # User Stats

    StatData_Favourite = Column(Boolean)
    StatData_OpenedCount = Column(Integer)
    StatData_LastOpened = Column(DateTime)
    StatData_LastSaved = Column(DateTime)

    #relationships

    website_id = Column(Integer, ForeignKey('piewebsites.id'))
    website = relationship("PieWebsite", 
                           backref=backref('referenced_objects', order_by=id))
    tag_id = Column(Integer, ForeignKey('pietags.id'))
    tags = relationship('PieTag', secondary=pieobject_tags, backref='pieobjects')
    
    folder_id = Column(Integer, ForeignKey('piefolders.id'))
    FileData_FolderAdv = relationship('PieFolder', 
                                      backref=backref('referenced_objects',
                                                      order_by=id))

    #detailed fields

    BibData_Key = Column(Unicode)
    BibData_Type = Column(Unicode(length=20))
    BibData_Editor = Column(Unicode)
    BibData_Journal = Column(Unicode)
    BibData_Note = Column(Unicode)
    BibData_Annote = Column(Unicode)
    BibData_Volume = Column(Unicode(length=10))
    BibData_Pages = Column(Unicode)
    BibData_Series = Column(Unicode)
    BibData_Number = Column(Unicode(length=10))
    BibData_Institution = Column(Unicode)
    BibData_Chapter = Column(Unicode)
    BibData_Address = Column(Unicode) 
    BibData_Publisher = Column(Unicode)
    BibData_HowPublished = Column(Unicode)
    BibData_DatePublished = Column(DateTime)

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
    FileData_Size = Column(Integer)

    PhysData_StorageLoc = Column(Unicode) # Storage location
    PhysData_StorageType = Column(Unicode) # Type of storage
                                           # (e.g. personal, library)
    PhysData_Dewey = Column(Unicode(length=20)) 
    PhysData_ISBN = Column(Unicode(length=50))
    PhysData_Accessed = Column(DateTime) # Borrowing/accession time

    def __init__(self, title='', author='', date=datetime.datetime.today(),
                 fileloc=None):

        self.title = title
        self.author = author
        self.corpauthor = ''
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
            'failed_dl': False,
            'bibdata': False,
            'physical': False
            }

    def __repr__(self):
        return "<PieObject %s - %s. (%s)>" % (self.Title()[:10], self.Author(), str(self.ReferDate()))

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
        if not self.title:
            if self.WebData_LinkText:
                return self.WebData_LinkText
            if self.FileData_FileName:
                return self.FileData_FileName
        return self.title

    def Author(self, favour_corporate=False):
        if favour_corporate and self.corpauthor:
            return self.corpauthor
        elif not self.author:
            return self.corpauthor
        else:
            return self.author

    def AuthorIsCorporate(self, favour_corporate=False):
        if favour_corporate and self.corpauthor:
            return True
        elif self.author == None and self.corpauthor:
            return True
        elif len(self.author) == 0 and self.corpauthor:
            return True
        else:
            return False

    def GetId(self):
        return self.id

    def ReferDate(self, prefer_created=False, prefer_modified=False,
                  prefer_downloaded=False):
        '''The most salient date for this document'''
        if prefer_created:
            if self.has_aspect('hasfile') and self.FileData_DateCreated:
                return self.FileData_DateCreated
        if prefer_modified:
            if self.has_aspect('hasfile') and self.FileData_DateModified:
                return self.FileData_DateModified
        if prefer_downloaded:
            if self.has_aspect('onweb') and self.WebData_DateDownloaded:
                return self.WebData_DateDownloaded
        # having exhausted preference cases, lets have implicit
        # preferences. Firstly for bibliographic data, since it's
        # explicitly set by user. Secondly, file metadata
        # dates. Thirdly, date of download.
        if self.BibData_DatePublished: 
            return self.BibData_DatePublished
        if self.FileData_DateCreated:
            return self.FileData_DateCreated
        if self.WebData_DateDownloaded:
            return self.WebData_DateDownloaded
        # I don't want to fall back to self.date in future, it should
        # have no purpose.
        return self.date

    def Url(self):
        '''The most salient url for _reference_ purposes. If the
        actual URL is definitely needed, access property
        WebData_Url'''
        if not self.WebData_Url: return ''
        behav = PIE_CONFIG.get('Format', 'url_level_represent')
        if behav  == 'full':
            return self.WebData_Url
        elif behav == 'referpage':
            if self.WebData_PageUrl: return self.WebData_PageUrl
            else: return self.WebData_Url
        elif behav == 'domain':
            return validify_domain(self.WebData_Url)
        else:
            raise ValueError, 'Invalid url handling variable'

    def Collection(self):
        return self.collection

    def has_aspect(self, t):
        if t == 'hasfile':
            if self.has_aspect('stored') or self.has_aspect('cached') or self.has_aspect('ondesktop'):
                return True
            else: return False
        if not t in self.aspects.keys():
            raise KeyError, 'Unknown type of aspect'
        return self.aspects[t]

    def remove_aspect(self, t):
        if t == 'hasfile':
            if self.has_aspect('stored'):
                self.aspects['stored'] = False
            if self.has_aspect('cached'):
                self.aspects['cached'] = False
            if self.has_aspect('ondesktop'):
                self.aspects['ondesktop'] = False
            return
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
                         category_phrase='', author_is_corporate=False,
                         tags=None):
        '''Add information gleaned from the document being on the web
        (in-situ)'''
        assert type(url) in (str, unicode)
        assert type(pageurl) in (str, unicode)
        assert type(linktext) in (str, unicode)
        self.WebData_Url = url
        self.WebData_PageUrl = pageurl
        self.WebData_LinkText = linktext
        if author_is_corporate: 
            self.corpauthor = defaultauthor
        else:
            self.author = defaultauthor
        self.collection = category_phrase
        # Set basic bibliographic data
        self.BibData_HowPublished = PIE_CONFIG.get(
            'Format', 'default_howpublished_text')
        self.BibData_Type = PIE_CONFIG.get(
            'Format', 'default_bibtex_entry_type')
        if tags:
            self.add_tags(tags)
        self.aspects['onweb']=True
        self.aspects['bibdata']=True

    # def _attempted_threadsafe_link(self, url):
    #     '''need a new session to do this in a thread'''
    #     newsession = Session()
        # self.website = referable_website(url, newsession)

    def add_aspect_cached_from_web(self, temp_location):
        '''Add information pertaining to the downloading and temporary
        caching of this object'''
        self.aspects['cached'] = True
        self.set_file(temp_location)
        self.set_file_type()
        self.date = datetime.datetime.today()
        self.WebData_DateDownloaded = datetime.datetime.today()

    def add_aspect_cached_from_desktop(self, temp_location):
        '''Add information pertaining to the temporary caching of this
        object'''
        self.aspects['cached'] = True
        self.set_file(temp_location)
        self.set_file_type()
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
        # TODO: probably unnecessary now
        pass

    def add_aspect_saved(self):
        '''Add information pertaining to the saving of this item into the
        database'''
        self.aspects['saved'] = True
        # do links at the time that things are to be committed to
        # db. Any earlier and it screws things up (and websites,
        # specifically, won't necessarily be in the piewebsites table)
        self.StatData_LastSaved = datetime.datetime.today()
        if self.WebData_Url:
            self.website = referable_website(self.WebData_Url, session)

    def add_aspect_bibdata(self, **kwargs):
        '''Add specifically (user requested or other) set
        bibliographic information'''
        self.aspects['bibdata'] = True
        for key, val in kwargs.items():
            if key in bibtexmap.values():
                setattr(self, key, val)
        if kwargs.has_key('WebData_Url'):
            # NOTE: Not sure about doing this. 
            self.aspects['onweb'] = True
            # if not self.WebData_PageUrl:
            #     self.WebData_PageUrl = kwargs['WebData_Url']
        pprint(kwargs)
        
    def set_session(self, sess):
        '''Mark a session flag for this object'''
        self.session = sess

    def set_file(self, loc):
        '''Set all kinds of data associated with this being a local file.
        Should have full absolute path given to it.'''
        if not os.path.exists(loc):
            raise IOError, 'Trying to set file data for non existant file'
        self.FileData_FileName = os.path.basename(loc)
        self.FileData_Size = os.stat(loc).st_size
        self.FileData_DateModified = datetime.datetime.fromtimestamp(
            os.stat(loc)[8])
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

    def get_icon_code(self, window_type=None):
        '''Return a code for iconic representation of this object. A
        context can be given through parameter window_type. The codes
        will correspond to various items in a wx.ImageList for the
        list/other type of window concerned. Values may include:
        'start' 'spin' 'blank' 'success' 'fail' 'warn' 'pass' 'tick'
        'exclude' 'pdf' 'doc'

        Contexts may include 'filewindow', 'bibwindow', 'dlwindow'''
        if window_type == 'filewindow':
            if self.FileData_Type == 'pdf':
                return 'pdf'
            else: return 'doc'
    
    def stats_opened(self):
        self.StatData.LastOpened = date=datetime.datetime.today()
        self.StatData.OpenedCount += 1
        print '%s opened %d times' % (self, self.StatData_OpenedCount)
        

# metadata = SQLABase.metadata
# metadata.create_all(engine)

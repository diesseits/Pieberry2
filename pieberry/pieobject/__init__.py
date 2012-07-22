#GPLv3 Raif Sarcich 2011

import datetime
import locale
import os, os.path, traceback
from pprint import pprint, pformat
from sqlalchemy import Column, Integer, String, DateTime, Unicode, PickleType, Boolean, Binary
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy import and_

from pieberry.piedb import *
from pieberry.pieobject.tags import TagHandler, PieTag, pieobject_tags
from pieberry.pieobject.biblio import BiblioHandler
from pieberry.pieobject.objectstore import PieObjectStore
from pieberry.pieobject.diagnostic import *
from pieberry.pieobject.folder import FOLDER_LOOKUP, PieFolder, recommend_folder, referable_folder_byobj
from pieberry.pieobject.website import PieWebsite, referable_website, validify_domain
from pieberry.pieobject.internals import PIE_INTERNALS
from pieberry.pieconfig.config import PIE_CONFIG
from pieberry.pieconfig.paths import ROOT_MAP
from pieberry.pieconfig.schemas import bibtexfields, bibtexmap
from pieberry.pieutility.latex import untexify

# Encryption states
EC_FALSE = 0
EC_TRUE_LOCKED = 1
EC_TRUE_UNLOCKED = 2

# from sqlalchemy.ext.mutable import Mutable

# class MutationDict(Mutable, dict):
#     @classmethod
#     def coerce(cls, key, value):
#         "Convert plain dictionaries to MutationDict."

#         if not isinstance(value, MutationDict):
#             if isinstance(value, dict):
#                 return MutationDict(value)

#             # this call will raise ValueError
#             return Mutable.coerce(key, value)
#         else:
#             return value

#     def __setitem__(self, key, value):
#         "Detect dictionary set events and emit change events."

#         dict.__setitem__(self, key, value)
#         self.changed()

#     def __delitem__(self, key):
#         "Detect dictionary del events and emit change events."

#         dict.__delitem__(self, key)
#         self.changed()


class PieObject(SQLABase, TagHandler, BiblioHandler):
    __tablename__ = 'pieobjects'

    # Fundamental fields
    id = Column(Integer, primary_key=True)
    title = Column(Unicode(length=1024))
    author = Column(Unicode(length=1024))
    date = Column(DateTime)

    collection = Column(Unicode(length=1024)) # i.e. 'category_phrase'
    corpauthor = Column(Unicode(length=255))
    aspects = Column(PickleType(mutable=True))
    filemetadata = Column(PickleType(mutable=True))
    notes = Column(Unicode)

    # User Stats

    StatData_Favourite = Column(Boolean)
    StatData_OpenedCount = Column(Integer)
    StatData_LastOpened = Column(DateTime)
    StatData_LastSaved = Column(DateTime)
    StatData_FollowUpDate = Column(DateTime)
    StatData_FollowUpDueDate = Column(DateTime)
    StatData_FollowUpFlag = Column(Boolean)
    StatData_Picture = Column(Binary)

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

    BibData_Key = Column(Unicode(length=255), unique=True)
    BibData_Type = Column(Unicode(length=20))
    BibData_Editor = Column(Unicode(length=255))
    BibData_Journal = Column(Unicode(length=255))
    BibData_Note = Column(Unicode)
    BibData_Annote = Column(Unicode)
    BibData_Volume = Column(Unicode(length=20))
    BibData_Pages = Column(Unicode(length=20))
    BibData_Series = Column(Unicode(length=255))
    BibData_Number = Column(Unicode(length=20))
    BibData_Institution = Column(Unicode(length=255))
    BibData_School = Column(Unicode(length=255))
    BibData_ThesisKey = Column(Unicode(length=255))
    BibData_ThesisType = Column(Unicode(length=255))
    BibData_BookTitle = Column(Unicode(length=1025))
    BibData_Chapter = Column(Unicode(length=255))
    BibData_Address = Column(Unicode(length=1024)) 
    BibData_Publisher = Column(Unicode(length=255))
    BibData_HowPublished = Column(Unicode(length=255))
    BibData_DatePublished = Column(DateTime)
    BibData_Abstract = Column(Unicode)
    # Future
    # BibData_Language = Column(Unicode(length=255))
    # BibData_Copyright = Column(Unicode(length=255))

    WebData_Url = Column(Unicode)
    WebData_PageUrl = Column(Unicode)
    WebData_LinkText = Column(Unicode)
    WebData_DateDownloaded = Column(DateTime)

    FileData_FileName = Column(Unicode(length=1024))
    FileData_Root = Column(Unicode(length=50))
    FileData_Folder = Column(PickleType)
    FileData_FileType = Column(Unicode(length=25))
    FileData_DateCreated = Column(DateTime)
    FileData_DateModified = Column(DateTime)
    FileData_Size = Column(Integer)

    PhysData_StorageLoc = Column(Unicode(length=255)) # Storage location
    PhysData_StorageType = Column(Unicode(length=255)) # Type of storage
                                           # (e.g. personal, library)
    PhysData_Dewey = Column(Unicode(length=20)) 
    PhysData_ISBN = Column(Unicode(length=50))
    # PhysData_ISSN = Column(Unicode(length=50))
    PhysData_Accessed = Column(DateTime) # Borrowing/accession time

    # Services utility fields
    GoogleData = Column(PickleType)
    AmazonData = Column(PickleType)

    def __init__(self, title=u'', author=u'', date=datetime.datetime.today(),
                 fileloc=None):

        TagHandler.__init__(self)

        assert type(title) == unicode
        assert type(author) == unicode

        self.title = title
        self.author = author
        self.corpauthor = u''
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
            'physical': False,
            'encrypted': EC_FALSE
            }

        self.StatData_OpenedCount = 0

    def __repr__(self):
        ec = locale.getpreferredencoding()
        return "<PieObject %s - %s. (%s)>" % (self.Title()[:10].encode(ec, 'ignore'), self.Author().encode(ec, 'ignore'), str(self.ReferDate()))

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

    def Title(self, atom_title_hack=False, texstuff=False):
        if not self.title:
            if self.WebData_LinkText:
                return self.WebData_LinkText
            if self.FileData_FileName:
                return self.FileData_FileName
        ttl = self.title if texstuff else untexify(self.title)
        if atom_title_hack and self.FileData_FileName:
            if self.FileData_Root in ('projectdir', 'meetingpaperdir'):
                return "%s [%s]" % (ttl, self.FileData_FileName)
        return ttl

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
                         tags=None, inferred_filetype=None, threaded=False):
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
        if not self.BibData_Type:
            self.BibData_HowPublished = PIE_CONFIG.get(
                'Format', 'default_howpublished_text')
            self.BibData_Type = PIE_CONFIG.get(
                'Format', 'default_bibtex_entry_type')
        if tags:
            self.add_tags(tags, threaded)
        if inferred_filetype:
            self.set_file_type(inferred_filetype)
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

    def add_aspect_cached(self, temp_location):
        self.add_aspect_cached_from_desktop(temp_location)

    def add_aspect_failed_download(self):
        '''Flag this as a failed download'''
        self.aspects['failed_dl'] = True

    def add_aspect_stored(self, final_fn=None, sqsess=session):
        '''Add information pertaining to the storage of this item in
        the system'''
        if not final_fn == self.FileData_FullPath:
            print 'SETTING IT', final_fn
            self.set_file(final_fn, sqsess=sqsess) #set filename if specified and different 
            self.aspects['stored'] = True
            self.set_file_type()
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
                if key == 'BibData_Key': print 'Setting key'
                setattr(self, key, val)
        if kwargs.has_key('WebData_Url'):
            # NOTE: Not sure about doing this. 
            self.aspects['onweb'] = True
            # if not self.WebData_PageUrl:
            #     self.WebData_PageUrl = kwargs['WebData_Url']

    def flag_followup(self, flagstatus, duedate=None):
        '''Flag this object for review or follow up by the user.'''
        assert type(flagstatus) == bool
        self.StatData_FollowUpFlag = flagstatus
        self.StatData_FollowUpDate = datetime.datetime.today()
        
    def set_session(self, sess):
        '''Mark a session flag for this object'''
        self.session = sess

    def est_folder_rel(self, sqsess=session):
        '''Establish a relationship with a folder'''
        # Only if this is going in the real storage dirs
        # We're assuming this isn't being done in a thread
        if self.FileData_Root in ('projectdir', 
                                  'librarydir',
                                  'meetingpaperdir',
                                  'recentdocsdir'):
            try:
                self.FileData_FolderAdv = referable_folder_byobj(self, sqsess=sqsess)
            except:
                traceback.print_exc()
                print 'Warning: Could not link file to its folder'
    
    def set_file(self, loc, sqsess=session):
        '''Set all kinds of data associated with this being a local file.
        Should have full absolute path given to it.'''
        if not os.path.exists(loc):
            raise IOError, 'Trying to set file data for non existant file'
        self.FileData_FileName = os.path.basename(loc)
        self.FileData_Size = os.stat(loc).st_size
        if not self.FileData_DateModified:
            # don't override mod_date that might come from metadata
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
                self.est_folder_rel(sqsess=sqsess)
                break
        if not fdroot: raise Exception, 'File stored outside pieberry domain'
        print "DONE", self.FileData_Root, self.FileData_FileName

    def set_file_type(self, ft=None):
        '''Set the type of file, drawing on mime information or specified type'''
        if not ft:
            try:
                # print 'GENNINIG', self.FileData_FullPath
                self.FileData_FileType = determine_file_type(
                    self.FileData_FullPath)
            except:
                traceback.print_exc()
                # if examination of the file fails to determine its
                # type, but the type has already been set, just return
                # (assume the type hasn't changed).
                if self.FileData_FileType: return
                else: print 'Warning - failed to determine a file ype' 
                    #raise Exception, 'Failed to determine a file type'
        elif ft != 'unknown':
            self.FileData_FileType = ft

    def clear_file(self):
        '''Clear all file data - the file is gone (but the object isn't)'''
        self.FileData_FileType = None
        self.FileData_FileName = None
        self.FileData_Size = None
        self.FileData_Root = None
        self.FileData_Folder = []
        self.FileData_DateCreated = None
        self.FileData_DateModified = None
        self.remove_aspect('hasfile')

    def get_icon_code(self, window_type=None):
        '''Return a code for iconic representation of this object. A
        context can be given through parameter window_type. The codes
        will correspond to various items in a wx.ImageList for the
        list/other type of window concerned. Values may include:
        'start' 'spin' 'blank' 'success' 'fail' 'warn' 'pass' 'tick'
        'exclude' 'pdf' 'doc' 'star'

        Contexts may include 'filewindow', 'bibwindow', 'dlwindow'''
        def xball():
            if self.FileData_Root:
                if self.FileData_Root == 'librarydir':
                    return 'yellowball'
                elif self.FileData_Root == 'projectdir':
                    if self.FileData_FolderAdv:
                        defcon = PIE_INTERNALS.getint(
                            'Security', 
                            'EncryptAfterSecurityLevel')
                        if self.FileData_FolderAdv.SecurityLevel > defcon:
                            if self.aspects['encrypted'] == EC_TRUE_UNLOCKED:
                                return 'unlocked'
                            elif self.aspects['encrypted'] == EC_TRUE_LOCKED:
                                return 'locked'
                            else: return 'neverlocked'
                    return 'greenball'
                elif self.FileData_Root == 'meetingpaperdir':
                    return 'redball'
                else: return 'blueball'
            else:
                return 'blueball'
        
        if window_type == 'filewindow':
            if self.aspects['encrypted'] in (EC_TRUE_LOCKED, EC_TRUE_UNLOCKED):
                return 'filelocked'
            if self.FileData_FileType == 'pdf': return 'pdf'
            elif self.FileData_FileType == 'word_doc': return 'doc'
            elif self.FileData_FileType == 'oxml_doc': return 'docx'
            elif self.FileData_FileType == 'odf': return 'odf'
            elif self.FileData_FileType == 'html': return 'html'
            else: return 'text'
        elif window_type == 'bibwindow':
            if self.StatData_FollowUpFlag and self.StatData_Favourite:
                return 'flagstar'
            elif self.StatData_FollowUpFlag:
                return 'flag'
            elif self.StatData_Favourite:
                return 'star'
            else: return xball()
    
    def stats_opened(self):
        self.StatData_LastOpened = date=datetime.datetime.today()
        self.StatData_OpenedCount += 1
        print '%s opened %d times' % (self, self.StatData_OpenedCount)

    def SortContext(self, context):
        '''Return a key to allow objectstore sorting, dependent on
        context (e.g. date, filename, title)'''
        if context == 'date':
            return self.ReferDate()
        elif context == 'filename':
            return self.FileData_FileName
        elif context == 'title':
            return self.Title()
        elif context == 'author':
            return self.Author()


# metadata = SQLABase.metadata
# metadata.create_all(engine)

# TODO - create a general version upgrade process and module
from copy import copy



def reconcile_object_folder_gen():
    '''Generator function to serve file-bearing objects which are
    ex-post linked to their folders, aslo some sanity checks needed
    post beta3'''
    # sift out folders that have a bug (null subdirectory)
    for fobj in session.query(PieFolder):
        if [ True for i in fobj.SubFolders if i == u'' ]:
            print 'sanity check deleting', fobj
            session.delete(fobj)
    # link folders to objects
    for obj in session.query(PieObject):
        # prepare for encryptability
        if not obj.aspects.has_key('encrypted'):
            obj.aspects['encrypted'] = EC_FALSE
        if obj.has_aspect('stored') and not obj.FileData_FolderAdv:
            # fix up null subdirs in the pieobject
            obj.FileData_Folder = [i for i in obj.FileData_Folder if i]
            # query whether our folder exists
            qf = session.query(PieFolder).filter(and_(
                    PieFolder.Root == obj.FileData_Root,
                    PieFolder.SubFolders == obj.FileData_Folder
                    )).first()
            if qf:
                print 'linking', obj, 'to', qf
                obj.FileData_FolderAdv = qf
                yield obj
            else:
                print 'no link to be made', obj
                yield obj
                # don't forget to commit the session in the calling fn

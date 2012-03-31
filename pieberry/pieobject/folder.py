# (c) Raif Sarcich, GPLv3, 2012

# DB object for storing information about folders

import sys, os, os.path, datetime
from pprint import pprint
from sqlalchemy import Column, Integer, String, DateTime, Unicode, PickleType
from sqlalchemy import and_
from ConfigParser import SafeConfigParser
from pieberry.piedb import SQLABase, session
from pieberry.pieconfig.paths import ROOT_MAP
from pieberry.pieconfig.globalvars import DEBUG
from pieberry.pieutility.decoding import *

global FOLDER_LOOKUP
FOLDER_LOOKUP = {}
SECURITY_CLASSES = (
    _("UNCLASSIFIED"),
    _("IN-CONFIDENCE"),
    _("RESTRICTED"),
    _("PROTECTED"),
    _("CONFIDENTIAL"),
    _("HIGHLY-PROTECTED"),
    _("SECRET"),
    _("TOP-SECRET"))
INFO_FNAME = '_Folder_Info.txt'

for key, val in ROOT_MAP.items():
    FOLDER_LOOKUP[key] = []

def recommend_folder(obj):
    fs = session.query(PieFolder).filter(PieFolder.Root == 'projectdir')
    f_cands = []
    for f in fs:
        score = 0
        for aterm in f.MatchTerms_Author:
            if aterm.lower() in obj.Author().lower():
                score += 1
        for tterm in f.MatchTerms_Title:
            if tterm.lower() in obj.Title().lower():
                score += 1
            if tterm.lower() in obj.FileData_FileName.lower():
                score += 1
        if score > 0: f_cands.append((score, f))
    if len(f_cands) == 0: return
    f_cands.sort(lambda x, y: cmp(y[0], x[0]))
    pprint(f_cands)
    return f_cands[0][1] # return a PieFolder

def add_new_folder(rootname, foldername):
    '''add a new folder to a root directory'''
    assert type(foldername) in (str, unicode)
    if not rootname in ROOT_MAP.keys():
        raise Exception, 'Root directory not found'
    foldername = translate_non_alphanumerics(foldername)
    existingfolders = session.query(PieFolder).filter(and_(
            PieFolder.EndName == foldername,
            PieFolder.Root == rootname)).all()
    if len(existingfolders) > 0:
        raise Exception, 'This folder already exists in database'
    folderpath = os.path.join(ROOT_MAP[rootname], foldername)
    if os.path.exists(folderpath) and not os.path.isdir(folderpath):
        raise Exception, 'Conflict: File with this name already exists on disk'
    newfolder = PieFolder(os.path.join(ROOT_MAP[rootname], foldername))
    if os.path.exists(folderpath) and os.path.isdir(folderpath):
        hfile = os.path.join(folderpath, _(INFO_FNAME))
        if os.path.isfile(hfile):
            hh = HeaderHandler(headerfile=hfile)
            newfolder.SecurityLevel = hh.securitylevel
            newfolder.RecordFile = hh.recordfile
    else:
        os.mkdir(newfolder.path())
    session.add(newfolder)
    session.commit()
    FOLDER_LOOKUP[rootname].append(newfolder)
    return newfolder

def get_project_folder_by_endname(endname):
    for fldr in session.query(PieFolder).filter(and_(
            PieFolder.Root == 'projectdir',
            PieFolder.EndName == endname)):
        return fldr
    return None


# Deprecated
def generate_initial_project_folder_list():
    '''Do a filesystem sweep and return a list of the existing folders'''
    FOLDER_LOOKUP['projectdir'] = []
    existing = session.query(
        PieFolder).filter(PieFolder.Root == 'projectdir').all()
    for folder in existing:
        if not os.path.isdir(folder.path()):
            print 'Warning - %s was loaded but does not exist' % existing.path()
    FOLDER_LOOKUP['projectdir'].extend(existing)
    for diry in os.walk(ROOT_MAP['projectdir']).next()[1]:
        if not get_project_folder_by_endname(diry):
            newf = add_new_folder('projectdir', diry)
            print 'Note: new unmapped project folder %s added' % os.path.join(
                ROOT_MAP['projectdir'], diry)


def generate_folder_list():
    '''Walk through the pieberry filesystem and ensure that all
    folders are indexed'''

    def gen_subfolders(root_key, curr_dir, sub_dir):
        '''cut up the path'''
        ds = curr_dir[len(ROOT_MAP[root_key]):].split(os.sep)
        ds.append(sub_dir)
        return [i for i in ds if i]

    def contribute_projectfolder(piefolder):
        '''init new primary project folder'''
        hh = HeaderHandler(piefolder=piefolder)
        hh.write_header()
        FOLDER_LOOKUP['projectdir'].append(piefolder)
    
    def verify_existing():
        for qf in session.query(PieFolder):
            if not os.path.isdir(qf.path()):
                print 'nonexistant folder -', qf
                session.delete(qf)
        session.commit()

    verify_existing()

    FOLDER_LOOKUP['projectdir'] = []
    for root_key in ROOT_MAP.keys():
        if root_key in ('cachedir', 'backupdir', 'desktopdir'): continue
        for curr_dir, subdirs, files in os.walk(ROOT_MAP[root_key]):
            for subdir in subdirs:
                cut_subdirs = gen_subfolders(root_key, curr_dir, subdir)
                # is there an existing piefolder in the db for this?
                exisf = session.query(PieFolder).filter(and_(
                        PieFolder.Root == root_key,
                        PieFolder.SubFolders == cut_subdirs,
                        )).first()
                if not exisf: # if the folder isn't already in the db
                    print 'creating:', os.path.join(curr_dir, subdir)
                    print 'vars:', cut_subdirs, root_key
                    # create a new piefolder object
                    n_piefolder = PieFolder()
                    n_piefolder.set_path_precut(root_key, cut_subdirs)
                    session.add(n_piefolder)
                    if curr_dir == ROOT_MAP['projectdir']:
                        contribute_projectfolder(n_piefolder)
                    print n_piefolder
                else:  
                    if curr_dir == ROOT_MAP['projectdir']:
                        FOLDER_LOOKUP['projectdir'].append(exisf)
                    print 'found folder:', exisf

def referable_folder_byobj(obj, sqsess=session):
    print 'Getting referable object'
    print 'Using:', obj.FileData_Root, obj.FileData_Folder
    qf = sqsess.query(PieFolder).filter(and_(
            PieFolder.Root == obj.FileData_Root,
            PieFolder.SubFolders == [i for i in obj.FileData_Folder if i]
            )).first()
    print 'Found:', qf
    return qf

def referable_folder_bypath(root, path, sqsess=session):
    subdirs = path[len(ROOT_MAP[root]):].split(os.sep)
    qf = sqsess.query(PieFolder).filter(and_(
            PieFolder.Root == root,
            PieFolder.SubFolders == [ i for i in subdirs if i ]
            )).first()
    return qf

def contribute_folder(path, components):
    '''Establish - if necessary a new folder on disk and a
    corresponding PieFolder entry in the database'''
    root, subfolders, fn = components
    if os.path.exists(path) and not os.path.isdir(path):
        raise ValueError, 'Conflict: a file with this path exists: %s' % path
    if os.path.isdir(path):
        return True # return if the folder exists
    else:
        os.makedirs(path)
    # don't do db stuff for things not in proper storage directories
    if root not in ('projectdir', 
                    'librarydir',
                    'meetingpaperdir',
                    'recentdocsdir'):
        return 
    # ensure we don't duplicate any dormant PieFolders
    existpf = session.query(PieFolder).filter(and_(
            PieFolder.Root == root,
            PieFolder.SubFolders == subfolders)).first()
    if existpf: return existpf
    else:
        newpf = PieFolder()
        newpf.set_path_precut(root, subfolders)
        session.add(newpf)
        session.commit()
        print 'CREATED', newpf
        return newpf

def contribute_and_get_folder(path, components):
    '''Like contribute_folder, but be sure to return the folder that
    was contributed (more DB intensive)'''
    root, subfolders, fn = components
    if os.path.exists(path) and not os.path.isdir(path):
        raise Exception, 'Conflict: a file with this path exists: %s' % path
    if not os.path.isdir(path):
        os.makedirs(path)
    existpf = session.query(PieFolder).filter(and_(
            PieFolder.Root == root,
            PieFolder.SubFolders == subfolders)).first()
    if existpf: return existpf
    else:
        newpf = PieFolder()
        newpf.set_path_precut(root, subfolders)
        session.add(newpf)
        session.commit()
        print 'CREATED', newpf
        return newpf
    
    
def commit_folders():
    session.commit()

def rollback_folders():
    session.rollback()

class HeaderHandler(SafeConfigParser):
    '''Class to write human readable folder info header files'''
    def __init__(self, piefolder=None, headerfile=None):
        SafeConfigParser.__init__(self)
        assert piefolder or headerfile
        if piefolder:
            assert type(piefolder) == PieFolder
            assert piefolder.initialised == 1
        if piefolder:
            self.add_section(_('Folder Information'))
            self.set(_('Folder Information'), 
                     _('Name'), piefolder.EndName.encode('utf8'))
            self.set(_('Folder Information'), 
                     _('Area'), piefolder.Root.encode('utf8'))
            self.set(_('Folder Information'), 
                     _('Record System No.'), 
                     piefolder.RecordFile.encode('utf8'))
            self.set(_('Folder Information'), 
                     _('Security Level'), 
                     SECURITY_CLASSES[piefolder.SecurityLevel])
            self.path = piefolder.path()
        elif headerfile:
            assert os.path.isfile(headerfile)
            self.read(headerfile)
        self.recordfile = self.get(_('Folder Information'), 
                                   _('Record System No.'))
        self.securitylevel = self.get(_('Folder Information'),
                                      _('Security Level'))
    
    def write_header(self):
        try:
            self.write(open(os.path.join(self.path, _(INFO_FNAME)), 'w'))
        except:
            raise 'Couldn\'t write folder info header file'

                

class PieFolder(SQLABase):
    '''A class for information about library and project folders'''
    __tablename__ = 'piefolders'

    id = Column(Integer, primary_key=True)
    initialised = Column(Integer)

    EndName = Column(Unicode(length=255))
    Root = Column(Unicode(length=255))
    SubFolders = Column(PickleType)
    RecordFile = Column(Unicode(length=255)) # Corresponding records
                                             # management file
    SecurityLevel = Column(Integer) # Security classification of
                                    # file/folder based on Aust Govt
                                    # email classification
                                    # system. (NB: These goggles do
                                    # nothing security-wise ... it's
                                    # just an fyi).
    MatchTerms_Author = Column(PickleType)
    MatchTerms_Title = Column(PickleType)

    def __init__(self, path=None):
        self.initialised = 0
        self.MatchTerms_Author = []
        self.MatchTerms_Title = []
        self.RecordFile = u''
        self.SecurityLevel = 0
        if path: self.set_path(path)

    def __repr__(self):
        return "<PieFolder %s>" % self.path()

    def set_path(self, path):
        # if not os.path.isdir(path):
        #     raise ValueError, "Not a valid folder"
        # ^^ actually, non-existent directories should be ok
        for key, pdir in ROOT_MAP.items():
            if path[:len(pdir)] == pdir:
                fdroot = key
                self.Root = key
                self.SubFolders=[i for i in path[len(pdir):].split(os.sep) if i]
        if self.SubFolders: 
            self.EndName = self.SubFolders[-1]
        else:
            self.EndName == ROOT_MAP[fdkey].split(os.sep)[-1]
        if not fdroot: raise Exception, 'Folder outside pieberry domain'
        self.initialised = 1
        print 'initialised:', self

    def set_path_precut(self, root, subfolders):
        '''Set the path, when we already have chopped up the path -
        more efficient'''
        assert root in ROOT_MAP.keys()
        assert type(subfolders) == list
        self.Root = root
        self.SubFolders = [i for i in subfolders if i]
        if self.SubFolders: 
            self.EndName = self.SubFolders[-1]
        else:
            self.EndName == ROOT_MAP[fdkey].split(os.sep)[-1]
        self.initialised = 1

    def path(self):
        pathlist = [ROOT_MAP[self.Root],] + self.SubFolders
        return os.path.join(*pathlist)

    def set_project_path(self, foldername):
        '''convenience function to set a path in the projects tree'''
        self.set_path_precut('projectdir', [foldername,])

    def name(self):
        if not self.initialised == 1:
            raise AttributeError
        if len(self.SubFolders) == 0:
            return self.Root
        else:
            return os.path.join(*self.SubFolders)

    def write_header(self):
        '''write a human-readable header file for the folder
        containing information on it.'''
        p = HeaderHandler(piefolder=self)
        p.write_header()

#DEBUG STUFF

spoof_folder_names = ('groening', 'parker', 'stone', 'judge', 'schultz')

def generate_spoof_folder_list():
    '''Generate test folders'''
    for i in range(len(spoof_folder_names)):
        add_new_folder('projectdir', spoof_folder_names[i])
    os.mkdir(os.path.join(ROOT_MAP['projectdir'], 'saturn'))


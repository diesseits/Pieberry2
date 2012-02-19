# (c) Raif Sarcich, GPLv3, 2012

# DB object for storing information about folders

import sys, os, os.path, datetime
from sqlalchemy import Column, Integer, String, DateTime, Unicode, PickleType
from sqlalchemy import and_

from pieobject.database import SQLABase, session
from pieconfig.paths import ROOT_MAP
from pieconfig.globals import DEBUG
from pieutility.decoding import *

FOLDER_LOOKUP = {}
global FOLDER_LOOKUP

for key, val in ROOT_MAP.items():
    FOLDER_LOOKUP[key] = []

def add_new_folder(rootname, foldername):
    '''add a new folder to a root directory'''
    if not rootname in ROOT_MAP.keys():
        raise Exception, 'Root directory not found'
    foldername = translate_non_alphanumerics(foldername)
    existingfolders = session.query(PieFolder).filter(and_(
            PieFolder.EndName == foldername,
            PieFolder.Root == rootname)).all()
    if len(existingfolders) > 0:
        raise Exception, 'This folder already exists in database'
    if os.path.exists(os.path.join(ROOT_MAP[rootname], foldername)):
        raise Exception, 'Something with this name already exists on disk'
    newfolder = PieFolder(os.path.join(ROOT_MAP[rootname], foldername))
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

def generate_initial_folder_list(rootdir):
    '''Do a filesystem sweep and return a list of the existing folders'''
    for diry in os.listdir(ROOT_MAP[projectdir]):
        continue
    
def commit_folders():
    session.commit()

def rollback_folders():
    session.rollback()

class PieFolder(SQLABase):
    '''A class for information about library and project folders'''
    __tablename__ = 'piefolders'

    id = Column(Integer, primary_key=True)
    initialised = Column(Integer)

    EndName = Column(Unicode)
    Root = Column(Unicode)
    SubFolders = Column(PickleType)
    RecordFile = Column(Unicode) # Corresponding records management file
    
    MatchTerms_Author = Column(PickleType)
    MatchTerms_Title = Column(PickleType)

    def __init__(self, path=None):
        self.initialised = 0
        self.MatchTerms_Author = []
        self.MatchTerms_Title = []
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
                self.SubFolders = path[len(pdir):].split(os.sep)
        if not self.SubFolders: 
            raise Exception, 'Folder is a root folder'
        self.EndName = self.SubFolders[-1]
        if not fdroot: raise Exception, 'Folder outside pieberry domain'
        self.initialised = 1
        print 'initialised:', self

    def path(self):
        pathlist = [ROOT_MAP[self.Root],] + self.SubFolders
        return os.path.join(*pathlist)

    def set_project_path(self, foldername):
        '''convenience function to set a path in the projects tree'''
        newpath = os.path.join(ROOT_MAP['projectdir'], foldername)
        self.set_path(newpath)

    def name(self):
        if not self.initialised == 1:
            raise AttributeError
        if len(self.SubFolders) == 0:
            return self.Root
        else:
            return os.path.join(*self.SubFolders)


#DEBUG STUFF

spoof_folder_names = ('groening', 'parker', 'stone', 'judge', 'schultz')

def generate_spoof_folder_list():
    '''Generate test folders'''
    for i in range(len(spoof_folder_names)):
        add_new_folder('projectdir', spoof_folder_names[i])


# (c) Raif Sarcich, GPLv3, 2012

# DB object for storing information about folders

import sys, os, os.path, datetime
from sqlalchemy import Column, Integer, String, DateTime, Unicode, PickleType


from pieobject.database import SQLABase
from pieconfig.paths import ROOT_MAP
from pieconfig.globals import DEBUG

FOLDER_LOOKUP = {}

for key, val in ROOT_MAP.items():
    FOLDER_LOOKUP[key] = []

class PieFolder(SQLABase):
    '''A class for information about library and project folders'''
    __tablename__ = 'piefolders'

    id = Column(Integer, primary_key=True)
    initialised = Column(Integer)
    
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
        if not fdroot: raise Exception, 'Folder outside pieberry domain'
        self.initialised = 1
        print 'initialised:', self

    def path(self):
        pathlist = [ROOT_MAP[self.Root],] + self.SubFolders
        return os.path.join(*pathlist)

    def name(self):
        if not self.initialised == 1:
            raise AttributeError
        if len(self.SubFolders) == 0:
            return self.Root
        else:
            return os.path.join(*self.SubFolders)

def generate_initial_folder_list(rootdir):
    '''Do a filesystem sweep and return a list of the existing folders'''
    pass

#DEBUG STUFF

spoof_folder_names = ('groening', 'parker', 'stone', 'judge', 'schultz')

def generate_spoof_folder_list():
    '''Generate test folders'''
    for i in range(len(spoof_folder_names)):
        path = os.path.join(ROOT_MAP['projectdir'], spoof_folder_names[i])
        fobj = PieFolder(path)
        FOLDER_LOOKUP['projectdir'].append(fobj)

if DEBUG:
    generate_spoof_folder_list()
    print 'DEBUG FOLDER LIST GENERATED'
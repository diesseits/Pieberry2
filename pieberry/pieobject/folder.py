# (c) Raif Sarcich, GPLv3, 2012

# DB object for storing information about folders

import sys, os, os.path, datetime
from pprint import pprint
from sqlalchemy import Column, Integer, String, DateTime, Unicode, PickleType
from sqlalchemy import and_

from piedb import SQLABase, session
from pieconfig.paths import ROOT_MAP
from pieconfig.globals import DEBUG
from pieutility.decoding import *

global FOLDER_LOOKUP
FOLDER_LOOKUP = {}

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
        pass
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
    os.mkdir(os.path.join(ROOT_MAP['projectdir'], 'saturn'))


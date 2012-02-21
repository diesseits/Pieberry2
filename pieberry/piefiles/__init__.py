import os, os.path, sys, wx
import piemeta

from threading import Thread

from ui.events import PieFileIndexEvent
from pieobject import PieObject, PieFolder
from pieobject.database import Session
from pieconfig.paths import *

def fl_in_db(fp, session):
    '''Is a file with this path in the database already?'''
    fn = os.path.basename(fp)
    q = session.query(PieObject).filter(PieObject.FileData_FileName == fn)
    for pmatch in q:
        if pmatch.FileData_FullPath == fp:
            return True
    return False

class PieFileIndexer(Thread):
    '''A class which indexes the user's files, looks for disappeared
    files, looks for where they may have reappeared, and looks for new
    files and puts them into the database.'''
    def __init__(self, notify_window):
        Thread.__init__(self)
        self.session = Session()
        self.nwin = notify_window

    def run(self):
        print self.DoScanForMissing('projectdir')

    def DoScanForMissing(self, rootdir):
        q = self.session.query(PieObject).filter(
            PieObject.FileData_Root == rootdir)
        count = q.count()
        track = 0
        missing = []
        for obj in q:
            track += 1
            newevt = PieFileIndexEvent(count=count, track=track,
                                       message=_('Scanning for missing files'))
            wx.PostEvent(self.nwin, newevt)
            if not os.path.exists(obj.FileData_FullPath):
                missing.append(obj)
        return missing

    def DoScanForNew(self, rootdir):
        newpaths = []
        for walk in os.walk(ROOT_MAP[rootdir]):
            track = 0
            count = len(walk[2])
            for fl in walk[2]:
                fp = os.path.join(walk[0], fl)
                if not fl_in_db(fp):
                    newpaths.append(fp)
                track += 1
                newevt = PieFileIndexEvent(
                    count=count, track=track,
                    message=_('Scanning for new files in %s' % walk[0]))
                wx.PostEvent(self.nwin, newevt)
        return newpaths

    def AddNewFiles(self, newpaths):
        for fp in newpaths:
            # Todo - check handle-able file types
            obj = piemeta.get_metadata_object(fp)
            self.session.add(obj)
        session.commit()
            
    def MatchMissingFile(self, obj, newpaths):
        l1_matches = []
        l2_matches = []
        for path in newpaths:
            foldermatch = 0
            sizematch = 0
            namematch = 0
            crdatematch = 0
            stat = os.stat(path)
            if stat.st_crdate == obj.FileData_DateCreated: crdatematch = 1
            if stat.st_size == obj.FileData_Size: sizematch = 1
            if os.path.dirname(path) == obj.FileData_ContainingFolder: 
                foldermatch = 1
            if os.path.basename(path) == obj.FileData_FileName: namematch = 1
            score = foldermatch + sizematch + namematch + crdatematch
            if score == 4: raise 'This is unaltered! How did this slip through?'
            if sizematch and namematch:
                l1_matches.append(path)
            if sizematch and foldermatch:
                l1_matches.append(path)
            if sizematch and crdatematch:
                l2_matches.append(path)
            if namematch and crdatematch:
                l2_matches.append(path)
        return l1_matches, l2_matches
        
    def AddNewFile(self, path):
        pass

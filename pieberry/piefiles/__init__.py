import os, os.path, sys, wx, traceback, datetime
import piemeta

from threading import Thread

from ui.events import PieFileIndexEvent
from pieobject import PieObject, PieFolder
from pieobject.database import Session
from pieconfig.paths import *

class TooManyMatchesError(Exception):
    '''This Exception means too many matching files were found'''
    def __init__(self, fl):
        msg = 'Too many good matches for %s' % fl
        Exception.__init__(self, msg)

class IdentityMatchError(Exception):
    '''This Exception means that an identity match was found (it is
    identical to the file it is being compared to, which shouldn't
    happen'''
    def __init__(self, fl):
        msg = 'Identity match found! Why? %s' % fl
        Exception.__init__(self, msg)

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
        # for f in self.DoScanForMissing('librarydir'):
        #     pass
        # Scan project dir, reassign moved files, delete deleted files
        newpaths = self.DoScanForNew('projectdir')
        print 'New paths found:', newpaths
        for f in self.DoScanForMissing('projectdir'):
            try:
                match, possible = self.MatchMissingFile(f, newpaths)
            except Exception, exc:
                traceback.print_exc()
                match = None
                match = None
            if match:
                print 'Changing file for the following object', f
                print 'From: %s\n To: %s' % (f.FileData_FullPath, match)
                try:
                    f.set_file(match)
                except Exception, exc:
                    print "An error occurred setting file", exc
                # whittle down the new files list
                newpaths.pop(newpaths.index(match))
            elif possible:
                for i in possible: 
                    p = newpaths.pop(newpaths.index(i))
                    # Todo - develop some sort of report-to-user on
                    # possible matches for user to resolve?
            else:
                # If we can't find it, it's gone. Delete the record.
                print 'Deleting %s' % f
                try:
                    self.session.delete(f)
                except:
                    print 'Could not delete %s - will try again next time' % f
            session.commit()

        # Now add new objects to the db - the residual left over from
        # the matching process above.
        self.AddNewFiles(newpaths)

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
                yield obj
        #         missing.append(obj)
        # return missing

    def DoScanForNew(self, rootdir):
        newpaths = []
        for walk in os.walk(ROOT_MAP[rootdir]):
            print 'DoScanForNew:', walk[0]
            track = 0
            count = len(walk[2])
            for fl in walk[2]:
                fp = os.path.join(walk[0], fl)
                if not fl_in_db(fp, self.session):
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
            print 'AddNewFiles: Adding object %s' % obj
        self.session.commit()
            
    def MatchMissingFile(self, obj, newpaths):
        l1_matches = []
        l2_matches = []
        for path in newpaths:
            foldermatch = 0
            sizematch = 0
            namematch = 0
            crdatematch = 0
            stat = os.stat(path)
            if datetime.datetime.fromtimestamp(
                stat.st_ctime) == obj.FileData_DateCreated: crdatematch = 1
            if stat.st_size == obj.FileData_Size: sizematch = 1
            if os.path.dirname(path) == obj.FileData_ContainingFolder: 
                foldermatch = 1
            if os.path.basename(path) == obj.FileData_FileName: namematch = 1
            score = foldermatch + sizematch + namematch + crdatematch
            if score == 4: raise IdentityMatchError, obj.FileData_FileName
            # good matches
            if sizematch and namematch:
                l1_matches.append(path)
            elif sizematch and foldermatch:
                l1_matches.append(path)
            elif crdatematch and foldermatch:
                l1_matches.append(path)
            # weaker matches
            # if sizematch and crdatematch:
            #     l2_matches.append(path)
            # if namematch and crdatematch:
            #     l2_matches.append(path)
        if len(l1_matches) == 1:
            return l1_matches[0], None
        elif len(l1_matches) > 1:
            # raise TooManyMatchesError, obj.FileData_FileName
            return None, l1_matches
        elif len(l1_matches) == 0:
            return None, None
        
    def AddNewFile(self, path):
        pass

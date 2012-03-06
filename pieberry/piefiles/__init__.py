import os, os.path, sys, wx, traceback, datetime, time, re
import pieberry.piemeta as piemeta

from threading import Thread

from pieberry.ui.events import PieFileIndexEvent, PieFileIndexFinishedEvent
from pieberry.pieobject import PieObject, PieFolder
from pieberry.piedb import Session
from pieberry.pieobject.diagnostic import *
from pieberry.pieconfig.paths import *

IGNOREFILES = (
    re.compile(r'^_Folder_Info.txt'),
    re.compile(r'^[#~].*'),
    re.compile(r'^Backup.*')
    )

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
        self.nwin = notify_window

    def run(self):
        self.session = Session()
        newpaths = []
        for rootdir in ROOT_MAP.keys():
            if rootdir in ('cachedir', 'desktopdir', 'backupdir'):
                # We don't want to scan the cache or desktop
                continue
            newpaths.extend(self.DoScanForNew(rootdir))
            for f in self.DoScanForMissing(rootdir):
                # work through the missing files
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
                        print 'Verifying set:', f.FileData_FullPath
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
                    if rootdir == 'librarydir':
                        # different behaviour for librarydir, we just
                        # erase the file record from the object - the
                        # object may still contain useful information.
                        f.clear_file()
                    else:
                        print 'Deleting %s' % f
                        try:
                            self.session.delete(f)
                        except:
                            print 'Could\'t delete %s - try again next time' % f

        # Now add new objects to the db - the residual left over from
        # the matching process above.
        self.AddNewFiles(newpaths)
        self.session.commit()
        newevt = PieFileIndexFinishedEvent()
        wx.PostEvent(self.nwin, newevt)

    def DoScanForMissing(self, rootdir):
        q = self.session.query(PieObject).filter(
            PieObject.FileData_Root == rootdir)
        errorcount = 0
        while 1:
            try:
                count = q.count()
                break
            except ProgrammingError:
                time.sleep(2)
                errorcount += 1
                if errorcount == 5:
                    raise Exception, 'Cannot access database - locked?'
        track = 0
        missing = []
        for obj in q:
            track += 1
            newevt = PieFileIndexEvent(
                count=count, track=track,
                message=_('Scanning for missing files - %d of %d' % (track, count)))
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
                newevt = PieFileIndexEvent(
                    count=count, track=track,
                    message=_('Scanning for new files in %s - %d of %d' % (walk[0], track, count)))
                wx.PostEvent(self.nwin, newevt)
                fp = os.path.join(walk[0], fl)
                try:
                    # we don't want to deal with unknowable file types
                    mt = determine_file_type(fp)
                except:
                    continue
                if mt == 'other': continue
                if not fl_in_db(fp, self.session):
                    newpaths.append(fp)
                track += 1
        return newpaths

    def AddNewFiles(self, newpaths):
        '''Add any new files found to the database'''
        def exclude(newpath):
            '''Indicate exclusion based on matching an re in
            IGNOREFILES'''
            f = os.path.basename(newpath)
            for re in IGNOREFILES:
                if re.match(f): return True
            return False

        count = len(newpaths)
        track = 0
        for fp in newpaths:
            track += 1
            if exclude(fp): continue
            # Todo - check handle-able file types
            obj = piemeta.get_metadata_object(fp)
            obj.add_aspect_stored(fp)
            obj.add_aspect_saved()
            self.session.add(obj)
            newevt = PieFileIndexEvent(
                count=count, track=track,
                message=_('Adding newfound files - %d of %d' % (track, count)))
            wx.PostEvent(self.nwin, newevt)
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

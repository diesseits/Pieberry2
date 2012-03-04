import sys, os, shutil

from initsys import *
from identity import *
from globalvars import *

def GetAppdir():
    '''get the directory of the application itself'''
    if not __file__:
        pathname = sys.argv[0]
        retval = os.path.split(os.path.abspath(pathname))[0]
    else:
        retval = os.path.dirname(__file__)
    return retval

def nuke_directories():
    '''Abolish directories (debug only)'''
    print 'DELETING ALL DIRECTORIES'
    for dr in ROOT_MAP.values():
        if os.path.exists(dr):
            shutil.rmtree(dr)
    if os.path.exists(DBDIR):
        shutil.rmtree(DBDIR)
    return True

def create_directories():
    '''Set up directories'''
    for dr in ROOT_MAP.values():
        if not os.path.exists(dr):
            os.makedirs(dr)
    return True

def default_paths_relative_to_root(root):
    ret = {
        'rootdir': root,
        'librarydir': os.path.join(root, 'Library'),
        'projectdir': os.path.join(root, 'Projects'),
        'meetingpaperdir': os.path.join(root, 'Meeting Papers'),
        'recentdocsdir': os.path.join(root, 'Recent Documents'),
        'cachedir': os.path.join(root, '.cache'),
        'backupdir': os.path.join(root, '.backups')
        }
    return ret

def init_storage_location(path):
    '''Initialise a storage location, given as a path to a folder,
    which should or will contain a pieberry database, and a series of
    subfolders containing the library, project dir, etc.'''
    assert os.path.isdir(path)
    global DBDIR
    DBDIR = path
    otherpaths = default_paths_relative_to_root(path)
    global LIBRARYDIR
    global PROJECTDIR
    global MEETINGPAPERDIR
    global RECENTDOCSDIR
    global CACHEDIR
    global BACKUPDIR
    LIBRARYDIR = otherpaths['librarydir']
    PROJECTDIR = otherpaths['projectdir']
    MEETINGPAPERDIR = otherpaths['meetingpaperdir']
    RECENTDOCSDIR = otherpaths['recentdocsdir']
    CACHEDIR = otherpaths['cachedir']
    BACKUPDIR = otherpaths['backupdir']
    print 'LIBRARYDIR =', LIBRARYDIR
    print 'PROJECTDIR =', PROJECTDIR
    print 'MEETINGPAPERDIR =', MEETINGPAPERDIR
    print 'RECENDOCSDIR =', RECENTDOCSDIR
    global ROOT_MAP
    ROOT_MAP = { #map these potential roots to allow portability
        'cachedir': CACHEDIR,
        'librarydir': LIBRARYDIR,
        'projectdir': PROJECTDIR,
        'meetingpaperdir': MEETINGPAPERDIR,
        'recentdocsdir': RECENTDOCSDIR,
        'backupdir': BACKUPDIR
        }

def init_desktop_location(path):
    '''Set the new desktop location'''
    assert os.path.isdir(path)
    global DESKTOPDIR
    DESKTOPDIR = path
    print 'DESKTOPDIR =', DESKTOPDIR
    ROOT_MAP['desktopdir'] = DESKTOPDIR


# if PY2EXE:
#     IMGDIR = os.getcwd()
#     HELPDIR = os.path.join(os.getcwd(), 'pieberry')
# else:
#     IMGDIR = GetAppdir()
#     HELPDIR = os.path.join(GetAppdir(), 'help')

#### Path Construction


# if DEBUG == True:
#     CACHEDIR = '/tmp/pieberry/cache'
# else:
#     CACHEDIR = os.path.join(SYSDIR, 'cache')

# if DEBUG == True:
#     TESTDATADIR = '/home/raif/development/v2Pieberry/pieberry/testdata'
#     LIBRARYDIR = '/tmp/pieberry/library'
#     PROJECTDIR = '/tmp/pieberry/projects'
#     MEETINGPAPERDIR = '/tmp/pieberry/meeting papers'
#     RECENTDOCSDIR = '/tmp/pieberry/recent documents'
#     DESKTOPDIR = '/tmp/pieberry/desktop'
#     DBDIR = '/tmp/pieberry'
# else:
#     DESKTOPDIR = os.getcwd()



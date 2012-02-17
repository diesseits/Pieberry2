import sys, os, shutil

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

if sys.platform == 'linux2':
    SYSDIR = os.path.join(os.environ["HOME"], "".join([".", PIE_APPNAME]))
elif sys.platform == 'win32':
    if os.path.exists(os.path.join(os.environ["HOMEPATH"], "Application Data")):
        SYSDIR = os.path.join(os.environ["HOMEPATH"], "Application Data", PIE_APPNAME)
    else:
        SYSDIR = os.getcwd()
else: 
    SYSDIR = os.getcwd()

print 'CWD =', os.getcwd()
print 'SYSDIR =', SYSDIR

PIE_CONFIG_LOCATION = os.path.join(SYSDIR, 'pieberry.ini')

print 'PIE_CONFIG_LOCATION =', PIE_CONFIG_LOCATION

# if PY2EXE:
#     IMGDIR = os.getcwd()
#     HELPDIR = os.path.join(os.getcwd(), 'pieberry')
# else:
#     IMGDIR = GetAppdir()
#     HELPDIR = os.path.join(GetAppdir(), 'help')

IMGDIR = os.path.join(os.getcwd(), 'ui')
HELPDIR = os.path.join(os.getcwd(), 'piehelp')

print 'IMGDIR =', IMGDIR
print 'HELPDIR =', HELPDIR

#### Path Construction

def default_paths_relative_to_root(root):
    ret = {
        'rootdir': root,
        'librarydir': os.path.join(root, 'Library'),
        'projectdir': os.path.join(root, 'Projects'),
        'meetingpaperdir': os.path.join(root, 'Meeting Papers'),
        'recentdocsdir': os.path.join(root, 'Recent Documents')
        }
    return ret

if not os.path.exists(SYSDIR):
    try:
        os.mkdir(SYSDIR)
        print 'Making settings directory'
    except:
        print 'No authority to create settings directory'
        sys.exit(1)

if DEBUG == True:
    CACHEDIR = '/tmp/pieberry/cache'
else:
    CACHEDIR = os.path.join(SYSDIR, 'cache')

if DEBUG == True:
    TESTDATADIR = '/home/raif/development/v2Pieberry/pieberry/testdata'
    LIBRARYDIR = '/tmp/pieberry/library'
    PROJECTDIR = '/tmp/pieberry/projects'
    MEETINGPAPERDIR = '/tmp/pieberry/meeting papers'
    RECENTDOCSDIR = '/tmp/pieberry/recent documents'
    DESKTOPDIR = '/tmp/pieberry/desktop'
    DBDIR = '/tmp/pieberry'
else:
    DESKTOPDIR = os.getcwd()

ROOT_MAP = { #map these potential roots to allow portability
    'cachedir': CACHEDIR,
    'librarydir': LIBRARYDIR,
    'projectdir': PROJECTDIR,
    'meetingpaperdir': MEETINGPAPERDIR,
    'recentdocsdir': RECENTDOCSDIR,
    'desktopdir': DESKTOPDIR,
    }

print 'LIBRARYDIR =', LIBRARYDIR
print 'PROJECTDIR =', PROJECTDIR
print 'MEETINGPAPERDIR =', MEETINGPAPERDIR
print 'RECENDOCSDIR =', RECENTDOCSDIR
print 'DESKTOPDIR =', DESKTOPDIR

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


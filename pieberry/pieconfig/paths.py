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
    # create decryption directory
    if not os.path.exists(os.path.join(CACHEDIR, u'.decrypted')):
        os.makedirs(os.path.join(CACHEDIR, u'.decrypted'))
    return True

def default_paths_relative_to_root(root):
    ret = {
        'rootdir': root,
        'librarydir': os.path.join(root, u'Library'),
        'projectdir': os.path.join(root, u'Projects'),
        'meetingpaperdir': os.path.join(root, u'Meeting Papers'),
        'recentdocsdir': os.path.join(root, u'Recent Documents'),
        'cachedir': os.path.join(root, u'.cache'),
        'backupdir': os.path.join(root, u'.backups')
        }
    return ret

def init_storage_location(path):
    '''Initialise a storage location, given as a path to a folder,
    which should or will contain a pieberry database, and a series of
    subfolders containing the library, project dir, etc.'''
    assert os.path.isdir(path)
    assert type(path) == unicode
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
    # bibtempfile is a temporary bibtex file for pasted-in data
    global BIBTEMPFILE
    BIBTEMPFILE = os.path.join(CACHEDIR, 'bibtmp.bib')

def init_desktop_location(path):
    '''Set the new desktop location'''
    assert os.path.isdir(path)
    global DESKTOPDIR
    DESKTOPDIR = path
    print 'DESKTOPDIR =', DESKTOPDIR
    ROOT_MAP['desktopdir'] = DESKTOPDIR


def clean_cache_path():
    '''Cleans out crud in the cache. Call only after having
    initialised CACHEDIR'''
    dirs = [d for d in os.listdir(CACHEDIR) if os.path.isdir(os.path.join(CACHEDIR, d))]
    webdirs = [os.path.join(CACHEDIR, d) for d in dirs if d[:2] == 'w_']
    deskdirs = [os.path.join(CACHEDIR, d) for d in dirs if d[:2] == 'd_']
    # delete all webdir caches - if the user didn't store'em last time
    # then what's the use?
    for w in webdirs:
        try:
            shutil.rmtree(w)
            print 'deleting %s' % w
        except:
            print 'could not delete %s' % w
    for d in deskdirs:
        if len(os.listdir(d)) == 0:
            try:
                shutil.rmtree(d)
                print 'deleting %s' % d
            except:
                print 'could not delete %s' % d

    

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



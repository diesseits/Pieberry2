import sys, os

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

if not os.path.exists(SYSDIR):
    try:
        os.mkdir(SYSDIR)
        print 'Making settings directory'
    except:
        print 'No authority to create settings directory'
        sys.exit(1)

CACHEDIR = os.path.join(SYSDIR, 'cache')

if not os.path.exists(CACHEDIR):
    os.mkdir(CACHEDIR)

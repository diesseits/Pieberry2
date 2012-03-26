from identity import *

global TEST
TEST = True
global DEBUG
DEBUG = False
global PY2EXE
PY2EXE = False

#Available modules
global PYNOTIFY
PYNOTIFY = True

# Unicode error behaviour
U_ERROR_BEHAV = 'replace'

try:
    import pynotify
    if pynotify.init(PIE_APPNAME):
        PYNOTIFY = True
    else:
        PYNOTIFY = False
except:
    PYNOTIFY = False

try: 
    import zbar
    ZBAR = True
except:
    ZBAR = False


def _dbg(t):
    print t

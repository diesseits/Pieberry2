import sys, os, os.path
from identity import *

# Paths vital to the internals of Pieberry
frozen = getattr(sys, 'frozen', '')

def init_config_location():
    '''Set up config location'''
    if sys.platform == 'linux2':
        SYSDIR = os.path.join(os.environ["HOME"], "".join([".", PIE_APPNAME]))
    elif sys.platform == 'win32':
        if os.path.exists(os.path.join(os.environ["HOMEPATH"], "Application Data")):
            SYSDIR = os.path.join(os.environ["HOMEPATH"], "Application Data", PIE_APPNAME)
        else:
            SYSDIR = os.getcwd()
    else: 
        SYSDIR = os.getcwd()
    if not os.path.exists(SYSDIR):
        try:
            os.mkdir(SYSDIR)
            print 'Making settings directory'
        except:
            print 'No authority to create settings directory'
            sys.exit(1)
    PIE_CONFIG_LOCATION = os.path.join(SYSDIR, 'pieberry.ini')
    global SYSDIR
    global PIE_CONFIG_LOCATION
    print 'CWD =', os.getcwd()
    print 'SYSDIR =', SYSDIR
    print 'PIE_CONFIG_LOCATION =', PIE_CONFIG_LOCATION

def init_resource_locations():
    '''Where to find various bits of the program like bitmaps & help docs'''
    if frozen in  ('dll', 'console_exe', 'windows_exe'):
        IMGDIR = os.path.dirname(sys.executable)
        HELPDIR = os.path.dirname(sys.executable)
    else:
        IMGDIR = os.path.join(os.getcwd(), 'ui')
        HELPDIR = os.path.join(os.getcwd(), 'piehelp')
    global IMGDIR
    global HELPDIR
    print 'IMGDIR =', IMGDIR
    print 'HELPDIR =', HELPDIR

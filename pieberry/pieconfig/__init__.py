from globalvars import *
from paths import *
from schemas import *

def setup_config(inipath):
    config = ConfigParser.RawConfigParser()
    config.read(inipath)
    # do stuff to set up defaults
    config.write(open(inipath, 'w'))
    return config



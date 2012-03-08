from ConfigParser import ConfigParser, SafeConfigParser
from pprint import pprint
from globalvars import *
from initsys import *
from schemas import *
from identity import *
from defaults import *
from profiles import *

class PieConfig(SafeConfigParser):
    '''ConfigParser with extra methods to allow the loading and
    manipulation of various config profiles'''
    def __init__(self, *args, **kwargs):
        SafeConfigParser.__init__(self)

    def get(self, section, name):
        '''Overriding to hack up a unicoding return for some things'''
        val = SafeConfigParser.get(self, section, name)
        if name in ('rootdir', 'desktopdir'):
            return val.decode('utf8')
        else: return val

    def get_profile_names(self):
        print PROFILES.keys()
        return PROFILES.keys()

    def get_profile(self, name):
        return PROFILES[name]

    def add_profile(self, name, configdict):
        print 'Adding profile:'
        pprint(configdict)
        add_profile(name, configdict)

    def update_profile(self, name, configdict):
        update_profile(name, configdict)

    def delete_profile(self, name):
        delete_profile(name)

    def write_pieconfig(self):
        self.write(open(PIE_CONFIG_LOCATION, 'w'))

def refresh_paths():
    '''Reset the various path global variables'''
    pass

def setup_config(inipath):
    config = PieConfig()
    config.read(inipath)
    for cat in PIE_CONFIG_CATEGORIES:
        if not config.has_section(cat):
            config.add_section(cat)
    for optionset in PIE_CONFIG_DEFAULTS:
        if not config.has_option(optionset[0], optionset[1]):
            config.set(optionset[0], optionset[1], str(optionset[2]))
    config.write(open(PIE_CONFIG_LOCATION, 'w'))
    return config

def make_config():
    PIE_CONFIG = setup_config(PIE_CONFIG_LOCATION)
    global PIE_CONFIG



import sys, traceback
from ConfigParser import ConfigParser, SafeConfigParser
from pprint import pprint
from globalvars import *
from initsys import *
from schemas import *
from identity import *
from defaults import *
from profiles import *

import keyring, getpass, hashlib

if sys.platform in ('win32', 'win64'):
    if sys.getwindowsversion().major == 6:
        keyring.set_keyring(keyring.backend.Win32CryptoKeyring())
    else:
        try:
            keyring.set_keyring(keyring.backend.UncryptedFileKeyring())
        except: #hack: think there may be a bug where uncrypted won't
                #work if there's no PATH variable
            traceback.print_exc()
            keyring.set_keyring(keyring.backend.Win32CryptoKeyring())

class PieConfig(SafeConfigParser):
    '''ConfigParser with extra methods to allow the loading and
    manipulation of various config profiles'''
    def __init__(self, *args, **kwargs):
        SafeConfigParser.__init__(self)

    def get(self, section, name):
        '''Overriding to hack up a unicoding return for some things'''
        if section == 'Security' and name == 'file_key':
            k = keyring.get_password(u'Pieberry', getpass.getuser())
            if k == None: return k
            r = hashlib.md5()
            r.update(k)
            return r.hexdigest()
        if section == 'Security' and name == 'file_key_unhashed':
            return keyring.get_password(u'Pieberry', getpass.getuser())
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

    def set(self, section, name, value):
        if section == 'Security' and name == 'file_key':
            keyring.set_password(u'Pieberry', getpass.getuser(), value)
        else:
            SafeConfigParser.set(self, section, name, value)

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
    global PIE_CONFIG
    PIE_CONFIG = setup_config(PIE_CONFIG_LOCATION)



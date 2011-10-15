import ConfigParser

from globalvars import *
from paths import *
from schemas import *
from identity import *
from defaults import *

def setup_config(inipath):
    config = ConfigParser.RawConfigParser()
    config.read(inipath)
    for cat in PIE_CONFIG_CATEGORIES:
        if not config.has_section(cat):
            config.add_section(cat)
    for optionset in PIE_CONFIG_DEFAULTS:
        if not config.has_option(optionset[0], optionset[1]):
            config.set(optionset[0], optionset[1], optionset[2])
    config.write(open(PIE_CONFIG_LOCATION, 'w'))
    return config

PIE_CONFIG = setup_config(PIE_CONFIG_LOCATION)



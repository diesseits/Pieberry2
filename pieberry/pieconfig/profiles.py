# Handle config "profiles" which allow the user to store different
# path settings, which in turns enables the user to point pieberry at
# different pieberry locations. This is to enable, in particular, a
# usable way of storing pieberry libraries on mobile devices, usb hard
# disks etc.

import cPickle, os.path, os
from pieberry.pieconfig.initsys import *
from pieberry.pieconfig.globalvars import DEBUG
from pieberry.pieconfig.defaults import PIE_PROFILE_KEYS

PROFILES={}
global PROFILES

def add_profile(name, prof):
    assert type(prof) == dict
    for pkey in PIE_PROFILE_KEYS:
        if not prof.has_key(pkey):
            raise KeyError, 'Profile lacks key %s' % pkey
    PROFILES[name] = prof
    pickle_profiles()

def update_profile(name, prof):
    add_profile(name, prof)

def delete_profile(name):
    if not PROFILES.has_key(name):
        raise KeyError, 'No such profile: %s' % name
    PROFILES.pop(name)
    pickle_profiles()

def pickle_profiles():
    f = open(os.path.join(SYSDIR, 'profiles.pickle'), 'w')
    cPickle.dump(PROFILES, f)
    f.close()

if not os.path.exists(os.path.join(SYSDIR, 'profiles.pickle')):
    pickle_profiles()

pf = open(os.path.join(SYSDIR, 'profiles.pickle'), 'r')
PROFILES=cPickle.load(pf)
pf.close()

# Create a table for keeping settings internal to the Pieberry store
# in question. Mimic operation of ConfigParser

import random, hashlib, string
from sqlalchemy import Column, Integer, String, DateTime, Unicode, PickleType, and_
from pieberry.piedb import SQLABase, session
from pieberry.pieconfig.identity import *

def salted_hash(salt, firsthash):
    '''Return a salted hash of a first hash of a password'''
    md5 = hashlib.md5()
    md5.update(firsthash)
    md5.update(salt)
    return md5.hexdigest()

class PieInternal(SQLABase):
    '''A class to hold internal settings and metadata for the Pieberry store'''
    __tablename__ = 'pieinternals'
    
    id = Column(Integer, primary_key=True)
    section = Column(Unicode(length=255))
    key = Column(Unicode(length=255))
    value = Column(Unicode)

    def __init__(self, section=None, key=None, value=None):
        if section and key and value:
            self.section = section
            self.key = key
            self.value = value

class PieInternalsHandler:
    '''A class to mimic a ConfigParser and store internal settings'''
    def __init__(self):
        pass

    def establish(self):
        '''Establish basic setttings on explicit command'''
        if not self.has_setting('Identity', 'Hitherto_unset'):
            self.set('Identity', 'Hitherto_unset', True)
        if not self.has_setting('Identity', 'Appname'):
            self.set('Identity', 'Appname', PIE_APPNAME)
        if not self.has_setting('Identity', 'Version'):
            self.set('Identity', 'Version', PIE_VERSION)
        if not self.has_setting('Security', 'Salt'):
            self.set('Security', 'Salt', 
                     ''.join(random.choice(string.letters) for i in xrange(16)))
        if not self.has_setting('Security', 'EncryptAfterSecurityLevel'):
            self.set('Security', 'EncryptAfterSecurityLevel', 2)

    def set(self, section, key, value):
        assert type(section) in (unicode, str)
        assert type(key) in (unicode, str)
        existingsetting = session.query(PieInternal).filter(and_(
                PieInternal.section == section,
                PieInternal.key == key
                )).first()
        if existingsetting:
            existingsetting.value = unicode(value)
        else:
            newsetting = PieInternal(section, key, value)
            session.add(newsetting)
        session.commit()
        
    def has_setting(self, section, key):
        existingsetting = session.query(PieInternal).filter(and_(
                PieInternal.section == section,
                PieInternal.key == key
                )).first()
        if existingsetting: return True
        else: return False

    def get(self, section, key):
        existingsetting = session.query(PieInternal).filter(and_(
                PieInternal.section == section,
                PieInternal.key == key
                )).first()
        if not existingsetting: raise AttributeError, 'No such setting'
        return existingsetting.value

    def set_encryption_hash(self, pwd):
        '''Set the hash of the valid encryption key (md5 hex digest of
        the user set password) for this archive'''
        self.set('Security', 'Hash',
                 salted_hash(self.get('Security', 'Salt'), pwd)
                 )

    def verify_encryption_hash(self, pwd):
        '''Verify that the provided password (md5 hex digest of the
        user-set password) is the correct one for this archive'''
        if not self.has_setting('Security', 'Hash'):
            raise Exception, 'No password set for this archive'
        if salted_hash(self.get('Security', 'Salt'), pwd) == self.get('Security', 'Hash'):
            return True
        else: return False

    def getboolean(self, section, key):
        val = self.get(section, key)
        print 'VAL =', val
        if val.lower() == 'true': return True
        elif val == '1': return True
        elif val.lower() == 'false': return False
        elif val == '0': return False
        else: raise ValueError, 'This setting is not boolean'

    def getint(self, section, key):
        val = self.get(section, key)
        return int(val)
            
PIE_INTERNALS = PieInternalsHandler()
    
        

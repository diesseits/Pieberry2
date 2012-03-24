# Create a table for keeping settings internal to the Pieberry store
# in question. Mimic operation of ConfigParser

from sqlalchemy import Column, Integer, String, DateTime, Unicode, PickleType, and_
from pieberry.piedb import SQLABase, session
from pieberry.pieconfig.identity import *

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

    def getboolean(self, section, key):
        val = self.get(section, key)
        if val.lower() == 'true': return True
        elif val.lower() == 'false': return False
        else: raise ValueError, 'This setting is not boolean'
            
PIE_INTERNALS = PieInternalsHandler()
    
        

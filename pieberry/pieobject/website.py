# (c) Raif Sarcich, GPLv3, 2012

# DB object for storing information about websites

import sys, os, os.path, datetime

from pieobject.database import SQLABase
from pieconfig.paths import ROOT_MAP

class PieWebsite(SQLABase):
    '''A class for information about library and project folders'''
    __tablename__ = 'piefolders'

    id = Column(Integer, primary_key=True)

    SiteName = Column(Unicode)
    Domain = Column(Unicode)
    CMSType = Column(Unicode)
    DefaultAuthor = Column(Unicode)
    DefaultAuthorIsCorporate = Column(Boolean)
    

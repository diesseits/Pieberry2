# (c) Raif Sarcich, GPLv3, 2012

# DB object for storing information about websites

import sys, os, os.path, datetime
import urlparse
from sqlalchemy import Column, Integer, String, DateTime, Unicode, PickleType, Boolean

from pieobject.database import SQLABase, Session
from pieconfig.paths import ROOT_MAP
from pieconfig.globals import DEBUG

class PieWebsite(SQLABase):
    '''A class for information about library and project folders'''
    __tablename__ = 'piewebsites'

    id = Column(Integer, primary_key=True)

    SiteName = Column(Unicode)
    Domain = Column(Unicode)
    CMSType = Column(Unicode)
    DefaultAuthor = Column(Unicode)
    DefaultAuthorIsCorporate = Column(Boolean)
    
def add_website(url, 
                defaultauthor,
                authiscorporate=False,
                name='',
                cmstype='CMSnormal'):
    session = Session()
    umatch = lookup_website(url)
    if umatch:
        # update website info 
        umatch.DefaultAuthor = defaultauthor
        umatch.CMSType = cmstype
    else:
        # create website info entry
        ws = PieWebsite(
            Domain=urlparse.urlsplit(url)[1],
            SiteName=name,
            CMSType=cmstype,
            DefaultAuthor=defaultauthor,
            DefaultAuthorIsCorporate=authiscorporate)
        session.add(ws)
    session.commit()

def lookup_website(url):
    domain = urlparse.urlsplit(url)[1]
    session = Session()
    lookup = session.query(
        PieWebsite.filter(PieWebsite.Domain==domain))
    if len(lookup) > 0:
        return lookup[1]
    else:
        return None

def get_authorlist():
    '''Get list of default authors known to the database'''
    session = Session()
    query = session.query(PieWebsite).order_by(PieWebsite.DefaultAuthor)
    return [pw.DefaultAuthor for pw in query]

def lookup_author(authorname):
    pass
    

# DEBUG STUFF

if DEBUG:
    pass
    

# (c) Raif Sarcich, GPLv3, 2012

# DB object for storing information about websites

import sys, os, os.path, datetime
import urlparse
from sqlalchemy import Column, Integer, String, DateTime, Unicode, PickleType, Boolean

from pieobject.database import SQLABase, Session
from pieconfig.paths import ROOT_MAP
from pieconfig.globals import DEBUG

session = Session()

class PieWebsite(SQLABase):
    '''A class for information about library and project folders'''
    __tablename__ = 'piewebsites'

    id = Column(Integer, primary_key=True)

    SiteName = Column(Unicode)
    Domain = Column(Unicode)
    CMSType = Column(Unicode)
    DefaultAuthor = Column(Unicode)
    DefaultAuthorIsCorporate = Column(Boolean)
    TagAppendBehaviour = Column(Integer)

    def __repr__(self):
        return '<class PieWebsite domain==%s>' % self.Domain


def validify_url(url):
    '''urlparse is strict about the // delimiter preceding a
    netloc, but we want to be looser and accept 'www.thing.com' as
    valid'''
    if not '//' in url[:8]:
        return 'http://%s' % url
    else:
        return url

def add_website(url, 
                defaultauthor,
                authiscorporate=False,
                name='',
                tag_append_behaviour=0,
                cmstype='CMSnormal'):
    '''Add a website to the historical store of websites'''
    # session = Session()
    umatch = lookup_website(url)
    if umatch:
        # update website info 
        umatch.DefaultAuthor = defaultauthor
        umatch.DefaultAuthorIsCorporate = authiscorporate
        umatch.CMSType = cmstype
    else:
        # create website info entry
        ws = PieWebsite(
            Domain=urlparse.urlsplit(validify_url(url))[1],
            SiteName=name,
            CMSType=cmstype,
            DefaultAuthor=defaultauthor,
            DefaultAuthorIsCorporate=authiscorporate,
            TagAppendBehaviour=tag_append_behaviour)
        session.add(ws)
        print 'Added:', ws
    session.commit()

def lookup_website(url):
    '''Is this website already stored?'''
    domain = urlparse.urlsplit(validify_url(url))[1]
    # if not session:
    #     session = Session()
    lookup = session.query(
        PieWebsite).filter(PieWebsite.Domain==domain)
    numrtd = session.query(
        PieWebsite).filter(PieWebsite.Domain==domain).count()
    if numrtd > 0:
        print '_#_#_#_ Website found:', url, lookup[0]
        return lookup[0]
    else:
        return None

def get_authorlist():
    '''Get list of default authors known to the database'''
    # session = Session()
    query = session.query(PieWebsite).order_by(PieWebsite.DefaultAuthor)
    return [pw.DefaultAuthor for pw in query]

def lookup_author(authorname):
    pass
    

# DEBUG STUFF

spoofurls = ('http://www.politics.com/', 'www.sex.org', 'www.drugs.co.uk', 'rocknroll.net/', 'religion.eu', 'http://www.aer.gov.au')
spoofauthors = ('POLTX', 'Funbags inc.', 'Spliffco', 'Drummer From Def Leppard', 'Kings of Eyore', 'Australian Energy Regulator')

def make_spoof_websites():
    for i in range(len(spoofurls)):
        add_website(
            url=spoofurls[i],
            defaultauthor=spoofauthors[i],
            authiscorporate=True)
    print '___ Authors:', get_authorlist()
    
#GPLv3 Raif Sarcich 2011
# (c) Raif Sarcich, GPLv3, 2012

# DB object for storing information about websites

import sys, os, os.path, datetime
from sqlalchemy import Column, Integer, String, DateTime, Unicode, PickleType, Boolean
from sqlalchemy import Table, Text, ForeignKey

print 'PIEDB working dir:', os.getcwd()

from pieconfig.paths import ROOT_MAP
from pieconfig.globalvars import DEBUG
from piedb import SQLABase, Session, session

# session = Session()

def get_tag(t):
    assert type(t) in (str, unicode)
    q = session.query(PieTag).filter(PieTag.TagName == t).all()
    if len(q) == 0: 
        raise ValueError, 'Tag %s does not exist' % t
    else:
        return q[0]

def tag_exists(t):
    # session = Session()
    q = session.query(PieTag).filter(PieTag.TagName == t).all()
    if q: return True
    return False

def fn_add_tag(tag):
    # session = Session()
    g = PieTag(tag)
    session.add(g)
    session.commit()
    return g

class TagHandler:
    '''tag functionality'''
    
    def __init__(self):
        pass

    def add_tag(self, tag):
        assert type(tag) in (unicode, str)
        pietag = get_tag(tag)
        self.tags.append(pietag)
        # if tag_exists(tag):
        #     self.tags.append(PieTag(tag))
        # else:
        #     g = fn_add_tag(tag)
        #     self.tags.append(g)

    def add_tags(self, tags):
        '''Add to list of tags. Argument must be a list of strings'''
        for tag in tags:
            self.add_tag(tag)

    def remove_tag(self, tagname):
        raise NotImplemented, 'Tag removal yet to be implemented'

pieobject_tags = Table(
    'pieobject_tags', SQLABase.metadata,
    Column('pieobject_id', Integer, ForeignKey('pieobjects.id')),
    Column('pietags_id', Integer, ForeignKey('pietags.id'))
    )

class PieTag(SQLABase):
    '''A class for information about tags'''
    __tablename__ = 'pietags'
    
    id = Column(Integer, primary_key=True)
    TagName = Column(Unicode)

    def __init__(self, tagname):
        self.TagName = tagname

    def __repr__(self):
        return self.TagName

    def __str__(self):
        return str(self.TagName)

    def __unicode__(self):
        return unicode(self.TagName)

def init_tags():
    '''Insert initial tags'''
    fn_add_tag('Submissions')
    fn_add_tag('Presentations')
    fn_add_tag('Secretarial')
    fn_add_tag('Test')
    fn_add_tag('Foo')
    fn_add_tag('Bar')

# if DEBUG:
#     init_tags()

#GPLv3 Raif Sarcich 2011
# (c) Raif Sarcich, GPLv3, 2012

# DB object for storing information about websites

import sys, os, os.path, datetime
from sqlalchemy import Column, Integer, String, DateTime, Unicode, PickleType, Boolean
from sqlalchemy import Table, Text, ForeignKey

print 'PIEDB working dir:', os.getcwd()

from pieberry.pieconfig.paths import ROOT_MAP
from pieberry.pieconfig.globalvars import DEBUG
from pieberry.piedb import SQLABase, Session, session

def gen_tag_lookup():
    global ALL_TAGS
    ALL_TAGS = {}
    q = session.query(PieTag)
    for tag in q:
        ALL_TAGS[tag.TagName] = tag

# session = Session()

def get_tag(t, threadsess=None):
    '''Get a tag (assumed to exist) in the tag table'''
    # TODO - tags are totally fuxxored
    raise ValueError, 'Tag %s does not exist' % t


    # assert type(t) in (str, unicode)
    # if not ALL_TAGS.has_key(t):
    #     raise KeyError, 'Tag %s does not exist' % t
    # return ALL_TAGS[t]

    # if threadsess: mysess = threadsess
    # else: mysess = session
    # q = mysess.query(PieTag).filter(PieTag.TagName == t).all()
    # if len(q) == 0: 
    #     raise ValueError, 'Tag %s does not exist' % t
    # else:
    #     # these operations somehow stop sqlalchemy panicking at having
    #     # more than one instance of the same object in the same
    #     # session.
    #     r = q[0]
    #     r = mysess.merge(r)
    #     return r

def tag_exists(t):
    q = session.query(PieTag).filter(PieTag.TagName == t).all()
    if q: return True
    return False

def fn_add_tag(tag):
    g = PieTag(tag)
    session.add(g)
    session.commit()
    return g

class TagHandler:
    '''tag functionality'''
    
    def __init__(self):
        pass

    def add_tag(self, tag, threadsess=None):
        assert type(tag) in (unicode, str)
        pietag = get_tag(tag, threadsess)
        self.tags.append(pietag)
        # if tag_exists(tag):
        #     self.tags.append(PieTag(tag))
        # else:
        #     g = fn_add_tag(tag)
        #     self.tags.append(g)

    def add_tags(self, tags, threaded=False):
        '''Add to list of tags. Argument must be a list of strings, if
        threaded, will generate own session for the transaction'''
        if threaded:
            threadsess = Session()
        for tag in tags:
            if threaded:
                try:
                    self.add_tag(tag, threadsess)
                except Exception, exc:
                    print 'Could not add tag %s, %s' % (tag, exc)
            else:
                try:
                    self.add_tag(tag)
                except Exception, exc:
                    print 'Could not add tag %s, %s' % (tag, exc)


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
    print 'ADDING INITIAL TAGS'
    fn_add_tag('Submissions')
    fn_add_tag('Presentations')
    fn_add_tag('Secretarial')
    fn_add_tag('Test')
    fn_add_tag('Foo')
    fn_add_tag('Bar')
    session.expire_all()

# if DEBUG:
#     init_tags()

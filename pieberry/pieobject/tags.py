#GPLv3 Raif Sarcich 2011
# (c) Raif Sarcich, GPLv3, 2012

# DB object for storing information about websites

import sys, os, os.path, datetime
from sqlalchemy import Column, Integer, String, DateTime, Unicode, PickleType, Boolean
from sqlalchemy import Table, Text, ForeignKey

print 'PIEDB working dir:', os.getcwd()

from pieberry.pieconfig.globalvars import DEBUG
from pieberry.piedb import SQLABase, Session, session

def gen_tag_lookup():
    global ALL_TAGS
    ALL_TAGS = {}
    q = session.query(PieTag)
    for tag in q:
        ALL_TAGS[tag.TagName] = tag

# session = Session()

def get_tag(t):
    '''Get a tag (assumed to exist) in the tag table'''
    # TODO - tags are totally fuxxored
    assert type(t) in (str, unicode)
    if not ALL_TAGS.has_key(t):
        raise KeyError, 'Tag %s does not exist' % t
    return ALL_TAGS[t]

def get_all_tags():
    return ALL_TAGS

def tag_exists(t):
    q = session.query(PieTag).filter(PieTag.TagName == t).all()
    if q: return True
    return False

def fn_add_tag(tag):
    '''Contribute a novel tag to the db'''
    g = PieTag(tag)
    session.add(g)
    session.commit()
    gen_tag_lookup()
    return g

class TagHandler:
    '''tag functionality'''
    
    def __init__(self):
        self.tag_queue = []

    def add_tags_queued(self, *tagnames):
        '''takes arbitrary strings, to be processed at a convenient
        time into proper tag links (this is the thread-safe
        method). Call process_queued_tags later'''
        for it in tagnames:
            if not type(it) in (str, unicode):
                raise TypeError
            if not it in self.tag_queue:
                self.tag_queue.append(it)

    def get_queued_tags(self):
        return self.tag_queue
            
    def process_queued_tags(self):
        for it in self.tag_queue:
            self.add_tag(it)

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
        '''Add to list of tags. Argument must be a list of strings, if
        threaded, will generate own session for the transaction'''
        for tag in tags:
            try:
                self.add_tag(tag)
            except Exception, exc:
                print 'Could not add tag %s, %s' % (tag, exc)

    def remove_tag(self, tagname):
        raise NotImplemented, 'Tag removal yet to be implemented'

    def get_taglist(self):
        '''get list of tags as strings'''
        return [ t.TagName for t in self.tags ]

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
        return "<PieTag - %s>" % str(self.TagName)

    def __unicode__(self):
        return unicode(self.TagName)

def init_tags():
    '''Insert initial tags'''
    print 'ADDING INITIAL TAGS'
    fn_add_tag('Submissions')
    fn_add_tag('Presentations')
    fn_add_tag('Secretarial')
    session.expire_all()

# if DEBUG:
#     init_tags()

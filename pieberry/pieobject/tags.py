#GPLv3 Raif Sarcich 2011
# (c) Raif Sarcich, GPLv3, 2012

# DB object for storing information about websites

import sys, os, os.path, datetime
from sqlalchemy import Column, Integer, String, DateTime, Unicode, PickleType, Boolean
from sqlalchemy import Table, Text, ForeignKey

from pieobject.database import SQLABase, Session
from pieconfig.paths import ROOT_MAP
from pieconfig.globals import DEBUG

session = Session()

def tag_exists(t):
    q = session.query(PieTag).filter(PieTag.TagName == t).all()
    if q: return True
    return False

class TagHandler:
    '''tag functionality'''
    
    def __init__(self):
        pass

    def add_tag(self, tag):
        assert type(tag) in (unicode, str)
        if tag_exists(tag):
            self.tags.append(PieTag(tag))
        else:
            g = PieTag(tag)
            session.add(g)
            session.commit()
            self.tags.append(g)

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


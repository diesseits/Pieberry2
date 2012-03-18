import re, datetime, os

if __name__ == '__main__':
    import sys
    print sys.argv[1]

from pieberry.pieconfig.config import PIE_CONFIG
from pieberry.pieconfig.schemas import bibtexmap
from pieberry.pieobject import PieObject
from pieberry.pieutility.latex import escape_bad_latex_chars as eblc
from pieberry.pieutility.latex import unescape_bad_latex_chars as ublc
from pieberry.pieutility.bibtex import *

from pieberry.pieoutput.formatter import Formatter
from pybtex.database.input import bibtex
from pybtex.backends import latex, html, plaintext


re_corpname = re.compile(r'^\{(.+?)\}(.*)')

def pybtex_to_pieberry(key, ent):
    '''Transform pybtex Entry class to a PieObject'''
    obj = PieObject()
    modfields = {}
    for bkey, val in ent.fields.items():
        if bibtexmap.has_key(bkey):
            modfields[bibtexmap[bkey]] = ublc(val)
    obj.add_aspect_bibdata(**modfields)
    obj.BibData_Key = key
    if not ent.fields.has_key('title'):
        if ent.fields.has_key('booktitle'):
            obj.title = ublc(ent.items['booktitle'])
        else:
            raise ValueError, 'No title in this entry'
    for persons in ent.persons.itervalues():
        for person in persons:
            person.text = unicode(person)
    formatter = Formatter()
    formatted_names = formatter.format_people(ent)
    rendered_names = formatted_names.render(plaintext.Backend()).rstrip('.')
    corpnamehere = re_corpname.match(rendered_names)
    if not ent.fields.has_key('year'):
        raise Exception, "No valid date for this item"
    if not ent.fields.has_key('month'):
        ent.fields['month'] = 'January'
    datestr = '01 %s %s' % (ent.fields['month'], ent.fields['year'])
    obj.BibData_DatePublished = datetime.datetime.strptime(datestr, '%d %B %Y')
    if corpnamehere:
        rendered_names = '%s%s' % (corpnamehere.group(1), corpnamehere.group(2))
        obj.corpauthor = rendered_names
    else:
        obj.author = rendered_names
    obj.BibData_Type = ent.type
    return obj


def pybtex_entries_from_file(filename):
    parser = bibtex.Parser(encoding='utf-8')
    bib_data = parser.parse_file(filename)
    return bib_data.entries

def read_from_file(fileloc):
    '''Read PieObjects from a bibtex file'''
    data = pybtex_entries_from_file(fileloc)
    print data


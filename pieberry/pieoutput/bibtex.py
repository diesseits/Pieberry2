import datetime

from pieconfig import PIE_CONFIG
from pieconfig.schemas import bibtexmap

from pieutility.latex import escape_bad_latex_chars as eblc
from pieutility.latex import unescape_bad_latex_chars as ublc
from pieutility.bibtex import *

from pieoutput.formatter import Formatter

from pybtex.richtext import Text, Tag
from pybtex.backends import latex, html, plaintext
from pybtex.bibtex.utils import split_name_list
from pybtex.core import Entry, Person
from StringIO import StringIO


re_href = re.compile(r'\\href\{(.+?)\}\{(.+?)\}')
re_corpname = re.compile(r'^\{(.+?)\}(.*)')
re_dateprefix = re.compile(r'^[12][0-9]{3}[01][0-9][0123][0-9]')

def get_pybtex_object(obj):
    '''convert from PieObject to a pybtex Entry'''

    if not obj.BibData_Type: 
        raise KeyError, 'Necessary fields missing - BibTeX type'

    pybtex_entry = Entry(obj.BibData_Type.lower())
    
    for btkey, objfield in bibtexmap.items():
        if btkey == 'author':
            if obj.AuthorIsCorporate():
                pybtex_entry.add_person(Person('{%s}' % obj.Author()), btkey)
            else:
                for name in split_name_list(obj.Author()):
                    pybtex_entry.add_person(Person(name), btkey)
            continue
        elif btkey == 'editor':
            if not getattr(obj, objfield): continue
            for name in split_name_list(getattr(obj, objfield)):
                pybtex_entry.add_person(Person(name), btkey)
            continue 
        elif btkey == 'title':
            pybtex_entry.fields[btkey] = obj.Title()
            continue
        else:
            if not getattr(obj, objfield): continue
            pybtex_entry.fields[btkey] = getattr(obj, bibtexmap[btkey])
    pybtex_entry.fields['month'] = obj.ReferDate().strftime('%B')
    pybtex_entry.fields['year'] = obj.ReferDate().strftime('%Y')

    return pybtex_entry


# def get_formatted_citation_from_bibtex(bibtex_entry):
#     parser = bibtex.Parser(encoding='utf-8')
#     f = open(os.path.join(sysdir, 'temp.bib'), 'w')
#     f.write(bibtex_entry)
#     f.close()
#     bib_data = parser.parse_file(os.path.join(sysdir, 'temp.bib'))
#     e = bib_data.entries[bib_data.entries.keys()[0]]
#     return get_formatted_citation(e)

def get_formatted_citation(e, key='k', format='html'):
    '''Return a string containing a formatted citation for a given
    _PybTeX_ entry (not a PieObject)'''
    formatter = Formatter()
    ents = ((key, e),)
    formatted_data = formatter.format_entries(ents)
    for d in formatted_data:
        if format == 'html':
            rendered_data = d.text.render(html.Writer())
        else:
            rendered_data = d.text.render(plaintext.Writer())
    # get hrefs in order
    href_search = re_href.search(rendered_data)
    output_data = None
    if format == 'html':
        if e.fields.has_key('url'):
            output_data = rendered_data.replace(
                e.fields['howpublished'], 
                '<a href="%s">%s</a>' % (
                    ublc(e.fields['url']), 
                    e.fields['howpublished']
                    )
                )
    elif format == 'plaintext':
        pass #nothing to be done in this case
    elif format == 'urlplaintext':
        if e.fields.has_key('url'):
            output_data = '%s\n%s' % (
                rendered_data,
                e.fields['url']
                )
    elif format == 'org':
        if e.fields.has_key('url'):
            output_data = rendered_data.replace(
                e.fields['howpublished'],
                '[[%s][%s]]' % (
                    ublc(e.fields['url']),
                    e.fields['howpublished']
                    )
                )
    else:
        raise Exception, 'Invalid format request'
    if not output_data: 
        output_data = rendered_data
    #obliterate curly brackets
    transtbl = {ord('{'): None, ord('}'): None}
    output_data = output_data.translate(transtbl)
    return output_data

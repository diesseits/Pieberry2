import datetime, os.path, shutil, traceback

from pieberry.pieconfig.config import PIE_CONFIG
from pieberry.pieconfig.schemas import bibtexmap

from pieberry.pieutility.latex import escape_bad_latex_chars as eblc
from pieberry.pieutility.latex import unescape_bad_latex_chars as ublc
from pieberry.pieutility.bibtex import *

from pieberry.pieoutput.formatter import Formatter

from pybtex.richtext import Text, Tag
from pybtex.backends import latex, html, plaintext
from pybtex.bibtex.utils import split_name_list
from pybtex.database.input import bibtex
from pybtex.database.output.bibtex import Writer
from pybtex.database import BibliographyDataError
from pybtex.core import Entry, Person

re_href = re.compile(r'\\href\{(.+?)\}\{(.+?)\}')
re_corpname = re.compile(r'^\{(.+?)\}(.*)')
re_dateprefix = re.compile(r'^[12][0-9]{3}[01][0-9][0123][0-9]')

def get_pybtex_object(obj, texify=False):
    '''convert from PieObject to a pybtex Entry'''
    def f_(text):
        if type(text) in (str, unicode):
            if texify:
                return eblc(text)
            else:
                return text
        else: #this ain't text, don't touch it
            return text

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
            pybtex_entry.fields[btkey] = f_(obj.Title())
            continue
        elif btkey == 'url':
            pybtex_entry.fields[btkey] = f_(obj.Url())
            continue
        elif btkey in ('bttype', 'pie_corpauthor'):
            continue
        else:
            if not getattr(obj, objfield): continue
            pybtex_entry.fields[btkey] = f_(getattr(obj, bibtexmap[btkey]))
    pybtex_entry.fields['month'] = obj.ReferDate().strftime('%B')
    pybtex_entry.fields['year'] = obj.ReferDate().strftime('%Y')

    return pybtex_entry


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
        if e.fields.has_key('url') and e.fields.has_key('howpublished'):
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
        if e.fields.has_key('url') and e.fields.has_key('howpublished'):
            output_data = '%s\n%s' % (
                rendered_data,
                e.fields['url']
                )
    elif format == 'org':
        if e.fields.has_key('url') and e.fields.has_key('howpublished'):
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

class PiePybtexWriter:
    '''Class to write out bibliographies as BibTex'''
    def __init__(self):
        '''entries is a list of bibdata dicts'''
        self._entries = []
        self._location = PIE_CONFIG.get('Profile', 'bibliography_file')

    def addEntry(self, obj):
        '''Add an entry to the output file'''
        if not obj.BibData_Key:
            obj.BibData_Key = autogen_bibtex_key(obj)
        try:
            self._entries.append((obj.BibData_Key, 
                                  get_pybtex_object(obj, texify=True)))
        except Exception, exc:
            msg =  'warning - %s - could not output item %s - skipping' % (
                str(exc), obj.BibData_Key)
            print msg
            return msg

    def setPath(self, location):
        '''Set the location of the file'''
        self._location = location

    def write(self, backup=True):
        '''Write to file. 'types' is a tuple of "contexts" to exclude
        from the write-out process, such as submissions.'''
        if os.path.exists(self._location):
            try:
                # backup 
                f = open(self._location, 'r')
                if backup:
                    b = open(os.path.join(os.path.split(self._location)[0], 'backup.bib'), 'w')
                    b.write(f.read())
                    b.close()
                f.close()
            except:
                raise _('Could not open file')
        # wipe the file clean
        f = open(self._location, 'w')
        f.write('')
        f.close()
        # import additional pybtex modules

        parser = bibtex.Parser(encoding='utf-8')
        bib_object = parser.parse_file(self._location)

        for bib_key, ent in self._entries:
            bib_object.add_entry(bib_key, ent)

        writer = Writer(encoding='utf-8')
        try:
            writer.write_file(bib_object, self._location)
        except Exception, exc:
            traceback.print_exc()
            # restore backed up bibliography file
            shutil.copyfile(
                os.path.join(os.path.split(self._location)[0], 'backup.bib'), 
                self._location)
            raise IOError, _('Saving of the bibliography file failed,\nmost likely because of invalid data.')

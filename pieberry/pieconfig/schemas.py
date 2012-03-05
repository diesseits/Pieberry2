#GPLv3 Raif Sarcich 2011

import os

DOC_CONTEXTS = {
    'submissions': ['submission'],
    'appendices': ['appendix', 'attachment', 'annexure'],
    'media': ['media release', 'media statement', 'bulletin'],
    'etc': ['agenda'],
    'notices': ['notice']
    }

PROFILE_KEYS = (
    'workingdir', 
    'default_bibliography', 
    'default_bibtex_entry_type', 
    'default_bibtex_entry_style', 
    'default_bibtex_url_handling', 
    'export_tsv')


#map file extensions to internal generic types
FEXTENSIONS = {'pdf': ('.pdf',),
               'word_doc': ('.doc', '.docx', '.rtf', '.xls', '.xlsx', '.xlsm'),
               'html': ('.htm', '.html'),
               'plaintext': ('.txt', '.org'),
               'hachoir_other': ('.zip',)
               }

PIE_TYPES_DOCUMENTS = ('pdf', 'word_doc')
PIE_TYPES_ALL = ('pdf', 'word_doc', 'html', 'plaintext', 'hachoir_other')

#map mime types to internal generic types
MIMEMAP = {'application/pdf': 'pdf',
           'application/msword': 'word_doc',
           'application/vnd.ms-office': 'word_doc',
           'application/vnd.oasis.opendocument.presentation': 'word_doc',
           'application/vnd.oasis.opendocument.text': 'word_doc',
           'application/vnd.oasis.opendocument.spreadsheet': 'word_doc',
           'application/vnd.sun.xml.calc': 'word_doc',
           'application/vnd.sun.xml.writer': 'word_doc',
           'application/vnd.sun.xml.impress': 'word_doc',
           'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'word_doc',
           'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'word_doc',
           'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'word_doc',
           'application/vnd.ms-word.document.macroEnabled.12': 'word_doc',
           'application/vnd.ms-excel.sheet.macroEnabled.12': 'word_doc',
           'application/vnd.ms-excel': 'word_doc',
           'application/vnd.ms-powerpoint': 'word_doc',
           'application/rtf': 'word_doc',
           'text/html': 'html',
           'text/plain': 'plaintext',
           'application/x-empty': 'plaintext',
           'application/x-compressed': 'hachoir_other'}

def mime_map(mt):
    '''Util function to map file type to mime type'''
    if MIMEMAP.has_key(mt):
        return MIMEMAP[mt]
    else:
        return 'other'

# bibtexmap = (
#     ('author', 'author'),
#     ('title', 'title'),
#     # ('month', None),
#     # ('year', None),
#     ('editor', 'BibData_Editor'),
#     ('url', 'WebData_Url'),
#     ('journal', 'BibData_Journal'),
#     ('note', 'BibData_Note'),
#     ('annote', 'BibData_Annote'),
#     ('volume', 'BibData_Volume'),
#     ('pages', 'BibData_Pages'),
#     ('series', 'BibData_Series'),
#     ('type', 'BibData_Type'),
#     ('number', 'BibData_Number'),
#     ('institution', 'BibData_Institution'),
#     ('chapter', 'BibData_Chapter'),
#     ('address', 'BibData_Address'),
#     ('publisher', 'BibData_Publisher')
#     )


bibtexmap = {
    'author': 'author',
    'title': 'title',
    # 'month': None,
    # 'year': None,
    'editor': 'BibData_Editor',
    'url': 'WebData_Url',
    'journal': 'BibData_Journal',
    'note': 'BibData_Note',
    'annote': 'BibData_Annote',
    'volume': 'BibData_Volume',
    'pages': 'BibData_Pages',
    'series': 'BibData_Series',
    'bttype': 'BibData_Type',
    'number': 'BibData_Number',
    'key': 'BibData_ThesisKey',
    'type': 'BibData_ThesisType',
    'school': 'BibData_School',
    'institution': 'BibData_Institution',
    'booktitle': 'BibData_BookTitle',
    'chapter': 'BibData_Chapter',
    'address': 'BibData_Address',
    'publisher': 'BibData_Publisher',
    'howpublished': 'BibData_HowPublished',
    'pie_corpauthor': 'corpauthor', # non-BibTeX fields
    'pie_datepublished': 'BibData_DatePublished',
    'pie_bibdatakey': 'BibData_Key'
    }



bibtexfields = {
    'article': (
        ('journal',), 
        ('volume', 'number', 'pages', 'note', 'annote', 'url')
        ),
    'book': (
        ('publisher',), 
        ('editor', 'volume', 'number', 'series', 'address', 'edition', 
         'note', 'annote', 'url')
        ),
    'booklet': (
        ('howpublished',), 
        ('note', 'annote', 'url')
        ),
    'inbook': (
        ('editor', 'chapter', 'publisher'),
        ('volume', 'number', 'series', 'type', 'address', 'edition', 
         'pages', 'note', 'annote', 'url')
        ),
    'incollection': (
        ('booktitle',),
        ('pages', 'publisher', 'editor', 'volume', 'number', 'series', 
         'type', 'chapter', 'address', 'edition', 'note', 'annote', 'url'),
        ),
    'mastersthesis': (
        ('school',),
        ('key', 'type', 'address', 'note', 'annote')
        ),
    'misc': (
        ('howpublished',), 
        ('url', 'note', 'annote')
        ),
    'online': (
        ('howpublished', 'url'), 
        ('note', 'annote')
        ),
    'phdthesis': (
        ('school',),
        ('key', 'type', 'address', 'note', 'annote')
        ),
    'techreport': (
        ('institution',),
        ('type', 'number', 'address', 'note', 'annote', 'url')
        ),
    'unpublished': (
        ('note',),
        ('annote', 'url')
        ),
    }


silentfields = (
    'pdflink', 'pdflink_context', 'tag', 'outfilename', 'final_fn', 
    'download_time', 'creation_date_guessed', 'exclude', 'internal_author', 
    'internal_title')

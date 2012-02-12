#GPLv3 Raif Sarcich 2011

import os

DOC_CONTEXTS = {
    'submissions': ['submission'],
    'appendices': ['appendix', 'attachment', 'annexure'],
    'media': ['media release', 'media statement', 'bulletin'],
    'etc': ['agenda'],
    'notices': ['notice']
    }

ENTRY_TYPE_CHOICES = {0: '@Misc with url field', 
                      1: '@Misc with \url{} in howpublished',
                      2: '@Misc with \href{} in howpublished', 
                      3: '@Online (biblatex only)'
                      }

ENTRY_TYPE_KEYS = {0: 'Misc',
                   1: 'Misc',
                   2: 'Misc',
                   3: 'Online',
                   }

PROFILE_KEYS = (
    'workingdir', 
    'default_bibliography', 
    'default_bibtex_entry_type', 
    'default_bibtex_entry_style', 
    'default_bibtex_url_handling', 
    'export_tsv')

AT_example_struct = {
    'rpwg': {
        'title': ['rpwg', 'necf', 'customer framework', 'energy customer'],
        'author': [],
        },
    'npwg': {
        'title': ['npwg', 'connections', 'connection framework'],
        'author': []
        }
}


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
           'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'word_doc',
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
    'type': 'BibData_Type',
    'number': 'BibData_Number',
    'institution': 'BibData_Institution',
    'chapter': 'BibData_Chapter',
    'address': 'BibData_Address',
    'publisher': 'BibData_Publisher',
    'howpublished': 'BibData_HowPublished',
    'pie_corpauthor': 'corpauthor', # non-BibTeX fields
    'pie_datepublished': 'BibData_DatePublished'
    }



bibtexfields = {
    'article': (
        ('journal',), 
        ('volume', 'number', 'pages', 'note', 'annote')
        ),
    'book': (
        ('publisher',), 
        ('editor', 'volume', 'number', 'series', 'address', 'edition', 
         'note', 'annote')
        ),
    'misc': (
        ('howpublished',), 
        ('url', 'note', 'annote')
        ),
    'booklet': (
        ('howpublished',), 
        ('note', 'annote')
        ),
    'online': (
        ('howpublished', 'url'), 
        ('note', 'annote')
        ),
    'inbook': (
        ('editor', 'chapter', 'publisher'),
        ('volume', 'number', 'series', 'type', 'address', 'edition', 
         'pages', 'note', 'annote')
        ),
    'incollection': (
        ('booktitle',),
        ('pages', 'publisher', 'editor', 'volume', 'number', 'series', 
         'type', 'chapter', 'address', 'edition', 'note', 'annote'),
        ),
    'techreport': (
        ('institution',),
        ('type', 'number', 'address', 'note', 'annote')
        ),
    'unpublished': (
        ('note',),
        ('annote',)
        )
    }


silentfields = (
    'pdflink', 'pdflink_context', 'tag', 'outfilename', 'final_fn', 
    'download_time', 'creation_date_guessed', 'exclude', 'internal_author', 
    'internal_title')

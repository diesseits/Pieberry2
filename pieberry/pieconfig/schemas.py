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
               'plaintext': ('.txt', '.org')
               }

#map mime types to internal generic types
MIMEMAP = {'application/pdf': 'pdf',
           'application/msword': 'word_doc',
           'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'word_doc',
           'application/rtf': 'word_doc',
           'text/html': 'html',
           'text/plain': 'plaintext'}

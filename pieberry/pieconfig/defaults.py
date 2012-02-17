from paths import *

import os, sys, os.path

PIE_CONFIG_CATEGORIES = ('TheProfile', 'Profile', 'Format', 'Paths')

PIE_CONFIG_DEFAULTS = [
    # ('Profile', 'sweep_directory', os.getcwd()),
    # ('Profile', 'temp_directory', os.path.join(SYSDIR, 'tempfiles')),
    # ('Profile', 'filing_directory', os.getcwd()),
    ('TheProfile', 'current_profile', 'Default'),
    ('Profile', 'bibliography_file', 'library.bib'),
    # ('Profile', 'exclude_by_default', 'submissions'),
    ('Profile', 'desktopdir', DESKTOPDIR),
    ('Format', 'default_bibtex_entry_type', 'Misc'),
    ('Format', 'default_howpublished_text', 'On The Web'),
    # ('Profile', 'default_bibtex_entry_style', '0'),
    # ('Profile', 'default_bibtex_url_handling', 'href_howpublished'),
    # ('Profile', 'export_tsv', 'false'),
    ('Profile', 'export_bibtex', 'true'),
    # ('Format', 'url_level_scrape', 'full'),
    ('Format', 'url_level_represent', 'full'),
    ('Format', 'plaintext_citation_format', 'plaintext'),
    ('Format', 'richtext_citation_format', 'html'),
    ('Format', 'filesystem_length_limit', 255),
    ('Format', 'write_pdf_metadata', True)
    ]

PIE_PROFILE_KEYS = [y for x, y, z in PIE_CONFIG_DEFAULTS if x == 'Profile']

for key, path in default_paths_relative_to_root(os.getcwd()).items():
    if key == 'rootdir':
        PIE_CONFIG_DEFAULTS.append(('Profile', key, path))
    else:
        PIE_CONFIG_DEFAULTS.append(('Paths', key, path))
     

from paths import *

import os, sys, os.path

PIE_CONFIG_CATEGORIES = ('Profile', 'Format', 'Paths')

PIE_CONFIG_DEFAULTS = [
    # ('Profile', 'sweep_directory', os.getcwd()),
    # ('Profile', 'temp_directory', os.path.join(SYSDIR, 'tempfiles')),
    # ('Profile', 'filing_directory', os.getcwd()),
    # ('Profile', 'default_bibliography', os.path.join(SYSDIR, 'library.bib')),
    # ('Profile', 'exclude_by_default', 'submissions'),
    ('Format', 'default_bibtex_entry_type', 'Misc'),
    ('Format', 'default_howpublished_text', 'On The Web'),
    # ('Profile', 'default_bibtex_entry_style', '0'),
    # ('Profile', 'default_bibtex_url_handling', 'href_howpublished'),
    # ('Profile', 'export_tsv', 'false'),
    ('Profile', 'export_bibtex', 'true'),
    ('Profile', 'current_profile', 'Default'),
    # ('Format', 'url_level_scrape', 'full'),
    ('Format', 'url_level_represent', 'full'),
    ('Format', 'plaintext_citation_format', 'plaintext'),
    ('Format', 'richtext_citation_format', 'html'),
    ('Format', 'filesystem_length_limit', 80),
    ('Format', 'write_pdf_metadata', True)
    ]

for key, path in default_paths_relative_to_root(os.getcwd()).items():
    PIE_CONFIG_DEFAULTS.append(('Paths', key, path))
     

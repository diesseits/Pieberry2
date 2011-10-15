from paths import *

import os, sys

PIE_CONFIG_CATEGORIES = ('Profile', 'Format')

PIE_CONFIG_DEFAULTS = (
    ('Profile', 'workingdir', os.getcwd()),
    ('Profile', 'sweep_directory', os.getcwd()),
    ('Profile', 'temp_directory', os.path.join(SYSDIR, 'tempfiles')),
    ('Profile', 'filing_directory', os.getcwd()),
    ('Profile', 'default_bibliography', os.path.join(SYSDIR, 'library.bib')),
    ('Profile', 'exclude_by_default', 'submissions'),
    ('Profile', 'default_bibtex_entry_type', 'Misc'),
    ('Profile', 'default_bibtex_entry_style', '0'),
    ('Profile', 'default_bibtex_url_handling', 'href_howpublished'),
    ('Profile', 'export_tsv', 'false'),
    ('Profile', 'export_bibtex', 'true'),
    ('Profile', 'current_profile', 'Default'),
    ('Format', 'url_level_scrape', 'full'),
    ('Format', 'url_level_represent', 'full'),
    ('Format', 'plaintext_citation_format', 'plaintext'),
    )

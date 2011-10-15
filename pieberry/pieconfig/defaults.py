from paths import *

import os, sys

PIE_CONFIG_DEFAULTS = (
    ('PBoptions', 'workingdir', os.getcwd()),
    ('PBoptions', 'default_bibliography', os.path.join(SYSDIR, 'library.bib')),
    ('PBoptions', 'exclude_by_default', 'submissions'),
    ('PBoptions', 'default_bibtex_entry_type', 'Misc'),
    ('PBoptions', 'default_bibtex_entry_style', '0'),
    ('PBoptions', 'default_bibtex_url_handling', 'href_howpublished'),
    ('PBoptions', 'export_tsv', 'false'),
    ('PBoptions', 'current_profile', 'Default'),
    ('FMToptions', 'url_level_scrape'),
    ('FMToptions', 'url_level_scrape', 'full'),
    ('FMToptions', 'url_level_represent', 'full'),
    ('FMToptions', 'plaintext_citation_format', 'plaintext'),
    ('AToptions', 'sweep_directory', os.getcwd()),
    ('AToptions', 'temp_directory', os.path.join(SYSDIR, 'tempfiles'))
    ('AToptions',  'filing_directory', os.getcwd())
    ('AToptions', 'guess_filename', 'true')
    )

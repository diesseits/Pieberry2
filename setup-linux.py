#!/usr/bin/env python

from pieberry.pieconfig.identity import PIE_APPNAME, PIE_VERSION
from distutils.core import setup
from glob import glob
import os, sys, shutil

# Make data go into site-packages (http://tinyurl.com/site-pkg)
# from distutils.command.install import INSTALL_SCHEMES
# for scheme in INSTALL_SCHEMES.values():
#     scheme['data'] = scheme['purelib']

setup(name='pieberry-library-assistant',
      version=PIE_VERSION,
      install_requires = ['pyPdf', 
                          'BeautifulSoup', 
                          'pybtex', 
                          'hachoir_metadata'],
      description = 'The swiss army knife of the public servant. A program encompassing web scraping, cataloguing, filing, search, citation, organisation and archival functions.',
      author = "Raif Sarcich",
      author_email = "raifsarcich@gmail.com",
      url = "http://members.iinet.net.au/~raifsarcich/pieberry/",
      # py_modules=['docx'],
      # data_files=[
      #   ('pieberry/ui', glob('pieberry/ui/*.png')),
      #   ],
      packages = ['pieberry', 
                  'pieberry.pieobject',
                  'pieberry.atomise',
                  'pieberry.pieconfig',
                  'pieberry.piedb',
                  'pieberry.piefiles',
                  'pieberry.piemeta',
                  'pieberry.piemeta.read',
                  'pieberry.piemeta.write',
                  'pieberry.pieoutput',
                  'pieberry.piescrape',
                  'pieberry.piescrape.cms',
                  'pieberry.pieutility',
                  'pieberry.ui',
                  'pieberry.ui.listpanels',
                  'pieberry.piedb',
                  'pieberry.pieinput',
                  'pieberry.pdfrw'
                  ],
      # package_dir = {
      #   'pieberry': '.',
      #   },
      package_data = {
        'pieberry.ui': ['*.png', '*.ico'],
        },
      scripts = ['runpieberry',],
      )

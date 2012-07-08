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
                          'hachoir-core',
                          'hachoir-parser',
                          'hachoir-metadata',
                          'zbar',
                          'sqlalchemy'
                          'keyring',
                          'pycrypto'
                          'gdata'],
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
        'pieberry': ['*.desktop',],
        'pieberry.ui': ['*.png', '*.ico'],
        },
      scripts = ['runpieberry', 'pieberry-library-assistant'],
      )


if sys.argv[1] == 'install':
    shutil.copyfile('./pieberry/pieberry-library-assistant.desktop',
                    '/usr/share/applications/pieberry-library-assistant.desktop')
    shutil.copyfile('./pieberry/ui/pie_128.png',
                    '/usr/share/icons/hicolor/128x128/apps/pieberry.png')
    shutil.copyfile('./pieberry/ui/pie_48.png',
                    '/usr/share/icons/hicolor/48x48/apps/pieberry.png')
    shutil.copyfile('./pieberry/ui/pie_36.png',
                    '/usr/share/icons/hicolor/36x36/apps/pieberry.png')
    shutil.copyfile('./pieberry/ui/pie_22.png',
                    '/usr/share/icons/hicolor/22x22/apps/pieberry.png')
    shutil.copyfile('./pieberry/ui/pie_16.png',
                    '/usr/share/icons/hicolor/16x16/apps/pieberry.png')


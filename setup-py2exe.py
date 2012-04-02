#!/usr/bin/python
from distutils.core import setup
import os, sys, shutil
from pprint import pprint
from glob import glob
from pieberry.pieconfig.identity import PIE_APPNAME, PIE_VERSION


# Remove the build folder
shutil.rmtree("build", ignore_errors=True)

# do the same for dist folder
shutil.rmtree("dist", ignore_errors=True)

ics = [os.path.join('pieberry', 'ui', i) for i in os.listdir('pieberry/ui') if os.path.splitext(i)[1] == '.png']

try:
    import py2exe
    imfiles = ('.', ics)
    # origIsSystemDLL = py2exe.build_exe.isSystemDLL
    # def isSystemDLL(pathname):
    #     if os.path.basename(pathname).lower() in ("msvcp71.dll", "dwmapi.dll"):
    #         return 0
    #     return origIsSystemDLL(pathname)
    # py2exe.build_exe.isSystemDLL = isSystemDLL
except:
    imfiles = ('pieberry', ics)

manifest_x86 = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="5.0.0.0"
    processorArchitecture="x86"
    name="Pieberry"
    type="win32"
  />
  <description>Pieberry</description>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel
            level="asInvoker"
            uiAccess="false">
        </requestedExecutionLevel>
      </requestedPrivileges>
    </security>
  </trustInfo>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity
            type="win32"
            name="Microsoft.VC90.CRT"
            version="9.0.21022.8"
            processorArchitecture="x86"
            publicKeyToken="1fc8b3b9a1e18e3b">
      </assemblyIdentity>
    </dependentAssembly>
  </dependency>
  <dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="x86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
  </dependency>
</assembly>
"""

classifiers_x86=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Science/Research',
    'Environment :: Win32 (MS Windows)',
    'Environment :: X11 Applications :: GTK',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Natural Language :: English',
    'Programming Language :: Python :: 2.7',
    'Topic :: Text Processing :: Markup :: LaTeX',
    'Operating System :: OS Independent'
    ]

opts = {
    "py2exe": {
        "packages": ["pieberry",],
        "includes": ["BeautifulSoup", 
                     "pyPdf", 
                     "pieberry", 
                     "pybtex", 
                     "hachoir_metadata",
                     'sqlalchemy',
                     'sqlalchemy.dialects.sqlite',
                     'sqlite3',
                     'pdfrw',
                     'keyring',
                     ],
#        "dll_excludes": ["MSVCP90.dll"]
        }
    }

files=[
    ('pieberry/ui', ['pieberry/ui/pieberry.ico', 'pieberry/ui/pieberry32.ico']), 
    imfiles, 
    # ('pieberry', ['pieberry/help/manual.html', 'pieberry/help/pieberrymanual.hhp', 'pieberry/help/pieberrymanual_contents.hhc', 'pieberry/help/pieberrymanual_index.hhk'])
    ]

#redist visual c runtime dlls for py2exe
if sys.platform == 'win32':
    files.append(("Microsoft.VC90.CRT", (r'C:\Python27\msvcp90.dll', r'C:\Python27\msvcr90.dll', r'C:\Python27\msvcm90.dll', r'C:\Python27\Microsoft.VC90.CRT.manifest')))

setup(name = "pieberry-library-assistant",
      version = PIE_VERSION,
      description = 'The swiss army knife of the public servant. A program encompassing web scraping, cataloguing, filing, search, citation, organisation and archival functions.',
      author = "Raif Sarcich",
      author_email = "raifsarcich@gmail.com",
      url = "http://members.iinet.net.au/~raifsarcich/pieberry/",
      download_url = 'http://members.iinet.net.au/~raifsarcich/pieberry/',
      classifiers = classifiers_x86,
      license = 'GNU General public licence',
      #Name the folder where your packages live:
          #(If you have other packages (dirs) or modules (py files) then
      #put them into the package directory - they will be found 
      #recursively.)
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
                  'pieberry.pieinput'
                  ],
      #'package' package must contain files (see list above)
      #I called the package 'package' thus cleverly confusing the whole issue...
      #This dict maps the package name =to=> directories
      #It says, package *needs* these files.
      package_data = {'pieberry' : ['*.png'],
                      # 'pieberry': ['help/*.html', 
                      #              'help/*.hhp', 'help/*.hhc', 'help/*.hhk']
                      },
      install_requires = ['pyPdf', 'BeautifulSoup', 'pybtex', 'hachoir_metadata'],
      # data_files = [("pieberry", "pieberry/*.png"), (".", "*.png")],
      #'runner' is in the root.
      scripts = ["runpieberry", 'pieberry.pyw'],
      long_description = """PIEBERRY (IT'S FOR YOUR LIBRARY)

This is a program which I wrote to automate a painful aspect of my
work-life - downloading, storing, cataloguing and referencing
documents from (mainly public sector & government) websites.

These websites publish reams of documents in pdf format, usually in a
random range of cryptic CMS-generated filename schemas, with
incomplete or non-existent file metadata. 

Typically I download these, rename them with an intelligible title, a
six-digit archival date prefix, store then in an appropriate folder,
and enter them into my database of reference materials for use with
LaTeX/BibTex.

Actually, scratch that. What I REALLY do is download them, leave them
on my Desktop folder, look at them once, forget them, fill up my disk
quota, delete them, realise I've lost them and download them all over
again.

Hence, Pieberry, which will do all of the good and none of the bad
described above.

It's mainly for my use, but I hope that someone else will find it
useful. I'm open to requests for features.

It's written in Python, with the PortablePython 2.5.4 distribution
(which contains wxpython) in mind, but also requires Beautiful Soup,
pyPdf and Pybtex, which are all available through easy_install from
setuptools.""",
      windows = [{
            "script": 'pieberry.pyw',
            #"console": 'pieberrydm.pyw',
            "icon_resources": [(0, 'pieberry/ui/pieberry.ico')],
            "other_resources": [(24, 1, manifest_x86)]
            }],
      data_files=files,#[('.', ['pieberry.ico', 'pieberry32.ico']),('pieberry',ics)],
      options = opts
    #
    #This next part it for the Cheese Shop, look a little down the page.
    #classifiers = []     
) 

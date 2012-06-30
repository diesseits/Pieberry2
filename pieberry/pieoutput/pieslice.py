# Export a glob of data called a pieslice, which bundles up available
# informationabout a document including it's file, bibliographic info,
# notes, etc into a zip file for easy import/export.
import zipfile
import os, os.path

from pieberry.pieobject import PieObject
from pieberry.pieobject.paths import suggest_path_slice_name
from pieberry.pieconfig.paths import CACHEDIR
from pieberry.pieoutput.bibtex import PiePybtexWriter

# Zipfile contents:
# - info.bib - bibtex file with bibliographic info
# - notes.xml - notes in wx xml format
# - corefile.txt - name of core file in a plain text file
# - [the core file, if relevant] the actual file referred to

# ensure there's a working subdir:
if not os.path.isdir(os.path.join(CACHEDIR, 'PieSlices')):
    os.makedirs(os.path.join(CACHEDIR, 'PieSlices'))
SLICEDIR = os.path.join(CACHEDIR, 'PieSlices')
# empty it out to prevent disk space wastage:
fls = [os.path.join(SLICEDIR, fl) for fl in os.listdir(SLICEDIR) if os.path.isfile(os.path.join(SLICEDIR, fl))]
for fl in fls:
    try: 
        os.remove(fl)
        print 'removing file - %s' % fl
    except:
        print 'file locked - %s' % fl
# TODO


class PieSlice:
    '''An object that translates between PieObjects and slices of
    pie'''
    def __init__(self, obj=None, slicepath=None):
        self._filemade = None
        if obj and slicepath: raise Exception, 'Not both!'
        if obj: self.SetObject(obj)
        elif slicepath: self.SetSlice(slicepath)

    def SetSlice(self, slicepath):
        '''Instantiate the slice by an existing slice on disk'''
        if not os.path.splitext(slicepath)[1] == '.pieslice':
            raise IOError, 'This does not appear to be a valid pieslice'
        pzipfile = zipfile.ZipFile(slicepath, 'r')
        contents = pzipfile.namelist()
        if not 'info.bib' in contents:
            raise AttributeError, 'Vital information missing'
        self._filemade = slicepath
        print 'set filemade:', slicepath

    def SetObject(self, obj):
        '''Instantiate the slice by an object in the database'''
        if not obj.has_aspect('bibdata'):
            raise AttributeError, 'Can only export objects with biblio info'
        self._obj = obj

    def _make(self):
        '''Make the object into a PieSlice file in the cache'''
        # decide on a file name for the slice
        slicepath = suggest_path_slice_name(self._obj)
        pzipfile = zipfile.ZipFile(slicepath, 'w')
        # if there is a file, first write its name to a string in the
        # zip
        if self._obj.has_aspect('hasfile'):
            pzipfile.writestr(
                'corefile.txt', 
                self._obj.FileData_FileName.encode('utf8'))
            # now copy the file itself to the archive
            pzipfile.write(
                self._obj.FileData_FullPath,
                self._obj.FileData_FileName
                )
        # write the bibliographic info to a bibtex file
        if self._obj.has_aspect('bibdata'):
            writer = PiePybtexWriter()
            writer.setPath(os.path.join(SLICEDIR, 'temp.bib'))
            writer.addEntry(self._obj)
            writer.write(backup=True)
            pzipfile.write(os.path.join(SLICEDIR, 'temp.bib'), 'info.bib')
        # if the object has notes made against it, include these
        if self._obj.notes:
            pzipfile.writestr('notes.xml', self._obj.notes)
        pzipfile.close()
        self._filemade = slicepath

    def HasFile(self):
        '''Return true if a core file is contained in the slice'''
        if not self._filemade: raise Exception, 'PieSlice not yet made'
        with zipfile.ZipFile(self._filemade, 'r') as pzipfile:
            if 'corefile.txt' in pzipfile.namelist():
                return True
            else:
                return False

    def GetFileName(self):
        '''Get the core filename'''
        if not self._filemade: raise Exception, 'PieSlice not yet made'
        with zipfile.ZipFile(self._filemade, 'r') as pzipfile:
            if 'corefile.txt' in pzipfile.namelist():
                return pzipfile.read('corefile.txt').decode('utf8')
            else:
                return None

    def ExtractFile(self, location):
        '''Extract the file contained in the slice to a given
        location'''
        if not self._filemade: raise IOError, 'No file to use'
        with zipfile.ZipFile(self._filemade, 'r') as pzipfile:
            if not 'corefile.txt' in pzipfile.namelist():
                return None
            fn = pzipfile.read('corefile.txt').decode('utf8')
            pzipfile.extract(fn, location)
            return os.path.join(location, fn)

    def ExtractNotes(self):
        '''Get the notes as a string'''
        with zipfile.ZipFile(self._filemade, 'r') as pzipfile:
            if 'notes.xml' in pzipfile.namelist():
                return pzipfile.read('notes.xml').decode('utf8')
            else: return None

    def ExtractBib(self):
        '''Return the temporary location of a file containing the
        bibtex data for the pieslice'''
        print 'filemade:', self._filemade
        with zipfile.ZipFile(self._filemade, 'r') as pzipfile:
            if not 'info.bib' in pzipfile.namelist():
                raise AttributeError, 'Missing vital data'
            pzipfile.extract('info.bib', SLICEDIR)
            return os.path.join(SLICEDIR, 'info.bib')

    def GetSlice(self):
        '''Get the slice file'''
        if self._filemade: 
            return self._filemade
        else:
            self._make()
            return self._filemade

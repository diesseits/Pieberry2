import mimetypes
from pieberry.pieconfig.schemas import FEXTENSIONS

try:
    import magic
    USE_MAGIC = True
except:
    USE_MAGIC = False

from pieberry.pieconfig.schemas import mime_map

# def redo_fext_guess(fn):
#     for 

def determine_file_type(fn):
    mtype = None
    if USE_MAGIC:
        m = magic.open(magic.MAGIC_MIME)
        m.load()
        mtype = m.file(fn).split(';')[0]
    # This is an alternative libmagic interface:
    # mime = magic.Magic(mime=True)
    # mtype = mime.from_file(self.FileData_FullPath)
    if not mtype:
        mtype = mimetypes.guess_type(fn)[0]
    if not mtype:
        raise Exception, "Could not determine mime type of file"
    print 'Found mime type -', mtype
    return mime_map(mtype)
    

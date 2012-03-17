import mimetypes, os, os.path
from pieberry.pieconfig.schemas import FEXTENSIONS
from hachoir_core.cmd_line import unicodeFilename
from hachoir_core.i18n import getTerminalCharset, _

try:
    import magic
    USE_MAGIC = True
except:
    USE_MAGIC = False

from pieberry.pieconfig.schemas import mime_map

# def redo_fext_guess(fn):
#     for 

def determine_file_type(fn):
    print 'TYPE', type(fn)
    assert type(fn) == unicode
    # if type(fn) == unicode:
    #     fn = fn.encode(getTerminalCharset())
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
    if (not mtype) or (mtype == 'application/zip'):
        # this is to override the fact that python's mimetype library
        # can't seem to find the correct type for docx files. it is a
        # hack. get over it.
        if os.path.splitext(fn)[1].lower() in FEXTENSIONS['oxml_doc']:
            return 'oxml_doc'
        if os.path.splitext(fn)[1].lower() in FEXTENSIONS['odf_doc']:
            return 'odf_doc'
    if not mtype:
        raise Exception, "Could not determine mime type of file"
    print 'File: %s' % fn
    print 'Found mime type -', mtype
    return mime_map(mtype)
    

import mimetypes, magic
from pieconfig.schemas import mime_map

def determine_file_type(fn):
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
    

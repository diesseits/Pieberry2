import traceback, datetime, os.path
from pieconfig.paths import SYSDIR

from pdfrw import PdfReader
from fake import get_fake_metadata_object

def pdfrw_object(fn):
    '''hachoir doesn't do pdf'''
    fakeobj = get_fake_metadata_object(fn)
    try:
        reader = PdfReader(fn)
    except Exception, exc:
        traceback.print_exc(file=open(os.path.join(SYSDIR, 'dbgop'), 'w'))
        return None
        # assert len(reader.Info.CreationDate) > 0
    if reader.Info.CreationDate:
        cd = reader.Info.CreationDate.split(':')[1] #get the 'good' bit 
        # md = reader.Info.ModDate.split(':')[1]
        creation_date = datetime.datetime.strptime("%s %s %s %s %s" % (
                cd[0:4], cd[4:6], cd[6:8], cd[8:10], cd[10:12]
                ), "%Y %m %d %H %M")
    else:
        creation_date = fakeobj.FileData_DateCreated
    if reader.Info.Author:
        author = unicode(
            reader.Info.Author, 'utf8', errors=U_ERROR_BEHAV).strip('()')
    else: author = u''
    if reader.Info.Title:
        title = unicode(
            reader.Info.Title, 'utf8', errors=U_ERROR_BEHAV).strip('()')
    else: title = u''
    obj = PieObject(
        title = title,
        author = author,
        date = creation_date)
    obj.FileData_DateCreated = creation_date
    return obj

def pdfrw_metadata(fn):
    reader = PdfReader(fn)
        # assert len(reader.Info.CreationDate) > 0
    cd = reader.Info.CreationDate.split(':')[1] #get the 'good' bit 
        # md = reader.Info.ModDate.split(':')[1]
    creation_date = datetime.datetime.strptime("%s %s %s %s %s" % (
            cd[0:4], cd[4:6], cd[6:8], cd[8:10], cd[10:12]
            ), "%Y %m %d %H %M")
    return {
        'author': unicode(reader.Info.Author, 'utf8', errors=U_ERROR_BEHAV),
        'title': unicode(reader.Info.Title, 'utf8', errors=U_ERROR_BEHAV),
        'creation_date': creation_date,
        'metadata_is_replaceable': True
        }

def scan_file_metadata(obj):
    if obj.FileData_FileType == 'pdf':
        print 'Reading', obj.FileData_FullPath
        return pdfrw_metadata(obj.FileData_FullPath)
    else:
        print 'Unknown file type'
        return {}

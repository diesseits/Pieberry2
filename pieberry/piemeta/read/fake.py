import os, os.path, datetime, re

from pieberry.pieobject import PieObject

re_dateprefix = re.compile(r'^[12][0-9]{3}[01][0-9][0123][0-9]')

def get_fake_metadata(fn):
    m = re_dateprefix.match(os.path.basename(fn))
    if m:
        # if it has a date prefix already, use that to infer the relevant
        # date of the file
        dateprefix = m.group(0)
        ftime = '%s %s %s' % (dateprefix[0:4], dateprefix[4:6], dateprefix[6:8])
        cdate = datetime.datetime.strptime(ftime, '%Y %m %d')
        ttl = path.splitext(os.path.basename(fn))[0][8:].lstrip(' -')
    else:
        # if no date prefix, use os.stat to infer the date of the file
        ttl = os.path.splitext(os.path.basename(fn))[0]
        cdate = datetime.datetime.fromtimestamp(os.stat(fn)[9])
    mdate = datetime.datetime.fromtimestamp(os.stat(fn)[8])
    r = {
        'creation_date': cdate,
        'creation_date_guessed': True,
        'modification_date': mdate,
        'title': ttl,
        'author': ''
        }
    return r

def get_fake_metadata_for_aspect(obj):
    return get_fake_metadata(obj.FileData_FullPath)
    
def get_fake_metadata_object(fn):
    '''get object with metadata gleaned only from the file system
    takes a full path'''
    d = get_fake_metadata(fn)
    obj = PieObject(
        title = d['title'],
        date = d['creation_date'])
    obj.FileData_DateCreated = d['creation_date']
    obj.FileData_DateModified = d['modification_date']
    return obj

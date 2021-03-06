import datetime, string, random, sys
import shutil, os

from pieberry.pieconfig.paths import CACHEDIR
from pieberry.pieobject.paths import auto_increment_fn
from pieberry.pieconfig.globalvars import DEBUG
import hachoir_metadata
from pieberry.piemeta.read.atomise_hachoir import processFileReturn
from pieberry.piemeta.read.fake import get_fake_metadata_object
from pieberry.pieobject.diagnostic import determine_file_type

def get_real_metadata_object(fn):
    '''get object with metadata gleaned from internal file metadata'''
    #TODO: workaround for file locking bug
    if sys.platform == 'win32':
        newfn = os.path.join(CACHEDIR, 'Workaround', os.path.basename(fn))
        if os.path.isfile(newfn):
            newfn = auto_increment_fn(newfn)
        shutil.copyfile(fn, newfn)
        fn = newfn
    obj = get_fake_metadata_object(fn)
    d = get_real_metadata(fn)
    if not d: return obj
    obj.author = d['author']
    obj.title = d['title']
    obj.date = d['creation_date']
    obj.FileData_DateCreated = d['creation_date']
    obj.FileData_DateModified = d['modification_date']
    obj.FileData_FileType = determine_file_type(fn)
    obj.FileData_FileName = os.path.basename(fn)
    return obj

def get_real_metadata_for_aspect(obj):
    return get_real_metadata(obj.FileData_FullPath)

def get_real_metadata(fn):
    raw_meta = processFileReturn(fn)
    if not raw_meta: return None
    r_title = string.join(
        [i[8:].strip() for i in raw_meta if i[:8] == '- Title:'], u' - ')

    mod_time = datetime.datetime.fromtimestamp(os.stat(fn)[8])
    for i in raw_meta: # go by modification not creation
        if i[:21] == '- Last modification: ':
            try:
                mod_time = datetime.datetime.strptime(
                    i[21:], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                print 'Could not parse time'
            break

    cr_time = datetime.datetime.fromtimestamp(os.stat(fn)[9])
    c_guessed = True
    for i in raw_meta: # go by modification not creation
        if i[:17] == '- Creation date: ':
            try:
                cr_time = datetime.datetime.strptime(
                    i[17:], "%Y-%m-%d %H:%M:%S")
                c_guessed = False
            except ValueError:
                print 'Could not parse time'
            break

    authorlist = [i[9:].strip() for i in raw_meta if i[:9] == '- Author:']
    authorstring = string.join(authorlist, _(' and '))
    
    r = {
        'author': authorstring,
        'title': r_title,
        'creation_date': cr_time,
        'modification_date': mod_time,
        'creation_date_guessed': c_guessed,
        'metadata_is_replaceable': False
        }
    return r

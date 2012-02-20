import datetime, string

import hachoir_metadata
import atomise.atomise_hachoir as atomise_hachoir

def get_real_metadata_object(fn):
    '''get object with metadata gleaned from internal file metadata'''
    #TODO: workaround for file locking bug
    raw_meta = atomise_hachoir.processFileReturn(fn)
    if not raw_meta: return None
    r_title = string.join(
        [i[8:].strip() for i in raw_meta if i[:8] == '- Title:'], ' - ')

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
    for i in raw_meta: # go by modification not creation
        if i[:17] == '- Creation date: ':
            try:
                cr_time = datetime.datetime.strptime(
                    i[17:], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                print 'Could not parse time'
            break

    authorlist = [i[9:].strip() for i in raw_meta if i[:9] == '- Author:']
    authorstring = string.join(authorlist, _(' and '))
    obj = PieObject(
        title = r_title,
        date = mod_time,
        author = authorstring)
    obj.FileData_DateCreated = cr_time
    obj.FileData_DateModified = mod_time
    return obj

def get_real_metadata_for_aspect(obj):
    pass

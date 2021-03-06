# Module for the reading and writing of file metadata
import traceback

from pieberry.pieobject.diagnostic import determine_file_type

from pieberry.piemeta.read import *
from pieberry.piemeta.write import *

# minimum metadata for "for aspect":
# 'author', 'title', 'creation_date', 'metadata_is_replaceable'
# optional:
# 'modification_date'

def get_metadata_object(fn, fakeonly=False):
    '''takes a filename, returns an object with relevant metadata gleaned from
    the file. If file type is unrecognised as handleable, then None will be
    returned'''
    ft = determine_file_type(fn)
    if ft == 'other':
        return None
    if fakeonly:
        return get_fake_metadata_object(fn)
    if ft == 'pdf':
        return get_pdf_metadata_object(fn)
    if ft == 'oxml_doc':
        return get_oxml_metadata_object(fn)
    if ft == 'odf_doc':
        return get_odf_metadata_object(fn)
    if ft in ('word_doc', 'hachoir_other'):
        return get_real_metadata_object(fn)
    return get_fake_metadata_object(fn)

def get_metadata_for_aspect(obj):
    '''You already have an object, you want to update it with file
    metadata'''
    assert obj.has_aspect('stored') or obj.has_aspect('cached')
    try:
        ft = obj.FileData_FileType
    except AttributeError:
        ft = determine_file_type(obj.FileData_FullPath)
    if ft == 'other':
        return None
    if ft == 'pdf':
        return get_pdf_metadata_for_aspect(obj)
    if ft == 'oxml_doc':
        return get_oxml_metadata_for_aspect(obj)
    if ft == 'odf_doc':
        return get_odf_metadata_for_aspect(obj)
    if ft in ('word_doc', 'hachoir_other'):
        return get_real_metadata_for_aspect(obj)
    return get_fake_metadata_for_aspect(obj)

def write_metadata_to_object(obj, **metadata):
    '''You have an object, you want to write metadata to its
    file. (works for pdfs, oxml and odf types)'''
    try:
        ft = obj.FileData_FileType
    except AttributeError:
        ft = determine_file_type(obj.FileData_FullPath)
    if not ft in ('pdf', 'odf_doc'):#, 'oxml_doc'):
        return False
    try:
        if ft == 'pdf':
            return write_pdf_metadata(obj)
        # OXML disabled as BeautifulSoup changes case of tags - bugger
        # elif ft == 'oxml_doc':
        #     return write_oxml_metadata(obj)
        elif ft == 'odf_doc':
            return write_odf_metadata(obj)
    except:
        traceback.print_exc()
        return False

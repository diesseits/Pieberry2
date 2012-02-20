# Module for the reading and writing of file metadata

from pieobject.diagnostic import determine_file_type

from read import *
from write import *

def get_metadata_object(fn):
    '''takes a filename, returns an object with relevant metadata gleaned from
    the file. If file type is unrecognised as handleable, then None will be
    returned'''
    ft = determine_file_type(fn)
    if ft == 'other':
        return None
    if ft == 'pdf':
        return get_pdf_metadata_object(fn)
    if ft in ('word_doc', 'hachoir_other'):
        return get_real_metadata_object(fn)
    return get_fake_metadata_object(fn)

def get_metadata_for_aspect(obj):
    '''You already have an object, you want to update it with file
    metadata'''
    pass

def write_metadata_to_object(obj, **metadata):
    '''You have an object, you want to write metadata to its
    file. (only going to work for pdfs for the forseeable future'''
    pass

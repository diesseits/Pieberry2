# (c) Raif Sarcich 2011 GPLv3

# Utility functions for paths

import os, sys, os.path, time, string, re
import urllib2, urlparse
from pieconfig import PIE_CONFIG
from pieconfig.paths import *
from pieconfig.schemas import FEXTENSIONS
from pieutility.decoding import *

def get_session(source=None):
    '''return a session code for dealing with grouped objects'''
    if source == 'desktop':
        return 'd_%s' % str(int(time.time()))
    else:
        return 'w_%s' % str(int(time.time()))

def auto_increment_fn(fn):
    counter = 0
    dn = os.path.dirname(fn)
    bn = os.path.splitext(os.path.basename(fn))[0]
    ext = os.path.splitext(os.path.basename(fn))[1]
    while os.path.exists(fn):
        counter += 1
        fn = os.path.join(dn, '%s_%d%s' % (bn, counter, ext))
        if counter == 1000: raise 'auto_increment_fn: Too many files - giving up'
    return fn

def suggest_path_cache_fromweb(obj):
    '''return a FULL PATH to cache a thing in'''
    if not hasattr(obj, 'session'): 
        raise AttributeError, 'No session flag for this object - illegal'
    fname = os.path.basename(urlparse.urlsplit(obj.WebData_Url).path)
    print 'suggest_path_cache_fromweb: ____'
    print 'I SUGGEST:', os.path.join(CACHEDIR, obj.session, fname)
    proposal = auto_increment_fn(os.path.join(CACHEDIR, obj.session, fname))
    return proposal

def suggest_path_cache_fromdesktop(obj):
    if not hasattr(obj, 'session'): 
        raise AttributeError, 'No session flag for this object - illegal'
    proposal = os.path.join(CACHEDIR, obj.session, obj.FileData_FileName)
    if os.path.exists(proposal):
        raise IOError, 'File already exists. TODO - auto-fix'
    return proposal

def suggest_path_store_fromweb(obj):
    assert obj.has_aspect('cached')
    root = LIBRARYDIR
    auth = obj.Author(favour_corporate=True)
    subd = obj.collection
    if obj.tags: tsubd = obj.tags[0]
    else: tsubd = ''
    print 'suggest_path_store_fromweb: ____'
    ext = os.path.splitext(obj.FileData_FullPath)[1]
    # try to fix odd file extensions (phtml, php etc)
    if not ext in FEXTENSIONS[obj.FileData_FileType]:
        if len(FEXTENSIONS[obj.FileData_FileType]) == 1:
            # only guess if there's only one possible extension
            ext = FEXTENSIONS[obj.FileData_FileType][0]
    fn_prop = "%s - %s%s" % (
        obj.ReferDate().strftime("%Y%m%d"),
        translate_non_alphanumerics(obj.Title()),
        ext)
    proposal = auto_increment_fn(os.path.join(
            root, auth, subd, tsubd,
            fn_prop[:PIE_CONFIG.getint('Format', 'filesystem_length_limit')]
            ))
    print 'SUGGESTING:', proposal
    if os.path.exists(proposal):
        raise IOError, 'File already exists. TODO - auto-fix'
    return proposal

def suggest_path_store_with_bibdata(obj):
    assert obj.has_aspect('cached')
    assert obj.has_aspect('bibdata')
    root = LIBRARYDIR
    auth = obj.Author(favour_corporate=False)
    if obj.BibData_Journal:
        subd = obj.BibData_Journal
    # elif obj.
    #     obj.
    else: subd = ''
    print 'suggest_path_store_with_bibdata: ____'
    ext = os.path.splitext(obj.FileData_FullPath)[1]
    # try to fix odd file extensions (phtml, php etc)
    if not ext in FEXTENSIONS[obj.FileData_FileType]:
        if len(FEXTENSIONS[obj.FileData_FileType]) == 1:
            # only guess if there's only one possible extension
            ext = FEXTENSIONS[obj.FileData_FileType][0]
    fn_prop = "%s - %s%s" % (
        obj.ReferDate().strftime("%Y%m%d"),
        translate_non_alphanumerics(obj.Title()),
        ext)
    proposal = auto_increment_fn(os.path.join(
            root, auth, subd, 
            fn_prop[:PIE_CONFIG.getint('Format', 'filesystem_length_limit')]
            ))
    print 'SUGGESTING:', proposal
    if os.path.exists(proposal):
        raise IOError, 'File already exists. TODO - auto-fix'
    return proposal
    

def suggest_path_store_fromdesktop(obj, folder, new_fn=None):
    assert obj.has_aspect('cached')
    root = PROJECTDIR
    print 'suggest_path_store_fromdesktop: ____'
    if new_fn: fn = new_fn
    else: fn = obj.FileData_FileName
    proposal = auto_increment_fn(os.path.join(root, folder, fn))
    print 'SUGGESTING:', proposal
    if os.path.exists(proposal):
        raise IOError, 'File already exists.'
    return proposal

def suggest_path_rehome(obj):
    pass


#ATOMISE SHIT


re_doc_creation_date = re.compile(r'^Creation date: ([0-9]{4})-([0-9]{2})-([0-9]{2}) ')
re_dateprefix = re.compile(r'^[12][0-9]{3}[01][0-9][0123][0-9]')


def suggest_initial_fn(obj, doctype=''):
    m = re_dateprefix.match(obj.FileData_FileName)
    if m: return obj.FileData_FileName
    else:
        ext = os.path.splitext(obj.FileData_FileName)[1]
        if m:
            usetitle = os.path.splitext(obj.FileData_FileName)[0][8:].lstrip(' -')
        else:
            usetitle = os.path.splitext(obj.FileData_FileName)[0].lstrip(' -')
        dateprefix = obj.ReferDate().strftime("%Y%m%d")
        return string.join(
                [t for t in (dateprefix, doctype, usetitle) if t], ' - ') + ext


#OLD: For reference only
# def suggest_fn(ifn, creationdate=None, title=None, doctype=None):
#     '''Suggest a suitable filename, taking the longer of the existing
#     filename or the title string of the document'''
#     ext = os.path.splitext(ifn)[1]
#     m = re_dateprefix.match(ifn)
#     if m:
#         dateprefix = m.group(0)
#         usetitle = os.path.splitext(ifn)[0][8:]
#     else:
#         usetitle = os.path.splitext(ifn)[0]
#         if creationdate:
#             dateprefix = time.strftime("%Y%m%d", creationdate)
#         else:
#             dateprefix = time.strftime("%Y%m%d", time.localtime())
#     if config.getboolean('AToptions', 'guess_filename') == True:
#         if len(title) > len(usetitle): usetitle = title[:90] #translate_non_alphanumerics(title[:90])
#     return string.join([s for s in [dateprefix, doctype, usetitle] if s != None], ' - ') + ext

# def score_item(docdata):
#     '''determine the most appropriate matching folder for a document
#     based on its metadata. Return folder name or None'''
#     cf = open(os.path.join(sysdir, 'criteria.pickle'), 'r')
#     criteria = cPickle.load(cf)
#     cf.close()

#     docscore = dict([(k, 0) for k, v in criteria.items()])
#     for directory, field_data in criteria.items():
#         for field, searchterms in field_data.items():
#             if not docdata.has_key(field):
#                 continue
#             for term in searchterms:
#                 if term.lower() in docdata[field].lower():
#                     docscore[directory] += 1
#                 if field == 'title': # title searches should also go
#                                      # through the initial file name
#                     if term.lower() in docdata['initial_fn'].lower():
#                         docscore[directory] += 1
#     topkey = ''
#     topscore = 0
#     for k, v in docscore.items():
#         if v > topscore: 
#             topscore = v
#             topkey = k
#     if topscore == 0:
#         return None
#     else:
#         return topkey

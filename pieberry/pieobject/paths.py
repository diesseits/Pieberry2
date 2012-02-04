# (c) Raif Sarcich 2011 GPLv3

# Utility functions for paths

import os, sys, os.path, time
import urllib2, urlparse
from pieconfig.paths import *

def get_session(source=None):
    '''return a session code for dealing with grouped objects'''
    if source == 'desktop':
        return 'd_%s' % str(int(time.time()))
    else:
        return 'w_%s' % str(int(time.time()))

def suggest_path_cache_fromweb(obj):
    '''return a FULL PATH to cache a thing in'''
    if not hasattr(obj, 'session'): 
        raise AttributeError, 'No session flag for this object - illegal'
    fname = os.path.basename(urlparse.urlsplit(obj.Url()).path)
    print 'suggest_path_cache_fromweb: ____'
    print 'I SUGGEST:', os.path.join(CACHEDIR, obj.session, fname)
    proposal = os.path.join(CACHEDIR, obj.session, fname)
    if os.path.exists(proposal):
        raise IOError, 'File already exists. TODO - auto-fix'
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
    print 'suggest_path_store_fromweb: ____'
    proposal = os.path.join(
        root, auth, subd, obj.FileData_FileName)
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
    proposal = os.path.join(root, folder, fn)
    print 'SUGGESTING:', proposal
    if os.path.exists(proposal):
        raise IOError, 'File already exists.'
    return proposal

def suggest_path_rehome(obj):
    pass


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

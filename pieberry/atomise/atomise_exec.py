#!/bin/python

# A program to tidy up a messy desktop.
# GNU GPL v3
# (c) Raif Sarcich 2010

import sys, os, time, re, string, traceback, shutil
import datetime
import wx
import hachoir_metadata
import atomise_hachoir

import piemeta

from pdfrw import PdfReader
from pprint import pprint

from pieutility.decoding import *
from pieconfig.paths import *
from pieobject import *
from pieobject.paths import *
from pieobject.folder import recommend_folder

def scan_desktop():
    '''Returns an object store of valid (handlable) file in the desktop 
    directory'''
    file_list = [os.path.join(DESKTOPDIR, filesystem_decode(fl)) 
                 for fl in os.listdir(DESKTOPDIR) 
                 if os.path.isfile(os.path.join(DESKTOPDIR, fl))]
    ostore = PieObjectStore()
    for fl in file_list:
        assert type(fl) == unicode
        d = piemeta.get_metadata_object(fl)
        if d:
            d.add_aspect_ondesktop(fl)
            ostore.Add(d)
    return ostore

def scan_previous_desktops():
    '''Return a list of objectstores for all the leftover directories
    containing desktop cleanouts'''
    dirs = [f for f in os.listdir(CACHEDIR) 
            if os.path.isdir(os.path.join(CACHEDIR, f)) and f[:1] == 'd']
    rdata = []
    for d in dirs:
        ostore = PieObjectStore()
        dd = os.path.join(CACHEDIR, d)
        flist = [os.path.join(dd, filesystem_decode(fl)) 
                 for fl in os.listdir(dd) 
                 if os.path.isfile(os.path.join(dd, fl))]
        for fl in flist:
            o = piemeta.get_metadata_object(fl)
            if o:
                o.add_aspect_cached_from_desktop(fl)
                ostore.Add(o)
        ostore.set_session(d)
        print 'Adding desktop dir %s with %d objects' % (d, len(ostore))
        rdata.append(ostore)
    return rdata



    # import sha
    # for doc in doc_list:
    #     d = {}
    #     try:
    #         # [HACKY WORKAROUND]
    #         #this is all to work around the stupid file-locking bug with hachoir
    #         shaobj = sha.new(doc + str(time.localtime()))
    #         cachedocname = shaobj.hexdigest() + os.path.splitext(doc)[1]
    #         shutil.copyfile(os.path.join(tempdir, doc), os.path.join(tempdir, 'cache', cachedocname))
    #         d['initial_fn'] = doc
    #         d.update(get_doc_metadata(os.path.join(tempdir, 'cache', cachedocname)))
    #         # [/HACKY WORKAROUND]
    #     except:
    #         traceback.print_exc()
    #         continue
        
    

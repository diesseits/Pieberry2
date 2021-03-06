#!/bin/python

# A program to tidy up a messy desktop.
# GNU GPL v3
# (c) Raif Sarcich 2010

import sys, os, time, re, string, traceback, shutil
import datetime
import wx

import pieberry.piemeta

from pprint import pprint

from pieberry.pieutility.decoding import *
from pieberry.pieconfig.paths import *
from pieberry.pieobject import *
from pieberry.pieobject.paths import *
from pieberry.pieobject.folder import recommend_folder

IGNOREFILES = (
    re.compile(r'^_Folder_Info.txt'),
    re.compile(r'^[#~].*'),
    re.compile(r'^Backup.*')
    )

def should_ignore(fl):
    for re in IGNOREFILES:
        if re.match(os.path.basename(fl)): return True
    return False

def scan_desktop_gen():
    '''Generator based version of scan_desktop()'''
    file_list = [os.path.join(DESKTOPDIR, filesystem_decode(fl)) 
                 for fl in os.listdir(DESKTOPDIR) 
                 if os.path.isfile(os.path.join(DESKTOPDIR, fl))]
    nofiles = len(file_list)
    progress = 0
    for fl in file_list:
        if should_ignore(fl): continue
        print 'ignore %s:' % fl, should_ignore(fl)
        progress += 1
        assert type(fl) == unicode
        try:
            d = pieberry.piemeta.get_metadata_object(fl)
        except Exception, exc:
            #traceback.print_exc()
            print 'Could not handle file: %s' % fl
            continue
        if d:
            d.add_aspect_ondesktop(fl)
            yield d, nofiles, progress

def scan_desktop():
    '''Returns an object store of valid (handlable) file in the desktop 
    directory'''
    file_list = [os.path.join(DESKTOPDIR, filesystem_decode(fl)) 
                 for fl in os.listdir(DESKTOPDIR) 
                 if os.path.isfile(os.path.join(DESKTOPDIR, fl))]
    ostore = PieObjectStore()
    for fl in file_list:
        assert type(fl) == unicode
        try:
            d = pieberry.piemeta.get_metadata_object(fl)
        except Exception, exc:
            #traceback.print_exc()
            print 'Could not handle file: %s' % fl
            continue
        if d:
            d.add_aspect_ondesktop(fl)
            ostore.Add(d)
    return ostore

def scan_previous_desktops_gen():
    '''Generator based version of scan_previous_desktops()'''
    dirs = [f for f in os.listdir(CACHEDIR) 
            if os.path.isdir(os.path.join(CACHEDIR, f)) and f[:2] == 'd_']
    for d in dirs:
        dd = os.path.join(CACHEDIR, d)
        flist = [os.path.join(dd, filesystem_decode(fl)) 
                 for fl in os.listdir(dd) 
                 if os.path.isfile(os.path.join(dd, fl))]
        for fl in flist:
            try:
                o = pieberry.piemeta.get_metadata_object(fl)
            except Exception, exc:
                print 'scan_previous_desktops_gen complaint: %s' % exc
            if o:
                o.add_aspect_cached_from_desktop(fl)
                yield o

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
            o = pieberry.piemeta.get_metadata_object(fl)
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
        
    

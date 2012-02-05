#!/bin/python

# A program to tidy up a messy desktop.
# GNU GPL v3
# (c) Raif Sarcich 2010

import sys, os, time, re, string, traceback, shutil
import datetime
import wx
import hachoir_metadata
import atomise_hachoir

from pdfrw import PdfReader

from atomise_utility import *
from pieconfig.paths import *
from pieobject import *


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

def get_fake_metadata_object(fn):
    '''get object with metadata gleaned only from the file system
    takes a full path'''
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
    obj = PieObject(
        title = ttl,
        date = cdate)
    return obj

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

def get_pdf_metadata_object(fn):
    '''hachoir doesn't do pdf'''
    fakeobj = get_fake_metadata_object(fn)
    try:
        reader = PdfReader(fn)
    except Exception, exc:
        traceback.print_exc(file=open('/tmp/pieberry/dbgop', 'w'))
        return None
        # assert len(reader.Info.CreationDate) > 0
    if reader.InfoCreationDate:
        cd = reader.Info.CreationDate.split(':')[1] #get the 'good' bit 
        # md = reader.Info.ModDate.split(':')[1]
        creation_date = time.strptime("%s %s %s %s %s" % (
                cd[0:4], cd[4:6], cd[6:8], cd[8:10], cd[10:12]
                ), "%Y %m %d %H %M")
    else:
        creation_date = fakeobj.FileData_DateCreated
    obj = PieObject(
        author = unicode(reader.Info.Author).strip('()'),
        title = unicode(reader.Info.Title).strip('()'),
        date = creation_date)
    obj.FileData_DateCreated = creation_date
    return obj

def scan_desktop():
    '''Returns an object store of valid (handlable) file in the desktop 
    directory'''
    file_list = [os.path.join(DESKTOPDIR, fl) for fl in os.listdir(DESKTOPDIR) if os.path.isfile(os.path.join(DESKTOPDIR, fl))]
    ostore = PieObjectStore()
    for fl in file_list:
        d = get_metadata_object(fl)
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
        flist = [os.path.join(dd, fl) 
                 for fl in os.listdir(dd) 
                 if os.path.isfile(os.path.join(dd, fl))]
        for fl in flist:
            o = get_metadata_object(fl)
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
        
    

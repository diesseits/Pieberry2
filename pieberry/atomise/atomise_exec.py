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
    reader = PdfReader(obj.FileData_FullPath)
        # assert len(reader.Info.CreationDate) > 0
    cd = reader.Info.CreationDate.split(':')[1] #get the 'good' bit 
        # md = reader.Info.ModDate.split(':')[1]
    creation_date = time.strptime("%s %s %s %s %s" % (
            cd[0:4], cd[4:6], cd[6:8], cd[8:10], cd[10:12]
            ), "%Y %m %d %H %M")
    obj = PieObject(
        author = reader.Info.Author,
        title = reader.Info.Title,
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
        

def desktop_sweep():
    sweepdir = config.get('AToptions', 'sweep_directory')
    tempdir = config.get('AToptions', 'temp_directory')

    # first sweep files into temp dir

    file_list = [fl for fl in os.listdir(sweepdir) if os.path.isfile(os.path.join(sweepdir, fl))]
    doc_list = [fl for fl in file_list if os.path.splitext(fl)[1].lower() in FEXTENSIONS['word_doc'] and fl[0] not in '~#']
    pdf_list = [fl for fl in file_list if os.path.splitext(fl)[1].lower() in FEXTENSIONS['pdf']]

    if not os.path.exists(config.get('AToptions', 'temp_directory')):
        os.makedirs(config.get('AToptions', 'temp_directory'))
    if not os.path.exists(os.path.join(config.get('AToptions', 'temp_directory'), 'cache')):
        os.makedirs(os.path.join(config.get('AToptions', 'temp_directory'), 'cache'))

    # [HACKY WORKAROUND]
    # clear the cache of documents as and when possible
    for fl in os.listdir(os.path.join(config.get('AToptions', 'temp_directory'), 'cache')):
        try:
            if os.path.isfile(os.path.join(config.get('AToptions', 'temp_directory'), 'cache', fl)):
                os.remove(os.path.join(config.get('AToptions', 'temp_directory'), 'cache', fl))
        except:
            print 'file deletion fail'
    # [/HACKY WORKAROUND]

    for fl in doc_list:
        try:
            # shutil.copyfile(os.path.join(sweepdir, fl), os.path.join(tempdir, fl))
            # os.remove(os.path.join(sweepdir, fl))
            # shutil.copyfile(os.path.join(sweepdir, fl), os.path.join(tempdir, 'cache', fl))
            os.rename(os.path.join(sweepdir, fl), os.path.join(tempdir, fl))
        except Exception, exc:
            print 'warning - could not move %s to temp\n(%s)' % (fl, unicode(exc))
    for fl in pdf_list:
        try:
            # shutil.copyfile(os.path.join(sweepdir, fl), os.path.join(tempdir, fl))
            # os.remove(os.path.join(sweepdir, fl))
            os.rename(os.path.join(sweepdir, fl), os.path.join(tempdir, fl))
        except Exception, exc:
            print 'warning - could not move %s to temp\n(%s)' % (fl, unicode(exc))

    # then generate data for all files in temp dir

    file_list = [fl for fl in os.listdir(tempdir) if os.path.isfile(os.path.join(tempdir, fl))]
    doc_list = [fl for fl in file_list if os.path.splitext(fl)[1].lower() in FEXTENSIONS['word_doc']] 
    pdf_list = [fl for fl in file_list if os.path.splitext(fl)[1].lower() in FEXTENSIONS['pdf']]

    returndata = []
    import sha
    for doc in doc_list:
        d = {}
        try:
            # [HACKY WORKAROUND]
            #this is all to work around the stupid file-locking bug with hachoir
            shaobj = sha.new(doc + str(time.localtime()))
            cachedocname = shaobj.hexdigest() + os.path.splitext(doc)[1]
            shutil.copyfile(os.path.join(tempdir, doc), os.path.join(tempdir, 'cache', cachedocname))
            d['initial_fn'] = doc
            d.update(get_doc_metadata(os.path.join(tempdir, 'cache', cachedocname)))
            # [/HACKY WORKAROUND]
        except:
            traceback.print_exc()
            continue
        d['recommended_dir'] = score_item(d)
        d['suggested_fn'] = suggest_fn(
            doc, 
            creationdate=d['creation_date'],
            title=d['title']
            )
        returndata.append(d)

    for pdf in pdf_list:
        d = {}
        try:
            d['initial_fn'] = pdf
            d.update(get_pdf_metadata(os.path.join(tempdir, pdf)))
        except:
            traceback.print_exc()
            continue
        d['recommended_dir'] = score_item(d)
        d['suggested_fn'] = suggest_fn(
            pdf, 
            creationdate=d['creation_date'],
            title=d['title']
            )
        print d['initial_fn']
        returndata.append(d)

    return tuple(returndata)
        
    

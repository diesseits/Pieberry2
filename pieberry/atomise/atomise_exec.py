#!/bin/python

# A program to tidy up a messy desktop.
# GNU GPL v3
# (c) Raif Sarcich 2010

import sys, os, time, re, string, traceback, shutil
import wx
import hachoir_metadata
import atomise_hachoir
import pyPdf

re_doc_creation_date = re.compile(r'^Creation date: ([0-9]{4})-([0-9]{2})-([0-9]{2}) ')
re_dateprefix = re.compile(r'^[12][0-9]{3}[01][0-9][0123][0-9]')

def get_fake_metadata(fn):
    '''get metadata gleaned only from the file system'''
    ret = {}
    m = re_dateprefix.match(os.path.basename(fn))
    if m:
        dateprefix = m.group(0)
        ftime = '%s %s %s' % (dateprefix[0:4], dateprefix[4:6], dateprefix[6:8])
        ret['creation_date'] = time.strptime(ftime, '%Y %m %d')
        ret['title'] = os.path.splitext(os.path.basename(fn))[0][8:]
    else:
        ret['title'] = os.path.splitext(os.path.basename(fn))[0]
        ret['creation_date'] = time.localtime(os.stat(fn)[9])
    ret['author'] = ''
    return ret
        
def get_doc_metadata(fn):
    raw_meta = atomise_hachoir.processFileReturn(fn)
    if not raw_meta:
        print 'Warning - no metadata for file %s' % fn
        return get_fake_metadata(fn)
    md = {}
    md['title'] = string.join([i[8:].strip() for i in raw_meta if i[:8] == '- Title:'], ' - ')
    # for i in raw_meta:
    #     if i[:17] == '- Creation date: ':
    #         ct = time.localtime(os.stat(fn)[9])
    #         try:
    #             ct = time.strptime(i[17:], "%Y-%m-%d %H:%M:%S")
    #         except ValueError:
    #             print 'Could not parse time'
    #         md['creation_date'] = ct
    #         break
    # for i in raw_meta:
    #     if i[:21] == '- Last modification: ':
    #         mt = time.localtime(os.stat(fn)[8])
    #         try:
    #             mt = time.strptime(i[21:], "%Y-%m-%d %H:%M:%S")
    #         except ValueError:
    #             print 'Could not parse time'
    #         md['modification date'] = mt
    #         break
    mt = time.localtime(os.stat(fn)[8])
    for i in raw_meta: # go by modification not creation
        if i[:21] == '- Last modification: ':
            try:
                mt = time.strptime(i[21:], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                print 'Could not parse time'
            break
    md['creation_date'] = mt
    md['authors'] = [i[9:].strip() for i in raw_meta if i[:9] == '- Author:']
    md['author'] = string.join([i[9:].strip() for i in raw_meta if i[:9] == '- Author:'], ' and ')
    return md

def get_pdf_metadata(fn):
    retinfo = {}
    retinfo['creation_date'] = time.localtime(os.stat(fn)[9])
    retinfo['author'] = ''
    retinfo['title'] = ''
    try:
        pdf_file = file(fn, 'rb')
        pdfread = pyPdf.PdfFileReader(pdf_file)
        docmetadata = pdfread.getDocumentInfo()
    except:
        print 'warning - could not read pdf metadata for %s' % fn
        traceback.print_exc()
        pdf_file.close()
        return get_fake_metadata(fn)
    if docmetadata == None:
        docmetadata = {} #pyPdf appears to send Nonetypes instead of
                         #empty dicts, annoyingly
    # creation date is found here. if not present, fall back to current date
    try:
        if docmetadata.has_key('/CreationDate'):
            rd = docmetadata['/CreationDate'][2:]
            retinfo['creation_date'] = time.strptime("%s %s %s %s %s" % (rd[0:4], rd[4:6], rd[6:8], rd[8:10], rd[10:12]), "%Y %m %d %H %M")
            retinfo['creation_date_guessed'] = False
        else:
            retinfo['creation_date_guessed'] = True
    except: #hack ... but sometimes /creationdate is bunged
        traceback.print_exc()
        retinfo['creation_date_guessed'] = True
    # some reformatting necessary when author names are computer-inserted
    splre = re.compile("[./_ ]")
    authst = ''
    if not pdfread.documentInfo:
        return retinfo
    if pdfread.documentInfo.author:
        authst = string.join(splre.split(pdfread.documentInfo.author))
        authst = string.capwords(authst)
    retinfo['author'] = authst
    retinfo['title'] = unicode(pdfread.documentInfo.title)
    pdf_file.close()
    return retinfo

def get_other_metadata(fn):
    pass

import traceback
import cPickle
from pieberry.pieberry_config import *

def periodic_sweep():
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
        
def score_item(docdata):
    '''determine the most appropriate matching folder for a document
    based on its metadata. Return folder name or None'''
    cf = open(os.path.join(sysdir, 'criteria.pickle'), 'r')
    criteria = cPickle.load(cf)
    cf.close()

    docscore = dict([(k, 0) for k, v in criteria.items()])
    for directory, field_data in criteria.items():
        for field, searchterms in field_data.items():
            if not docdata.has_key(field):
                continue
            for term in searchterms:
                if term.lower() in docdata[field].lower():
                    docscore[directory] += 1
                if field == 'title': # title searches should also go
                                     # through the initial file name
                    if term.lower() in docdata['initial_fn'].lower():
                        docscore[directory] += 1
    topkey = ''
    topscore = 0
    for k, v in docscore.items():
        if v > topscore: 
            topscore = v
            topkey = k
    if topscore == 0:
        return None
    else:
        return topkey

def suggest_fn(ifn, creationdate=None, title=None, doctype=None):
    '''Suggest a suitable filename, taking the longer of the existing
    filename or the title string of the document'''
    ext = os.path.splitext(ifn)[1]
    m = re_dateprefix.match(ifn)
    if m:
        dateprefix = m.group(0)
        usetitle = os.path.splitext(ifn)[0][8:]
    else:
        usetitle = os.path.splitext(ifn)[0]
        if creationdate:
            dateprefix = time.strftime("%Y%m%d", creationdate)
        else:
            dateprefix = time.strftime("%Y%m%d", time.localtime())
    if config.getboolean('AToptions', 'guess_filename') == True:
        if len(title) > len(usetitle): usetitle = title[:90] #translate_non_alphanumerics(title[:90])
    return string.join([s for s in [dateprefix, doctype, usetitle] if s != None], ' - ') + ext
    
def main(argv):  
    file_list = [fl for fl in os.listdir(os.getcwd()) if os.path.isfile(fl)]
    doc_list = [fl for fl in file_list if os.path.splitext(fl)[1].lower() == '.doc']
    pdf_list = [fl for fl in file_list if os.path.splitext(fl)[1].lower() == '.pdf']

    print file_list
    print doc_list
    print pdf_list

    for fl in doc_list:
        print get_doc_metadata(fl)
    for fl in pdf_list:
        print get_pdf_metadata(fl)
        

if __name__ == '__main__':
    main(sys.argv)

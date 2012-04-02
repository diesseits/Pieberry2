import pyPdf, traceback, datetime, string, re, os, os.path, shutil, sys

from pieberry.pieobject.paths import auto_increment_fn
from pieberry.pieconfig.paths import CACHEDIR
from pieberry.pieobject import PieObject
from pieberry.piemeta.read.fake import get_fake_metadata

# TODO: bring up to date for P2
splre = re.compile("[./_ ]")

def pypdf_object(fn):
    if sys.platform == 'win32':
        newfn = os.path.join(CACHEDIR, 'Workaround', os.path.basename(fn))
        if os.path.isfile(newfn):
            newfn = auto_increment_fn(newfn)
        shutil.copyfile(fn, newfn)
        fn = newfn
    data = pypdf_metadata(fn)
    obj = PieObject(
        title=data['title'],
        author=data['author'],
        date=data['creation_date']
        )
    obj.FileData_DateCreated = data['creation_date']
    return obj

def pypdf_metadata(fn):
    retinfo = {}
    retinfo['creation_date'] = datetime.datetime.fromtimestamp(os.stat(fn)[9])
    retinfo['author'] = u''
    retinfo['title'] = u''
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
            retinfo['creation_date'] = datetime.datetime.strptime("%s %s %s %s %s" % (rd[0:4], rd[4:6], rd[6:8], rd[8:10], rd[10:12]), "%Y %m %d %H %M")
            retinfo['creation_date_guessed'] = False
        else:
            retinfo['creation_date_guessed'] = True
    except: #hack ... but sometimes /creationdate is bunged
        traceback.print_exc()
        retinfo['creation_date_guessed'] = True
    # some reformatting necessary when author names are computer-inserted
    authst = u''
    if not pdfread.documentInfo:
        return retinfo
    if pdfread.documentInfo.author:
        authst = string.join(splre.split(pdfread.documentInfo.author))
        authst = string.capwords(authst)
    retinfo['author'] = authst
    retinfo['title'] = unicode(pdfread.documentInfo.title) if pdfread.documentInfo.title else u''
    pdf_file.close()
    return retinfo

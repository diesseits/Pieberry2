import pyPdf, traceback, datetime, string, re, os, os.path
from pieobject import PieObject
from fake import get_fake_metadata

# TODO: bring up to date for P2
splre = re.compile("[./_ ]")

def pypdf_object(fn):
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
            retinfo['creation_date'] = datetime.datetime.strptime("%s %s %s %s %s" % (rd[0:4], rd[4:6], rd[6:8], rd[8:10], rd[10:12]), "%Y %m %d %H %M")
            retinfo['creation_date_guessed'] = False
        else:
            retinfo['creation_date_guessed'] = True
    except: #hack ... but sometimes /creationdate is bunged
        traceback.print_exc()
        retinfo['creation_date_guessed'] = True
    # some reformatting necessary when author names are computer-inserted
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

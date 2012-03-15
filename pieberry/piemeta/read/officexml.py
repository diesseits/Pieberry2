# Metadata extraction from office xml data formats

import zipfile, BeautifulSoup, os, os.path, sys, re, datetime, traceback
from pprint import pprint
from pieberry.pieconfig.paths import CACHEDIR
from pieberry.pieobject.paths import auto_increment_fn
from pieberry.pieconfig.globalvars import DEBUG
from pieberry.piemeta.read.fake import get_fake_metadata_object

def get_oxml_metadata(fn):
    r = {}
    unzipped = zipfile.ZipFile(fn)
    bs = BeautifulSoup.BeautifulSoup(unzipped.open(u'docProps/core.xml'))
    r['title'] = bs.find(u'dc:title').text if bs.find(u'dc:title') else ''
    r['author'] = bs.find(u'dc:creator').text
    r['creation_date'] = datetime.datetime.strptime(
        bs.find('dcterms:created').text, "%Y-%m-%dT%H:%M:%SZ")
    r['modification_date'] = datetime.datetime.strptime(
        bs.find('dcterms:modified').text, "%Y-%m-%dT%H:%M:%SZ")
    r['creation_date_guessed'] = False
    r['metadata_is_replaceable'] = False
    unzipped.close()
    return r

def get_oxml_metadata_object(fn):
    # if sys.platform == 'win32':
    #     newfn = os.path.join(CACHEDIR, 'Workaround', os.path.basename(fn))
    #     if os.path.isfile(newfn):
    #         newfn = auto_increment_fn(newfn)
    #     shutil.copyfile(fn, newfn)
    #     fn = newfn
    obj = get_fake_metadata_object(fn)
    try:
        d = get_oxml_metadata(fn)
    except:
        traceback.print_exc()
        print 'Parsing oxml document %s failed' % fn
        return obj
    obj.author = d['author']
    obj.title = d['title']
    obj.date = d['creation_date']
    obj.FileData_DateCreated = d['creation_date']
    obj.FileData_DateModified = d['modification_date']
    return obj

def get_oxml_metadata_for_aspect(obj):
    return get_oxml_metadata(obj.FileData_FullPath)

if __name__ == '__main__':
    pprint(get_oxml_metadata('test.docx'))

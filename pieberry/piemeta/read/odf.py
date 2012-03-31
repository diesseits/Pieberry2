# Metadata extraction from Open Document Foundation data formats

import zipfile, BeautifulSoup, os, os.path, sys, re, datetime, traceback
from pprint import pprint
# from pieberry.pieconfig.paths import CACHEDIR
# from pieberry.pieobject.paths import auto_increment_fn
# from pieberry.pieconfig.globalvars import DEBUG
if __name__ != "__main__":
    from pieberry.piemeta.read.fake import get_fake_metadata_object

def get_odf_metadata(fn):
    r = {}
    unzipped = zipfile.ZipFile(fn)
    bs = BeautifulSoup.BeautifulSoup(unzipped.open(u'meta.xml'))
    r['title'] = bs.find(u'dc:title').text if bs.find(u'dc:title') else ''
    r['author'] = bs.find(u'dc:creator').text if bs.find(u'dc:creator') else ''
    r['description'] = bs.find(u'dc:description').text if bs.find(u'dc:description') else None
    r['subject'] = bs.find(u'dc:subject').text if bs.find(u'dc:subject') else None
    r['creation_date'] = datetime.datetime.strptime(
        bs.find('meta:creation-date').text[:19], "%Y-%m-%dT%H:%M:%S")
    r['modification_date'] = datetime.datetime.strptime(
        bs.find('dc:date').text[:19], "%Y-%m-%dT%H:%M:%S")
    r['creation_date_guessed'] = False
    r['metadata_is_replaceable'] = False
    unzipped.close()
    return r

def get_odf_metadata_object(fn):
    # if sys.platform == 'win32':
    #     newfn = os.path.join(CACHEDIR, 'Workaround', os.path.basename(fn))
    #     if os.path.isfile(newfn):
    #         newfn = auto_increment_fn(newfn)
    #     shutil.copyfile(fn, newfn)
    #     fn = newfn
    obj = get_fake_metadata_object(fn)
    try:
        d = get_odf_metadata(fn)
    except:
        traceback.print_exc()
        print 'Parsing oxml document %s failed' % fn
        return obj
    obj.author = d['author']
    obj.title = d['title']
    obj.date = d['creation_date']
    obj.FileData_DateCreated = d['creation_date']
    obj.FileData_DateModified = d['modification_date']
    if d['description']: obj.BibData_Annote = d['description']
    return obj

def get_odf_metadata_for_aspect(obj):
    return get_odf_metadata(obj.FileData_FullPath)

if __name__ == '__main__':
    # md = get_odf_metadata('test.odt')
    # pprint(md)
    # print type(md['subject'])
    write_odf_metadata('test.odt')
    


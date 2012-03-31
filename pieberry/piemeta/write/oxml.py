import zipfile, BeautifulSoup, os, os.path, sys, re, datetime, traceback
from pprint import pprint

def write_oxml_metadata(obj):
    '''Support changing title and author only for now'''
    print 'write_oxml_metadata'
    unzipped = zipfile.ZipFile(obj.FileData_FullPath, 'a')
    bs = BeautifulSoup.BeautifulSoup(unzipped.open(u'docProps/core.xml'))
    title = bs.find(u'dc:title') #if bs.find(u'dc:title') else ''
    md_changed = False
    if title and title.text != obj.Title():
        title.string = obj.Title()
        md_changed = True
    author = bs.find(u'dc:creator')
    if author and author.text != obj.Author():
        author.string = obj.Author()
        md_changed = True
    if md_changed:
        unzipped.writestr(u'docProps/core.xml', str(bs))
    unzipped.close()
    return True

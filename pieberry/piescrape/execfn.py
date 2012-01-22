import os.path, os, wx, traceback, urllib, time
from urlparse import urlparse

def download_file(
    url, # the url
    suggested_path, # where to download to
    # notify_window, # the main window to notify of what goes right/wrong
    # code, # a particular code, to pass back to the main window
    cj=None,  # a cookie jar, if you like
    filetype=None # type of file - allows special html behaviour
    ):
    try:
        print "I am trying to download %s to %s" % (url, suggested_path)
        # if not os.path.isdir(suggested_path): raise IOError, "Non-directory supplied to download_file"
        if not os.path.exists(os.path.dirname(suggested_path)):
            os.makedirs(os.path.dirname(suggested_path))
        urllib.urlretrieve(url, suggested_path)
        return 'success'
    except Exception, err:
        traceback.print_exc()
        # tell the main window this download failed
        return 'fail'


#TODO this probably merits a separate file
if __name__ == '__main__':
    import sys
    sys.path.append('/home/raif/development/v2Pieberry/pieberry')

from pdfrw import PdfReader

def scan_file_metadata(obj):
    if obj.FileData_FileType == 'pdf':
        print 'Reading', obj.FileData_FullPath
        reader = PdfReader(obj.FileData_FullPath)
        # assert len(reader.Info.CreationDate) > 0
        cd = reader.Info.CreationDate.split(':')[1] #get the 'good' bit 
        # md = reader.Info.ModDate.split(':')[1]
        creation_date = time.strptime("%s %s %s %s %s" % (
                cd[0:4], cd[4:6], cd[6:8], cd[8:10], cd[10:12]
                ), "%Y %m %d %H %M")
        return {
            'author': reader.Info.Author,
            'title': reader.Info.Title,
            'creation_date': creation_date
            }
    else:
        print 'Unknown file type'
        return {}

class Arbitrary:
    FileData_FileType = 'pdf'
    FileData_FullPath = '/home/raif/development/v2Pieberry/pieberry/piescrape/test.pdf'
    def __str__(self):
        print 'arbitrary class'
            
if __name__ == '__main__':
    obj = Arbitrary()
    print scan_file_metadata(obj)




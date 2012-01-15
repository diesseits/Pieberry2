import os.path, os, wx, traceback, urllib
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

import pdfrw

def scan_file_metadata(
    obj #the object
    ):
    if obj.file_type == 'pdf':
        pass




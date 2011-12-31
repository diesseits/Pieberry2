import os.path, os, wx, traceback, urllib

def download_file(
    url, # the url
    suggested_path, # where to download to
    notify_window, # the main window to notify of what goes right/wrong
    code, # a particular code, to pass back to the main window
    cj=None,  # a cookie jar, if you like
    filetype=None # type of file - allows special html behaviour
    ):
    try:
        print "I am trying to download %s to %s" % (url, suggested_path)
        # urllib.urlretrieve(url, outfilename)
    except Exception, err:
        traceback.print_exc()
        # tell the main window this download failed


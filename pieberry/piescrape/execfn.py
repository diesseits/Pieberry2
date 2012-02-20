import os.path, os, traceback, urllib
from urlparse import urlparse
from pieconfig.globalvars import U_ERROR_BEHAV, DEBUG

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

def suggest_title(linktext, category_phrase, append_behav):
    '''Suggest a slightly amended title to reflect the pre/appending
    of category phrases. (This is a good thing because websites often
    just title things "Draft report" when what they mean is "Draft
    Report - Review of the blah"'''
    assert type(linktext) == unicode
    assert type(category_phrase) == unicode
    if linktext.strip(' :;-_').lower() == category_phrase.strip(' :;-_').lower():
        return linktext # sanity check - don't double up 
    if append_behav == 0: # append to title with dash:
        return u"%s - %s" % (linktext.strip(' :;-_'), category_phrase.strip())
    elif append_behav == 1: # append with brackets
        return u"%s (%s)" % (linktext.strip(' :;-_'), category_phrase.strip())
    elif append_behav == 2: # prepend with colon
        return u"%s: %s" % (category_phrase.strip(), linktext.strip(' :;-_')) 
    elif append_behav == 3: #none
        return linktext.strip(' :;-_')
    else: raise Exception, "Invalid append behaviour"


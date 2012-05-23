import os.path, os, traceback, urllib, urllib2
from urlparse import urlparse, urlunparse
from pieberry.pieconfig.globalvars import U_ERROR_BEHAV, DEBUG
from pieberry.piescrape.resource import *

def safequote(url):
    if not '%' in url:#hackity hack
        parse = [i for i in urlparse(url)]
        parse[2] = urllib2.quote(parse[2])
        return urlunparse(parse)
    else:
        return url

def download_file(
    url, # the url
    suggested_path, # where to download to
    # notify_window, # the main window to notify of what goes right/wrong
    # code, # a particular code, to pass back to the main window
    # cj=None,  # a cookie jar, if you like
    filetype=None # type of file - allows special html behaviour
    ):
    try:
        print "I am trying to download %s to %s" % (url, suggested_path)
        # if not os.path.isdir(suggested_path): raise IOError, "Non-directory supplied to download_file"
        if not os.path.exists(os.path.dirname(suggested_path)):
            os.makedirs(os.path.dirname(suggested_path))
        if os.path.exists(suggested_path):
            raise 'download_file: File already exists!'
        
        request = urllib2.Request(safequote(url), headers=headers)
        response = urllib2.urlopen(request)
        cj.extract_cookies(response,request)
        cookie_handler= urllib2.HTTPCookieProcessor( cj )
        redirect_handler= urllib2.HTTPRedirectHandler()
        opener = urllib2.build_opener(redirect_handler,cookie_handler)
        urlopened = opener.open(request)
        fileopened = open(suggested_path, 'wb')
        fileopened.write(urlopened.read())
        fileopened.close()
        opener.close()
        
        # urllib.urlretrieve(url, suggested_path)
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


if __name__ == '__main__':
    import sys
    sys.path.append('..')

import traceback
import wx
import os
import re
import locale
import cookielib
#from BeautifulSoup import *
from pieconfig.paths import *
from pieobject import *
from cms import *
from pieobject.website import add_website
from piescrape.execfn import suggest_title

cj = cookielib.CookieJar()
prefenc = locale.getpreferredencoding()
user_agent = 'Mozilla/Linux'
headers = { 'User-Agent' : user_agent }

class PieScraper:
    '''Functionality for scraping web pages'''
    def __init__(self, 
                 url, 
                 default_author='', 
                 author_is_corporate=False, 
                 category_phrase='',
                 tag_append_behaviour=0,
                 notify_window=None
                 ):
        print 'PieScraper.__init__'
        self._origin_url = url
        self._default_author = default_author
        self._author_is_corporate = author_is_corporate
        self._category_phrase = category_phrase
        self._tag_append_behaviour = tag_append_behaviour
        self._notify_window = notify_window
        self._further_init_done = False

    def _further_init(self):
        '''do further crunching of the url, involves crunching, will usually
        happen as a consequence of threaded methods. Also updates the website
        memory with new details of the website being scraped.'''
        print 'PieScraper._further_init'
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        self._urlopener = opener.open(self._origin_url)
        # self._urlopener = urllib2.urlopen(self._origin_url)
        self._cmstype = DiagnoseCMS(self._urlopener)

    def set_context(self, 
                    default_author='', 
                    author_is_corporate=False, 
                    category_phrase=''):
        '''Reset user-given context'''
        self._default_author = default_author
        self._author_is_corporate = author_is_corporate
        self._category_phrase = category_phrase

    def get_cmstype(self):
        '''return the cmstype being used'''
        return self._cmstype

    def get_page_context(self):
        '''get relevant context of the url in question'''
        if not self._further_init_done:
            self._further_init()
        co = GetContextObject(self._urlopener, self._cmstype)
        # in old money this was:        translate_non_alphanumerics(readup.title.string.split(' - ')[0][:100].strip())
        ttl = co.get_context_title().strip()
        print 'PieScraper.get_page_context:', ttl
        return ttl #in future maybe return a more complex object

    def snarf_urls(self, threaded=False, propagate_to=None, types=('pdf', 'word_doc')):
        '''return a tuple of pieobjects representing all the in-situ
        potential documents of a page. Arguments:
         - threaded - bool - is this being run threaded?
         - propagate_to - is data to be propagated to somewhere'''
        print 'PieScraper.snarf_urls'
        if not self._further_init_done:
            self._further_init()
        co = GetContextObject(self._urlopener, self._cmstype)
        try:
            urlz = co.get_links(types=types, baseurl=self._origin_url)
        except:
            traceback.print_exc()
            raise Exception
        ret = PieObjectStore()
        ret.set_session_data(
            # store information about the session in the ostore
            url=self._origin_url,
            cmstype=self._cmstype,
            defaultauthor=self._default_author,
            authiscorporate=self._author_is_corporate,
            category_phrase=self._category_phrase,
            tag_append_behaviour=self._tag_append_behaviour
            )
        print 'wunn...'
        for linky in urlz:
            ob = PieObject()
            try:
                ob.add_aspect_onweb(
                    url=linky['Url'],
                    pageurl=self._origin_url,
                    linktext=linky['LinkText'],
                    defaultauthor=self._default_author,
                    category_phrase=self._category_phrase,
                    author_is_corporate=self._author_is_corporate,
                    tags=linky['Tags']
                    )
                ob.title = suggest_title(
                    linky['SuggestedTitle'],
                    self._category_phrase,
                    self._tag_append_behaviour)
            except Exception, exc:
                traceback.print_exc()
            ret.Add(ob)
        print 'twwwoooo....'
        if threaded: #use callback if threaded, otherwise just return data
            if not self._notify_window:
                raise Exception, 'No window nominated to pass data to'
            wx.CallAfter(
                self._notify_window.Callback_FillPane, 
                ret, propagate_to #args - data and propagate dest'n
                )
        else:
            return ret

    def snarf_documents(self):
        '''return all the documents on the page'''
        pass

    def cache_locally(self):
        '''cache the web page'''
        pass

    def gen_siteinfo(self):
        '''generate site info for database'''


if __name__ == '__main__':
    ps = PieScraper('file:test.pdf')
    ps.gen_test_data()
    ps.set_context('Fnee', True, 'Giant huge big large')
    # print ps.hdtw()
    # print ps.get_context()

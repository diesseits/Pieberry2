if __name__ == '__main__':
    import sys
    sys.path.append('..')

import wx
import os
import re
import locale
from BeautifulSoup import *
from pieconfig.paths import *
from cms import *

prefenc = locale.getpreferredencoding()
user_agent = 'Mozilla/Linux'
headers = { 'User-Agent' : user_agent }

class PieScraper:
    '''Functionality for scraping web pages'''
    def __init__(self, 
                 url, 
                 default_author='', 
                 author_is_corporate=False, 
                 category_phrase=''):
        self._origin_url = url
        self._default_author = default_author
        self._author_is_corporate = author_is_corporate
        self._category_phrase = category_phrase
        self._further_init()

    def _further_init(self):
        '''do further crunching of the url'''
        self._urlopener = urllib2.urlopen(self._origin_url)
        self._cmstype = DiagnoseCMS(self._urlopener)
        print 'PieScraper._further_init - self._cmstype:', self._cmstype

    def set_context(self, 
                    default_author='', 
                    author_is_corporate=False, 
                    category_phrase=''):
        '''Reset user-given context'''
        self._default_author = default_author
        self._author_is_corporate = author_is_corporate
        self._category_phrase = category_phrase

    def get_page_context(self):
        '''get relevant context of the url in question'''
        co = GetContextObject(self._urlopener, self._cmstype)
        # in old money this was:        translate_non_alphanumerics(readup.title.string.split(' - ')[0][:100].strip())
        ttl = co.get_context_title()
        print 'PieScraper.get_page_context:', ttl

    def snarf_urls(self):
        '''return all the urls on a page (& type)'''
        pass

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

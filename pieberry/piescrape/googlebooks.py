import sys, wx, datetime

from string import join
from threading import Thread

from pieberry.pieconfig.identity import *
from pieberry.pieconfig.schemas import *
from pieberry.pieconfig.config import PIE_CONFIG
from pieberry.pieobject import PieObject, PieObjectStore
from pieberry.ui.events import PieGoogleSearchEvent

from pprint import pprint
from gdata import service
import gdata.books.service
import gdata.books


__author__ = 'raifsarcich@gmail.com (Raif Sarcich)'
__apikey__ = 'AIzaSyAUARZHHM23uSIDgBLGiM_GCJO7rRNobYk'
__source__ = 'Raif Sarcich - %s - %s' % (PIE_APPNAME, PIE_VERSION)
__nresults__ = 20

def fmt_authors(authlist):
    if len(authlist) == 0: return _(u'None')
    elif len(authlist) == 1: return authlist[0]
    elif len(authlist) == 2: return join(authlist, _(u'and'))
    else: return join([join(authlist[:-1], ', '), authlist[-1]], _(u'and')) 

def suggest_type(fmt, bd):
    '''Suggest a bibtex type based on google's format field and
    whether appropriate fields are filled'''
    if fmt.lower() in bibtexfields.keys():
        canuse = True
        for f in bibtexfields[fmt][0]:
            if not f in bd.keys():
                canuse = False
                break
        if canuse:
            return fmt
        else:
            return PIE_CONFIG.get('Format', 'default_bibtex_entry_type')
    else:
        return PIE_CONFIG.get('Format', 'default_bibtex_entry_type')

def pieberry_from_google(gdict, url):
    '''Take a google books dict and produce a PieObject'''
    bd = {
        'author': fmt_authors(gdict['authors']),
        'title': gdict['title'],
        'BibData_DatePublished': datetime.datetime.strptime(
            gdict['date'], '%Y-%m-%d')}
    if gdict.has_key('description') and gdict['description']:
        bd['BibData_Annote'] = gdict['description']
    if gdict.has_key('publishers') and gdict['publishers']:
        bd['BibData_Publisher'] = join(gdict['publishers'], ' - ')
    bd['BibData_Type'] = suggest_type(gdict['format'], bd)
    bd['WebData_Url'] = url
    obj = PieObject()
    obj.add_aspect_bibdata(**bd)
    return obj

class GoogleBooksScraper(Thread):
    '''A class to scrape Google Books for relevant titles to a search string'''
    def __init__(self, search_string, notify_window):
        Thread.__init__(self)
        self.service = gdata.books.service.BookService(
            email=__author__, source=__source__)
        self.search_string = search_string
        self.notify_window = notify_window

    def run(self):
        feed = self.service.search(self.search_string)#, max_results=__nresults__)
        ostore = PieObjectStore()
        for item in feed.entry:
            obj = pieberry_from_google(item.to_dict(), item.GetHtmlLink().href)
            ostore.Add(obj)
        newevt = PieGoogleSearchEvent(
            ostore=ostore,
            notify_window=self.notify_window)
        wx.PostEvent(self.notify_window, newevt)


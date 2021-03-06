import sys, wx, datetime

#from unicode import join
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
    authlist = [unicode(a, 'utf8') for a in authlist]
    if len(authlist) == 0: return _(u'None')
    elif len(authlist) == 1: return authlist[0]
    elif len(authlist) == 2: return u' and '.join(authlist)
    else: return u' and '.join([u', '.join(authlist[:-1]), authlist[-1]])
    # elif len(authlist) == 2: return join(authlist, _(u' and '))
    # else: return join([join(authlist[:-1], ', '), authlist[-1]], _(u' and ')) 

def suggest_type(gd, bd):
    '''Suggest a bibtex type based on google's format field and
    whether appropriate fields are filled'''
    if gd.has_key('format'): fmt = gd['format']
    else: return PIE_CONFIG.get('Format', 'default_bibtex_entry_type')
    if fmt.lower() in bibtexfields.keys():
        # canuse = True
        # for f in bibtexfields[fmt][0]:
        #     if not f in bd.keys():
        #         canuse = False
        #         break
        # if canuse:
        #     return fmt
        # else:
        #     return PIE_CONFIG.get('Format', 'default_bibtex_entry_type')
        return fmt
    else:
        return PIE_CONFIG.get('Format', 'default_bibtex_entry_type')

def pieberry_from_google(gdict, url):
    '''Take a google books dict and produce a PieObject'''
    bd = {
        'title': unicode(gdict['title'], 'utf8'),
        }
    if gdict.has_key('authors') and gdict['authors']:
        bd['author'] = fmt_authors(gdict['authors'])
    try:
        bd['BibData_DatePublished'] = datetime.datetime.strptime(
            gdict['date'], '%Y-%m-%d')
    except:
        try:
            bd['BibData_DatePublished'] = datetime.datetime.strptime(
                gdict['date'], '%Y')
        except:
            bd['BibData_DatePublished'] = datetime.datetime.today()
    if gdict.has_key('description') and gdict['description']:
        bd['BibData_Abstract'] = unicode(gdict['description'], 'utf8')
    if gdict.has_key('publishers') and gdict['publishers']:
        bd['BibData_Publisher'] = u' - '.join([unicode(p, 'utf8') for p in gdict['publishers']])
    googlekey = ''
    for i, k in gdict['identifiers']:
        if i == 'ISBN': 
            bd['PhysData_ISBN'] = k
        elif i == 'google_id':
            googlekey = k
    bd['BibData_Type'] = suggest_type(gdict, bd)
    bd['WebData_Url'] = url
    obj = PieObject()
    obj.GoogleData = {'google_id': googlekey}
    if gdict.has_key('subjects'):
        obj.GoogleData['subjects'] = gdict['subjects']
    if gdict.has_key('thumbnail'):
        obj.GoogleData['thumbnail'] = gdict['thumbnail']
    if gdict.has_key('summary'):
        obj.GoogleData['summary'] = gdict['summary']
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
        print 'Running google books scraper'
        feed = self.service.search(self.search_string, max_results='20')#, max_results=__nresults__)
        print 'Feed obtained'
        self.proc_results(feed)

    def proc_results(self, feed):
        ostore = PieObjectStore()
        for item in feed.entry:
            idict = item.to_dict()
            obj = pieberry_from_google(idict, item.GetHtmlLink().href)
            ostore.Add(obj)
        print 'Feed parsed into objects'
        newevt = PieGoogleSearchEvent(
            ostore=ostore,
            notify_window=self.notify_window)
        wx.PostEvent(self.notify_window, newevt)
        print 'Objects posted'

class GoogleBooksISBNScraper(GoogleBooksScraper):
    '''Subclassed GoogleBooksScraper to deal specifically with ISBN
    searches, for the benefit of the zbar functionality'''
    def __init__(self, isbn, notify_window):
        self.isbn = isbn
        GoogleBooksScraper.__init__(self, None, notify_window)

    def run(self):
        feed = self.service.search_by_keyword(isbn=self.isbn)
        self.proc_results(feed)


# feed.to_dict() Dict  will look something like this:

# <gdata.books.service.BookService object at 0x116f4d0>
# {'annotation': 'http://www.google.com/books/feeds/users/me/volumes',
#  'authors': ['Franz Kafka'],
#  'date': '1998-10-06',
#  'description': 'The story of Karl Rossman who, after an embarrassing sexual misadventure with a servant girl, is banished to America by his parents.',
#  'embeddability': 'not_embeddable',
#  'format': 'book',
#  'identifiers': [('google_id', 'VZoNdyYAweoC'),
#                  ('ISBN', '0749399511'),
#                  ('ISBN', '9780749399511')],
#  'info': 'http://books.google.com/books?id=VZoNdyYAweoC&dq=Kafka+America&as_brr=0&ie=ISO-8859-1&source=gbs_gdata',
#  'preview': 'http://books.google.com/books?id=VZoNdyYAweoC&dq=Kafka+America&as_brr=0&ie=ISO-8859-1&cd=1&source=gbs_gdata',
#  'publishers': ['Vintage Classics'],
#  'subjects': ['Literary Criticism'],
#  'thumbnail': 'http://bks6.books.google.com/books?id=VZoNdyYAweoC&printsec=frontcover&img=1&zoom=5&source=gbs_gdata',
#  'title': 'America',
#  'viewability': 'view_no_pages'}

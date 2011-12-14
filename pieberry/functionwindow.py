import wx
import pprint

from pieobject import *
from piescrape import *
from ui import BaseMainWindow
from pieconfig.globals import *



class FunctionMainWindow(BaseMainWindow):
    '''The main window with the actual programmatic functionality added. 
    
    Mit liebe und mit function.

     ..
    !!!!,

    '''

    def __init__(self, *args, **kwds):
        BaseMainWindow.__init__(self, *args, **kwds)

    def OnWebScrape(self, evt):
        print 'functionmainwindow.OnWebScrape'
        ts = PieScraper(
            url='file:piescrape/test.html',#evt.url,
            default_author=evt.author,
            author_is_corporate=evt.authoriscorporate,
            category_phrase=evt.catstring)
        #get rid of the following
        urlz = ts.snarf_urls()
        #pprint(urlz)
        self.OpenWebPane()
        pan = self.GetCurrentPane()
        for obj in urlz:
            pan.AddObject(obj)
        
    

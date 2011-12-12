import wx

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
        ts.get_page_context()
        
    

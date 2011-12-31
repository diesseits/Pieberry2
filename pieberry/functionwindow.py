import wx
import pprint
import thread

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
        self.OpenWebPane()
        pan = self.GetCurrentPane()
        ts = PieScraper(
            url='file:piescrape/test.html',#evt.url,
            default_author=evt.author,
            author_is_corporate=evt.authoriscorporate,
            category_phrase=evt.catstring,
            notify_window=self)
        thread.start_new_thread(ts.snarf_urls, (True, pan))
        
    def Callback_FillPane(self, ostore, propagate_window):
        '''Callback function to propagate data into a pane'''
        print 'FunctionMainWindow.Callback_FillPane'
        propagate_window.AddObjects(ostore)
        if self.WebPanel:
            self.WebPanel.LockPanel(False)

    

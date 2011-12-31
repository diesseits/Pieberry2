import wx
import pprint
import thread

from pieobject import *
from pieobject.paths import *
from piescrape import *
from piescrape.execfn import *
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
        print 'FunctionMainWindow.Callback_FillPane()'
        propagate_window.AddObjects(ostore)
        if self.WebPanel:
            self.WebPanel.LockPanel(False)

    def Callback_AddToPane(self, obj, propagate_window):
        '''Stub - in future, maybe add one object at a time as the
        web scraper does its business in the background'''
        pass

    def OnWebPaneDownload(self, evt):
        '''Functionality for downloading/caching scraped docs'''
        print 'functionwindow.OnWebPaneDownload()'
        if len(evt.ostore) == 0:
            wx.MessageBox(_('No items are selected'), style=wx.ICON_ERROR)
            return
        evt.ostore.set_session(get_session())
        for obj in evt.ostore:
            storepath = suggest_path_cache_fromweb(obj)
            #download_file(url=obj.Url(), suggested_path=storepath)
            obj.add_aspect_cached_from_web(storepath)
            print 'Downloading', obj
        wx.CallAfter( #deletepage seems finicky about timing
            self.TabBook.DeletePage,
            self.TabBook.GetPageIndex(evt.pane)
            )
        self.CloseUtilityPanes()
        self.OpenStagingPane(ostore=evt.ostore)

    
        

        

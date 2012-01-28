import wx
import pprint
import thread
import time
import traceback
import shutil, os, os.path

from pieobject import *
from pieobject.paths import *
from piescrape import *
from piescrape.execfn import *
from ui import BaseMainWindow
from ui.events import *
from pieconfig.globals import *
from atomise import *


class FunctionMainWindow(BaseMainWindow):
    '''The main window with the actual programmatic functionality added. 
    
    Mit liebe und mit function.

     ..
    !!!!,

    '''

    def __init__(self, *args, **kwds):
        BaseMainWindow.__init__(self, *args, **kwds)
        EVT_PIE_DOWNLOAD_NOTIFY(self, self.Callback_DownloadNotification)

    def OnWebScrape(self, evt):
        print 'functionmainwindow.OnWebScrape'
        self.OpenWebPane()
        pan = self.GetCurrentPane()
        ts = PieScraper(
            url=evt.url,#'file:piescrape/test.html',#evt.url,
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
        wx.CallAfter( #deletepage seems finicky about timing
            self.TabBook.DeletePage,
            self.TabBook.GetPageIndex(evt.pane)
            )
        self.CloseUtilityPanes()
        self.OpenStagingPane()
        self.GetCurrentPane().Disable() #don't let no stupids happen
        thread.start_new_thread(self._thread_downloads, (evt.ostore, self.GetCurrentPane()))

    def _thread_downloads(self, ostore, notify_window):
        '''threaded method called by OnWebPaneDownload'''
        for obj in ostore:
            storepath = suggest_path_cache_fromweb(obj)
            newevt = PieDownloadNotifyEvent(
                msgtype='start', 
                obj=obj, 
                notify_window=notify_window)
            wx.PostEvent(self, newevt)
            # TESTING
            # time.sleep(0.25)
            msgtype = download_file(url=obj.Url(), suggested_path=storepath)
            if msgtype == 'success':
                obj.add_aspect_cached_from_web(storepath)
                filemetadata = {}
                # try:
                filemetadata = scan_file_metadata(obj)
                # except:
                #     traceback.print_exc()
                #     msgtype='warn'
                # print 'filemetadata', filemetadata
                obj.filemetadata = filemetadata
            else:
                obj.add_aspect_failed_download()
            newevt = PieDownloadNotifyEvent(
                msgtype=msgtype, 
                obj=obj, 
                notify_window=notify_window)
            wx.PostEvent(self, newevt)
        wx.CallAfter(notify_window.Enable)

    def Callback_DownloadNotification(self, evt):
        '''Do when a download has begun or terminated'''
        if evt.msgtype in ('start', 'spin'):
            print 'Download started:', evt.obj
            # wx.CallAfter(evt.notify_window.AddObject, evt.obj)
            # store the currently downloading item reference for
            # future reference
            self.downloadingitem = evt.notify_window.AddObject(
                evt.obj, msgtype='spin')
        else:
            print 'Download stopped - condition', evt.msgtype
            outcome = evt.msgtype
            evt.notify_window.DownloadDone(
                self.downloadingitem,
                outcome)

    def OnPrefetch(self, evt):
        '''happens when the webpanel wants to prefetch something'''
        thread.start_new_thread(self._thread_prefetch, (evt.url,))

    def _thread_prefetch(self, url):
        ts = PieScraper(
            url=url,
            notify_window=self)
        tag = ts.get_page_context()
        newevt = PiePrefetchDoneEvent(tag=tag)
        wx.PostEvent(self, newevt)

    def OnCommitStaged(self, evt):
        ostore = evt.ostore
        for obj in ostore:
            path = obj.FileData_FullPath
            dpath = suggest_path_store_fromweb(obj)
            if not os.path.isdir(os.path.dirname(dpath)):
                os.makedirs(os.path.dirname(dpath))
            print 'COPYING: %s to %s' % (path, dpath)
            os.renames(path, dpath)
            obj.add_aspect_stored(dpath)
        session = Session()
        session.add_all(ostore)
        session.commit()
        self.CloseUtilityPanes()
        # wx.MessageBox(
        #     'Successfully added %d items to your library' % len(evt.ostore))
        wx.CallAfter( #deletepage seems finicky about timing
            self.TabBook.DeletePage,
            self.TabBook.GetPageIndex(evt.pane)
            )

    def DoSearch(self, evt):
        print 'Actor: doSearch: %s' % evt.searchtext
        session = Session()
        self.OpenSearchPane(caption=evt.searchtext[:20])
        searchpane = self.GetCurrentPane()
        query = build_query(evt.searchtext.strip(), session)
        ostore = PieObjectStore()
        for instance in query:
            ostore.Add(instance)
        ostore.instantiate_nonstored()
        searchpane.AddObjects(ostore)
        wx.CallAfter(self.CloseUtilityPanes)

    def OnDesktopProcess(self, evt):
        '''Clean out desktop, move to cache dir, present results'''
        self.OpenAtomisePane()
        atompane = self.GetCurrentPane()
        session = get_session('desktop')
        ostore = scan_desktop()
        ostore.set_session(session)
        for obj in ostore:
            storepath = suggest_path_cache_fromdesktop(obj)
            os.renames(obj.FileData_FullPath, storepath)
            obj.add_aspect_cached_from_desktop(storepath)
            obj.remove_aspect('ondesktop')
        atompane.AddObjects(ostore)
        


# TODO: move to a search module

from sqlalchemy import or_

def build_query(t, session):
    return session.query(
        PieObject
        ).filter(or_(
            PieObject.title.like('%' + t + '%'), 
            PieObject.author.like('%' + t + '%'), 
            PieObject.WebData_Url.like('%' + t + '%')
            ))#.order_by(PieObject.title)
        

                
            


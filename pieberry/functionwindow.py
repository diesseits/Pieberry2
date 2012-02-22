import wx
import pprint
import thread
import time
import traceback
import shutil, os, os.path


from pieobject import *
from pieobject.paths import *
from piescrape import *
from piescrape.execfn import download_file
from ui import BaseMainWindow, PieBibEditDialog
from ui.events import *
from ui.timers import FileIndexTimer
from pieconfig import PIE_CONFIG
from pieconfig.globalvars import *
from pieoutput.bibtex import *
from atomise import *
from searches import *

import piemeta
import piefiles

if PYNOTIFY: import pynotify

import pieobject.website as website

class FunctionMainWindow(BaseMainWindow):
    '''The main window with the actual programmatic functionality added. 
    
    Mit liebe und mit funktion.

     ..
    !!!!,

    '''

    def __init__(self, *args, **kwds):
        BaseMainWindow.__init__(self, *args, **kwds)
        EVT_PIE_DOWNLOAD_NOTIFY(self, self.Callback_DownloadNotification)
        self.indextimer = FileIndexTimer(self)
        self.indextimer.Start(
            PIE_CONFIG.getint('Internal', 'minutes_between_file_indexes') * 60 * 1000)

    def OnWebScrape(self, evt):
        print 'functionmainwindow.OnWebScrape'
        self.OpenWebPane()
        pan = self.GetCurrentPane()
        self.StatusBar.SetStatusText(_('Finding documents...'))
        ts = PieScraper(
            url=evt.url,#'file:piescrape/test.html',#evt.url,
            default_author=evt.author,
            author_is_corporate=evt.authiscorporate,
            category_phrase=evt.catstring,
            tag_append_behaviour=evt.catbehaviour,
            notify_window=self)
        thread.start_new_thread(ts.snarf_urls, (True, pan))
        wx.CallAfter(self.ToggleWebPanel)

    def OnWebPaneRefresh(self, evt):
        pan = self.GetCurrentPane()
        pan.ClearAllData()
        assert pan.paneltype == 'WebListPanel'
        self.StatusBar.SetStatusText(_('Finding documents...'))
        ts = PieScraper(
            url=evt.session_data['url'],
            default_author=evt.session_data['defaultauthor'],
            author_is_corporate=evt.session_data['authiscorporate'],
            category_phrase=evt.session_data['category_phrase'],
            tag_append_behaviour=evt.session_data['tag_append_behaviour'],
            notify_window=self)
        thread.start_new_thread(ts.snarf_urls, (True, pan), {'types': evt.types})
        
    def Callback_FillPane(self, ostore, propagate_window):
        '''Callback function to propagate data into a pane'''
        print 'FunctionMainWindow.Callback_FillPane()'
        propagate_window.AddObjects(ostore)
        if self.WebPanel:
            self.WebPanel.LockPanel(False)
        self.StatusBar.SetStatusText('')

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
        self.StatusBar.SetStatusText(_('Downloading files...'))
        evt.ostore.set_session(get_session())
        website.add_website(
            url=evt.ostore.url,
            defaultauthor=evt.ostore.defaultauthor,
            authiscorporate=evt.ostore.authiscorporate,
            tag_append_behaviour=evt.ostore.tag_append_behaviour,
            cmstype=evt.ostore.cmstype)
        wx.CallAfter( #deletepage seems finicky about timing
            self.TabBook.DeletePage,
            self.TabBook.GetPageIndex(evt.pane)
            )
        self.CloseUtilityPanes()
        self.OpenStagingPane()
        self.GetCurrentPane().Disable() #don't let no stupids happen
        if evt.download == True:
            thread.start_new_thread(
                self._thread_downloads, (evt.ostore, self.GetCurrentPane()))
        else:
            self._not_threaded_reference(evt.ostore, self.GetCurrentPane())

    def _not_threaded_reference(self, ostore, notify_window):
        '''unthreaded method called by OnWebPaneDownload'''
        for obj in ostore:
            newevt = PieDownloadNotifyEvent(
                msgtype='normal',
                obj=obj,
                notify_window=notify_window)
            wx.PostEvent(self, newevt)
        wx.CallAfter(notify_window.Enable)
        wx.CallAfter(self.StatusBar.SetStatusText, '')

    def _thread_downloads(self, ostore, notify_window):
        '''threaded method called by OnWebPaneDownload'''
        for obj in ostore:
            storepath = suggest_path_cache_fromweb(obj)
            newevt = PieDownloadNotifyEvent(
                msgtype='start', 
                obj=obj, 
                notify_window=notify_window)
            wx.PostEvent(self, newevt)
            msgtype = download_file(url=obj.WebData_Url, 
                                    suggested_path=storepath)
            if msgtype == 'success':
                obj.add_aspect_cached_from_web(storepath)
                try:
                    filemetadata = piemeta.get_metadata_for_aspect(obj)
                except:
                    traceback.print_exc()
                    msgtype='warn'
                    filemetadata = {}
                obj.filemetadata = filemetadata
                if filemetadata.has_key('creation_date'):
                    obj.FileData_DateCreated = filemetadata['creation_date']
            else:
                obj.add_aspect_failed_download()
            newevt = PieDownloadNotifyEvent(
                msgtype=msgtype, 
                obj=obj, 
                notify_window=notify_window)
            wx.PostEvent(self, newevt)
        wx.CallAfter(notify_window.Enable)
        wx.CallAfter(self.StatusBar.SetStatusText, '')

    def Callback_DownloadNotification(self, evt):
        '''Do when a download has begun or terminated'''
        if evt.msgtype == 'normal':
            evt.notify_window.AddObject(evt.obj, msgtype='success')
        elif evt.msgtype in ('start', 'spin'):
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
            self.downloadingitem = None

    def OnPrefetch(self, evt):
        '''happens when the webpanel wants to prefetch something'''
        self.StatusBar.SetStatusText('Pre-fetching website information...')
        ws = website.lookup_website(evt.url)
        thread.start_new_thread(self._thread_prefetch, (evt.url, ws))

    def _thread_prefetch(self, url, ws):
        '''Threaded actions for prefetching website info'''
        ts = PieScraper(
            url=url,
            notify_window=self)
        success = True
        try:
            tag = ts.get_page_context()
        except:
            traceback.print_exc()
            # unreadable url ...
            print 'unreadable url'
            tag = None
            success = False
        if ws:
            auth = ws.DefaultAuthor
            iscorp = ws.DefaultAuthorIsCorporate
            tagbehav = ws.TagAppendBehaviour
        else:
            auth = None
            iscorp = None
            tagbehav = None
        newevt = PiePrefetchDoneEvent(success=success, tag=tag, 
                                      auth=auth, iscorp=iscorp,
                                      tagbehav=tagbehav)
        wx.PostEvent(self, newevt)
        wx.CallAfter(self.StatusBar.SetStatusText, '')

    def OnCommitStaged(self, evt):
        self.StatusBar.SetStatusText(_('Storing staged files'))
        ostore = evt.ostore
        progress_dialog = wx.ProgressDialog( 
            'Committing to the database', 
            '________________________________________', maximum = len(ostore) )
        counter = 1
        for ref, obj in ostore.GetNext(): # move files - if no file, continue
            progress_dialog.Update(counter, 'Adding: %s' % obj.Title())
            if not obj.has_aspect('cached'): continue
            if obj.has_aspect('onweb'):
                # test if this has been downloaded/referenced before
                no_dupes = session.query(PieObject).filter(
                    PieObject.WebData_Url == obj.WebData_Url).count()
                if no_dupes > 0:
                    dia = wx.MessageDialog(
                        self, 
                        _('''You have downloaded "%s" before.\nDo you still want to add it to your library?''' % obj.Title().strip('. ,-:')), 
                        style=wx.YES|wx.NO)
                    ans = dia.ShowModal()
                    if ans == wx.ID_NO:
                        ostore.Del(ref)
            # Write metadata to file if possible
            if PIE_CONFIG.getboolean('Format', 'write_pdf_metadata'):
                piemeta.write_metadata_to_object(obj)
            path = obj.FileData_FullPath
            dpath = suggest_path_store_fromweb(obj)
            if not os.path.isdir(os.path.dirname(dpath)):
                os.makedirs(os.path.dirname(dpath))
            print 'COPYING: %s to %s' % (path, dpath)
            os.renames(path, dpath)
            obj.add_aspect_stored(dpath)
            counter += 1
        # session = Session()
        session.add_all(ostore)
        ostore.set_aspect_saved()
        session.commit()
        progress_dialog.Destroy()
        self.CloseUtilityPanes()
        self.StatusBar.SetStatusText('')
        wx.CallAfter( #deletepage seems finicky about timing
            self.TabBook.DeletePage,
            self.TabBook.GetPageIndex(evt.pane)
            )

    def OnEditedBibData(self, evt):
        '''Handle user editing an item'''
        print 'Edited', evt.obj
        # Recommit object if it's already in the db
        if evt.obj.has_aspect('saved'):
            session.commit()
        # Update the ui reflecting changes
        pan = self.GetCurrentPane()
        pan.UpdateObject(evt.obj)
        if self.ContextPane:
            self.ContextPane.SetObject(evt.obj)
        # TODO: Rewrite metadata, rehome file

    def OnContextPanelUpdate(self, evt):
        '''Handle update of metadata from context panel'''
        evt.obj.StatData_Favourite = evt.favourite
        print evt.obj.StatData_Favourite
        if evt.obj.has_aspect('saved'):
            session.commit()
        pan = self.GetCurrentPane()
        pan.UpdateObject(evt.obj)

    def OnCreateNewBibObj(self, evt):
        '''Handle creation of a new user-created bibliography entry
        from scratch'''
        obj = PieObject()
        edwin = PieBibEditDialog(obj, self)
        # edwin.Bind(
        #     EVT_PIE_BIB_EDIT, self.OnEditedBibData)
        res = edwin.ShowModal()
        if not res == wx.ID_OK:
            return
        self.OpenStagingPane()
        pan = self.GetCurrentPane()
        obj = edwin.obj
        pan.AddObject(obj)

    def DoSearch(self, evt):
        print 'Actor: doSearch: %s' % evt.searchtext
        if len(evt.searchtext) < 3: return
        self.StatusBar.SetStatusText(_('Searching for "%s"' % evt.searchtext))
        # session = Session()
        # query = build_query(evt.searchtext.strip(), session)
        query = build_query_simple(
            evt.origin,
            evt.searchtext,
            evt.fields,
            session)
        ostore = PieObjectStore()
        for instance in query:
            ostore.Add(instance)
        if len(ostore) == 0:
            # wx.MessageBox(_('No matches found'))
            self.StatusBar.SetStatusText(_('No matches found'))
            wx.CallAfter(self.CloseUtilityPanes)
            return
        if evt.fields == 'filename':
            self.OpenFilePane(caption=evt.searchtext[:20])
        else:
            self.OpenSearchPane(caption=evt.searchtext[:20])
        searchpane = self.GetCurrentPane()
        ostore.instantiate_nonstored()
        searchpane.AddObjects(ostore)
        self.StatusBar.SetStatusText('')
        wx.CallAfter(self.CloseUtilityPanes)

    def OnDesktopProcess(self, evt):
        '''Clean out desktop, move to cache dir, present results'''
        self.StatusBar.SetStatusText(_('Scanning desktop'))
        self.OpenAtomisePane()
        atompane = self.GetCurrentPane()
        previous_files = scan_previous_desktops()
        session = get_session('desktop')
        ostore = scan_desktop()
        ostore.set_session(session)
        for obj in ostore:
            storepath = suggest_path_cache_fromdesktop(obj)
            #can't use os.renames - it'll delete the desktop directory
            if not os.path.isdir(os.path.dirname(storepath)):
                os.makedirs(os.path.dirname(storepath))
            os.rename(obj.FileData_FullPath, storepath)
            obj.add_aspect_cached_from_desktop(storepath)
            obj.remove_aspect('ondesktop')
        for p_ostore in previous_files: ostore.Extend(p_ostore)
        atompane.AddObjects(ostore)
        self.StatusBar.SetStatusText('')
        
    def OnDesktopFileFile(self, evt):
        '''Add desktop items to the system'''
        print 'functionwindow.OnDesktopFileFile'
        #move the file
        obj = evt.obj
        # session = Session()
        if obj.has_aspect('bibdata'):
            storepath = suggest_path_store_with_bibdata(obj)
            if PIE_CONFIG.getboolean('Format', 'write_pdf_metadata'):
                piemeta.write_metadata_to_object(obj)
        else:
            storepath = suggest_path_store_fromdesktop(
                obj, 
                evt.dest_folder,
                evt.new_fn)
        os.renames(obj.FileData_FullPath, storepath)
        obj.add_aspect_stored(storepath)
        obj.add_aspect_saved()
        session.add(obj)
        session.commit()
        wx.CallAfter(evt.notify_window.Callback_onGoFile, evt.rowid)

    def onSaveBibs(self, evt):
        '''Export bibliography to file nominated in config via pybtex'''
        exporter = PiePybtexWriter()
        # handle time-of-use export file selection
        bibfilepath = PIE_CONFIG.get('Profile', 'bibliography_file')
        if not PIE_CONFIG.getboolean('Profile', 'export_bibtex'):
            fdia = wx.FileDialog(self, wildcard="*.bib", style=wx.FD_SAVE)
            res = fdia.ShowModal()
            if res == wx.ID_CANCEL: return
            bibfilepath = fdia.GetPath()
            exporter.setPath(bibfilepath)
        for obj in query_favourites(session):
            msg = exporter.addEntry(obj)
            if msg:
                wx.MessageBox(msg, _('There is a problem'), wx.ICON_EXCLAMATION)
        try:
            exporter.write()
        except Exception, exc:
            traceback.print_exc()
            wx.MessageBox(unicode(exc), _('Error'), wx.ICON_ERROR)
            return
        msg = _('Successfully exported bibliography to %s' % bibfilepath)
        self.StatusBar.SetStatusText(msg)
        if PYNOTIFY:
            n = pynotify.Notification(
                'Pieberry', msg, os.path.join(IMGDIR, 'pie_48.png'))
            n.show()
                
    def onClose(self, evt):
        self.indextimer.Stop()
        session.commit()
        sys.exit()

    def OnStartIndexer(self):
        '''Begin a threaded file indexer session'''
        indexer = piefiles.PieFileIndexer(self)
        self.Bind(EVT_PIE_FILE_INDEX, self.DisplayIndexerStatus)
        self.Bind(EVT_PIE_FILE_INDEX_FINISHED, self.OnIndexerFinished)
        indexer.start()
            
    def OnIndexerFinished(self, evt):
        '''Receive notification that the indexer is done'''
        session.expire_all()
        self.StatusBar.SetStatusText(_('File indexing finished'))


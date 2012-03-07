import wx
import pprint
import thread
import time
import traceback
import shutil, os, os.path

from sqlalchemy.exc import IntegrityError

from pieberry.pieobject import *
from pieberry.pieobject.paths import *
from pieberry.piescrape import *
from pieberry.piescrape.execfn import download_file
from pieberry.ui.altmainwindow import BaseMainWindow 
from pieberry.ui.editdialog import PieBibEditDialog
from pieberry.ui.events import *
from pieberry.ui.timers import FileIndexTimer
from pieberry.ui.settingsdialog import PieSettingsDialog
from pieberry.pieconfig.config import PIE_CONFIG
from pieberry.pieconfig.globalvars import *
from pieberry.pieoutput.bibtex import *
from pieberry.atomise import *
from pieberry.searches import *

import pieberry.piedb as piedb
import pieberry.piemeta as piemeta
import pieberry.piefiles as piefiles
import pieberry.pieinput as pieinput

if PYNOTIFY: import pynotify

import pieberry.pieobject.website as website

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

    def OnGBPaneReference(self, evt):
        '''Cut down version of web pane download for google books'''
        if len(evt.ostore) == 0:
            wx.MessageBox(_('No items are selected'), style=wx.ICON_ERROR)
            return
        self.StatusBar.SetStatusText(_('Downloading files...'))
        evt.ostore.set_session(get_session())
        wx.CallAfter( #deletepage seems finicky about timing
            self.TabBook.DeletePage,
            self.TabBook.GetPageIndex(evt.pane)
            )
        self.CloseUtilityPanes()
        self.OpenStagingPane()
        self.GetCurrentPane().Disable() #don't let no stupids happen
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
        print 'making piescraper'
        ts = PieScraper(
            url=url,
            notify_window=self)
        success = True
        print 'trying to get context'
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
        counter = 0
        for ref, obj in ostore.GetNext(): 
            counter += 1
            progress_dialog.Update(counter, 'Adding: %s' % obj.Title())
            # handle need to input a unique bibtex key:
            if obj.has_aspect('bibdata'):
                bkey = self._find_unique_key(obj)
                # if there's already a key in the db same as the user
                # set key, query the user whether to proceed (the item
                # may be a dupe).
                if (bkey != obj.BibData_Key) and obj.BibData_Key:
                    dia = wx.MessageDialog(self, _('''A record with a BibTeX key of %s already exists. Change to %s? (If 'no', then the record won't be added).''' % (obj.BibData_Key, bkey)), style=wx.YES|wx.NO)
                    ans = dia.ShowModal()
                    if ans == wx.ID_NO:
                        ostore.Del(ref)
                    obj.BibData_Key = bkey
                elif (bkey != obj.BibData_Key) and not obj.BibData_Key:
                    obj.BibData_Key = bkey
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
            # All activity past this point pertains to files 
            if not obj.has_aspect('cached'): continue
            # Write metadata to file if possible
            if PIE_CONFIG.getboolean('Format', 'write_pdf_metadata'):
                piemeta.write_metadata_to_object(obj)
            path = obj.FileData_FullPath
            dpath = suggest_path_store_fromweb(obj)
            # I don't trust windows filesystems
            if sys.platform == 'win32':
                dpath = dpath.encode('ascii', 'ignore')
            # Ensure relevant directory exists
            if not os.path.isdir(os.path.dirname(dpath)):
                os.makedirs(os.path.dirname(dpath))
            print 'COPYING: %s to %s' % (path, dpath)
            assert os.path.exists(path)
            assert os.path.exists(os.path.dirname(dpath))
            shutil.move(path, dpath)
            # os.renames(path, dpath)
            obj.add_aspect_stored(dpath)
        # session = Session()
        ostore.set_aspect_saved()
        session.add_all(ostore)
        # time.sleep(1)
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
            try:
                session.commit()
            except IntegrityError:
                # Probably means the key isn't unique - tell the user
                # to fix the damn thing
                wx.MessageBox(_('Database Integrity Error - You are probably trying to use a BibTeX key that is already in use. Changes made to this item have been rolled back. Apologies.'), style=wx.ICON_ERROR)
                session.rollback()
                return
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
        try:
            pan = self.GetCurrentPane()
            pan.UpdateObject(evt.obj)
        except:
            print 'No panel to refer to'

    def OnNotesPaneUpdate(self, evt):
        evt.obj.notes = evt.htmlcontent
        if evt.obj.has_aspect('saved'):
            session.commit()
        wx.CallAfter(self.CloseCurrentPane)

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

    def DoGoogleSearch(self, evt):
        from pieberry.piescrape.googlebooks import GoogleBooksScraper
        wx.CallAfter(self.CloseUtilityPanes)
        if len(evt.searchtext) < 4: return
        self.OpenGBListPane()
        pan = self.GetCurrentPane()
        pan.Disable()
        self.StatusBar.SetStatusText(_('Searching for books'))
        gbs = GoogleBooksScraper(evt.searchtext, pan)
        pan.Bind(EVT_PIE_GOOGLE_SEARCH, self.Callback_GoogleSearch)
        gbs.start()

    def Callback_GoogleSearch(self, evt):
        self.StatusBar.SetStatusText('')
        evt.notify_window.AddObjects(evt.ostore)
        evt.notify_window.Enable()

    def DoSearch(self, evt):
        # print 'Actor: doSearch: %s' % evt.searchtext
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

    def OnDesktopProcessGen(self, evt):
        '''Clean out desktop, move to cache dir, present results'''

        
        self.StatusBar.SetStatusText(_('Scanning desktop'))
        self.OpenAtomisePane()
        atom_pane = self.GetCurrentPane()
        
        osession = get_session('desktop')
        
        progress_count = 0
        for obj, maxi in scan_desktop_gen():
            if progress_count == 0:
                progress_dialog = wx.ProgressDialog(
                    _('Cleaning up desktop'),
                    '____________________________________________',
                    maximum = maxi)

            # Keep track of the object 
            obj.set_session(osession)

            # Do the file movement stuff
            storepath = suggest_path_cache_fromdesktop(obj)
            if not os.path.isdir(os.path.dirname(storepath)):
                os.makedirs(os.path.dirname(storepath))
            try:
                os.rename(obj.FileData_FullPath, storepath)
            except:
                traceback.print_exc()
                progress_count += 1
                progress_dialog.Update(progress_count, obj.FileData_FileName)
                atom_pane.AddObject(obj)
                continue

            # Update object aspects
            obj.add_aspect_cached_from_desktop(storepath)
            obj.remove_aspect('ondesktop')
            
            # Update ui
            progress_count += 1
            progress_dialog.Update(progress_count, obj.FileData_FileName)
            atom_pane.AddObject(obj)
        
        # Make a progress dialog even if no files on desktop
        if progress_count == 0:
            progress_dialog = wx.ProgressDialog(
                _('Cleaning up desktop'),
                '____________________________________________',
                maximum = 1)

        progress_dialog.UpdatePulse(_('Fetching cached files'))
        
        for obj in scan_previous_desktops_gen():
            atom_pane.AddObject(obj)
            progress_dialog.Pulse()
        
        progress_dialog.Destroy()
        self.StatusBar.SetStatusText('')

    def OnDesktopProcess(self, evt):
        '''Clean out desktop, move to cache dir, present results'''
        self.StatusBar.SetStatusText(_('Scanning desktop'))
        self.OpenAtomisePane()
        atompane = self.GetCurrentPane()
        previous_files = scan_previous_desktops()
        session = get_session('desktop')
        ostore = scan_desktop()
        ostore.set_session(session)
        for idx, obj in ostore.GetNext():
            storepath = suggest_path_cache_fromdesktop(obj)
            #can't use os.renames - it'll delete the desktop directory
            if not os.path.isdir(os.path.dirname(storepath)):
                os.makedirs(os.path.dirname(storepath))
            try:
                os.rename(obj.FileData_FullPath, storepath)
            except:
                traceback.print_exc()
                ostore.Del(idx)
                continue
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
            # # this is a hack to make things more legible
            # if PIE_CONFIG.getboolean('Format', 'atom_title_hack'):
            #     obj.title = "%s [%s]" % (obj.title, evt.new_fn)
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
        print 'Closing'
        self.indextimer.Stop()
        session.commit()
        try:
            piedb.close_piedb_engine()
        except:
            traceback.print_exc()
        finally:
            sys.exit()

    def OnStartIndexer(self, evt=0):
        '''Begin a threaded file indexer session'''
        indexer = piefiles.PieFileIndexer(self)
        self.Bind(EVT_PIE_FILE_INDEX, self.DisplayIndexerStatus)
        self.Bind(EVT_PIE_FILE_INDEX_FINISHED, self.OnIndexerFinished)
        indexer.start()
            
    def OnIndexerFinished(self, evt):
        '''Receive notification that the indexer is done'''
        session.expire_all()
        self.StatusBar.SetStatusText(_('File indexing finished'))

    def onConfig(self, evt):
        dia = PieSettingsDialog(self)
        dia.Bind(EVT_PIE_LOCATION_CHANGED, self.OnChangeLocation)
        dia.ShowModal()
        dia.Destroy()

    def OnChangeLocation(self, evt):
        wx.MessageBox(_('As you have changed the database location, Pieberry will need to close and be restarted for the changes to come into effect. Closing now (no data will be lost).'))
        self.onClose(1)
        # Totally failed at trying to dynamically close and reopen the database. 

        # self.StatusBar.SetStatusText(_("Changing Pieberry's storage location"))
        # newloc = PIE_CONFIG.get('Profile', 'rootdir')
        # assert os.path.isdir(newloc)
        # self.CloseAllPanes()
        # piedb.close_piedb_engine()
        # # session.close()
        # # piedb.del_all()
        # piedb.create_piedb_engine(newloc)
        # init_storage_location(PIE_CONFIG.get('Profile', 'rootdir'))
        # create_directories()
        # self.StatusBar.SetStatusText(_("Changed Pieberry's storage location to %s" % newloc))

    def _find_unique_key(self, obj, bibkey=None):
        '''Set a valid unique BibTeX key for an object'''
        if obj.BibData_Key and not bibkey:
            bibkey = obj.BibData_Key
        validkey = False
        while validkey == False:
            if not bibkey:
                bibkey = autogen_bibtex_key(obj)
                assert type(bibkey) == unicode
            validkey = query_unique_key(session, bibkey)
            if not validkey:
                bibkey = increment_bibtex_key(bibkey)
        return bibkey

    def OnImportBibtex(self, evt):
        fdia = wx.FileDialog(self, wildcard="*.bib", style=wx.FD_OPEN, defaultDir=PIE_CONFIG.get('Profile', 'rootdir'))
        res = fdia.ShowModal()
        if res == wx.ID_CANCEL: return
        self.StatusBar.SetStatusText(_('Importing from file'))
        bibfilepath = fdia.GetPath()
        from pieberry.pieutility.bibtex import autogen_bibtex_key
        progress_dialog = wx.ProgressDialog( 
            _('Importing from file'), 
            _('Reading %s' % bibfilepath), maximum = 1)
        progress_dialog.Pulse()
        ents = pieinput.pybtex_entries_from_file(bibfilepath)
        self.OpenStagingPane()
        pan = self.GetCurrentPane()
        count = 0
        for bibkey, ent in ents.items():
            try:
                obj = pieinput.pybtex_to_pieberry(bibkey, ent)
                pan.AddObject(obj)
                count += 1
                progress_dialog.UpdatePulse('%d items added' % count)
            except:
                traceback.print_exc()
                print 'Unhandleable entry with key: %s' % bibkey
        progress_dialog.Destroy()
        self.StatusBar.SetStatusText(
            _('Imported %d items from %s.' % (count, bibfilepath)))
                
    def OnViewMostRecent(self, evt):
        '''Bring up a view of the most recently added db items'''
        self.OpenSearchPane(caption=_('Recent Documents'))
        pan = self.GetCurrentPane()
        q = query_most_recent(
            session,
            PIE_CONFIG.getint('Internal', 'number_new_docs_to_show'))
        pan.AddObjects(q)

    def OnViewFlagged(self, evt):
        print 'wot ho'
        self.OpenSearchPane(caption=_('Flagged Documents'))
        pan = self.GetCurrentPane()
        q = query_flagged(session)
        pan.AddObjects(q)

    def OnFlagChecked(self, evt):
        assert evt.flagkey in ('StatData_Favourite', 'StatData_FollowUpFlag')
        assert type(evt.flagval) == bool
        if evt.flagkey == 'StatData_FollowUpFlag':
            evt.obj.flag_followup(evt.flagval)
        else:
            setattr(evt.obj, evt.flagkey, evt.flagval)
        session.commit()
        pan = self.GetCurrentPane()
        pan.UpdateObject(evt.obj)
            
        

import wx
import wx.lib.agw.aui as wxauip
# import wx.lib.agw.flatnotebook as fnb
import wx.aui as wxaui
import os, sys

from pieberry.ui.events import *
from pieberry.ui.searchpanel import *
from pieberry.ui.webpanel import *
from pieberry.ui.contextpanel import *
from pieberry.ui.listpanels import *
from pieberry.ui.actor import PieActor
from pieberry.pieconfig.globalvars import *
from pieberry.pieconfig.paths import IMGDIR
from pieberry.pieconfig.config import PIE_CONFIG
from pieberry.atomise.atomise_widget import atomWidget
from pieberry.ui.notespane import NotesPane
from pieberry.pieconfig.globalvars import ZBAR

class BaseMainWindow(wx.Frame, PieActor):
    def __init__(self, *args, **kwds):
        # begin wxGlade: GladeMainWindow.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)

        self._mgr = wxaui.AuiManager(self)
        self.ContextPane = BetterContextPanel(self, -1)

        # self.TabPane = NBPanel(self)
        # self.TabBook = self.TabPane.nb
        self.TabBook = wxauip.AuiNotebook(self, -1)
        if PIE_CONFIG.get('Internal', 'tab_art') == 'simple':
            self.TabBook.SetArtProvider(wxauip.AuiSimpleTabArt())
        # self.TabBook.SetMinSize((500,500))
        # self.TabBook = fnb.FlatNotebook(self, -1)
        self.StatusBar = wx.StatusBar(self, -1)
        if sys.platform != 'win32':
            self.StatusBar.SetStatusStyles([1, wx.SB_FLAT])

        # Menu Bar
        menuBar = wx.MenuBar()
        fileMenu = wx.Menu()
        toolMenu = wx.Menu()
        locateMenu = wx.Menu()
        gatherMenu = wx.Menu()
        viewMenu = wx.Menu()
        helpMenu = wx.Menu()
        atomMenu = wx.Menu()
        debugMenu = wx.Menu()
        self.menu_savebibs = wx.MenuItem(
            fileMenu, -1, 
            _('&Export Bibliography\tCtrl-shift-b'),
            _('Export all starred items with bibliographic data to a BibTeX file'))
        self.menu_savebibs.SetBitmap(
            wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_MENU, (16, 16)))
        # self.menu_discard = wx.MenuItem(
        #     fileMenu, -1, 
        #     _('&Discard Bibliography Changes'), _('Discard'))
        self.menu_quit = wx.MenuItem(
            fileMenu, -1, _('&Quit\tCtrl-q'), _('Quit'))
        self.menu_quit.SetBitmap(
            wx.ArtProvider.GetBitmap(wx.ART_QUIT, wx.ART_MENU))
        self.menu_rescan = wx.MenuItem(
            fileMenu, -1, _('&Index folders now'), 
            _('Make Pieberry scan and index files and folders in your Pieberry directory'))
        self.menu_config = wx.MenuItem(fileMenu, -1, _('S&ettings'), _('Configure Pieberry'))
        self.menu_about = wx.MenuItem(helpMenu, -1, _('&About'), _('About Pieberry'))
        # self.menu_pageref = wx.MenuItem(
        #     toolMenu, 
        #     -1, 
        #     _('Create &reference for top-level page'), 
        #     _('Reference'))
        self.menu_emptyref = wx.MenuItem(
            toolMenu, 
            -1, 
            _('&Create new (empty) bibliography entry\tCtrl-n'), 
            _('Bring up a dialog to allow you to enter bibliographic data'))
        self.menu_emptyref.SetBitmap(
            wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_MENU))
        self.menu_manual = wx.MenuItem(helpMenu, -1, _('&Manual'))
        self.menu_atom_process = wx.MenuItem(
            atomMenu, -1, _('&Process files from desktop\tCtrl-m'), _('Get documents off your desktop and sort them into folders'))
        self.menu_atom_process.SetBitmap(
            wx.Bitmap(os.path.join(IMGDIR, 'ic_broom16.png')))
        # self.menu_atom_settings = wx.MenuItem(
        #     atomMenu, -1, _('Desktop cleaner settings'), 'Settings')
        self.menu_find = wx.MenuItem(
            toolMenu, -1, _('&Find items in bibliography\tCtrl-f'), _('Search Pieberry\'s internal database'))
        self.menu_find.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_FIND, wx.ART_MENU))
        self.menu_find_in_folders = wx.MenuItem(
            toolMenu, -1, _('F&ind your files\tCtrl-shift-f'), _('Search database by file name'))
        self.menu_find_in_folders.SetBitmap(
            wx.ArtProvider.GetBitmap(wx.ART_FIND, wx.ART_MENU))
        self.menu_scan_web_page = wx.MenuItem(
            gatherMenu, -1, _('Scan &web page for documents\tCtrl-w'), _('Read and find links to documents on a given web page'))
        self.menu_scan_web_page.SetBitmap(
            wx.Bitmap(os.path.join(IMGDIR, 'ic_globe16.png')))
        self.menu_google_books = wx.MenuItem(
            gatherMenu, -1, _('Search &Google Books\tCtrl-g'), _('Search Google Books for relevant references'))
        self.menu_google_books.SetBitmap(
            wx.Bitmap(os.path.join(IMGDIR, 'ic_google16.png')))
        if ZBAR:
            self.menu_scan_barcode = wx.MenuItem(
                gatherMenu, -1, _('Scan ISBN &barcode\tCtrl-shift-b'), _('Scan a book\'s barcode containing its ISBN and look it up in Google Books'))
        self.menu_import_bibtex = wx.MenuItem(
            gatherMenu, -1, _('&Import from BibTeX file'), _('Import biblographic items from a BibTeX file'))
        self.menu_import_bibtex.SetBitmap(
            wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_MENU))
        self.menu_filter = wx.MenuItem(
            locateMenu, -1, _('Fil&ter\tCtrl-t'), _('Filter the items in the current view'))
        self.menu_toggle_context = wx.MenuItem(
            viewMenu, -1, _('&Toggle context panel'))
        self.menu_toggle_context.SetCheckable(True)
        self.menu_view_starred = wx.MenuItem(
            viewMenu, -1, _('View &important documents\tCtrl-1'))
        self.menu_view_flagged = wx.MenuItem(
            viewMenu, -1, _('View documents &flagged for review/follow-up\tCtrl-2'))
        self.menu_view_recentact = wx.MenuItem(
            viewMenu, -1, _('View most r&ecently used documents\tCtrl-3'))
        self.menu_view_recent = wx.MenuItem(
            viewMenu, -1, _('View most &recently added documents\tCtrl-4'))
        self.menu_view_folders = wx.MenuItem(
            viewMenu, -1, _('&View folders and contents\tCtrl-5'))

        # BEGIN debug menu
        if PIE_CONFIG.getboolean('Internal', 'show_debug_ui'):
            self.menu_debug_addwebpane = wx.MenuItem(
                debugMenu, -1, _('Add Web Pane'))
            self.menu_debug_addbibpane = wx.MenuItem(
                debugMenu, -1, _('Add Bib Pane'))
            self.menu_debug_adddlpane = wx.MenuItem(
                debugMenu, -1, _('Add Pane with dld items'))
            self.menu_debug_addatompane = wx.MenuItem(
                debugMenu, -1, _('Add Pane with desktop items'))
            self.menu_debug_forcescan = wx.MenuItem(
                debugMenu, -1, _('Force scan of folders'))
            self.menu_debug_notespane = wx.MenuItem(
                debugMenu, -1, 'Add notes pane')
            self.menu_debug_rectifyobjectrels = wx.MenuItem(
                debugMenu, -1, 'Rectify object relationships'
                )
            debugMenu.AppendItem(self.menu_debug_addatompane)
            debugMenu.AppendItem(self.menu_debug_adddlpane)
            debugMenu.AppendItem(self.menu_debug_addwebpane)
            debugMenu.AppendItem(self.menu_debug_addbibpane)
            debugMenu.AppendItem(self.menu_debug_forcescan)
            debugMenu.AppendItem(self.menu_debug_notespane)
            debugMenu.AppendItem(self.menu_debug_rectifyobjectrels)
            self.Bind(wx.EVT_MENU, self.DebugAddNotesPane, self.menu_debug_notespane)
            self.Bind(wx.EVT_MENU, self.DebugAddAtomisePane, 
                      self.menu_debug_addatompane)
            self.Bind(wx.EVT_MENU, self.DebugAddDownloadedPane, 
                      self.menu_debug_adddlpane)
            self.Bind(wx.EVT_MENU, self.DebugAddWebPane, self.menu_debug_addwebpane)
            self.Bind(wx.EVT_MENU, self.DebugAddBibPane, self.menu_debug_addbibpane)
            self.Bind(wx.EVT_MENU, self.DebugForceScan, self.menu_debug_forcescan)
            self.Bind(wx.EVT_MENU, self.DebugRectifyObjectRels, self.menu_debug_rectifyobjectrels)
            # END debug menu

        fileMenu.AppendItem(self.menu_savebibs)
        # fileMenu.AppendItem(self.menu_discard)
        fileMenu.AppendItem(self.menu_config)
        # fileMenu.AppendItem(self.menu_atom_settings)
        fileMenu.AppendItem(self.menu_rescan)
        fileMenu.AppendSeparator()
        fileMenu.AppendItem(self.menu_quit)
        helpMenu.AppendItem(self.menu_manual)
        helpMenu.AppendItem(self.menu_about)
        # gatherMenu.AppendItem(self.menu_pageref)
        locateMenu.AppendItem(self.menu_find)
        locateMenu.AppendItem(self.menu_find_in_folders)
        locateMenu.AppendItem(self.menu_filter)
        gatherMenu.AppendItem(self.menu_scan_web_page)
        gatherMenu.AppendItem(self.menu_google_books)
        if ZBAR:
            gatherMenu.AppendItem(self.menu_scan_barcode)
        gatherMenu.AppendSeparator()
        gatherMenu.AppendItem(self.menu_emptyref)
        gatherMenu.AppendItem(self.menu_import_bibtex)
        gatherMenu.AppendSeparator()
        gatherMenu.AppendItem(self.menu_atom_process)
        viewMenu.AppendItem(self.menu_toggle_context)
        viewMenu.AppendSeparator()
        viewMenu.AppendItem(self.menu_view_starred)
        viewMenu.AppendItem(self.menu_view_flagged)
        viewMenu.AppendItem(self.menu_view_recentact)
        viewMenu.AppendItem(self.menu_view_recent)
        viewMenu.AppendSeparator()
        viewMenu.AppendItem(self.menu_view_folders)
        menuBar.Append(fileMenu, _('&File'))
        menuBar.Append(gatherMenu, _('&Gather'))
        menuBar.Append(locateMenu, _('&Locate'))
        menuBar.Append(viewMenu, _('&View'))
        menuBar.Append(helpMenu, _('&Help'))
        if PIE_CONFIG.getboolean('Internal', 'show_debug_ui'): menuBar.Append(debugMenu, _('&Debug'))
        self.SetMenuBar(menuBar)
        self.SetAutoLayout(True)

        self.Bind(wx.EVT_MENU, self.onFind, self.menu_find)
        self.Bind(wx.EVT_MENU, self.onFindInFolders, self.menu_find_in_folders)
        self.Bind(wx.EVT_MENU, self.OnDesktopProcessGen, self.menu_atom_process)
        # self.Bind(wx.EVT_MENU, self.onDesktopSettings, self.menu_atom_settings)
        self.Bind(wx.EVT_MENU, self.onSaveBibs, self.menu_savebibs)
        self.Bind(wx.EVT_MENU, self.onClose, self.menu_quit)
        wx.EVT_CLOSE(self, self.onClose)
        self.Bind(wx.EVT_MENU, self.onConfig, self.menu_config)
        self.Bind(wx.EVT_MENU, self.onAbout, self.menu_about)
        # self.Bind(wx.EVT_MENU, self.onDiscard, self.menu_discard)
        # self.Bind(wx.EVT_MENU, self.onPageReference, self.menu_pageref)
        self.Bind(wx.EVT_MENU, self.OnCreateNewBibObj, self.menu_emptyref)
        self.Bind(wx.EVT_MENU, self.onShowManual, self.menu_manual)
        self.Bind(wx.EVT_MENU, self.ToggleWebPanel, self.menu_scan_web_page)
        self.Bind(wx.EVT_MENU, self.ToggleFilterPanel, self.menu_filter)
        self.Bind(wx.EVT_MENU, self.ToggleContextPanel, self.menu_toggle_context)
        self.Bind(wx.EVT_MENU, self.OnImportBibtex, self.menu_import_bibtex)
        self.Bind(wx.EVT_MENU, self.OnViewMostRecent, self.menu_view_recent)
        self.Bind(wx.EVT_MENU, self.OnViewFlagged, self.menu_view_flagged)
        self.Bind(wx.EVT_MENU, self.OnViewRecentlyInteracted, self.menu_view_recentact)
        self.Bind(wx.EVT_MENU, self.OnViewStarred, self.menu_view_starred)
        self.Bind(wx.EVT_MENU, self.OnViewFolders, self.menu_view_folders)
        self.Bind(wx.EVT_MENU, self.OnStartIndexer, self.menu_rescan)
        self.Bind(wx.EVT_MENU, self.ToggleGoogleSearchPanel, self.menu_google_books)
        if ZBAR:
            self.Bind(wx.EVT_MENU, self.OnScanBarcode, self.menu_scan_barcode)
        # self.menu_savebibs.Enable(False)
        # self.menu_discard.Enable(False)


        # Menu Bar end

        self.__set_properties()
        self.__do_layout()
        self._do_bindings()

        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: GladeMainWindow.__set_properties
        self.SetTitle("Pieberry")
        _icon = wx.EmptyIcon()
        if sys.platform == 'win32':
            _icon.CopyFromBitmap(wx.Bitmap(os.path.join(IMGDIR, 'pie_16.png')))
        else:
            _icon.CopyFromBitmap(wx.Bitmap(os.path.join(IMGDIR, 'pieberry.ico'), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.SetSize((862, 546))
        # end wxGlade
        self.SearchPanel = None
        self.WebPanel = None
        self.FilterPanel = None
        self.GoogleSearchPanel = None

    def __do_layout(self):
        self._mgr.AddPane(
            self.TabBook, 
            wxaui.AuiPaneInfo().Center().CloseButton(False).Gripper(False), 
            _("Tab Book"))
        self._mgr.AddPane(
            self.ContextPane, 
            wxaui.AuiPaneInfo().Right().MinSize((200,200)).Floatable(False).CaptionVisible(True),
            _("Context"))
        self.menu_toggle_context.Check()
        self.ContextPane.Bind(wxaui.EVT_AUI_PANE_CLOSE, self.menu_toggle_context.Toggle)
        self._mgr.Update()
        # self.TabBook.SetMinSize(self.TabPane.sizer.GetSize())
        self.OpenIntroPane()
        

    def _do_bindings(self):
        self.TabBook.Bind(wxaui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.onChangeTab)
        self.ContextPane.Bind(EVT_PIE_CONTEXT_PANEL_UPDATE, 
                              self.OnContextPanelUpdate)

    def GetPaneIdxOfType(self, panetype):
        '''Get the indexes of all panes with a certain paneltype'''
        paneidxs = range(self.TabBook.GetPageCount())
        ret = []
        for i in paneidxs:
            p = self.TabBook.GetPage(i)
            if p.paneltype == panetype:
                ret.append(i)
        return ret

    def ClosePanesOfTypes(self, *panetypes):
        '''Closes panes which .paneltypes match arbitrary args'''
        for ptype in panetypes:
            [ self.TabBook.DeletePage(i) for i in self.GetPaneIdxOfType(ptype) ]

    def CloseCurrentPane(self, evt=None):
        panid = self.TabBook.GetSelection()
        self.TabBook.DeletePage(panid)

    def CloseAllPanes(self):
        paneidxs = range(self.TabBook.GetPageCount())
        for i in paneidxs:
            self.TabBook.DeletePage(i)

    def CloseUtilityPanes(self, event=None):
        '''close the search and filter panels'''
        if self.FilterPanel: 
            self.ToggleFilterPanel()
            if hasattr(event, 'OldSelection'): 
                self.ClearFiltering(event.OldSelection)
                # that's probably too hackish
        if self.SearchPanel: self.ToggleSearchPanel()
        if self.GoogleSearchPanel: self.ToggleGoogleSearchPanel()

    def onChangeTab(self, event):
        # print event.OldSelection
        # print 'onChangeTab captures new: %s old: %s' % (
        #     self.TabBook.GetPage(event.Selection).paneltype,
        #     self.TabBook.GetPage(event.OldSelection).paneltype
        #     )
        self.CloseUtilityPanes(event)

    def onNewContextToShow(self, evt):
        # print 'mainwindow: onNewContextToShow'
        self.ContextPane.SetObject(evt.pieobject)

    def GetCurrentPane(self):
        try:
            return self.TabBook.GetPage(self.TabBook.GetSelection())
        except:
            raise Exception, 'Cannot select panel'

    def ClearFiltering(self, pageref=None):
        '''Clear filtering on current page'''
        if pageref == None:
            pan = self.TabBook.GetPage(self.TabBook.GetSelection())
        else:
            pan = self.TabBook.GetPage(pageref)
        pan.Repopulate()

    def ToggleContextPanel(self, evt):
        pan = self._mgr.GetPane(self.ContextPane)
        if pan.IsShown() and not evt.IsChecked():
            pan.Hide()
            self._mgr.Update()
        elif evt.IsChecked() and not pan.IsShown():
            pan.Show()
            self._mgr.Update()

    def ToggleFilterPanel(self, evt=0):
        print 'ToggleFilterPanel'
        if self.FilterPanel:
            spinfo = self._mgr.GetPane(self.FilterPanel)
            self._mgr.ClosePane(spinfo)
            self._mgr.Update()
            self.ClearFiltering()
            return
        if self.GetCurrentPane().paneltype not in (
            'FileListPanel', 
            'WebListPanel',
            'BibListPanel',
            'BibImpPanel',
            'StagingListPanel',
            'GBListPanel',
            'RecentView',
            'RecentActView',
            'StarredView',
            'FlaggedView'):
            if evt: evt.Skip()
            return
        if self.SearchPanel:
            spinfo = self._mgr.GetPane(self.SearchPanel)
            self._mgr.ClosePane(spinfo)
        self.FilterPanel = FilterToolsPanel(self)
        self._mgr.AddPane(
            self.FilterPanel, 
            wxaui.AuiPaneInfo().Bottom().MinSize((300,50)).Floatable(False).Caption(_('Filter Current View')).DestroyOnClose(True)
            )
        self._mgr.Update()
        self.FilterPanel.Bind(EVT_PIE_SEARCH_EVENT, self.GetCurrentPane().onFilterView)

    def ToggleSearchPanel(self, evt=0, origin=None, field=None):
        if self.SearchPanel:
            spinfo = self._mgr.GetPane(self.SearchPanel)
            self._mgr.ClosePane(spinfo)
            self._mgr.Update()
            return
        if self.FilterPanel:
            spinfo = self._mgr.GetPane(self.FilterPanel)
            self._mgr.ClosePane(spinfo)
            self.ClearFiltering()
        self.SearchPanel = SearchToolsPanel(self, origin, field)
        self._mgr.AddPane(
            self.SearchPanel, 
            wxaui.AuiPaneInfo().Bottom().MinSize((300,50)).Floatable(False).Caption(_('New Search')).DestroyOnClose(True)
            )
        self._mgr.Update()
        self.SearchPanel.Bind(EVT_PIE_SEARCH_EVENT, self.DoSearch)

    def ToggleWebPanel(self, evt=0):
        if self.WebPanel:
            wpinfo = self._mgr.GetPane(self.WebPanel)
            self._mgr.ClosePane(wpinfo)
            self._mgr.Update()
            return
        self.WebPanel = WebScrapePanel(self)
        self._mgr.AddPane(
            self.WebPanel, 
            wxaui.AuiPaneInfo().Top().MinSize((300,120)).Floatable(False).DestroyOnClose(True)
            )
        self.WebPanel.Bind(EVT_PIE_SCRAPE_EVENT, self.OnWebScrape)
        self.WebPanel.Bind(EVT_PIE_PREFETCH_START, self.OnPrefetch)
        self.Bind(EVT_PIE_PREFETCH_DONE, self.WebPanel.onPrefetchResult)
        self._mgr.Update()

    def ToggleGoogleSearchPanel(self, evt=0):
        if self.WebPanel: self.ToggleWebPanel()
        if self.GoogleSearchPanel:
            spinfo = self._mgr.GetPane(self.GoogleSearchPanel)
            self._mgr.ClosePane(spinfo)
            self._mgr.Update()
            return
        if self.FilterPanel:
            spinfo = self._mgr.GetPane(self.FilterPanel)
            self._mgr.ClosePane(spinfo)
            self.ClearFiltering()
        self.GoogleSearchPanel = PlainSearchPanel(self)
        self._mgr.AddPane(
            self.GoogleSearchPanel, 
            wxaui.AuiPaneInfo().Top().MinSize((300,50)).Floatable(False).Caption(_('Search Google Books')).DestroyOnClose(True)
            )
        self._mgr.Update()
        self.GoogleSearchPanel.Bind(EVT_PIE_SEARCH_EVENT, self.DoGoogleSearch)

    def OpenSearchPane(self, evt=0, ostore=None, caption=_('Search Result')):
        # if self.SearchPanel:
        tab = BibListPanel(self.TabBook)
        tab.Bind(EVT_PIE_LIST_SELECTION_EVENT, self.onNewContextToShow)
        tab.Bind(EVT_PIE_FLAG_CHECKED, self.OnFlagChecked)
        self.TabBook.AddPage(
            tab, caption, select=True, 
            bitmap = wx.ArtProvider.GetBitmap(wx.ART_FIND, wx.ART_MENU))

    def OpenStagingPane(self, evt=0, ostore=None, caption=_('Staging ground')):
        tab = StagingListPanel(self.TabBook)
        tab.Bind(EVT_PIE_LIST_SELECTION_EVENT, self.onNewContextToShow)
        tab.Bind(EVT_PIE_COMMIT_STAGED, self.OnCommitStaged)
        self.TabBook.AddPage(tab, caption, select=True)
        if ostore:
            tab.AddObjects(ostore)

    def OpenWebPane(self, evt=0, ostore=None, caption=_('Web Scrape')):
        tab = WebListPanel(self.TabBook)
        tab.Bind(EVT_PIE_LIST_SELECTION_EVENT, self.onNewContextToShow)
        tab.Bind(EVT_PIE_DOWNLOAD, self.OnWebPaneDownload)
        tab.Bind(EVT_PIE_REFRESH_WEB_LIST, self.OnWebPaneRefresh)
        self.TabBook.AddPage(
            tab, caption, select=True,
            bitmap = wx.Bitmap(os.path.join(IMGDIR, 'ic_globe16.png')))

    def OpenGBListPane(self, evt=0, ostore=None, caption=_('Google Books Results')):
        tab = GBListPanel(self.TabBook)
        tab.Bind(EVT_PIE_LIST_SELECTION_EVENT, self.onNewContextToShow)
        tab.Bind(EVT_PIE_DOWNLOAD, self.OnGBPaneReference)
        self.TabBook.AddPage(
            tab, caption, select=True,
            bitmap = wx.Bitmap(os.path.join(IMGDIR, 'ic_google16.png')))

    def OpenBibImpPane(self, evt=0, ostore=None, caption=_('BibTeX Import')):
        tab = BibImpPanel(self.TabBook)
        tab.Bind(EVT_PIE_LIST_SELECTION_EVENT, self.onNewContextToShow)
        tab.Bind(EVT_PIE_COMMIT_STAGED, self.OnCommitStaged)
        self.TabBook.AddPage(tab, caption, select=True)
        if ostore:
            tab.AddObjects(ostore)

    def OpenFilePane(self, evt=0, ostore=None, caption=_('Files')):
        tab = FileListPanel(self.TabBook)
        tab.Bind(EVT_PIE_LIST_SELECTION_EVENT, self.onNewContextToShow)
        tab.Bind(EVT_PIE_FLAG_CHECKED, self.OnFlagChecked)
        self.TabBook.AddPage(
            tab, caption, select=True,
            bitmap = wx.ArtProvider.GetBitmap(wx.ART_FIND, wx.ART_MENU))

    def OpenAtomisePane(self, evt=0, ostore=None, caption=_('Desktop items')):
        tab = atomWidget(self.TabBook, -1)
        tab.Bind(EVT_ATOM_FILE_FILE, self.OnDesktopFileFile)
        tab.Bind(EVT_PIE_CLOSE_PANE, self.CloseCurrentPane)
        self.TabBook.AddPage(
            tab, caption, select=True, 
            bitmap=wx.Bitmap(os.path.join(IMGDIR, 'ic_broom16.png')))

    def OpenNotesPane(self, obj=None, caption=_('Notes')):
        caption = 'Notes: %s' % obj.Title()[:20]
        tab = NotesPane(self.TabBook, -1)
        self.TabBook.AddPage(
            tab, caption, select=True,
            bitmap = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_MENU))
        if not obj: return
        tab.SetObject(obj)
        # tab.Bind(wxauip.EVT_AUINOTEBOOK_PAGE_CLOSED, tab.OnDone)
        tab.Bind(EVT_PIE_NOTES_PANE_UPDATE, self.OnNotesPaneUpdate)

    def OpenIntroPane(self):
        caption = _('Welcome to Pieberry')
        tab = IntroPanel(self.TabBook, -1)
        self.TabBook.AddPage(
            tab, caption, select=True,
            bitmap = wx.Bitmap(os.path.join(IMGDIR, 'pie_16.png'))
            )

    def OpenFolderPane(self):
        caption = _('Folders')
        tab = DirListPanel(self.TabBook, -1)
        self.TabBook.AddPage(
            tab, caption, select=True,
            bitmap = wx.ArtProvider.GetBitmap(wx.ART_FOLDER_OPEN, wx.ART_MENU))

    def DoSearch(self, evt):
        '''stub'''
        print 'altmainwindow.DoSearch'

    def OnCommitStaged(self, evt):
        '''stub'''
        print 'altmainwindow.OnCommitStaged'

    def OnWebScrape(self, evt):
        '''stub function for web scrape events'''
        print 'altmainwindow.OnWebScrape'

    def OnWebPaneDownload(self, evt):
        '''happens when user elects to download stuff from a web pane'''
        print 'altmainwindow.OnWebPaneDownload'

    def OnPrefetch(self, evt):
        '''happens when the webpanel wants to prefetch something'''
        print 'altmainwindow.OnPrefetch'

    def OnUpdateAtomChoices(self, evt):
        apanes = self.GetPaneIdxOfType('AtomPanel')
        [ self.TabBook.GetPage(p).OnSetDestinations(evt) for p in apanes ]

    def OnViewFolders(self, evt):
        self.OpenFolderPane()

# end of class GladeMainWindow


if __name__ == "__main__":
    import gettext
    gettext.install('pietest')
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = BaseMainWindow(None, -1, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()

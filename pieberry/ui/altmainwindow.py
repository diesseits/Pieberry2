import wx
import wx.lib.agw.aui as wxaui
#import wx.aui as wxaui

from events import *
from searchpanel import *
from webpanel import *
from contextpanel import *
from listpanels import BibListPanel, WebListPanel, FileListPanel
from actor import PieActor

class AltMainWindow(wx.Frame, PieActor):
    def __init__(self, *args, **kwds):
        # begin wxGlade: GladeMainWindow.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)

        self._mgr = wxaui.AuiManager(self)


        self.ContextPane = SimpleContextPanel(self, -1)
        self.TabBook = wxaui.AuiNotebook(self, -1)

        # Menu Bar
        menuBar = wx.MenuBar()
        fileMenu = wx.Menu()
        toolMenu = wx.Menu()
        locateMenu = wx.Menu()
        gatherMenu = wx.Menu()
        helpMenu = wx.Menu()
        atomMenu = wx.Menu()
        self.menu_savebibs = wx.MenuItem(
            fileMenu, -1, 
            '&Save Bibliography Changes') # [%s]\tCtrl-s' % os.path.basename(config.get('PBoptions', 'default_bibliography')), 'Save')
        self.menu_savebibs.SetBitmap(
            wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_MENU, (16, 16)))
        self.menu_discard = wx.MenuItem(
            fileMenu, -1, 
            '&Discard Bibliography Changes', 'Discard')
        self.menu_quit = wx.MenuItem(
            fileMenu, -1, '&Quit\tCtrl-q', 'Quit')
        self.menu_quit.SetBitmap(
            wx.ArtProvider.GetBitmap(wx.ART_QUIT, wx.ART_MENU))
        self.menu_config = wx.MenuItem(fileMenu, -1, 'S&ettings', 'Config')
        self.menu_about = wx.MenuItem(helpMenu, -1, '&About', 'About')
        self.menu_pageref = wx.MenuItem(
            toolMenu, 
            -1, 
            'Create &reference for top-level page', 
            'Reference')
        self.menu_emptyref = wx.MenuItem(
            toolMenu, 
            -1, 
            '&Create new (empty) bibliography entry\tCtrl-n', 
            'Newref')
        self.menu_emptyref.SetBitmap(
            wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_MENU))
        self.menu_manual = wx.MenuItem(helpMenu, -1, '&Manual')
        self.menu_find = wx.MenuItem(
            toolMenu, -1, '&Find items in bibliography\tCtrl-f', 'Find')
        self.menu_find.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_FIND, wx.ART_MENU))
        self.menu_atom_process = wx.MenuItem(
            atomMenu, -1, '&Process files from desktop\tCtrl-m', 'Process')
        # self.menu_atom_process.SetBitmap(
        #     wx.Bitmap(os.path.join(IMGDIR, 'ic_broom16.png')))
        self.menu_atom_settings = wx.MenuItem(
            atomMenu, -1, 'Desktop cleaner settings', 'Settings')
        self.menu_find_in_folders = wx.MenuItem(
            toolMenu, -1, 'F&ind your files\tCtrl-shift-f', 'Findall')
        self.menu_find_in_folders.SetBitmap(
            wx.ArtProvider.GetBitmap(wx.ART_FIND, wx.ART_MENU))
        self.menu_scan_web_page = wx.MenuItem(
            gatherMenu, -1, _('Scan &web page for documents\tCtrl-w'))
        self.menu_filter = wx.MenuItem(
            locateMenu, -1, _('Fi&lter\tCtrl-i'))

        fileMenu.AppendItem(self.menu_savebibs)
        fileMenu.AppendItem(self.menu_discard)
        fileMenu.AppendItem(self.menu_config)
        fileMenu.AppendItem(self.menu_atom_settings)
        fileMenu.AppendSeparator()
        fileMenu.AppendItem(self.menu_quit)
        helpMenu.AppendItem(self.menu_manual)
        helpMenu.AppendItem(self.menu_about)
        gatherMenu.AppendItem(self.menu_scan_web_page)
        gatherMenu.AppendItem(self.menu_emptyref)
        gatherMenu.AppendItem(self.menu_pageref)
        locateMenu.AppendItem(self.menu_find)
        locateMenu.AppendItem(self.menu_find_in_folders)
        locateMenu.AppendItem(self.menu_filter)
        gatherMenu.AppendItem(self.menu_atom_process)
        menuBar.Append(fileMenu, '&File')
        menuBar.Append(gatherMenu, _('&Gather'))
        menuBar.Append(locateMenu, _('&Locate'))
        # menuBar.Append(toolMenu, '&Tools')
        # menuBar.Append(atomMenu, '&Desktop cleaner')
        menuBar.Append(helpMenu, '&Help')
        self.SetMenuBar(menuBar)
        # self.SetAutoLayout(True)

        self.Bind(wx.EVT_MENU, self.onFind, self.menu_find)
        self.Bind(wx.EVT_MENU, self.onFindInFolders, self.menu_find_in_folders)
        self.Bind(wx.EVT_MENU, self.onDesktopProcess, self.menu_atom_process)
        self.Bind(wx.EVT_MENU, self.onDesktopSettings, self.menu_atom_settings)
        self.Bind(wx.EVT_MENU, self.onSaveBibs, self.menu_savebibs)
        self.Bind(wx.EVT_MENU, self.onClose, self.menu_quit)
        self.Bind(wx.EVT_MENU, self.onConfig, self.menu_config)
        self.Bind(wx.EVT_MENU, self.onAbout, self.menu_about)
        self.Bind(wx.EVT_MENU, self.onDiscard, self.menu_discard)
        self.Bind(wx.EVT_MENU, self.onPageReference, self.menu_pageref)
        self.Bind(wx.EVT_MENU, self.onEmptyReference, self.menu_emptyref)
        self.Bind(wx.EVT_MENU, self.onShowManual, self.menu_manual)
        self.Bind(wx.EVT_MENU, self.ShowWebPanel, self.menu_scan_web_page)
        self.Bind(wx.EVT_MENU, self.ShowFilterPanel, self.menu_filter)

        self.menu_savebibs.Enable(False)
        self.menu_discard.Enable(False)


        # Menu Bar end

        self.__set_properties()
        self.__do_layout()
        self._do_bindings()

        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: GladeMainWindow.__set_properties
        self.SetTitle("Pieberry II")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("/home/raif/development/v2Pieberry/pieberry/ui/pieberry.ico", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.SetSize((862, 546))
        # end wxGlade
        self.SearchPanel = None
        self.WebPanel = None
        self.FilterPanel = None

    def __do_layout(self):
        self._mgr.AddPane(
            self.TabBook, 
            wxaui.AuiPaneInfo().Center().CloseButton(False).Gripper(False), 
            "Tab Book")
        self._mgr.AddPane(
            self.ContextPane, 
            wxaui.AuiPaneInfo().Right().MinSize((200,200)).Floatable(False).CaptionVisible(True),
            _("Context"))
        self._mgr.Update()
        
        self.tab0 = BibListPanel(self.TabBook)
        self.tab1 = WebListPanel(self.TabBook)
        self.tab2 = FileListPanel(self.TabBook)

        self.TabBook.AddPage(self.tab0, "Bib Tab")
        self.TabBook.AddPage(self.tab1, "Web Tab")
        self.TabBook.AddPage(self.tab2, "File Tab")

        self.tab0.Bind(EVT_PIE_LIST_SELECTION_EVENT, self.onNewContextToShow)
        self.tab1.Bind(EVT_PIE_LIST_SELECTION_EVENT, self.onNewContextToShow)
        self.tab2.Bind(EVT_PIE_LIST_SELECTION_EVENT, self.onNewContextToShow)

    def _do_bindings(self):
        self.TabBook.Bind(wxaui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.onChangeTab)

    def onChangeTab(self, event): # wxGlade: GladeMainWindow.<event_handler>
        print "Event handler `onChangeTab' not implemented!"
        print self.TabBook.GetSelection()

    def onNewContextToShow(self, evt):
        # print 'mainwindow: onNewContextToShow'
        self.ContextPane.SetObject(evt.pieobject)

    def ShowFilterPanel(self, evt=0):
        if self.FilterPanel:
            spinfo = self._mgr.GetPane(self.FilterPanel)
            self._mgr.ClosePane(spinfo)
            self._mgr.Update()
            return
        if self.SearchPanel:
            spinfo = self._mgr.GetPane(self.SearchPanel)
            self._mgr.ClosePane(spinfo)
        self.FilterPanel = FilterToolsPanel(self)
        self._mgr.AddPane(
            self.FilterPanel, 
            wxaui.AuiPaneInfo().Bottom().MinSize((300,50)).Floatable(False).Caption(_('Filter')).DestroyOnClose(True)
            )
        self._mgr.Update()
        self.FilterPanel.Bind(EVT_PIE_SEARCH_EVENT, self.tab0.onFilterView)

    def ShowSearchPanel(self, evt=0):
        if self.SearchPanel:
            spinfo = self._mgr.GetPane(self.SearchPanel)
            self._mgr.ClosePane(spinfo)
            self._mgr.Update()
            return
        if self.FilterPanel:
            spinfo = self._mgr.GetPane(self.FilterPanel)
            self._mgr.ClosePane(spinfo)
        self.SearchPanel = SearchToolsPanel(self)
        self._mgr.AddPane(
            self.SearchPanel, 
            wxaui.AuiPaneInfo().Bottom().MinSize((300,50)).Floatable(False).Caption(_('Search')).DestroyOnClose(True)
            )
        self._mgr.Update()
        
    def ShowWebPanel(self, evt=0):
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
        self._mgr.Update()

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

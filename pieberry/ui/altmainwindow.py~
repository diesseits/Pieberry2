import wx, wx.aui

from events import *
from searchpanel import *
from tabpanel import *
from webpanel import *
from contextpanel import *
from listpanels import BibListPanel, WebListPanel, FileListPanel

class BaseMainWindow(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: GladeMainWindow.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)

        self.SplitterWindow = wx.SplitterWindow(self, -1, style=wx.SP_3D|wx.SP_BORDER)

        self.LeftPanel = wx.Panel(self.SplitterWindow, -1)
        self.LeftSizer = wx.BoxSizer(wx.VERTICAL)
        self.LeftPanel.SetSizer(self.LeftSizer)

        self.WebPanel = WebScrapePanel(self)
        self.SearchPanel = SearchToolsPanel(self)
        

        self.ContextPane = SimpleContextPanel(self.SplitterWindow, -1)
        self.TabBook = wx.aui.AuiNotebook(self.LeftPanel, -1)
        
        # Menu Bar
        self.PMWmenubar = wx.MenuBar()
        self.fileMenu = wx.Menu()
        self.fileMenuQuit = wx.MenuItem(self.fileMenu, wx.NewId(), "&Quit", "", wx.ITEM_NORMAL)
        self.fileMenu.AppendItem(self.fileMenuQuit)
        self.PMWmenubar.Append(self.fileMenu, "&File")
        self.SetMenuBar(self.PMWmenubar)
        # Menu Bar end

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onChangeTab, self.TabBook)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: GladeMainWindow.__set_properties
        self.SetTitle("Pieberry II")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("/home/raif/development/v2Pieberry/pieberry/ui/pieberry.ico", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.SetSize((862, 546))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: GladeMainWindow.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        contextsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ContextPane.SetSizer(contextsizer)
        self.SplitterWindow.SplitVertically(self.LeftPanel, self.ContextPane, 551)

        self.LeftSizer.Add(self.WebPanel, 0, wx.EXPAND, 0)
        self.LeftSizer.Add(self.TabBook, 1, wx.EXPAND, 0)
        self.LeftSizer.Add(self.SearchPanel, 0, wx.EXPAND, 0)
        sizer_1.Add(self.SplitterWindow, 1, wx.EXPAND, 0)
        # end wxGlade

        self.tab0 = BibListPanel(self.TabBook)
        self.tab1 = WebListPanel(self.TabBook)
        self.tab2 = FileListPanel(self.TabBook)
        # tab2 = ManagedTabPanel(self.TabBook)
        # tab3 = GeneralRedrawablePanel(self.TabBook)

        self.TabBook.AddPage(self.tab0, "Bib Tab")
        self.TabBook.AddPage(self.tab1, "Web Tab")
        self.TabBook.AddPage(self.tab2, "File Tab")
        # self.TabBook.AddPage(tab1, "Plain Tab")
        # self.TabBook.AddPage(tab2, "Managed Tab")

        self.SetSizer(sizer_1)
        self.Layout()

        self.tab0.Bind(EVT_PIE_LIST_SELECTION_EVENT, self.onNewContextToShow)
        self.tab1.Bind(EVT_PIE_LIST_SELECTION_EVENT, self.onNewContextToShow)
        self.tab2.Bind(EVT_PIE_LIST_SELECTION_EVENT, self.onNewContextToShow)

    def onChangeTab(self, event): # wxGlade: GladeMainWindow.<event_handler>
        print "Event handler `onChangeTab' not implemented!"
        event.Skip()

    def onNewContextToShow(self, evt):
        # print 'mainwindow: onNewContextToShow'
        self.ContextPane.SetObject(evt.pieobject)

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

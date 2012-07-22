#GPLv3 Raif Sarcich 2011

import wx
import pieberry.pieutility
from pieberry.pieconfig.schemas import PIE_TYPES_DOCUMENTS, PIE_TYPES_ALL

from pieberry.ui.events import *
from pieberry.ui.timers import SpinnyTimer
from pieberry.ui.listpanels.listwidgets import *
from pieberry.pieobject import *
from pieberry.ui.listpanels.baselistpanel import BaseListPanel # <-- todo
from pieberry.pieconfig.initsys import IMGDIR

WEBBMP = wx.Bitmap(os.path.join(IMGDIR, 'ic_globe16.png'))

class GBListPanel(BaseListPanel):
    '''Class for working with web scrapes'''
    paneltype = 'GBListPanel'

    def _setup_data(self):
        self.objectstore = PieObjectStore()

    def _do_layout(self):
        self.sizer0 = wx.BoxSizer(wx.VERTICAL)
        self.sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        self.ListDisplay = GBListCtrl(self)
        self.SelAllButton = wx.Button(self, -1, label=_('Select All'))
        self.ReferenceButton = wx.Button(self, -1, label=_('Reference selected'))
        self.sizer1.Add(self.SelAllButton, 0, wx.ALL, 5)
        self.sizer1.Add((20,20), 1)
        self.sizer1.Add(self.ReferenceButton, 0, wx.ALL, 5)
        self.sizer0.Add(self.ListDisplay, 1, wx.ALL|wx.EXPAND, 5)
        self.sizer0.Add(self.sizer1, 0, wx.EXPAND)
        self.SetSizer(self.sizer0)
        self.Layout()

    def _do_bindings(self):
        self.ListDisplay.Bind(wx.EVT_LIST_ITEM_SELECTED,
                              self.onSelectionChanged)
        self.SelAllButton.Bind(wx.EVT_BUTTON, self.onToggleSelectAll)
        self.ReferenceButton.Bind(wx.EVT_BUTTON, self.onReference)
        self.ListDisplay.Bind(wx.EVT_LIST_ITEM_ACTIVATED, 
                              self.onSelectionActivated)

    def Repopulate(self, filtertext=None, checkstatus=False):
        '''repopulate the list from current data, possibly filtering it
        (web panel specific version also with check-all ability)'''
        print 'BaseListPanel: Repopulate: filtertext=%s' % filtertext
        print self.paneltype
        cl = self.ListDisplay.GetCheckedList()
        print cl
        self.ListDisplay.DeleteAllItems()
        for ref, i in self.objectstore.GetNext():
            if ref in cl:
                cs = True
            else:
                cs = checkstatus
            self.ListDisplay.AddObject(i, ref, 
                                       filtertext=filtertext,
                                       checkstatus=cs)

    def _on_download_or_reference(self, evt, download=True):
        ret = PieObjectStore(
            [ self.objectstore[x] for x in self.ListDisplay.GetCheckedList() ]
            )
        # transfer relevant session data across
        ret.set_session_data(**self.objectstore.get_session_data())
        newevt = PieDownloadEvent(
            ostore=ret,
            pane=self,
            download=download
            )
        wx.PostEvent(self, newevt)

    def onReference(self, evt):
        '''when the user just wants to make bibliography references to
        web pages, not download anything.'''
        self._on_download_or_reference(evt, False)

    def onToggleSelectAll(self, evt):
        print 'WebListPanel.onToggleSelectAll'
        self.Repopulate(checkstatus=True)

    def MakeMenu(self, menu, obj):
        '''Function to construct a particular context menu'''
        rcm_openinbrowser = wx.MenuItem(menu, 0, _('Open in Browser'))
        rcm_openinbrowser.SetBitmap(WEBBMP)
        menu.AppendItem(rcm_openinbrowser)
        self.Bind(wx.EVT_MENU, self.onOpenInBrowser, rcm_openinbrowser)
        if not obj.has_aspect('hasfile'):
            rcm_attachfile = wx.MenuItem(menu, 23, _('Attach File'))
            rcm_attachfile.SetBitmap(
                wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_MENU))
            menu.AppendItem(rcm_attachfile)
            self.Bind(wx.EVT_MENU, self.onAttachFile, rcm_attachfile)



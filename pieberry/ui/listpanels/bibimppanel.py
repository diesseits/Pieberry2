
#GPLv3 Raif Sarcich 2011

import wx
import pieberry.pieutility

from pieberry.ui.events import *
from pieberry.ui.listpanels.listwidgets import *
from pieberry.pieobject import *
from pieberry.ui.listpanels.baselistpanel import *


class BibImpPanel(BaseListPanel):
    paneltype = 'BibImpPanel'

    def _setup_data(self):
        self.objectstore = PieObjectStore()

    def _do_layout(self):
        self.sizer0 = wx.BoxSizer(wx.VERTICAL)
        self.sizer1 = wx.BoxSizer(wx.HORIZONTAL)

        self.ListDisplay = GBListCtrl(self)
        #self.RemoveButton = wx.Button(self, -1, label=_("Remove"))
        self.SelAllButton = wx.Button(self, -1, label=_('Select All'))
        self.DiscardButton = wx.Button(self, -1, label=_("Discard all"))
        self.CommitButton = wx.Button(self, -1, label=_("Store these"))
        self.sizer1.Add(self.SelAllButton, 0, wx.ALL, 5)
        self.sizer1.Add(self.DiscardButton, 0, wx.ALL, 5)
        self.sizer1.Add((20,20), 1)
        self.sizer1.Add(self.CommitButton, 0, wx.ALL, 5)
        self.sizer0.Add(self.ListDisplay, 1, wx.ALL|wx.EXPAND, 5)
        self.sizer0.Add(self.sizer1, 0, wx.EXPAND)
        self.SetSizer(self.sizer0)
        # self.Layout()

    def _do_bindings(self):
        self.ListDisplay.Bind(wx.EVT_LIST_ITEM_ACTIVATED, 
                              self.onSelectionActivated)
        self.ListDisplay.Bind(wx.EVT_LIST_ITEM_SELECTED,
                              self.onSelectionChanged)
        self.SelAllButton.Bind(wx.EVT_BUTTON, self.onToggleSelectAll)
        self.CommitButton.Bind(wx.EVT_BUTTON,
                            self.onCommitObjects)
        self.DiscardButton.Bind(wx.EVT_BUTTON,
                                self.onDiscardAll)

    def AddObject(self, obj, msgtype='success'):
        print 'StagingListPanel.AddObject, msgtype =', msgtype
        ref = BaseListPanel.AddObject(self, obj, msgtype=msgtype)
        return ref

    def onDiscardAll(self, evt):
        print 'StagingListPanel.onDiscardAll()'
        #TODO: insert stuff to delete files, tidy up etc.
        self.objectstore.delete_all()
        p = self.GetParent()
        wx.CallAfter(p.DeletePage, p.GetPageIndex(self))
        
    def onCommitObjects(self, evt):
        print 'StagingListPanel.onCommitObjects()'
        self._on_download_or_reference(evt, False)

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
        newevt = PieCommitStagedEvent(
            ostore=ret,
            pane=self)
        wx.PostEvent(self, newevt)

    def onToggleSelectAll(self, evt):
        print 'WebListPanel.onToggleSelectAll'
        self.Repopulate(checkstatus=True)

    def MakeMenu(self, menu, obj):
        '''Function to construct a particular context menu'''
        if obj.has_aspect('onweb'):
            rcm_openinbrowser = wx.MenuItem(menu, 0, _('Open in Browser'))
            rcm_openinbrowser.SetBitmap(
                wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_MENU))
            menu.AppendItem(rcm_openinbrowser)
            self.Bind(wx.EVT_MENU, self.onOpenInBrowser, rcm_openinbrowser)
        # if obj.has_aspect('cached'):
        #     rcm_openfile = wx.MenuItem(menu, 1, _('Open file'))
        #     rcm_openfile.SetBitmap(
        #         wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_MENU))
        #     menu.AppendItem(rcm_openfile)
        #     self.Bind(wx.EVT_MENU, self.onOpenFile, rcm_openfile)
        #     rcm_deletefile = wx.MenuItem(menu, 2, _('Delete'))
        #     rcm_deletefile.SetBitmap(
        #         wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_MENU))
        #     menu.AppendItem(rcm_deletefile)
        #     self.Bind(wx.EVT_MENU, self.onDeleteObj, rcm_deletefile)

        rcm_editbibdata = wx.MenuItem(menu, 3, 
                                      _('Edit bibliographic information'))
        menu.AppendItem(rcm_editbibdata)
        self.Bind(wx.EVT_MENU, self.onEditBibData, rcm_editbibdata)
        if not obj.has_aspect('hasfile'):
            rcm_attachfile = wx.MenuItem(menu, 23, _('Attach File'))
            rcm_attachfile.SetBitmap(
                wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_MENU))
            menu.AppendItem(rcm_attachfile)
            self.Bind(wx.EVT_MENU, self.onAttachFile, rcm_attachfile)

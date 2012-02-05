#GPLv3 Raif Sarcich 2011

import wx
import pieutility

from ui.events import *
from ui.timers import SpinnyTimer
from listwidgets import *
from pieobject import *
from baselistpanel import BaseListPanel # <-- todo

class StagingListPanel(BaseListPanel):
    '''Class for displaying and working with bibliographic data, with
    appropriate stuff for dealing with staged/cached objects (yet to
    be committed to the internal db'''
    paneltype = 'StagingListPanel'

    def _setup_data(self):
        self.objectstore = PieObjectStore()
        self.spinTimer = None
        self.spinnerstate = -1

    def _do_layout(self):
        self.sizer0 = wx.BoxSizer(wx.VERTICAL)
        self.sizer1 = wx.BoxSizer(wx.HORIZONTAL)

        self.ListDisplay = BibListCtrl(self)
        #self.RemoveButton = wx.Button(self, -1, label=_("Remove"))
        self.DiscardButton = wx.Button(self, -1, label=_("Discard all"))
        self.CommitButton = wx.Button(self, -1, label=_("Store locally"))
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
        self.CommitButton.Bind(wx.EVT_BUTTON,
                            self.onCommitObjects)
        self.DiscardButton.Bind(wx.EVT_BUTTON,
                                self.onDiscardAll)

    def AddObject(self, obj, msgtype):
        '''An augmented AddObject incorporating spinning trigger'''
        print 'StagingListPanel.AddObject, msgtype =', msgtype
        if msgtype=='spin':
            ref = BaseListPanel.AddObject(self, obj, msgtype='spin')
            self.spinnerStart(ref)
        else:
            if self.spinTimer: self.spinnerStop()
            ref = BaseListPanel.AddObject(self, obj, msgtype=msgtype)
        return ref

    def onDiscardAll(self, evt):
        print 'StagingListPanel.onDiscardAll()'
        #TODO: insert stuff to delete files, tidy up etc.
        p = self.GetParent()
        wx.CallAfter(p.DeletePage, p.GetPageIndex(self))
        
    def onCommitObjects(self, evt):
        print 'StagingListPanel.onCommitObjects()'
        newevt = PieCommitStagedEvent(
            ostore=self.objectstore,
            pane=self)
        wx.PostEvent(self, newevt)

    def spinnerStart(self, ref):
        '''start a spinning icon to indicate download'''
        self.spin_item_ref = ref
        self.spinTimer = SpinnyTimer(self)
        self.spinTimer.Start(200)

    def spinnerTick(self):
        '''progress through the icon animation'''
        if self.spinnerstate == 5:
            self.spinnerstate = -1
        self.spinnerstate += 1
        sli = self.spinnerstate + 6 #because the images are 6 - 11
        self.ListDisplay.SetItemImage(
            self.ListDisplay.GetIndexFromRef(self.spin_item_ref), 
            sli)
        
    def spinnerStop(self):
        self.spinTimer.Stop()
        self.spinTimer.Destroy()
        self.spinTimer = None

    def DownloadDone(self, ref, outcome):
        '''The download is done ... let the user know'''
        idx = self.ListDisplay.GetIndexFromRef(ref)
        assert outcome in MessageType.keys()
        self.spinnerStop()
        self.ListDisplay.DeleteItem(
            self.ListDisplay.GetIndexFromRef(ref))
        self.ListDisplay.AddObject(
            obj=self.objectstore[ref],
            ref=ref,
            msgtype=outcome)
        print 'StagingListPanel.DownloadDone'

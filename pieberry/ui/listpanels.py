#GPLv3 Raif Sarcich 2011

import wx

from events import *
from timers import SpinnyTimer
from listwidgets import *
from pieobject import *
#from baselistpanel import BaseListPanel # <-- todo


class BaseListPanel(wx.Panel):
    '''Basic class for displaying and working with "results"'''

    def __init__(self, parent, id=-1, style=wx.EXPAND|wx.TAB_TRAVERSAL):
        wx.Panel.__init__(self, parent, id=id, style=style)
        self._setup_data()
        self._do_layout()
        self._do_bindings()

    def _setup_data(self):
        pass

    def _do_layout(self):
        pass

    def _do_bindings(self):
        pass

    def AddObjects(self, ostore):
        self.ListDisplay.DeleteAllItems()
        self.objectstore = ostore
        for ref, i in self.objectstore.GetNext():
            self.ListDisplay.AddObject(i, ref)

    def AddObject(self, obj):
        ref = self.objectstore.Add(obj)
        nexidx = self.ListDisplay.AddObject(obj, ref)
        return nexidx

    def Repopulate(self, filtertext=None):
        '''repopulate the list from current data, possibly filtering it'''
        print 'BaseListPanel: Repopulate: filtertext=%s' % filtertext
        print self.paneltype
        self.ListDisplay.DeleteAllItems()
        for ref, i in self.objectstore.GetNext():
            self.ListDisplay.AddObject(i, ref, filtertext=filtertext)

    def GetSelectedItem(self):
        '''Return the currently selected object'''
        print 'BaseListPanel: GetSelectedItem: not implemented'

    def onSelectionChanged(self, evt):
        # print 'BibListPanel.onSelectionChanged'
        # print 'Item index:', evt.GetIndex()
        # print 'Item data:', self.ListDisplay.GetItemData(evt.GetIndex())
        self.ListDisplay.onItemSelected(evt)
        ref = self.ListDisplay.GetItemData(evt.GetIndex())
        newevt = PieListSelectionEvent(
            ref=ref, 
            pieobject=self.objectstore[ref])
        wx.PostEvent(self, newevt)

    def onSelectionActivated(self, evt):
        print 'BaseListPanel.onSelectionActivated'
        print 'Item index from list event:', evt.GetIndex()
        print 'Item data (reference stored against list):', self.ListDisplay.GetItemData(evt.GetIndex())
        print 'Object in objectstore by index:', self.objectstore[self.ListDisplay.GetItemData(evt.GetIndex())]

    def onFilterView(self, evt):
        print evt.searchtext
        self.Repopulate(filtertext=evt.searchtext)


class WebListPanel(BaseListPanel):
    '''Class for working with web scrapes'''
    paneltype = 'WebListPanel'

    def _setup_data(self):
        self.objectstore = PieObjectStore()

    def _do_layout(self):
        self.sizer0 = wx.BoxSizer(wx.VERTICAL)
        self.sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        self.ListDisplay = WebListCtrl(self)
        self.SelAllButton = wx.Button(self, -1, label=_('Select All'))
        self.DownloadButton = wx.Button(self, -1, label=_('Download selected'))
        self.sizer1.Add(self.SelAllButton, 0, wx.ALL, 5)
        self.sizer1.Add((20,20), 1)
        self.sizer1.Add(self.DownloadButton, 0, wx.ALL, 5)
        self.sizer0.Add(self.ListDisplay, 1, wx.ALL|wx.EXPAND, 5)
        self.sizer0.Add(self.sizer1, 0, wx.EXPAND)
        self.SetSizer(self.sizer0)
        self.Layout()

    def _do_bindings(self):
        self.ListDisplay.Bind(wx.EVT_LIST_ITEM_SELECTED,
                              self.onSelectionChanged)
        self.SelAllButton.Bind(wx.EVT_BUTTON, self.onToggleSelectAll)
        self.DownloadButton.Bind(wx.EVT_BUTTON, self.onDownload)
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

    def onDownload(self, evt):
        '''when the user clicks the download button to actually get
        stuff off the web page'''
        print 'WebListPanel.onDownload'
        ret = PieObjectStore(
            [ self.objectstore[x] for x in self.ListDisplay.GetCheckedList() ]
            )
        for i in ret: print i
        print ret
        newevt = PieDownloadEvent(
            ostore=ret,
            pane=self
            )
        wx.PostEvent(self, newevt)

    def onToggleSelectAll(self, evt):
        print 'WebListPanel.onToggleSelectAll'
        self.Repopulate(checkstatus=True)

class FileListPanel(BaseListPanel):
    paneltype = 'FileListPanel'

    def _setup_data(self):
        self.objectstore = PieObjectStore()

    def _do_layout(self):
        self.sizer0 = wx.BoxSizer(wx.VERTICAL)
        self.ListDisplay = FileListCtrl(self)
        self.sizer0.Add(self.ListDisplay, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(self.sizer0)
        self.Layout()

    def _do_bindings(self):
        self.ListDisplay.Bind(wx.EVT_LIST_ITEM_SELECTED,
                              self.onSelectionChanged)

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

    def AddObject(self, obj, spin=True):
        nexidx = BaseListPanel.AddObject(obj)
        if spin: #TODO: spinny functionality
            pass

    def onDiscardAll(self, evt):
        print 'StagingListPanel.onDiscardAll()'
        #TODO: insert stuff to delete files, tidy up etc.
        p = self.GetParent()
        wx.CallAfter(p.DeletePage, p.GetPageIndex(self))
        
    def onCommitObjects(self, evt):
        print 'StagingListPanel.onCommitObjects()'

    def spinnerStart(self, list_item):
        '''start a spinning icon to indicate download'''
        self.spin_list_item = list_item
        self.spinTimer = SpinnyTimer(self)
        self.spinTimer.Start(200)

    def spinnerTick(self):
        '''progress through the icon animation'''
        if self.spinnerstate == 5:
            self.spinnerstate = -1
        self.spinnerstate += 1
        sli = self.spinnerstate + 6
        self.outputList.SetItemImage(self.spin_list_item, sli)
        
    def spinnerStop(self):
        self.spinTimer.Stop()
        self.spinTimer.Destroy()
        self.spinTimer = None

    def DownloadDone(self, outcome):
        '''The download is done ... let the user know'''
        pass


class BibListPanel(BaseListPanel):
    '''Class for displaying and working with bibliographic data'''
    paneltype = 'BibListPanel'

    def _setup_data(self):
        self.objectstore = PieObjectStore()

    def _do_layout(self):
        self.sizer0 = wx.BoxSizer(wx.VERTICAL)
        self.sizer1 = wx.BoxSizer(wx.HORIZONTAL)

        self.ListDisplay = BibListCtrl(self)
        self.DelButton = wx.Button(self, -1, label=_("Delete"))
        self.sizer1.Add(self.DelButton, 1, wx.ALL, 5)
        self.sizer0.Add(self.ListDisplay, 1, wx.ALL|wx.EXPAND, 5)
        self.sizer0.Add(self.sizer1)
        self.SetSizer(self.sizer0)
        # self.Layout()


    def _do_bindings(self):
        self.ListDisplay.Bind(wx.EVT_LIST_ITEM_ACTIVATED, 
                              self.onSelectionActivated)
        self.ListDisplay.Bind(wx.EVT_LIST_ITEM_SELECTED,
                              self.onSelectionChanged)
        self.DelButton.Bind(wx.EVT_BUTTON,
                            self.onDeleteItem)


    def onDeleteItem(self, evt):
        print self.GetSelectedItem() 
        self.objectstore.Del(self.GetSelectedItemRef())
        self.ListDisplay.DeleteItem(self.ListDisplay.currentitem)

    def GetSelectedItem(self):
        return self.objectstore[self.GetSelectedItemRef()]

    def GetSelectedItemRef(self):
        '''return the index (for the _objectstore_ not the list) of 
        the selected item'''
        return self.ListDisplay.GetItemData(self.ListDisplay.currentitem)


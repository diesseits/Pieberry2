#GPLv3 Raif Sarcich 2011

import wx

from events import *
from listwidgets import *
from piedb.objectstore import *
#from baselistpanel import BaseListPanel # <-- todo


class BaseListPanel(wx.Panel):
    '''Basic class for displaying and working with "results"'''

    def __init__(self, parent, id=-1, style=wx.EXPAND|wx.TAB_TRAVERSAL):
        wx.Panel.__init__(self, parent, id=id, style=style)
        self._setup_data()
        self._do_layout()
        self._do_bindings()

    def AddObjects(self, ostore):
        self.ListDisplay.DeleteAllItems()
        self.objectstore = ostore
        for ref, i in self.objectstore.GetNext():
            self.ListDisplay.AddObject(i, ref)

    def AddObject(self, obj):
        ref = self.objectstore.Add(obj)
        self.ListDisplay.AddObject(obj, ref)

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

    def onFilterView(self, evt):
        print evt.searchtext
        self.Repopulate(filtertext=evt.searchtext)

class WebListPanel(BaseListPanel):
    '''Class for working with web scrapes'''
    paneltype = 'WebListPanel'

    def _setup_data(self):
        self.objectstore = BetterPieObjectStore()

    def _do_layout(self):
        self.sizer0 = wx.BoxSizer(wx.VERTICAL)
        self.ListDisplay = WebListCtrl(self)
        self.sizer0.Add(self.ListDisplay, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(self.sizer0)
        self.Layout()

    def _do_bindings(self):
        self.ListDisplay.Bind(wx.EVT_LIST_ITEM_SELECTED,
                              self.onSelectionChanged)

class FileListPanel(BaseListPanel):
    paneltype = 'FileListPanel'

    def _setup_data(self):
        self.objectstore = BetterPieObjectStore()

    def _do_layout(self):
        self.sizer0 = wx.BoxSizer(wx.VERTICAL)
        self.ListDisplay = FileListCtrl(self)
        self.sizer0.Add(self.ListDisplay, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(self.sizer0)
        self.Layout()

    def _do_bindings(self):
        self.ListDisplay.Bind(wx.EVT_LIST_ITEM_SELECTED,
                              self.onSelectionChanged)

class BibListPanel(BaseListPanel):
    '''Class for displaying and working with bibliographic data'''
    paneltype = 'BibListPanel'

    def _setup_data(self):
        self.objectstore = BetterPieObjectStore()

    def _do_layout(self):
        self.sizer0 = wx.BoxSizer(wx.VERTICAL)
        self.sizer1 = wx.BoxSizer(wx.HORIZONTAL)

        self.ListDisplay = BibListCtrl(self)
        self.DelButton = wx.Button(self, -1, label=_("Delete"))
        self.sizer1.Add(self.DelButton, 1, wx.ALL, 5)
        self.sizer0.Add(self.ListDisplay, 1, wx.ALL|wx.EXPAND, 5)
        self.sizer0.Add(self.sizer1)
        self.SetSizer(self.sizer0)
        self.Layout()

    def _do_bindings(self):
        self.ListDisplay.Bind(wx.EVT_LIST_ITEM_ACTIVATED, 
                              self.onSelectionActivated)
        self.ListDisplay.Bind(wx.EVT_LIST_ITEM_SELECTED,
                              self.onSelectionChanged)
        self.DelButton.Bind(wx.EVT_BUTTON,
                            self.onDeleteItem)


    def onSelectionActivated(self, evt):
        print 'BibListPanel.onSelectionActivated'
        print 'Item index from list event:', evt.GetIndex()
        print 'Item data (reference stored against list):', self.ListDisplay.GetItemData(evt.GetIndex())
        print 'Object in objectstore by index:', self.objectstore[self.ListDisplay.GetItemData(evt.GetIndex())]

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


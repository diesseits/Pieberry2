#GPLv3 Raif Sarcich 2011

import wx
import pieutility

from ui.events import *
from ui.timers import SpinnyTimer
from listwidgets import *
from pieobject import *

class BaseListPanel(wx.Panel):
    '''Basic class for displaying and working with "results"'''

    def __init__(self, parent, id=-1, style=wx.EXPAND|wx.TAB_TRAVERSAL):
        wx.Panel.__init__(self, parent, id=id, style=style)
        self._setup_data()
        self._do_layout()
        self.__do_base_bindings()
        self._do_bindings()

    def _setup_data(self):
        pass

    def _do_layout(self):
        pass

    def _do_bindings(self):
        pass

    def _makemenu(self, evt):
        '''Prepare to create and display a context menu. Calls a
        "MakeMenu" method which should be overriden by inheriting
        classes to provide a menu with appropriate context'''
        if evt.GetIndex() == -1: return
        right_click_context = evt.GetIndex()
        menu = wx.Menu()
        it_idx = self.ListDisplay.GetItemData(right_click_context)
        obj = self.objectstore[it_idx]
        print "## Object for popup menu:", obj
        self.MakeMenu(menu, obj)
        self.ListDisplay.PopupMenu( menu, evt.GetPoint() )
        menu.Destroy() # destroy to avoid mem leak

    def __do_base_bindings(self):
        wx.EVT_LIST_ITEM_RIGHT_CLICK(self.ListDisplay, -1, self._makemenu)

    def MakeMenu(self, menu, obj):
        pass

    def AddObjects(self, ostore):
        self.ListDisplay.DeleteAllItems()
        self.objectstore = ostore
        for ref, i in self.objectstore.GetNext():
            self.ListDisplay.AddObject(i, ref)

    def AddObject(self, obj, msgtype=None):
        '''Add an object into the panel. Returns the reference by which 
        the object may be found in the item's objectstore, and also the list
        widget's itemDataMap, if it is visible'''
        ref = self.objectstore.Add(obj)
        if msgtype:
            nexidx = self.ListDisplay.AddObject(obj, ref, msgtype=msgtype)
        else:
            nexidx = self.ListDisplay.AddObject(obj, ref)
        return ref

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

    def onListRightClick(self, evt):
        '''build a context menu'''
        print 'BaseListPanel.onListRightClick'

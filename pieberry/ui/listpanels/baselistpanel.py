#GPLv3 Raif Sarcich 2011

import wx
import pieberry.pieutility

from pprint import pprint
from pieberry.ui.events import *
from pieberry.ui.timers import SpinnyTimer
from pieberry.ui.listpanels.listwidgets import *
from pieberry.pieobject import *
from pieberry.ui.listpanels.menufunctions import *

class BaseListPanel(wx.Panel, MenuFunctionsMixin):
    '''Basic class for displaying and working with "results"'''

    def __init__(self, parent, id=-1, style=wx.EXPAND|wx.TAB_TRAVERSAL):
        wx.Panel.__init__(self, parent, id=id, style=style)
        self._setup_data()
        self._do_layout()
        self.__do_base_bindings()
        self._do_bindings()
        self._last_item_right_clicked = 0

    def _setup_data(self):
        pass

    def _do_layout(self):
        pass

    def _do_bindings(self):
        pass

    def __do_base_bindings(self):
        wx.EVT_LIST_ITEM_RIGHT_CLICK(self.ListDisplay, -1, self._makemenu)
        self.ListDisplay.Bind(wx.EVT_LIST_BEGIN_DRAG, self.onLeftDown)

    def _makemenu(self, evt):
        '''Prepare to create and display a context menu. Calls a
        "MakeMenu" method which should be overriden by inheriting
        classes to provide a menu with appropriate context'''
        if evt.GetIndex() == -1: return
        right_click_context = evt.GetIndex()
        menu = wx.Menu()
        it_idx = self.ListDisplay.GetItemData(right_click_context)
        self._last_item_right_clicked
        obj = self.objectstore[it_idx]
        # print "## Object for popup menu:", obj
        self.MakeMenu(menu, obj)
        self.ListDisplay.PopupMenu( menu, evt.GetPoint() )
        menu.Destroy() # destroy to avoid mem leak

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

    def UpdateObject(self, obj):
        '''Update the displayed data for an object already in the pane. May
        only work for saved objects'''
        for stidx, stobj in self.objectstore.GetNext():
            if obj == stobj:
                self.ListDisplay.DeleteItemByOstoreRef(stidx)
                self.ListDisplay.AddObject(obj, stidx)

    def onSelectionChanged(self, evt):
        # print 'BibListPanel.onSelectionChanged'
        # print 'Item index:', evt.GetIndex()
        # print 'Item data:', self.ListDisplay.GetItemData(evt.GetIndex())
        self.ListDisplay.onItemSelected(evt)
        ref = self.ListDisplay.GetItemData(evt.GetIndex())
        # pprint(self.objectstore[ref].aspects)
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

    def GetSelectedItem(self):
        '''Get the currently selected object'''
        return self.objectstore[self.GetSelectedItemRef()]

    def GetSelectedItemRef(self):
        '''return the index (for the _objectstore_ not the list) of 
        the selected item'''
        return self.ListDisplay.GetItemData(self.ListDisplay.currentitem)

    def onLeftDown(self, evt):
        '''called at beginning of drag event'''

        # old pieberry stuff - still relevant?
        self.suppress_tipwindow = True
        self.isdragging = True
        # the tortuous process of getting the right list item
        xy = wx.GetMousePosition()
        ol_xy = self.ListDisplay.ScreenToClient(xy)
        it_idx, flags = self.ListDisplay.HitTest(ol_xy)
        cur_it = self.ListDisplay.GetItemData(it_idx)
        obj = self.objectstore[cur_it]

        # if there's no file, don't do anything
        if not obj.has_aspect('hasfile'):
            evt.Skip()
            self.isdragging = False
            return

        # sanity check for file existence
        if not os.path.exists(obj.FileData_FullPath):
            evt.Skip()
            self.isdragging = False
            return

        do = wx.FileDataObject()
        do.AddFile(obj.FileData_FullPath)
        dropsource = wx.DropSource(self.ListDisplay)
        dropsource.SetData(do)

        result = dropsource.DoDragDrop()
        if result == wx.DragCopy:
            print 'Successful drag and copy'
        self.suppress_tipwindow = False
        self.isdragging = False
    
    def ClearAllData(self, evt=0):
        '''Clear everthing including object store and list view'''
        self.objectstore = {}
        self.ListDisplay.DeleteAllItems()

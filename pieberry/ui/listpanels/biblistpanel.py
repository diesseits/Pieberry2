#GPLv3 Raif Sarcich 2011

import wx
import pieutility

from ui.events import *
from ui.timers import SpinnyTimer
from listwidgets import *
from pieobject import *
from baselistpanel import BaseListPanel # <-- todo

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

    def onSelectionActivated(self, evt):
        pieutility.open_file(
            self.objectstore[
                self.ListDisplay.GetItemData(evt.GetIndex())].FileData_FullPath)
        
    

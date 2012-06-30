#GPLv3 Raif Sarcich 2011

import wx
import pieberry.pieutility

from pieberry.ui.events import *
from pieberry.ui.timers import SpinnyTimer
from pieberry.ui.listpanels.listwidgets import *
from pieberry.pieobject import *
# from pieberry.ui.listpanels.baselistpanel import BaseListPanel # <-- todo
from pieberry.ui.listpanels.biblistpanel import *
from pieberry.pieconfig.initsys import IMGDIR

from pieberry.pieobject.tags import get_tag, get_all_tags
from pieberry.pieobject.objectstore import PieObjectStore

class TagListPanel(BibListPanel):
    '''A slightly modded version of BibListPanel with a choice box to
    pull up results for one tag or another'''
    paneltype = 'TagListPanel'

    def _do_layout(self):
        self.sizer0 = wx.BoxSizer(wx.VERTICAL)
        self.sizer1 = wx.BoxSizer(wx.HORIZONTAL)

        tagselections = get_all_tags().keys()
        tagselections.sort()
        self.TagChoice = wx.Choice(self, -1, choices=tagselections)
        self.TagChoice.SetStringSelection('')
        self.ListDisplay = BibListCtrl(self)
        # self.DelButton = wx.Button(self, -1, label=_("Delete"))
        # self.sizer1.Add(self.DelButton, 1, wx.ALL, 5)
        self.sizer0.Add(self.TagChoice, 0, wx.ALL|wx.EXPAND, 5)
        self.sizer0.Add(self.ListDisplay, 1, wx.ALL|wx.EXPAND, 5)
        self.sizer0.Add(self.sizer1)
        self.SetSizer(self.sizer0)
        self.SelectTag(tagselections[0])
        # self.Layout()

    def _do_bindings(self):
        self.ListDisplay.Bind(wx.EVT_LIST_ITEM_ACTIVATED, 
                              self.onSelectionActivated)
        self.ListDisplay.Bind(wx.EVT_LIST_ITEM_SELECTED,
                              self.onSelectionChanged)
        self.ListDisplay.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
        self.TagChoice.Bind(wx.EVT_CHOICE, self.OnTagChosen)

    def OnTagChosen(self, evt):
        print evt.GetString()
        tag = get_tag(evt.GetString())
        ostore = PieObjectStore([ t for t in tag.pieobjects ])
        self.AddObjects(ostore)

    def SelectTag(self, strtag):
        self.TagChoice.SetStringSelection(strtag)
        tag = get_tag(strtag)
        ostore = PieObjectStore([ t for t in tag.pieobjects ])
        self.AddObjects(ostore)

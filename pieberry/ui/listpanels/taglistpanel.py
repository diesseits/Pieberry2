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

from pieberry.pieobject.tags import get_tag, get_all_tags, fn_del_tag
from pieberry.pieobject.objectstore import PieObjectStore

class TagListPanel(BibListPanel):
    '''A slightly modded version of BibListPanel with a choice box to
    pull up results for one tag or another'''
    paneltype = 'TagListPanel'

    def _do_layout(self):
        self.sizer0 = wx.BoxSizer(wx.VERTICAL)
        self.sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)

        tagselections = get_all_tags().keys()
        tagselections.sort()
        self.TagChoice = wx.Choice(self, -1, choices=tagselections)
        self.TagChoice.SetStringSelection('')
        self.TagDelButton = wx.BitmapButton(
            self, -1, 
            bitmap=wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_TOOLBAR))
        tdbtt = wx.ToolTip(_('Delete this tag'))
        self.TagDelButton.SetToolTip(tdbtt)
        self.ListDisplay = BibListCtrl(self)
        self.reportButton = wx.Button(self, -1, label=("Generate Report"))
        self.sizer1.Add((20,20), 1)
        self.sizer1.Add(self.reportButton, 0, wx.ALL, 5)
        self.sizer2.Add(self.TagChoice, 1, wx.ALL|wx.EXPAND, 5)
        self.sizer2.Add(self.TagDelButton, 0, wx.ALL, 5)
        self.sizer0.Add(self.sizer2, 0, wx.ALL|wx.EXPAND, 5)
        self.sizer0.Add(self.ListDisplay, 1, wx.ALL|wx.EXPAND, 5)
        self.sizer0.Add(self.sizer1, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(self.sizer0)
        if len(tagselections) > 0: self.SelectTag(tagselections[0])
        # self.Layout()

    def _do_bindings(self):
        self.ListDisplay.Bind(wx.EVT_LIST_ITEM_ACTIVATED, 
                              self.onSelectionActivated)
        self.ListDisplay.Bind(wx.EVT_LIST_ITEM_SELECTED,
                              self.onSelectionChanged)
        self.ListDisplay.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
        self.TagChoice.Bind(wx.EVT_CHOICE, self.OnTagChosen)
        self.TagDelButton.Bind(wx.EVT_BUTTON, self.OnDelTag)
        self.reportButton.Bind(wx.EVT_BUTTON, self.OnMakeReport)

    def OnMakeReport(self, evt):
        newevt = PieGenReportEvent(
            ostore = self.objectstore,
            subject = self.TagChoice.GetStringSelection()
            )
        wx.PostEvent(self, newevt)

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

    def OnDelTag(self, evt):
        if not self.TagChoice.GetStringSelection(): return
        msg = wx.MessageDialog(self, _('Are you sure you want to delete this tag?'), _('Delete Tag'), style=wx.YES|wx.NO|wx.ICON_QUESTION|wx.NO_DEFAULT)
        ans = msg.ShowModal()
        if ans == wx.ID_YES: 
            fn_del_tag(self.TagChoice.GetStringSelection())
            tagselections = get_all_tags().keys()
            tagselections.sort()
            self.TagChoice.Clear()
            [ self.TagChoice.Append(i) for i in tagselections ]
            if len(tagselections) > 0:
                self.SelectTag(tagselections[0])
            else:
                self.ClearAllData()
            

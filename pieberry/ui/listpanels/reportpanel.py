#GPLv3 Raif Sarcich 2012

import wx
import wx.richtext as rt
import pieberry.pieutility
from pieberry.pieconfig.schemas import PIE_TYPES_DOCUMENTS, PIE_TYPES_ALL

from pieberry.ui.events import *
from pieberry.ui.timers import SpinnyTimer
from pieberry.ui.listpanels.listwidgets import *
from pieberry.pieobject import *
from pieberry.ui.listpanels.baselistpanel import BaseListPanel # <-- todo
from pieberry.pieconfig.initsys import IMGDIR

from pieberry.pieoutput.report import *

class ReportPanel(BaseListPanel):
    '''Class for selecting contents of, and displaying, a report'''
    paneltype = 'ReportPanel'

    def _setup_data(self):
        self.objectstore = PieObjectStore()

    def _do_layout(self):
        #sizers
        self.sizer0 = wx.BoxSizer(wx.VERTICAL)
        self.sizer1 = wx.BoxSizer(wx.HORIZONTAL)

        #widgets
        self.ListDisplay = GBListCtrl(self) # google books listctrl will do
        self.RichText = rt.RichTextCtrl(
            self, style=wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER|wx.TE_READONLY)
        self.PrintButton = wx.Button(self, -1, label=_('Print'))
        self.SelAllButton = wx.Button(self, -1, label=_('Select All'))
        self.DoReportButton = wx.Button(self, -1, label=_('Make Report'))
        self.HeaderFmtChoice = wx.Choice(self, -1, choices=ORDERS.keys())

        #tooltips
        tt1 = wx.ToolTip(_('Make a report with the selected contents'))
        self.DoReportButton.SetToolTip(tt1)

        #add to sizers
        self.sizer1.Add(self.SelAllButton, 0, wx.ALL, 5)
        self.sizer1.Add((20,20), 1)
        self.sizer1.Add(self.PrintButton, 0, wx.ALL, 5)
        self.sizer1.Add(self.HeaderFmtChoice, 0, wx.ALL|wx.EXPAND, 5)
        self.sizer1.Add(self.DoReportButton, 0, wx.ALL, 5)
        self.sizer0.Add(self.ListDisplay, 1, wx.ALL|wx.EXPAND, 5)
        self.sizer0.Add(self.RichText, 1, wx.ALL|wx.EXPAND, 5)
        self.sizer0.Add(self.sizer1, 0, wx.EXPAND)

        #layout
        self.PrintButton.Hide()
        self.RichText.Hide()

        self.SetSizer(self.sizer0)
        self.Layout()

    def _change_mode(self):
        '''Change mode from selection of sources to presentation of report'''
        self.SelAllButton.Hide()
        self.HeaderFmtChoice.Hide()
        self.DoReportButton.Hide()
        self.ListDisplay.Hide()
        self.RichText.Show()
        self.PrintButton.Show()
        self.Layout()

    def _do_bindings(self):
        self.ListDisplay.Bind(wx.EVT_LIST_ITEM_SELECTED,
                              self.onSelectionChanged)
        self.SelAllButton.Bind(wx.EVT_BUTTON, self.onToggleSelectAll)
        self.ListDisplay.Bind(wx.EVT_LIST_ITEM_ACTIVATED, 
                              self.onSelectionActivated)
        self.DoReportButton.Bind(wx.EVT_BUTTON, self.onShowReport)

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

    def onShowReport(self, evt):
        '''User chooses to compile the report, show it'''
        self._change_mode()

    def onToggleSelectAll(self, evt):
        print 'ReportPanel.onToggleSelectAll'
        self.Repopulate(checkstatus=True)

    def MakeMenu(self, menu, obj):
        '''Function to construct a particular context menu'''
        pass


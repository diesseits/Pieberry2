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
        self.RevertButton = wx.Button(self, -1, label=_('Review Sources'))
        self.SelAllButton = wx.Button(self, -1, label=_('Select All'))
        self.DoReportButton = wx.Button(self, -1, label=_('Make Report'))
        self.OrderChoice = wx.Choice(self, -1, choices=ORDERS.keys())
        self.OrderChoice.SetSelection(2)

        rtcfont = wx.Font(
            12, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.RichText.SetFont(rtcfont)

        #tooltips
        tt1 = wx.ToolTip(_('Make a report with the selected contents'))
        self.DoReportButton.SetToolTip(tt1)

        #add to sizers
        self.sizer1.Add(self.SelAllButton, 0, wx.ALL, 5)
        self.sizer1.Add((20,20), 1)
        self.sizer1.Add(self.RevertButton, 0, wx.ALL, 5)
        self.sizer1.Add(self.OrderChoice, 0, wx.ALL|wx.EXPAND, 5)
        self.sizer1.Add(self.DoReportButton, 0, wx.ALL, 5)
        self.sizer0.Add(self.ListDisplay, 1, wx.ALL|wx.EXPAND, 5)
        self.sizer0.Add(self.RichText, 1, wx.ALL|wx.EXPAND, 5)
        self.sizer0.Add(self.sizer1, 0, wx.EXPAND)

        #layout
        self.RevertButton.Hide()
        self.RichText.Hide()

        self.SetSizer(self.sizer0)
        self.Layout()

    def _change_mode(self):
        '''Change mode from selection of sources to presentation of report'''
        self.SelAllButton.Hide()
        self.OrderChoice.Hide()
        self.DoReportButton.Hide()
        self.ListDisplay.Hide()
        self.RichText.Show()
        self.RevertButton.Show()
        self.Layout()

    def _revert_mode(self):
        '''Opposite of _change_mode'''
        self.SelAllButton.Show()
        self.OrderChoice.Show()
        self.DoReportButton.Show()
        self.ListDisplay.Show()
        self.RichText.Hide()
        self.RevertButton.Hide()
        self.Layout()

    def AddObjects(self, ostore):
        '''Overriding to ensure they're pre-ticked'''
        self.ListDisplay.DeleteAllItems()
        self.objectstore = ostore
        for ref, i in self.objectstore.GetNext():
            try:
                self.ListDisplay.AddObject(i, ref, 
                                           checkstatus=True)
            except:
                traceback.print_exc()
                print 'Had trouble here:', ref, i

    def SetXMLContent(self, content):
        # print content
        from cStringIO import StringIO
        out = StringIO()
        handler = wx.richtext.RichTextXMLHandler()
        buffer = self.RichText.GetBuffer()
        buffer.AddHandler(handler)
        out.write(content)
        out.seek(0)
        handler.LoadStream(buffer, out)
        # print out.read()
        self.RichText.Refresh()

    def _do_bindings(self):
        self.ListDisplay.Bind(wx.EVT_LIST_ITEM_SELECTED,
                              self.onSelectionChanged)
        self.SelAllButton.Bind(wx.EVT_BUTTON, self.onToggleSelectAll)
        self.ListDisplay.Bind(wx.EVT_LIST_ITEM_ACTIVATED, 
                              self.onSelectionActivated)
        self.DoReportButton.Bind(wx.EVT_BUTTON, self.onShowReport)
        self.RevertButton.Bind(wx.EVT_BUTTON, self.onRevert)

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

    def GetBuffer(self):
        '''return buffer for printing'''
        return self.RichText.GetBuffer()

    def SetSubject(self, subject):
        self.subject = subject

    def onRevert(self, evt):
        self._revert_mode()

    def onShowReport(self, evt):
        '''User chooses to compile the report, show it'''
        self._change_mode()
        reporter = ReportFormatter()
        reporter.AddObjects(
            PieObjectStore(
                [ self.objectstore[x] 
                  for x in self.ListDisplay.GetCheckedList() ]
                )
            )
        reporter.SetSubject(self.subject)
        reporter.Sort(order=
                      ORDERS[self.OrderChoice.GetStringSelection()])
        xml = reporter.GenerateReport()
        self.SetXMLContent(xml)


    def onToggleSelectAll(self, evt):
        print 'ReportPanel.onToggleSelectAll'
        self.Repopulate(checkstatus=True)

    def MakeMenu(self, menu, obj):
        '''Function to construct a particular context menu'''
        pass


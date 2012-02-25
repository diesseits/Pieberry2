import wx
from events import *

origin_choices = (
    _('All'),
    _('Library'),
    _('Projects'),
    _('Meeting Papers')
    )

origin_choice_codes = ('all', 'library', 'projects', 'meetingpapers')

searchable_fields = (
    _('Main fields'), 
    _('All fields'),
    _('File name'),
    _('Title'),
    _('Author'),
    _('Website'),
    _('Journal')
    )

search_field_codes = ('main', 'all', 'filename', 'title', 'author', 'website', 'journal')
   
class FilterToolsPanel(wx.Panel):
    '''Simpler panel for filtering results'''
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=-1, style=wx.EXPAND|wx.TAB_TRAVERSAL)
        sizer = wx.BoxSizer(wx.VERTICAL)
        hsizer_top = wx.BoxSizer(wx.HORIZONTAL)

        lbl = wx.StaticText(self, -1, _("Filter:"), style=wx.EXPAND)
        self.searchctrl = wx.SearchCtrl(
            self, -1, style = wx.TE_PROCESS_ENTER|wx.EXPAND)
        hsizer_top.Add(lbl, 0, wx.ALL, 5)
        hsizer_top.Add(self.searchctrl, 1, wx.ALL, 5)
        sizer.Add(hsizer_top, 1, wx.EXPAND, 0)
        self.SetSizer(sizer)
        self.Layout()
        self.searchctrl.SetFocus()
        self.searchctrl.Bind(wx.EVT_TEXT, self.onTextUpdated)
        self.searchctrl.Bind(wx.EVT_KEY_UP, self.keyTrap)

    def onTextUpdated(self, evt):
        newevt = PieSearchEvent(searchtext=self.searchctrl.GetValue())
        wx.PostEvent(self, newevt)

    def keyTrap(self, evt):
        if evt.GetKeyCode() == wx.WXK_ESCAPE:
            newevt = PieCloseFilterPanelEvent()
            self.GetParent().ToggleFilterPanel()

class SearchToolsPanel(wx.Panel):
    '''Generic search tools panel'''

    def __init__(self, parent, origin=None, field=None):
        wx.Panel.__init__(self, parent=parent, id=-1, style=wx.EXPAND|wx.TAB_TRAVERSAL)
        sizer = wx.BoxSizer(wx.VERTICAL)
        hsizer_top = wx.BoxSizer(wx.HORIZONTAL)

        # lbl = wx.StaticText(self, -1, _("Search:"), style=wx.EXPAND)
        self.originchoice = wx.Choice(self, -1, choices=origin_choices)
        self.originchoice.SetSelection(0)
        self.searchctrl = wx.SearchCtrl(
            self, -1, style = wx.TE_PROCESS_ENTER|wx.EXPAND)
        self.fieldchoice = wx.Choice(self, -1, choices=searchable_fields)
        self.fieldchoice.SetSelection(0)
        # self.closebutton = wx.BitmapButton(
        #     self, -1, 
        #     wx.ArtProvider.GetBitmap(wx.ART_CROSS_MARK, 
        #                              wx.ART_TOOLBAR, (16, 16)), 
        #     style=wx.NO_BORDER)

        # hsizer_top.Add(lbl, 0, wx.ALL, 5)
        hsizer_top.Add(self.originchoice, 0, wx.ALL, 5)
        hsizer_top.Add(self.searchctrl, 1, wx.ALL, 5)
        hsizer_top.Add(self.fieldchoice, 0, wx.ALL, 5)
        # hsizer_top.Add(self.closebutton, 0, wx.ALL, 5)

        sizer.Add(hsizer_top, 1, wx.EXPAND, 0)
        self.SetSizer(sizer)
        self.Layout()

        self.searchctrl.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch)
        self.searchctrl.Bind(wx.EVT_TEXT_ENTER, self.OnSearch)
        # self.closebutton.Bind(wx.EVT_BUTTON, self.OnClose)
        if origin:
            assert origin in origin_choice_codes
            self.originchoice.SetSelection(origin_choice_codes.index(origin))
        if field:
            assert field in search_field_codes
            self.fieldchoice.SetSelection(search_field_codes.index(field))

        self.searchctrl.SetFocus()

    def SetSearchChoices(self, choices=[]):
        '''Set available search type choices'''
        print 'SetSearchChoices'

    def SetSearchHistory(self, historyprovider):
        print 'SetSearchHistory'

    def GetSearch(self):
        print 'GetSearch'

    def OnSearch(self, evt):
        newevt = PieSearchEvent(
            searchtext=unicode(self.searchctrl.GetValue()),
            origin=origin_choice_codes[self.originchoice.GetSelection()],
            fields=search_field_codes[self.fieldchoice.GetSelection()]
            )
        wx.PostEvent(self, newevt)

    def OnClose(self, evt):
        print "OnClose"

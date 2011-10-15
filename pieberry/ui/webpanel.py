import wx

class WebScrapePanel(wx.Panel):
    '''Generic search tools panel'''
    _BUTTON_SIZE = wx.Size(100, 50)
    _DEF_WIDTH = (300, -1)

    def __init__(self, parent):
        wx.Panel.__init__(
            self, parent=parent, id=-1, style=wx.EXPAND|wx.TAB_TRAVERSAL)

        self.pasteButton = wx.BitmapButton(
            self, -1, 
            wx.ArtProvider.GetBitmap(wx.ART_PASTE, wx.ART_TOOLBAR, (16, 16)), 
            style=wx.NO_BORDER)
        tt7 = wx.ToolTip(_('Paste from clipboard'))
        self.pasteButton.SetToolTip(tt7)

        self.urlField = wx.TextCtrl(
            self, -1, size=self._DEF_WIDTH, #validator = pieUrlValidator(), 
            style=wx.TE_PROCESS_ENTER|wx.TE_BESTWRAP)
        self.urlField.ChangeValue('http://')
        self.urlField.SetBackgroundColour("pink")
        tt1 = wx.ToolTip(_('Website to scan for PDF documents to download.'))

        self.urlField.SetToolTip(tt1)
        lburl = wx.StaticText(self, -1, 'URL:')

        self.authorField = wx.ComboBox(
            self, -1, size=self._DEF_WIDTH, #choices=dirlist, 
            #validator=piePlainTextValidator(), 
            style=wx.EXPAND|wx.CB_DROPDOWN)
        tt2 = wx.ToolTip(
            '''Generic "author" to use for downloaded documents. 
This will also be used as a first level 
subdirectory in which to store these documents.''')
        self.authorField.SetToolTip(tt2)

        self.corpAuthorCb = wx.CheckBox(
            self, -1, label="Author is a corporate entity")
        self.corpAuthorCb.SetValue(True)
        tt5 = wx.ToolTip(_('Treat this author as a corporate entity rather than person(s). This matters to how bibliographies treat these entries.'))
        self.corpAuthorCb.SetToolTip(tt5)

        self.tagField = wx.TextCtrl(
            self, -1, size=self._DEF_WIDTH, 
            #validator=piePlainTextValidator(), style=wx.EXPAND
            )
        tt3 = wx.ToolTip(_('Category tag and second level subdirectory for downloaded documents.'))
        self.tagField.SetToolTip(tt3)
        
        pf_use_choices = (
            _('Append to title - " ... - Phrase"'), 
            _('Append to title - " ... (Phrase)"'), 
            _('Prepend to title - "Phrase: ..."'), 
            _('Use as subdirectory only'))
        self.use_choice_lookup = (
            'append_hyphen', 
            'append_brackets', 
            'prepend', 
            'dironly')
        self.pfUseChoice = wx.Choice(
            self, -1, choices=pf_use_choices, style=wx.EXPAND)
        tt6 = wx.ToolTip(_('Select how to use the category phrase. It will always be used to create a subdirectory for the downloaded documents. It may also be appended to the titles of the downloaded documents'))
        self.pfUseChoice.SetToolTip(tt6)
        self.pfUseChoice.SetSelection(0)

        self.scanButton = wx.Button(self, -1, label=_('Scan'))

        sizerA = wx.BoxSizer(wx.HORIZONTAL)

        sizer0 = wx.FlexGridSizer(5, 3, 5, 5)
        sizer0.AddGrowableCol(1, 1)
        sizer0.SetFlexibleDirection(wx.BOTH)

        sizerA.Add(lburl, 1, wx.EXPAND|wx.ALL, 3)
        sizerA.Add(self.pasteButton, 0, wx.ALL, 3)
        sizer0.Add(sizerA, 1, wx.EXPAND)
        sizer0.Add(self.urlField, 1, wx.EXPAND|wx.ALL, 3)
        sizer0.Add(self.scanButton, 1, wx.EXPAND|wx.ALL, 3)
        sizer0.Add(wx.StaticText(
                self, -1, _("Default author:")), 1, wx.EXPAND|wx.ALL, 3)
        sizer0.Add(self.authorField, 1, wx.EXPAND|wx.ALL, 3)
        sizer0.Add(self.corpAuthorCb, 1, wx.EXPAND|wx.ALL, 3)
        sizer0.Add(wx.StaticText(
                self, -1, _('Category phrase:'), size=(120,0)), 1, wx.EXPAND|wx.ALL, 3)
        sizer0.Add(self.tagField, 1, wx.EXPAND|wx.ALL, 3)
        sizer0.Add(self.pfUseChoice, 1, wx.EXPAND|wx.ALL, 3)

        self.SetSizer(sizer0)
        self.Layout()

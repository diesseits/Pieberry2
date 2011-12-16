import wx, time
from validators import *
from events import PieWebScrapeEvent

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
            self, -1, size=self._DEF_WIDTH, validator = pieUrlValidator(), 
            style=wx.TE_PROCESS_ENTER|wx.TE_BESTWRAP)
        self.urlField.ChangeValue('http://')
        self.urlField.SetBackgroundColour("pink")
        tt1 = wx.ToolTip(_('Website to scan for PDF documents to download.'))

        self.urlField.SetToolTip(tt1)
        lburl = wx.StaticText(self, -1, 'URL:')

        self.authorField = wx.ComboBox(
            self, -1, size=self._DEF_WIDTH, #choices=dirlist, 
            validator=piePlainTextValidator(), 
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
            validator=piePlainTextValidator(), style=wx.EXPAND
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
        self.urlField.SetFocus()
        self._do_bindings()

    def _do_bindings(self):
        '''bind various events'''
        self.scrape_in_progress = False
        self.authorField.Bind(wx.EVT_TEXT, self.onAuthorValidate)
        self.tagField.Bind(wx.EVT_TEXT, self.onTagValidate)
        self.urlField.Bind(wx.EVT_TEXT_ENTER, self.onScan)
        self.scanButton.Bind(wx.EVT_BUTTON, self.onWebPanelAction)
        self.urlField.Bind(wx.EVT_TEXT, self.onUrlTextChanged)
        self.pasteButton.Bind(wx.EVT_BUTTON, self.onPasteButton)

    def onWebPanelAction(self, evt):
        '''sort out what sort of action is required - scrape or abort'''
        if self.scrape_in_progress:
            self.onAbort(0)
        else:
            self.onScan(0)
        
    def LockPanel(self, tf):
        '''Substitute for Enable() - (un)lock things that need (un)locking, 
        takes boolean'''
        if tf: tf = False 
        else: tf = True
        self.urlField.Enable(tf)
        self.tagField.Enable(tf)
        self.authorField.Enable(tf)
        self.pfUseChoice.Enable(tf)
        self.corpAuthorCb.Enable(tf)
        self.scanButton.SetLabel(_('Scan'))

    def GetData(self, evt=0):
        '''return the current user entered data on the panel'''
        self.sc_url = self.urlField.GetValue().strip()
        self.sc_tag = self.tagField.GetValue().strip()
        self.sc_auth = self.authorField.GetValue().strip()
        self.sc_tagbehav = self.use_choice_lookup[self.pfUseChoice.GetCurrentSelection()]
        self.sc_corpauth = self.corpAuthorCb.IsChecked()
        if not (self.urlField.GetValidator().Validate() and self.authorField.GetValidator().Validate() and self.tagField.GetValidator().Validate()):
            raise Exception, "Invalid data for this operation"
        return (self.sc_url,
                self.sc_tag,
                self.sc_auth,
                self.sc_tagbehav,
                self.sc_corpauth
                )
        
    def onScan(self, evt):
        '''set of actions to perform to do a web scrape'''
        print 'webpanel.OnGo'
        self.GetData()
        self.LockPanel(True)
        self.scanButton.SetLabel(_('Abort'))
        self.scrape_in_progress = True
        newevt = PieWebScrapeEvent(
            url = self.sc_url,
            catstring = self.sc_tag,
            catbehaviour = self.sc_tagbehav,
            author = self.sc_auth,
            authoriscorporate = self.sc_corpauth
            )
        wx.PostEvent(self, newevt)

    def Aborted(self, evt=0):
        '''when abort is confirmed'''
        self.LockPanel(False)
        self.scanButton.SetLabel(_('Scan'))
        self.scrape_in_progress = False

    def onAbort(self, evt):
        '''when user says to abort'''
        # in future: send event to terminate thread
        self.Aborted()

    def onPasteButton(self, evt):
        if not wx.TheClipboard.IsOpened():
            wx.TheClipboard.Open()
            do = wx.TextDataObject()
            success = wx.TheClipboard.GetData(do)
            wx.TheClipboard.Close()
            if success:
                self.urlField.SetValue(do.GetText())

    def onAuthorValidate(self, evt=1):
        self.authorField.GetValidator().Validate()
        self.authorField.Refresh()

    def onTagValidate(self, evt=1):
        self.tagField.GetValidator().Validate()
        self.tagField.Refresh()

    def onUrlTextChanged(self, evt=1):
        self.url_text_last_changed = time.time()
        self.urlField.GetValidator().Validate()
        self.urlField.Refresh() 

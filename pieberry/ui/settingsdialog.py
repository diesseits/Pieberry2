import wx, os.path, os

if __name__ == '__main__':
    import sys
    sys.path.append('/home/raif/development/v2Pieberry/pieberry')
    IMGDIR = os.getcwd()
    PROFILES = {'Profile1': 0, 'Profile2': 1}
else:
    from pieconfig.paths import IMGDIR

class ProfilePanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.profileChoice = wx.Choice(self, -1, choices=PROFILES.keys())
        self.profileaddbt = wx.Button(self, -1, 'Add')
        self.basedirctrl = wx.DirPickerCtrl(
            self, -1, 
            path = os.getcwd(),
            style = wx.DIRP_USE_TEXTCTRL)
        self.desktopdirctrl = wx.DirPickerCtrl(
            self, -1, 
            path = os.getcwd(),
            style = wx.DIRP_USE_TEXTCTRL)
        self.bib_cb = wx.CheckBox(self, -1, 'Export bibliography')
        self.bibfilectrl = wx.FilePickerCtrl(
            self, -1,
            wildcard = "*.bib",
            style = wx.FLP_USE_TEXTCTRL)
        self._do_layout()

    def _do_layout(self):
        self.mainsizer = wx.BoxSizer(wx.VERTICAL)
        self.mainsizer.Add(wx.StaticText(self, -1, 'Profile:'), 0, wx.ALL, 5)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(self.profileChoice, 1, wx.ALL|wx.EXPAND, 5)
        sizer2.Add(self.profileaddbt, 0, wx.ALL, 5)
        self.mainsizer.Add(sizer2, 0, wx.EXPAND)
        self.mainsizer.Add(wx.StaticText(self, -1, 'Pieberry Folder:'), 0, 
                           wx.ALL, 5)
        self.mainsizer.Add(self.basedirctrl, 0, wx.ALL|wx.EXPAND, 5)
        self.mainsizer.Add(wx.StaticText(self, -1, 'Desktop Folder:'), 0, 
                           wx.ALL, 5)
        self.mainsizer.Add(self.desktopdirctrl, 0, wx.ALL|wx.EXPAND, 5)
        self.mainsizer.Add(self.bib_cb, 0, wx.ALL, 5)
        self.mainsizer.Add(wx.StaticText(self, -1, 'Bibliography file:'), 0, 
                           wx.ALL, 5)
        self.mainsizer.Add(self.bibfilectrl, 0, wx.ALL|wx.EXPAND, 5)


        self.SetSizer(self.mainsizer)
        self.Layout()


class FormatPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self._do_layout()

    def _do_layout(self):
        pass

class PieSettingsDialog(wx.Dialog):
    
    def __init__(self, *args, **kwds):
        # begin wxGlade: pieConfigDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        kwds["size"] = (600, 400)
        wx.Dialog.__init__(self, *args, **kwds)

        self.listbook = wx.Listbook(self, -1)
        self.listbook.SetImageList(SettingsImageList)

        self.profilepanel = ProfilePanel(self, -1)
        self.formatpanel = FormatPanel(self, -1)

        self.okBt = wx.Button(self, wx.ID_OK, "Ok")
        self.cancelBt = wx.Button(self, wx.ID_CANCEL, "Cancel")
        
        self._do_layout()
        self._do_bindings()

    def _do_layout(self):
        self.mainsizer = wx.BoxSizer(wx.VERTICAL)
        self.mainsizer.Add(self.listbook, 1, wx.EXPAND)

        self.listbook.AddPage(self.profilepanel, 'Profile', True, 0)
        self.listbook.AddPage(self.formatpanel, 'Format', False, 1)

        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3.Add((20, 20), 3, 0, 0)
        sizer_3.Add(self.cancelBt, 0, wx.ALL, 3)
        sizer_3.Add(self.okBt, 0, wx.ALL, 3)
        sizer_3.Add((5, 5), 0, 0, 0)

        self.mainsizer.Add(sizer_3, 0, wx.EXPAND)

        self.SetSizer(self.mainsizer)
        self.Layout()
        
    def _do_bindings(self):
        pass


if __name__ == '__main__':
    import sys
    sys.path.append('/home/raif/development/v2Pieberry/pieberry')
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()

SettingsImageList = wx.ImageList(32, 32)
SettingsImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_profile32.png')))
SettingsImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_format32.png')))

if __name__ == '__main__':
    dialog_1 = PieSettingsDialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.Show()
    app.MainLoop()

class pieConfigDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: pieConfigDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.panel_2 = wx.Panel(self, -1)
        self.panel_1 = wx.Panel(self, -1)
        self.label_profile = wx.StaticText(self.panel_1, -1, "Profile")
        self.profileChoice = wx.Choice(self.panel_1, -1, choices=PROFILES.keys())
        self.profileNewBt = wx.Button(self.panel_1, -1, "New")
        self.label_1 = wx.StaticText(self.panel_1, -1, "Root directory for library:")
        self.workDirCtrl = wx.TextCtrl(self.panel_1, -1, "", style=wx.TE_READONLY)
        self.workDirBt = wx.Button(self.panel_1, -1, "Select")
        self.label_2 = wx.StaticText(self.panel_1, -1, "Principal bibliography file:")
        self.mainBibCtrl = wx.TextCtrl(self.panel_1, -1, "", style=wx.TE_READONLY)
        self.mainBibBt = wx.Button(self.panel_1, -1, "Select")
        self.tsvBibCb = wx.CheckBox(self.panel_1, -1, label='Also export to tab-separated-values spreadsheet')
        self.defaultEntryTypeChoice = wx.Choice(self.panel_1, -1, choices=ENTRY_TYPE_CHOICES.values())
        self.okBt = wx.Button(self.panel_2, -1, "Ok")
        self.cancelBt = wx.Button(self.panel_2, wx.ID_CANCEL, "Cancel")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.onSelectRoot, self.workDirBt)
        self.Bind(wx.EVT_BUTTON, self.onSelectBib, self.mainBibBt)
        self.Bind(wx.EVT_BUTTON, self.onOk, self.okBt)
        self.Bind(wx.EVT_BUTTON, self.onCancel, self.cancelBt)
        self.Bind(wx.EVT_BUTTON, self.onNewProfile, self.profileNewBt)
        self.Bind(wx.EVT_CHOICE, self.onProfileSelected, self.profileChoice)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: pieConfigDialog.__set_properties
        self.SetTitle("Pieberry Settings")
        self.panel_2.SetMinSize((532, 34))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: pieConfigDialog.__do_layout
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4 = wx.BoxSizer(wx.VERTICAL)
        sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_7 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4.Add(self.label_profile, 0, wx.ALL, 5)
        sizer_7.Add(self.profileChoice, 1, wx.ALL, 5)
        sizer_7.Add(self.profileNewBt, 0, wx.ALL, 5)
        sizer_4.Add(sizer_7, 1, wx.EXPAND, 0)
        sizer_4.Add(self.label_1, 0, wx.ALL, 5)
        sizer_5.Add(self.workDirCtrl, 2, wx.ALL, 5)
        sizer_5.Add(self.workDirBt, 0, wx.ALL, 5)
        sizer_4.Add(sizer_5, 1, wx.EXPAND, 0)
        sizer_4.Add(self.label_2, 0, wx.ALL, 5)
        sizer_6.Add(self.mainBibCtrl, 2, wx.ALL, 5)
        sizer_6.Add(self.mainBibBt, 0, wx.ALL, 5)
        sizer_4.Add(sizer_6, 1, wx.EXPAND, 0)
        sizer_4.Add(self.tsvBibCb, 0, wx.EXPAND|wx.ALL, 5)
        sizer_a = wx.BoxSizer(wx.HORIZONTAL)
        sizer_a.Add(wx.StaticText(self.panel_1, -1, 'Default BibTex style:'), 1, wx.EXPAND|wx.ALL, 5)
        sizer_a.Add(self.defaultEntryTypeChoice, 0, wx.ALL, 5)
        sizer_4.Add(sizer_a, 1, wx.EXPAND, 0)
        self.panel_1.SetSizer(sizer_4)
        sizer_2.Add(self.panel_1, 5, wx.EXPAND, 0)
        sizer_3.Add((20, 20), 3, 0, 0)
        sizer_3.Add(self.cancelBt, 0, wx.ALL, 3)
        sizer_3.Add(self.okBt, 0, wx.ALL, 3)
        sizer_3.Add((5, 5), 0, 0, 0)
        self.panel_2.SetSizer(sizer_3)
        sizer_2.Add(self.panel_2, 0, wx.EXPAND, 0)
        self.SetSizer(sizer_2)
        sizer_2.Fit(self)
        self.Layout()
        # end wxGlade

    def onSelectRoot(self, event): # wxGlade: pieConfigDialog.<event_handler>
        print "Event handler `onSelectRoot' not implemented"
        event.Skip()

    def onSelectBib(self, event): # wxGlade: pieConfigDialog.<event_handler>
        print "Event handler `onSelectBib' not implemented"
        event.Skip()

    def onNewProfile(self, event):
        print "Event handler 'onNewProfile' not implemented"
        event.Skip()

    def onProfileSelected(self, event):
        print "Event handler 'onProfileSelected' not implemented"
        event.Skip()

    def onOk(self, event): # wxGlade: pieConfigDialog.<event_handler>
        print "Event handler `onOk' not implemented"
        event.Skip()

    def onCancel(self, event): # wxGlade: pieConfigDialog.<event_handler>
        print "Event handler `onCancel' not implemented"
        event.Skip()

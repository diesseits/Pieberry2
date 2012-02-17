import wx, os.path, os
from validators import pieBibtexValidator

if __name__ == '__main__':
    import sys
    sys.path.append('/home/raif/development/v2Pieberry/pieberry')
    IMGDIR = os.getcwd()
else:
    from pieconfig.paths import IMGDIR

from pieconfig import PIE_CONFIG

class ProfilePanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.profileChoice = wx.Choice(self, -1, 
                                       choices=PIE_CONFIG.get_profile_names())
        self.profileaddbt = wx.Button(self, -1, 'Add')
        self.rootdirctrl = wx.DirPickerCtrl(
            self, -1, 
            path = PIE_CONFIG.get('Profile', 'rootdir'),
            style = wx.DIRP_USE_TEXTCTRL)
        self.rootdirctrl.SetPath(PIE_CONFIG.get('Profile', 'rootdir'))
        self.desktopdirctrl = wx.DirPickerCtrl(
            self, -1, 
            path = PIE_CONFIG.get('Profile', 'desktopdir'),
            style = wx.DIRP_USE_TEXTCTRL)
        self.bib_cb = wx.CheckBox(self, -1, 'Export bibliography',
                                  style=wx.ALIGN_RIGHT)
        self.bib_cb.SetValue(PIE_CONFIG.getboolean('Profile', 
                                                    'export_bibtex'))
        self.bibfilectrl = wx.FilePickerCtrl(
            self, -1,
            wildcard = "*.bib",
            style = wx.FLP_USE_TEXTCTRL|wx.FLP_SAVE)
        self.bibfilectrl.SetPath(PIE_CONFIG.get('Profile', 'bibliography_file'))
        self._do_layout()
        self._do_bindings()

    def GetData(self):
        retdata = ('Profile',
                   {'bibliography_file': self.bibfilectrl.GetPath(),
                    'desktopdir': self.desktopdirctrl.GetPath(),
                    'rootdir': self.rootdirctrl.GetPath(),
                    'export_bibtex': self.bib_cb.GetValue()})
        return retdata

    def GetProfile(self):
        return self.profileChoice.GetStringSelection()

    def OnAddProfile(self, evt):
        tedia = wx.TextEntryDialog(
            self, 'Name of new settings profile', 'New profile', defaultValue='')
        tedo = tedia.ShowModal()
        if tedo == wx.ID_CANCEL:
            return
        profile_name = tedia.GetValue()
        if len(profile_name) < 1 or len(profile_name) > 30:
            return
        retdata = self.GetData()
        PIE_CONFIG.add_profile(profile_name, retdata[1])
        self._refill_profile_choice()
        self.profileChoice.SetStringSelection(profile_name)

    def _refill_profile_choice(self):
        self.profileChoice.Clear()
        for i in PIE_CONFIG.get_profile_names():
            self.profileChoice.Append(i)

    def _do_bindings(self):
        self.profileaddbt.Bind(wx.EVT_BUTTON, self.OnAddProfile)

    def _do_layout(self):
        self.mainsizer = wx.BoxSizer(wx.VERTICAL)
        self.mainsizer.Add(wx.StaticText(self, -1, 'Profile:'), 0, wx.ALL, 5)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(self.profileChoice, 1, wx.ALL|wx.EXPAND, 5)
        sizer2.Add(self.profileaddbt, 0, wx.ALL, 5)
        self.mainsizer.Add(sizer2, 0, wx.EXPAND)
        self.mainsizer.Add(wx.StaticText(self, -1, 'Pieberry Folder:'), 0, 
                           wx.ALL, 5)
        self.mainsizer.Add(self.rootdirctrl, 0, wx.ALL|wx.EXPAND, 5)
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
    uchz = {'Full Url': 'full', 'Domain only': 'domain'}
    uchz_rv = {'full': 'Full Url', 'domain': 'Domain only'}
    ptxtfchz = {'Citation text only': 'plaintext', 
                'Citation with url': 'urlplaintext'}
    ptxtfchz_rv = {'plaintext': 'Citation text only', 
                   'urlplaintext': 'Citation with url'}
    bibtexchoices = {'Misc': 'Misc', 'Online': 'Online'}

    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        
        self.defbibtexchoice = wx.Choice(self, -1, 
                                         choices=self.bibtexchoices.keys())
        self.defbibtexchoice.SetStringSelection(
            PIE_CONFIG.get('Format', 'default_bibtex_entry_type'))
        self.howpublishedtext = wx.TextCtrl(self, -1, 
                                            validator=pieBibtexValidator(True))
        self.howpublishedtext.SetValue(
            PIE_CONFIG.get('Format', 'default_howpublished_text'))
        self.urlchoice = wx.Choice(self, -1, choices = self.uchz.keys())
        self.urlchoice.SetStringSelection(
            self.uchz_rv[PIE_CONFIG.get('Format', 'url_level_represent')])
        self.plaintextfmtchoice = wx.Choice(self, -1, 
                                       choices=self.ptxtfchz.keys())
        self.plaintextfmtchoice.SetStringSelection(
            self.ptxtfchz_rv[PIE_CONFIG.get('Format', 'plaintext_citation_format')])
        self.writepdf_cb = wx.CheckBox(self, -1, 
                                       'Write PDF metadata when possible')
        self.writepdf_cb.SetValue(
            PIE_CONFIG.getboolean('Format', 'write_pdf_metadata'))
        self.fnlen_spinner = wx.SpinCtrl(self, -1, min=40, max=255)
        self.fnlen_spinner.SetValue(
            PIE_CONFIG.getint('Format', 'filesystem_length_limit'))
        self._do_layout()
        self._do_bindings()

    def GetData(self):
        retdata = ('Format',
                   {
                'default_bibtex_entry_type': self.bibtexchoices[self.defbibtexchoice.GetStringSelection()],
                'default_howpublished_text': self.howpublishedtext.GetValue(),
                'url_level_represent': self.uchz[self.urlchoice.GetStringSelection()],
                'plaintext_citation_format': self.ptxtfchz[self.plaintextfmtchoice.GetStringSelection()],
                'write_pdf_metadata': self.writepdf_cb.GetValue(),
                'filesystem_length_limit': self.fnlen_spinner.GetValue()
                })
        return retdata

    def _do_layout(self):
        self.mainsizer = wx.BoxSizer(wx.VERTICAL)
        self.mainsizer.Add(wx.StaticText(self, -1, 'Bibliography Options'),
                           0, wx.ALL, 5)
        self.mainsizer.Add(wx.StaticLine(self, -1, style=wx.LI_HORIZONTAL), 
                           0, wx.EXPAND|wx.ALL, 5)
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(
            wx.StaticText(self, -1, 'Default BibTeX entry style for downloads:'), 
            1, wx.ALL, 5)
        sizer1.Add(self.defbibtexchoice, 0, wx.ALL, 5)
        self.mainsizer.Add(sizer1, 0, wx.EXPAND)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(
            wx.StaticText(self, -1, 'Default "how published" text for downloads:'),
            1, wx.ALL, 5)
        sizer2.Add(self.howpublishedtext, 1, wx.ALL, 5)
        self.mainsizer.Add(sizer2, 0, wx.EXPAND)
        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer3.Add(
            wx.StaticText(self, -1, 'Extent of URL to represent in citations:'),
            1, wx.ALL, 5)
        sizer3.Add(self.urlchoice, 0, wx.ALL, 5)
        self.mainsizer.Add(sizer3, 0, wx.EXPAND)
        sizer4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer4.Add(
            wx.StaticText(self, -1, 'Format of plain text citations:'),
            1, wx.ALL, 5)
        sizer4.Add(self.plaintextfmtchoice, 0, wx.ALL, 5)
        self.mainsizer.Add(sizer4, 0, wx.EXPAND)
        self.mainsizer.Add((20, 20))
        self.mainsizer.Add(wx.StaticText(self, -1, 'File Handling Options'))
        self.mainsizer.Add(wx.StaticLine(self, -1, style=wx.LI_HORIZONTAL),
                           0, wx.ALL|wx.EXPAND, 5)
        self.mainsizer.Add(self.writepdf_cb, 0, wx.EXPAND|wx.ALL, 5)
        sizer5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer5.Add(
            wx.StaticText(self, -1, 'Maximum filename length:'),
            1, wx.ALL, 5)
        sizer5.Add(self.fnlen_spinner, 0, wx.ALL, 5)
        self.mainsizer.Add(sizer5, 0, wx.EXPAND)
        self.SetSizer(self.mainsizer)
        self.Layout()

    def _do_bindings(self):
        self.howpublishedtext.Bind(wx.EVT_TEXT, self.OnHowPubValidate)
    
    def OnHowPubValidate(self, evt=0):
        self.howpublishedtext.GetValidator().Validate()
        self.howpublishedtext.Refresh()


class CleanerPanel(wx.Panel):
    '''Desktop cleaner settings'''
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.dirListCtrl = wx.ListBox(self, -1, choices=[], style=wx.LB_SORT)
        self.createNewDirBt = wx.Button(self, -1, label='Create new project directory')
        self.delDirBt = wx.Button(self, -1, label='Delete')
        self.authorKwdTC = wx.TextCtrl(self, -1)
        self.titleKwdTC = wx.TextCtrl(self, -1)
        self._do_layout()

    def _do_layout(self):
        s1 = wx.BoxSizer(wx.VERTICAL)
        s2 = wx.BoxSizer(wx.HORIZONTAL)
        s1.Add(wx.StaticText(self, -1, 'Project directories:'), 0, wx.ALL, 3)
        s1.Add(self.dirListCtrl, 1, wx.ALL|wx.EXPAND, 3)
        s2.Add(self.createNewDirBt, 3, wx.ALL|wx.EXPAND, 3)
        s2.Add(self.delDirBt, 1, wx.ALL|wx.EXPAND, 3)
        s1.Add(s2, 0, wx.EXPAND)
        s1.Add(wx.StaticText(self, -1, 'Move files to directory with Author:'), 0, wx.ALL, 3)
        s1.Add(self.authorKwdTC, 0, wx.ALL|wx.EXPAND, 3)
        s1.Add(wx.StaticText(self, -1, 'Move files to directory with Title:'), 0, wx.ALL, 3)
        s1.Add(self.titleKwdTC, 0, wx.ALL|wx.EXPAND, 3)
        self.SetSizer(s1)
        self.Layout()

    def _do_bindings(self):
        pass

class PieSettingsDialog(wx.Dialog):
    
    def __init__(self, *args, **kwds):
        # begin wxGlade: pieConfigDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        kwds["size"] = (600, 400)
        kwds["title"] = 'Pieberry Settings'
        wx.Dialog.__init__(self, *args, **kwds)

        self.listbook = wx.Listbook(self, -1)
        self.listbook.SetImageList(SettingsImageList)

        self.profilepanel = ProfilePanel(self, -1)
        self.formatpanel = FormatPanel(self, -1)
        self.cleanerpanel = CleanerPanel(self, -1)

        self.okBt = wx.Button(self, -1, "Ok")
        self.cancelBt = wx.Button(self, wx.ID_CANCEL, "Cancel")
        
        self._do_layout()
        self._do_bindings()

    def _do_layout(self):
        self.mainsizer = wx.BoxSizer(wx.VERTICAL)
        self.mainsizer.Add(self.listbook, 1, wx.EXPAND)

        self.listbook.AddPage(self.profilepanel, 'Profile', True, 0)
        self.listbook.AddPage(self.formatpanel, 'Format', False, 1)
        self.listbook.AddPage(self.cleanerpanel, 'Desktop Cleaner', False, 2)

        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3.Add((20, 20), 3, 0, 0)
        sizer_3.Add(self.cancelBt, 0, wx.ALL, 3)
        sizer_3.Add(self.okBt, 0, wx.ALL, 3)
        sizer_3.Add((5, 5), 0, 0, 0)

        self.mainsizer.Add(sizer_3, 0, wx.EXPAND)

        self.SetSizer(self.mainsizer)
        self.Layout()
        
    def _do_bindings(self):
        self.okBt.Bind(wx.EVT_BUTTON, self.onOk)

    def onOk(self, evt=1):
        alldata = []
        alldata.append(self.profilepanel.GetData())
        alldata.append(('TheProfile', 
                        {'current_profile': self.profilepanel.GetProfile()}))
        alldata.append(self.formatpanel.GetData())
        for sectionkey, dataset in alldata:
            for key, val in dataset.items():
                PIE_CONFIG.set(sectionkey, key, str(val))
        PIE_CONFIG.write_pieconfig()
        self.EndModal(wx.ID_OK)


if __name__ == '__main__':
    import sys
    sys.path.append('/home/raif/development/v2Pieberry/pieberry')
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()

SettingsImageList = wx.ImageList(32, 32)
SettingsImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_profile32.png')))
SettingsImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_format32.png')))
SettingsImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_broom32.png')))

if __name__ == '__main__':
    dialog_1 = PieSettingsDialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.Show()
    app.MainLoop()


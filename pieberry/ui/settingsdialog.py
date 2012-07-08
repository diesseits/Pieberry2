import wx, os.path, os
from pieberry.ui.validators import pieBibtexValidator
from pieberry.ui.events import PieLocationChangedEvent, PieUpdateAtomChoicesEvent
from pieberry.pieobject.folder import *
from pieberry.pieobject.internals import PIE_INTERNALS

if __name__ == '__main__':
    import sys
    sys.path.append('/home/raif/development/v2Pieberry/pieberry')
    IMGDIR = os.getcwd()
else:
    from pieberry.pieconfig.paths import IMGDIR

from pieberry.pieconfig.config import PIE_CONFIG

class ProfilePanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.profileChoice = wx.Choice(self, -1, 
                                       choices=PIE_CONFIG.get_profile_names())
        self.profileChoice.SetStringSelection(
            PIE_CONFIG.get('TheProfile', 'current_profile'))
        tta = wx.ToolTip(_('A profile allows you to point Pieberry at different Pieberry directories and databases'))
        self.profileChoice.SetToolTip(tta)
        self.profileaddbt = wx.Button(self, -1, _('Add'))
        self.rootdirctrl = wx.DirPickerCtrl(
            self, -1, 
            path = PIE_CONFIG.get('Profile', 'rootdir'),
            style = wx.DIRP_USE_TEXTCTRL)
        self.rootdirctrl.SetPath(PIE_CONFIG.get('Profile', 'rootdir'))
        self.rootdiratstart = PIE_CONFIG.get('Profile', 'rootdir')
        self.desktopdirctrl = wx.DirPickerCtrl(
            self, -1, 
            path = PIE_CONFIG.get('Profile', 'desktopdir'),
            style = wx.DIRP_USE_TEXTCTRL)
        self.desktopdirctrl.SetPath(PIE_CONFIG.get('Profile', 'desktopdir'))
        self.bib_cb = wx.CheckBox(self, -1, 
                                  _('Export bibliography to pre-specified file'))
                                  # style=wx.ALIGN_RIGHT)
        ttb = wx.ToolTip(_("Setting the bibliography here means that Pieberry won't prompt you for a bibliography file every time you export it."))
        self.bib_cb.SetToolTip(ttb)
        self.bib_cb.SetValue(PIE_CONFIG.getboolean('Profile', 
                                                    'export_bibtex'))
        self.bibfilectrl = wx.FilePickerCtrl(
            self, -1,
            wildcard = "BibTeX files (*.bib;*.bibtex)|*.bib;*.bibtex",
            style = wx.FLP_USE_TEXTCTRL|wx.FLP_SAVE)
        if PIE_CONFIG.getboolean('Profile', 'export_bibtex') == True: 
            self.bibfilectrl.Enable(True)
        else: self.bibfilectrl.Enable(False)
        self.bibfilectrl.SetPath(PIE_CONFIG.get('Profile', 'bibliography_file'))
        self.bibexpstarred_cb = wx.CheckBox(self, -1, 
                                         _('Export starred items only'))
        ttc = wx.ToolTip(_('Export only starred items with adequate bibliographic data (unchecking will export all with adequate bibliographic data in the library but not project folders)'))
        self.bibexpstarred_cb.SetToolTip(ttc)
        self.bibexpstarred_cb.SetValue(
            PIE_CONFIG.getboolean('Profile', 'export_starred_only'))
        self._do_layout()
        self._do_bindings()

    def GetData(self):
        retdata = ('Profile',
                   {'bibliography_file': self.bibfilectrl.GetPath(),
                    'desktopdir': self.desktopdirctrl.GetPath(),
                    'rootdir': self.rootdirctrl.GetPath(),
                    'export_bibtex': self.bib_cb.GetValue(),
                    'export_starred_only': self.bibexpstarred_cb.GetValue(),
                    'last_dir_saved_to': PIE_CONFIG.get('Profile', 
                                                        'last_dir_saved_to'),
                    'last_dir_opened': PIE_CONFIG.get('Profile', 
                                                      'last_dir_opened')
                    })
        return retdata

    def GetProfile(self):
        return self.profileChoice.GetStringSelection()

    def Refresh(self):
        '''Re-set the config controls from the configuation holder'''
        pass

    def OnBibCbChecked(self, evt):
        if evt.IsChecked():
            self.bibfilectrl.Enable(True)
        else:
            self.bibfilectrl.Enable(False)

    def OnChangeProfile(self, evt=0):
        nprofile = PIE_CONFIG.get_profile(evt.GetString())
        self.rootdirctrl.SetPath(nprofile['rootdir'])
        self.desktopdirctrl.SetPath(nprofile['desktopdir'])
        self.bib_cb.SetValue(nprofile['export_bibtex'])
        self.bibexpstarred_cb.SetValue(nprofile['export_starred_only'])
        if nprofile['export_bibtex'] == True: self.bibfilectrl.Enable(True)
        else: self.bibfilectrl.Enable(False)
        self.bibfilectrl.SetPath(nprofile['bibliography_file'])

    def OnAddProfile(self, evt):
        tedia = wx.TextEntryDialog(
            self, _('Name of new settings profile'), _('New profile'), defaultValue='')
        tedo = tedia.ShowModal()
        if tedo == wx.ID_CANCEL:
            return
        profile_name = tedia.GetValue()
        if len(profile_name) < 1 or len(profile_name) > 30:
            return
        retdata = self.GetData()
        PIE_CONFIG.add_profile(profile_name, retdata[1])
        # PIE_CONFIG.set('TheProfile', 'current_profile', self.GetProfile())
        self._refill_profile_choice()
        self.profileChoice.SetStringSelection(profile_name)

    def _refill_profile_choice(self):
        self.profileChoice.Clear()
        for i in PIE_CONFIG.get_profile_names():
            self.profileChoice.Append(i)

    def _do_bindings(self):
        self.profileaddbt.Bind(wx.EVT_BUTTON, self.OnAddProfile)
        self.profileChoice.Bind(wx.EVT_CHOICE, self.OnChangeProfile)
        self.bib_cb.Bind(wx.EVT_CHECKBOX, self.OnBibCbChecked)

    def _do_layout(self):
        self.mainsizer = wx.BoxSizer(wx.VERTICAL)
        self.mainsizer.Add(wx.StaticText(self, -1, _('Profile Options')), 0,
                           wx.ALL, 5)
        self.mainsizer.Add(wx.StaticLine(self, -1), 0, wx.ALL|wx.EXPAND, 5)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(wx.StaticText(self, -1, _('Profile:')), 0, wx.ALL, 5)
        sizer2.Add(self.profileChoice, 1, wx.ALL|wx.EXPAND, 5)
        sizer2.Add(self.profileaddbt, 0, wx.ALL, 5)
        self.mainsizer.Add(sizer2, 0, wx.EXPAND)
        self.mainsizer.Add(wx.StaticText(self, -1, _('Pieberry Folder:')), 0, 
                           wx.ALL, 5)
        self.mainsizer.Add(self.rootdirctrl, 0, wx.ALL|wx.EXPAND, 5)
        self.mainsizer.Add(wx.StaticText(self, -1, _('Desktop Folder:')), 0, 
                           wx.ALL, 5)
        self.mainsizer.Add(self.desktopdirctrl, 0, wx.ALL|wx.EXPAND, 5)
        self.mainsizer.Add(self.bib_cb, 0, wx.ALL, 5)
        self.mainsizer.Add(wx.StaticText(self, -1, _('Bibliography file:')), 0, 
                           wx.ALL, 5)
        self.mainsizer.Add(self.bibfilectrl, 0, wx.ALL|wx.EXPAND, 5)
        self.mainsizer.Add(self.bibexpstarred_cb, 0, wx.ALL, 5)

        self.SetSizer(self.mainsizer)
        self.Layout()


class FormatPanel(wx.Panel):
    uchz = {_('Full Url'): 'full', _('Domain only'): 'domain',
            _('Referring Page'): 'referpage'}
    uchz_rv = {'full': _('Full Url'), 'domain': _('Domain only'),
               'referpage': _('Referring Page')}
    ptxtfchz = {_('Citation text only'): 'plaintext', 
                _('Citation with url'): 'urlplaintext'}
    ptxtfchz_rv = {'plaintext': _('Citation text only'), 
                   'urlplaintext': _('Citation with url')}
    bibtexchoices = {'Misc': 'Misc', 'Online': 'Online'}

    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        
        self.defbibtexchoice = wx.Choice(self, -1, 
                                         choices=self.bibtexchoices.keys())
        self.defbibtexchoice.SetStringSelection(
            PIE_CONFIG.get('Format', 'default_bibtex_entry_type'))
        tta = wx.ToolTip(_('Web pages and downloads will use this type by default'))
        self.defbibtexchoice.SetToolTip(tta)
        self.howpublishedtext = wx.TextCtrl(self, -1, 
                                            validator=pieBibtexValidator(True))
        ttb = wx.ToolTip(_('Web pages and downloads will use this text in the "howpublished" field by default'))     
        self.howpublishedtext.SetValue(
            PIE_CONFIG.get('Format', 'default_howpublished_text'))
        self.urlchoice = wx.Choice(self, -1, choices = self.uchz.keys())
        ttc = wx.ToolTip(_("When referencing urls, should pieberry use the full URL, the page that referred to the full URL (where possible) or just the domain name of the site?"))
        self.urlchoice.SetToolTip(ttc)
        self.urlchoice.SetStringSelection(
            self.uchz_rv[PIE_CONFIG.get('Format', 'url_level_represent')])
        self.plaintextfmtchoice = wx.Choice(self, -1, 
                                       choices=self.ptxtfchz.keys())
        self.plaintextfmtchoice.SetStringSelection(
            self.ptxtfchz_rv[PIE_CONFIG.get('Format', 'plaintext_citation_format')])
        self.protectcaps_cb = wx.CheckBox(self, -1, 
                                          _('Prevent reformatting of capital letters in citations'))
        self.protectcaps_cb.SetValue(
            PIE_CONFIG.getboolean('Format', 'protect_all_caps_in_citations'))

        self.writepdf_cb = wx.CheckBox(self, -1, 
                                       _('Write file metadata when possible'))
        ttd = wx.ToolTip(_('''
Pieberry will try to update metadata fields of pdf, office-xml and open
document files to reflect the known bibliographic data to a limited extent
(generally just the title and author). It doesn\'t always, however, work 
(but should fail safe)'''))
        self.writepdf_cb.SetToolTip(ttd)
        self.writepdf_cb.SetValue(
            PIE_CONFIG.getboolean('Format', 'write_file_metadata'))
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
                'write_file_metadata': self.writepdf_cb.GetValue(),
                'filesystem_length_limit': self.fnlen_spinner.GetValue(),
                'protect_all_caps_in_citations': self.protectcaps_cb.GetValue()
                })
        return retdata

    def _do_layout(self):
        self.mainsizer = wx.BoxSizer(wx.VERTICAL)
        self.mainsizer.Add(wx.StaticText(self, -1, _('Bibliography Options')),
                           0, wx.ALL, 5)
        self.mainsizer.Add(wx.StaticLine(self, -1, style=wx.LI_HORIZONTAL), 
                           0, wx.EXPAND|wx.ALL, 5)
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(
            wx.StaticText(self, -1, _('Default BibTeX entry style for downloads:')), 
            1, wx.ALL, 5)
        sizer1.Add(self.defbibtexchoice, 0, wx.ALL, 5)
        self.mainsizer.Add(sizer1, 0, wx.EXPAND)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(
            wx.StaticText(self, -1, _('Default "how published" text for downloads:')),
            1, wx.ALL, 5)
        sizer2.Add(self.howpublishedtext, 1, wx.ALL, 5)
        self.mainsizer.Add(sizer2, 0, wx.EXPAND)
        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer3.Add(
            wx.StaticText(self, -1, _('Extent of URL to represent in citations:')),
            1, wx.ALL, 5)
        sizer3.Add(self.urlchoice, 0, wx.ALL, 5)
        self.mainsizer.Add(sizer3, 0, wx.EXPAND)
        sizer4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer4.Add(
            wx.StaticText(self, -1, _('Format of plain text citations:')),
            1, wx.ALL, 5)
        sizer4.Add(self.plaintextfmtchoice, 0, wx.ALL, 5)
        self.mainsizer.Add(sizer4, 0, wx.EXPAND)
        self.mainsizer.Add(self.protectcaps_cb, 0, wx.EXPAND|wx.ALL, 5)

        self.mainsizer.Add((20, 20))
        self.mainsizer.Add(wx.StaticText(self, -1, _('File Handling Options')), 
                           0, wx.ALL, 5)
        self.mainsizer.Add(wx.StaticLine(self, -1, style=wx.LI_HORIZONTAL),
                           0, wx.ALL|wx.EXPAND, 5)
        self.mainsizer.Add(self.writepdf_cb, 0, wx.EXPAND|wx.ALL, 5)
        sizer5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer5.Add(
            wx.StaticText(self, -1, _('Maximum filename length:')),
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
        self.currentitem = None
        self.dirListCtrl = wx.ListBox(self, -1, choices=[], style=wx.LB_SORT)
        self.createNewDirBt = wx.Button(self, -1, label=_('New project directory'))
        # self.delDirBt = wx.Button(self, -1, label=_('Delete'))
        self.authorKwdTC = wx.TextCtrl(self, -1)
        tta = wx.ToolTip(_('List author names, separated by semicolons, that indicate documents should going to this directory'))
        self.authorKwdTC.SetToolTip(tta)
        self.titleKwdTC = wx.TextCtrl(self, -1)
        ttb = wx.ToolTip(_('List words, separated by semicolons, that indicate documents should be going to this directory'))
        self.titleKwdTC.SetToolTip(ttb)
        
        self.RecFileTC = wx.TextCtrl(self, -1)
        ttc = wx.ToolTip(_('To assist you in dealing with records management, you can indicate a particular file/record for this folder here'))
        self.RecFileTC.SetToolTip(ttc)
        self.SecLevelCH = wx.Choice(self, -1, choices=SECURITY_CLASSES)
        ttd = wx.ToolTip(_('Warning: this does nothing, it is here just to remind you what type of documents you are holding'))
        self.SecLevelCH.SetToolTip(ttd)
        self.SecLevelCH.SetSelection(0)
        self._do_layout()
        self._do_bindings()
        self._set_properties()

    def _set_properties(self):
        self.dirListCtrl.Clear()
        self.dirListCtrl.SetItems(
            [f.EndName for f in FOLDER_LOOKUP['projectdir']])

    def Finalise(self):
        '''Store filtering criteria for selected item'''
        if not self.currentitem: return
        currentfolder = get_project_folder_by_endname(self.currentitem)
        currentfolder.MatchTerms_Author = [i for i in self.authorKwdTC.GetValue().split(';') if len(i) > 0]
        currentfolder.MatchTerms_Title = [i for i in self.titleKwdTC.GetValue().split(';') if len(i) > 0]
        currentfolder.SecurityLevel = self.SecLevelCH.GetSelection()
        currentfolder.RecordFile = self.RecFileTC.GetValue()
        try:
            currentfolder.write_header()
        except Exception, exc:
            wx.MessageBox(unicode(exc), 'Warning', wx.ICON_WARNING)

    def onListSelChanged(self, evt):
        '''Store filtering criteria for selected item and display it
        for the next'''
        def fill_fields():
            self.titleKwdTC.SetValue(
                string.join(nextfolder.MatchTerms_Title, ';'))
            self.authorKwdTC.SetValue(
                string.join(nextfolder.MatchTerms_Author, ';'))
            self.RecFileTC.SetValue(nextfolder.RecordFile)
            self.SecLevelCH.SetSelection(nextfolder.SecurityLevel)
        if type(evt) in (str, unicode):
            nextfolder = get_project_folder_by_endname(evt)
        else:
            nextfolder = get_project_folder_by_endname(evt.GetString())
        if nextfolder == None: return
        if not self.currentitem:
            fill_fields()
        elif nextfolder.EndName != self.currentitem:
            self.Finalise()
            fill_fields()
        self.currentitem = nextfolder.EndName

    def onCreateNewDir(self, evt=1):
        dia = wx.TextEntryDialog(
            self, _('Enter name of new project directory'), 
            _('New project directory'))
        res = dia.ShowModal()
        if res == wx.ID_OK:
            add_new_folder('projectdir', dia.GetValue())
            self.dirListCtrl.Insert(dia.GetValue(), 0)
            self.dirListCtrl.SetSelection(
                self.dirListCtrl.FindString(dia.GetValue()))
            self.onListSelChanged(dia.GetValue())

    def onDeleteDir(self, evt=1):
        pass
    #     if not self.currentitem:
    #         return
    #     dia = wx.MessageDialog(self, 'Delete %s?' % self.currentitem, 'Delete directory', style=wx.YES_NO|wx.ICON_QUESTION)
    #     ans = dia.ShowModal()
    #     if ans == wx.ID_YES:
    #         self.criteria.pop(self.currentitem)
    #         self.dirListCtrl.SetItems(self.criteria.keys())
    #         self.currentitem = None

    def _do_layout(self):
        s1 = wx.BoxSizer(wx.VERTICAL)
        s1.Add(wx.StaticText(self, -1, _('Desktop Cleaner Settings')), 0, 
               wx.ALL, 5)
        s1.Add(wx.StaticLine(self, -1), 0, wx.ALL|wx.EXPAND, 5)
        s2 = wx.BoxSizer(wx.HORIZONTAL)
        s2.Add(wx.StaticText(self, -1, _('Project directories:')), 1, wx.ALL|wx.EXPAND, 3)
        s2.Add(self.createNewDirBt, 0, wx.ALL|wx.EXPAND, 3)
        s1.Add(s2, 0, wx.EXPAND)
        s1.Add(self.dirListCtrl, 1, wx.ALL|wx.EXPAND, 3)
        # s2.Add(self.delDirBt, 1, wx.ALL|wx.EXPAND, 3)
        s1.Add(wx.StaticText(self, -1, _('Move files to directory with Author:')), 0, wx.ALL, 3)
        s1.Add(self.authorKwdTC, 0, wx.ALL|wx.EXPAND, 3)
        s1.Add(wx.StaticText(self, -1, _('Move files to directory with Title:')), 0, wx.ALL, 3)
        s1.Add(self.titleKwdTC, 0, wx.ALL|wx.EXPAND, 3)
        sg1 = wx.GridSizer(2, 2, 0, 5)
        sg1.Add(wx.StaticText(self, -1, _('Records system file name/number:')), 0, wx.ALL, 3)
        sg1.Add(wx.StaticText(self, -1, _('Security level for folder contents')), 0, wx.ALL, 3)
        sg1.Add(self.RecFileTC, 0, wx.ALL|wx.EXPAND, 3)
        sg1.Add(self.SecLevelCH, 0, wx.ALL|wx.EXPAND, 3)
        s1.Add(sg1, 0, wx.EXPAND)
        self.SetSizer(s1)
        self.Layout()

    def _do_bindings(self):
        self.dirListCtrl.Bind(wx.EVT_LISTBOX, self.onListSelChanged)
        self.createNewDirBt.Bind(wx.EVT_BUTTON, self.onCreateNewDir)
        # self.delDirBt.Bind(wx.EVT_BUTTON, self.onDeleteDir)

class SecurityPanel(wx.Panel):
    def __init__(self, *args, **kwds):
        wx.Panel.__init__(self, *args, **kwds)
        self.mainsizer = wx.BoxSizer(wx.VERTICAL)
        self.mainsizer.Add(
            wx.StaticText(self, -1, _('Security settings')), 0, wx.ALL, 5)
        self.mainsizer.Add(
            wx.StaticLine(self, -1), 0, wx.EXPAND)
        self.mainsizer.Add((20,20),1)
        self.setpwdbt = wx.Button(self, -1, "Set password")
        self.mainsizer.Add(self.setpwdbt, 0, wx.ALL, 5)
        self.mainsizer.Add(
            wx.StaticText(
                self, -1,
                _('''This password will enable the encryption of files 
that are placed in project folders with a security 
level set at or above PROTECTED. The password will be 
stored in a local safe storage location which is accessible
only from your current login. 

If you are storing files on a portable device, then you 
will be able to decrypt them from another installation of 
Pieberry but only if you have set the same password there. 
The password is not stored anywhere in the Pieberry database.''')),
            0, wx.ALL, 5)
        self.mainsizer.Add((20,20),1)
        self.SetSizer(self.mainsizer)
        self.Layout()
        self.setpwdbt.Bind(wx.EVT_BUTTON, self.OnSetPassword)
    
    def OnSetPassword(self, evt):
        existpwd = PIE_CONFIG.get('Security', 'file_key_unhashed')
        if existpwd:
            dia0 = wx.MessageDialog(self, _('There already appears to be a password set.\nChanging it now will mean that any files you have already\nencrypted will become UNREADABLE.\nChanging your password should NOT be necessary, but you can\nproceed if you wish.'), _('Warning'), style=wx.OK|wx.CANCEL)
            ans = dia0.ShowModal()
            if ans == wx.ID_CANCEL: return
            dia0a = wx.PasswordEntryDialog(self, _('Enter existing password'))
            ans = dia0a.ShowModal()
            if ans == wx.ID_CANCEL: return
            pwd0 = dia0a.GetValue()
            dia0a.Destroy()
            if pwd0 != existpwd: 
                wx.MessageBox(_('That is not your current password'), _('Error'))
                return
        dia1 = wx.PasswordEntryDialog(self,  _('Enter password'))
        ans = dia1.ShowModal()
        if ans == wx.ID_CANCEL: return
        pwd1 = dia1.GetValue()
        dia1.Destroy()
        dia2 = wx.PasswordEntryDialog(self,  _('Confirm password'))
        ans = dia2.ShowModal()
        if ans == wx.ID_CANCEL: return
        pwd2 = dia2.GetValue()
        dia2.Destroy()
        if pwd1 != pwd2: 
            wx.MessageBox(_('The passwords did not match.'), _('Error'))
            return
        if len(pwd1) < 4:
            wx.MessageBox(_('This password seems a bit short. Try another'))
            return
        PIE_CONFIG.set('Security', 'file_key', pwd1)
        assert PIE_CONFIG.get('Security', 'file_key') != None
        PIE_INTERNALS.set_encryption_hash(PIE_CONFIG.get('Security', 'file_key'))
        

class SimplePanel(wx.Panel):
    def __init__(self, *args, **kwds):
        wx.Panel.__init__(self, *args, **kwds)
        self.mainsizer = wx.BoxSizer(wx.VERTICAL)
        self.bt = wx.Button(self, -1, "Hello")
        self.mainsizer.Add(self.bt, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(self.mainsizer)
        self.Layout()

class PieSettingsDialog(wx.Dialog):
    
    def __init__(self, *args, **kwds):
        # begin wxGlade: pieConfigDialog.__init__
        kwds["size"] = (600, 400)
        kwds["title"] = _('Pieberry Settings')
        wx.Dialog.__init__(self, *args, **kwds)
        self.mainsizer = wx.BoxSizer(wx.VERTICAL)

        self.listbook = wx.Listbook(self, -1)
        self.listbook.SetImageList(SettingsImageList)

        self.profilepanel = ProfilePanel(self.listbook, -1)
        self.formatpanel = FormatPanel(self.listbook, -1)
        self.cleanerpanel = CleanerPanel(self.listbook, -1)
        self.securitypanel = SecurityPanel(self.listbook, -1)

        self.okBt = wx.Button(self, wx.ID_OK, "Ok")
        self.cancelBt = wx.Button(self, wx.ID_CANCEL, "Cancel")
        
        self._do_layout()
        self._do_bindings()

    def _do_layout(self):
        self.mainsizer.Add(self.listbook, 1, wx.EXPAND|wx.ALL, 5)
        
        self.listbook.AddPage(self.profilepanel, _('Profile'), True, 0)
        self.listbook.AddPage(self.formatpanel, _('Format'), False, 1)
        self.listbook.AddPage(self.cleanerpanel, _('Desktop Cleaner'), False, 2)
        self.listbook.AddPage(self.securitypanel, _('Security'), False, 3)

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
        self.cancelBt.Bind(wx.EVT_BUTTON, self.onCancel)

    def onOk(self, evt=1):
        # commit changes to folders
        self.cleanerpanel.Finalise()
        commit_folders()
        # compile PIE_CONFIG settings
        profiledata = self.profilepanel.GetData()
        theprofile = self.profilepanel.GetProfile()
        alldata = []
        alldata.append(profiledata)
        alldata.append(('TheProfile', 
                        {'current_profile': theprofile}))
        alldata.append(self.formatpanel.GetData())
        for sectionkey, dataset in alldata:
            for key, val in dataset.items():
                PIE_CONFIG.set(sectionkey, key, str(val))
        PIE_CONFIG.update_profile(theprofile, profiledata[1])
        PIE_CONFIG.write_pieconfig()
        if PIE_CONFIG.get('Profile', 'rootdir') != self.profilepanel.rootdiratstart:
            # tell the system if the root directory has changed
            newevt = PieLocationChangedEvent()
            wx.PostEvent(self, newevt)
        # tell the system that the folder choices should be updated
        aevt = PieUpdateAtomChoicesEvent(
            dests=[f.EndName for f in FOLDER_LOOKUP['projectdir']])
        wx.PostEvent(self, aevt)
        self.EndModal(wx.ID_OK)

    def onCancel(self, evt=1):
        rollback_folders()
        self.EndModal(wx.ID_CANCEL)


if __name__ == '__main__':
    import sys
    sys.path.append('/home/raif/development/v2Pieberry/pieberry')
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()

SettingsImageList = wx.ImageList(32, 32)
SettingsImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_profile32.png')))
SettingsImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_format32.png')))
SettingsImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_broom32.png')))
SettingsImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_padlock32.png')))

if __name__ == '__main__':
    dialog_1 = PieSettingsDialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.Show()
    app.MainLoop()


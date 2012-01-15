import wx
import cPickle, string
import pprint

from pieberry.pieberry_config import *

class atomSettingsPanel(wx.Panel):
    def __init__(self, data, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        cf = open(os.path.join(sysdir, 'criteria.pickle'), 'r')
        self.criteria = cPickle.load(cf)
        cf.close()
        self.__do_layout()

        self.Bind(wx.EVT_LISTBOX, self.onListSelChanged, self.dirListCtrl)
        self.Bind(wx.EVT_BUTTON, self.onCreateNewDir, self.createNewDirBt)
        self.Bind(wx.EVT_BUTTON, self.onDeleteDir, self.delDirBt)
        self.currentitem = None # keep track of what's selected in listbox

    def __do_layout(self):
        self.dirListCtrl = wx.ListBox(self, -1, choices=self.criteria.keys(), style=wx.LB_SORT)
        self.createNewDirBt = wx.Button(self, -1, label='Create new project directory')
        self.delDirBt = wx.Button(self, -1, label='Delete')
        self.authorKwdTC = wx.TextCtrl(self, -1)
        self.titleKwdTC = wx.TextCtrl(self, -1)
        self.sweepDirCh = wx.DirPickerCtrl(
            self, 
            -1, 
            path = config.get('AToptions', 'sweep_directory'),
            style = wx.DIRP_USE_TEXTCTRL
            )
        self.fileDirCh = wx.DirPickerCtrl(
            self,
            -1, 
            path = config.get('AToptions', 'filing_directory'),
            style = wx.DIRP_USE_TEXTCTRL
            )
        
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
        s1.Add(wx.StaticText(self, -1, 'Directory to sweep:'), 0, wx.ALL, 3)
        s1.Add(self.sweepDirCh, 0, wx.ALL|wx.EXPAND, 3)
        s1.Add(wx.StaticText(self, -1, 'Root directory for filing system:'), 0, wx.ALL, 3)
        s1.Add(self.fileDirCh, 0, wx.ALL|wx.EXPAND, 3)

        self.SetSizer(s1)
        self.Layout()

    def getCriteria(self):
        if self.currentitem:
            self.criteria[self.currentitem]['title'] = [i for i in self.titleKwdTC.GetValue().split(';') if len(i) > 0]
            self.criteria[self.currentitem]['author'] = [i for i in self.authorKwdTC.GetValue().split(';') if len(i) > 0]
        return self.criteria

    def onListSelChanged(self, evt=1):
        if self.currentitem and evt.GetString() != self.currentitem:
            self.criteria[self.currentitem]['title'] = [i for i in self.titleKwdTC.GetValue().split(';') if len(i) > 0]
            self.criteria[self.currentitem]['author'] = [i for i in self.authorKwdTC.GetValue().split(';') if len(i) > 0]
        self.titleKwdTC.SetValue(string.join(self.criteria[evt.GetString()]['title'], ';'))
        self.authorKwdTC.SetValue(string.join(self.criteria[evt.GetString()]['author'], ';'))
        self.currentitem = evt.GetString()

    def onCreateNewDir(self, evt=1):
        dia = wx.TextEntryDialog(self, 'Enter name of new project directory', 'New project directory')
        res = dia.ShowModal()
        if res == wx.ID_OK:
            self.criteria[dia.GetValue()] = {'title': [], 'author': []}
            self.dirListCtrl.InsertItems([dia.GetValue(),], 0)

    def onDeleteDir(self, evt=1):
        if not self.currentitem:
            return
        dia = wx.MessageDialog(self, 'Delete %s?' % self.currentitem, 'Delete directory', style=wx.YES_NO|wx.ICON_QUESTION)
        ans = dia.ShowModal()
        if ans == wx.ID_YES:
            self.criteria.pop(self.currentitem)
            self.dirListCtrl.SetItems(self.criteria.keys())
            self.currentitem = None

class atomSettingsDialog(wx.Dialog):
    def __init__(self, *args, **kwargs):
        kwargs['size'] = (400, 500)
        kwargs['title'] = 'Desktop cleaner settings'
        wx.Dialog.__init__(self, *args, **kwargs)
        self.atomSettingsPanel = atomSettingsPanel(0, self)
        self.btCancel = wx.Button(self, -1, label='Cancel')
        self.btOk = wx.Button(self, -1, label='Ok')
        s2 = wx.BoxSizer(wx.HORIZONTAL)
        s1 = wx.BoxSizer(wx.VERTICAL)
        s1.Add(self.atomSettingsPanel, 1, wx.EXPAND|wx.ALL, 3)
        s2.Add((20,20), 1)
        s2.Add(self.btCancel, 0, wx.ALL, 3)
        s2.Add(self.btOk, 0, wx.ALL, 3)
        s1.Add(s2, 0, wx.EXPAND)
        self.SetSizer(s1)
        self.Layout()
        self.Bind(wx.EVT_BUTTON, self.onOk, self.btOk)
        self.Bind(wx.EVT_BUTTON, self.onCancel, self.btCancel)
        print self.atomSettingsPanel.fileDirCh.GetPath()

    def onOk(self, evt):
        if os.path.exists(os.path.join(sysdir, 'criteria.bak')):
            os.remove(os.path.join(sysdir, 'criteria.bak'))
        os.rename(os.path.join(sysdir, 'criteria.pickle'), os.path.join(sysdir, 'criteria.bak'))
        f = open(os.path.join(
                sysdir,
                'criteria.pickle'), 'w')
        cPickle.dump(self.atomSettingsPanel.getCriteria(), f)
        f.close()
        config.set('AToptions', 'sweep_directory', self.atomSettingsPanel.sweepDirCh.GetPath())
        config.set('AToptions', 'filing_directory', self.atomSettingsPanel.fileDirCh.GetPath())
        config.write(open(inipath, 'w'))
        # self.EndModal(wx.ID_OK)
        self.Destroy()

    def onCancel(self, evt):
        # self.EndModal(wx.ID_CANCEL)
        self.Destroy()

if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    w = atomSettingsDialog()
    app.SetTopWindow(w)
    w.Show()
    app.MainLoop()


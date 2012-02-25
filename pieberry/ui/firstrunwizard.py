import os, os.path, sys
import wx
import wx.wizard as wiz
 
def makePageTitle(wizPg, title):
    sizer = wx.BoxSizer(wx.VERTICAL)
    wizPg.SetSizer(sizer)
    title = wx.StaticText(wizPg, -1, title)
    title.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
    sizer.AddWindow(title, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
    sizer.AddWindow(wx.StaticLine(wizPg, -1), 0, wx.EXPAND|wx.ALL, 5)
    return sizer
 
class TitledPage(wiz.WizardPageSimple):
    def __init__(self, parent, title):
        wiz.WizardPageSimple.__init__(self, parent)
        self.sizer = makePageTitle(self, title)

class SelRootPage(TitledPage):
    def __init__(self, parent):
        TitledPage.__init__(self, parent, 
                            _('Please select a folder for Pieberry to use'))
        self.rootdirctrl = wx.DirPickerCtrl(
            self, -1, 
            # path = PIE_CONFIG.get('Profile', 'rootdir'),
            path = os.getcwd(),
            # path = '/tmp/pieberry/',
            style = wx.DIRP_USE_TEXTCTRL|wx.DIRP_DIR_MUST_EXIST)
        self.sizer.AddWindow((20,20), 1)
        self.sizer.AddWindow(
            self.rootdirctrl, 0, wx.ALIGN_CENTRE|wx.EXPAND|wx.ALL, 5)
        self.sizer.AddWindow((20,20), 1)

class SelDeskPage(TitledPage):
    def __init__(self, parent):
        TitledPage.__init__(self, parent, 
                            _('Please select your desktop folder'))
        self.deskdirctrl = wx.DirPickerCtrl(
            self, -1, 
            # path = PIE_CONFIG.get('Profile', 'rootdir'),
            path = os.getcwd(),
            style = wx.DIRP_USE_TEXTCTRL|wx.DIRP_DIR_MUST_EXIST)
        self.sizer.AddWindow((20,20), 1)
        self.sizer.AddWindow(
            self.deskdirctrl, 0, wx.ALIGN_CENTRE|wx.EXPAND|wx.ALL, 5)
        self.sizer.AddWindow((20,20), 1)

def show_wizard():
    wizard = wiz.Wizard(None, -1, _("Pieberry Setup Wizard"))
    page1 = SelRootPage(wizard)
    page2 = SelDeskPage(wizard)
    wiz.WizardPageSimple_Chain(page1, page2)
    wizard.FitToPage(page1)
    a = wizard.RunWizard(page1)
    wizard.Destroy()
    return a, (page1.rootdirctrl.GetPath(), page2.deskdirctrl.GetPath())

if __name__ == '__main__': 
    app = wx.PySimpleApp()
    wizard = wiz.Wizard(None, -1, "Simple Wizard")
    page1 = SelRootPage(wizard)
    page2 = SelDeskPage(wizard)
    wiz.WizardPageSimple_Chain(page1, page2)
    wizard.FitToPage(page1)
    a = wizard.RunWizard(page1)
    print a
    wizard.Destroy()
    app.MainLoop()

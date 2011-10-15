import wx
import sys

class PieActor:
    '''Class containing the action-directing functions of the main window'''
    
    def __init__(self):
        pass

    def onFind(self, evt):
        self.ShowSearchPanel()

    def onFindInFolders(self, evt):
        pass

    def onDesktopProcess(self, evt):
        pass
    
    def onDesktopSettings(self, evt):
        pass

    def onSaveBibs(self, evt):
        pass

    def onClose(self, evt):
        sys.exit()

    def onConfig(self, evt):
        pass

    def onAbout(self, evt):
        info = wx.AboutDialogInfo()
        info.AddDeveloper('Raif Sarcich')
        info.SetVersion('2.0alpha1')
        info.SetCopyright('(c) 2010 Raif Sarcich et. al.')
        info.SetLicence(
    '''This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.''')
        info.SetDescription(_('A program to download pdf documents from public websites, and catalogue them in BibTeX format'))
        info.SetName('Pieberry (...for your library)')
        info.SetWebSite('http://members.iinet.net.au/~raifsarcich/pieberry/')
        # _icon = wx.EmptyIcon()
        # _icon.CopyFromBitmap(wx.Bitmap(os.path.join(IMGDIR, 'pie_48.png')))
        # info.SetIcon(_icon)
        wx.AboutBox(info)

    def onDiscard(self, evt):
        pass

    def onPageReference(self, evt):
        pass

    def onEmptyReference(self, evt):
        pass

    def onShowManual(self, evt):
        pass

    def doSearch(self, evt):
        pass

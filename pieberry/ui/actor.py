import wx
import sys, os

from pieberry.ui.events import *
from pieberry.pieconfig.config import *
from pieberry.spoofgeneration import *
from pieberry.ui.settingsdialog import PieSettingsDialog

class PieActor:
    '''Class containing basic action-directing functions of the main window'''
    
    def __init__(self):
        pass

    def onFind(self, evt):
        self.ToggleSearchPanel()

    def onFindInFolders(self, evt):
        self.ToggleSearchPanel(field='filename')

    def OnDesktopProcess(self, evt):
        pass

    def onDesktopFileFile(self, evt):
        pass
    
    def onDesktopSettings(self, evt):
        pass

    def onSaveBibs(self, evt):
        pass

    def onClose(self, evt):
        sys.exit()

    def onConfig(self, evt):
        dia = PieSettingsDialog(self)
        dia.ShowModal()
        dia.Destroy()

    def onAbout(self, evt):
        info = wx.AboutDialogInfo()
        info.AddDeveloper('Raif Sarcich')
        info.SetVersion(PIE_VERSION)
        info.SetCopyright('(c) 2012 Raif Sarcich et. al.')
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
        info.SetDescription(_('The swiss army knife of the public servant. A program encompassing web scraping, cataloguing, filing, search, citation, organisation and archival functions.'))
        info.SetName(_('Pieberry (...for your library)'))
        info.SetWebSite('http://members.iinet.net.au/~raifsarcich/pieberry/')
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(os.path.join(IMGDIR, 'pie_48.png')))
        info.SetIcon(_icon)
        wx.AboutBox(info)

    def onDiscard(self, evt):
        pass

    def onPageReference(self, evt):
        pass

    def onEmptyReference(self, evt):
        pass
    
    def onShowManual(self, evt):
        pass

    def DebugAddWebPane(self, evt=0, noobjects=5):
        self.OpenWebPane()
        pan = self.GetCurrentPane()
        for i in range(noobjects):
            p = spoof_pieobject('web')
            pan.AddObject(p)

    def DebugAddBibPane(self, evt=0, noobjects=5):
        self.OpenSearchPane()
        pan = self.GetCurrentPane()
        for i in range(noobjects):
            p = spoof_pieobject('normal')
            pan.AddObject(p)

    def DebugAddDownloadedPane(self, evt=0, noobjects=5):
        ostore = spoof_pieobjectstore('pdffull', noobjects)
        self.OpenStagingPane()
        pan = self.GetCurrentPane()
        pan.AddObjects(ostore)
        
    def DebugAddAtomisePane(self, evt=0, noobjects=5):
        ostore = spoof_pieobjectstore('desktop', noobjects)
        self.OpenAtomisePane()
        pan = self.GetCurrentPane()
        pan.AddObjects(ostore)
        
    def DebugForceScan(self, evt=0):
        import piefiles
        indexer = piefiles.PieFileIndexer(self)
        self.Bind(EVT_PIE_FILE_INDEX, self.DisplayIndexerStatus)
        self.Bind(EVT_PIE_FILE_INDEX_FINISHED, self.OnIndexerFinished)
        indexer.start()

    def DisplayIndexerStatus(self, evt):
        self.StatusBar.SetStatusText(evt.message)
        # print evt.message
        # print '%d of %d' % (evt.track, evt.count)
    
    def OnIndexerFinished(self, evt):
        pass

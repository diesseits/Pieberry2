import wx
import sys, os

from pieberry.ui.events import *
from pieberry.pieconfig.config import *
from pieberry.spoofgeneration import *
from pieberry.ui.settingsdialog import PieSettingsDialog

import pieberry.ui.stdlines as stdlines

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
        # info.AddDeveloper('Various icons from openclipart.org and the open icon library')
        info.SetVersion(PIE_VERSION)
        info.SetCopyright('(c) 2012 Raif Sarcich et. al.')
        info.SetLicence(stdlines.LICENCE)
        info.SetDescription(stdlines.DESCRIPTION)
        info.SetName(stdlines.SLOGAN)
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
        import pieberry.piefiles
        indexer = pieberry.piefiles.PieFileIndexer(self)
        self.Bind(EVT_PIE_FILE_INDEX, self.DisplayIndexerStatus)
        self.Bind(EVT_PIE_FILE_INDEX_FINISHED, self.OnIndexerFinished)
        indexer.start()

    def DebugAddNotesPane(self, evt):
        self.OpenNotesPane()
        # self.OpenNotesPane()
        # pan = self.GetCurrentPane()

    def DisplayIndexerStatus(self, evt):
        self.StatusBar.SetStatusText(evt.message)
        # print evt.message
        # print '%d of %d' % (evt.track, evt.count)

    def OnIndexerFinished(self, evt):
        pass

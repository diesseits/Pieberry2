# (c) Raif Sarcich 2012, GPLv3

import wx
import pieberry.pieutility
from pieberry.pieconfig.schemas import PIE_TYPES_DOCUMENTS, PIE_TYPES_ALL

from pieberry.ui.events import *
from pieberry.ui.listpanels.listwidgets import *
from pieberry.pieobject import *
from pieberry.ui.listpanels.baselistpanel import BaseListPanel
from pieberry.ui.listpanels.biblistpanel import BibListPanel
from pieberry.ui.listpanels.filelistpanel import FileListPanel
from pieberry.ui.listpanels.breadcrumb import PieBreadcrumbTrail
from pieberry.pieconfig.initsys import IMGDIR

# from wx.lib.buttons import ThemedGenBitmapToggleButton 

class DirListPanel(BibListPanel, FileListPanel):
    '''Class for displaying the contents of directories'''
    paneltype = 'DirListPanel'

    def _setup_data(self):
        self.objectstore = PieObjectStore()
        self.fobjectstore = PieObjectStore()
        
    def _do_layout(self):
        self.sizer0 = wx.BoxSizer(wx.VERTICAL)
        self.sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        self.Bread = PieBreadcrumbTrail(self, -1)
        self.ListDisplay = DirListCtrl(self)
        
        self.rd_BibButton = wx.RadioButton(self, -1, _('Biblio'))
        self.rd_FileButton = wx.RadioButton(self, -1, _('File'))
        
        self.sizer1.Add(self.rd_BibButton, 0, wx.ALL, 5)
        self.sizer1.Add(self.rd_FileButton, 0, wx.ALL, 5)
        self.sizer1.Add((20,20), 1)
        self.sizer0.Add(self.Bread, 0, wx.ALL|wx.EXPAND, 3)
        self.sizer0.Add(self.ListDisplay, 1, wx.ALL|wx.EXPAND, 5)
        self.sizer0.Add(self.sizer1, 0, wx.EXPAND)
        self.SetSizer(self.sizer0)
        self.Layout()

    def _do_bindings(self):
        self.ListDisplay.Bind(wx.EVT_LIST_ITEM_SELECTED,
                              self.onSelectionChanged)
        self.rd_BibButton.Bind(wx.EVT_RADIOBUTTON, self.onToggleMode)
        self.ListDisplay.Bind(wx.EVT_LIST_ITEM_ACTIVATED, 
                              self.onSelectionActivated)
        self.rd_FileButton.Bind(wx.EVT_RADIOBUTTON, self.onToggleMode)

    def AddObject(self, obj, msgtype=None):
        '''This remaking of AddObject can add a PieObject or
        PieFolder, as appropriate - DO NOT USE, use AddObjects only,
        with an objectstore with the containing_folder attribute'''
        if type(obj) == PieObject:
            BaseListPanel.AddObject(self, obj)
        elif type(obj) == PieFolder:
            self.AddFolder(obj)

    def AddFolder(self, fobj):
        '''Add a folder - DO NOT USE - use AddObjects only'''
        ref = self.objectstore.Add(fobj)
        self.ListDisplay.AddFolder(fobj)
        return ref

    def AddObjects(self, ostore):
        '''Subclass AddObjects to specially handle folder view ostores'''
        def fill_class(objtype):
            '''Fill display, certain class at a time'''
            for ref, i in self.objectstore.GetNext(objtype=objtype):
                try:
                    if objtype == 'piefolders':
                        self.ListDisplay.AddFolder(i, ref)
                    elif objtype == 'pieobjects':
                        self.ListDisplay.AddObject(i, ref)
                except:
                    traceback.print_exc()
                    print 'Had trouble here:', ref, i

        if not ostore.get_session_data().has_key('containing_folder'):
            raise Exception, 'Cannot use this objectstore'

        self.ListDisplay.DeleteAllItems()
        self.objectstore = ostore
        fill_class('piefolders')
        fill_class('pieobjects')

    def UpLevel(self, ostore):
        self.AddObjects(ostore)
        self.Bread.AddCrumb(ostore.get_session_data()['containing_folder'])

    def DownLevel(self, ostore):
        self.AddObjects(ostore)

    def onToggleMode(self, evt):
        print evt.GetId()
        print evt.GetInt()
        print self.rd_BibButton.GetId()
        print self.rd_FileButton.GetId()
        if evt.GetId() == self.rd_BibButton.GetId():
            self.ListDisplay.ChangeMode('bib')
        else:
            self.ListDisplay.ChangeMode('file')
        self.AddObjects(self.objectstore)
        # for ref, obj in self.objectstore.GetNext():
        #     self.ListDisplay.AddObject(obj, ref)
        self.Layout()

    def onSelectionActivated(self, evt):
        if type(self.objectstore[self.ListDisplay.GetItemData(evt.GetIndex())]) == PieFolder:
            newevt = PieFolderClickedEvent(
                fobj=self.objectstore[self.ListDisplay.GetItemData(evt.GetIndex())], 
                notify_window=self)
            wx.PostEvent(self, newevt)
        else:
            BaseListPanel.onSelectionActivated(self, evt)

    def MakeMenu(self, menu, obj):
        if type(obj) == PieObject:
            if self.ListDisplay. mode == 'bib':
                BibListPanel.MakeMenu(self, menu, obj)
            elif self.ListDisplay.mode == 'file':
                FileListPanel.MakeMenu(self, menu, obj)

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

class DirDropTarget(wx.FileDropTarget):
    """ This object implements Drop Target functionality for Files """
    def __init__(self, panel):
        """ Initialize the Drop Target, passing in the Object Reference to
        indicate what should receive the dropped files """
        # Initialize the wxFileDropTarget Object
        wx.FileDropTarget.__init__(self)
        # Store the Object Reference for dropped files
        self.panel = panel
 
    def OnDropFiles(self, x, y, filenames):
        """ Implement File Drop """
        print filenames
        path = self.panel.GetCurrentFolder()
        # if path.path() in ROOT_MAP.keys(): 
        #     wx.MessageBox('Dragging into root folders not supported for various reasons')
        newevt = PieFileDroppedEvt(
            panel = self.panel,
            path = path,
            filenames = filenames)
        wx.PostEvent(self.panel, newevt)
        print self.panel.GetCurrentFolder()
        print newevt

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
        droptarget = DirDropTarget(self)
        self.ListDisplay.SetDropTarget(droptarget)
        
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
        self.ListDisplay.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)

    def onKeyDown(self, evt):
        if self.ListDisplay.mode == 'bib':
            BibListPanel.onKeyDown(self, evt)
        elif self.ListDisplay.mode == 'file':
            FileListPanel.onKeyDown(self, evt)

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
        # if self.ListDisplay.mode == 'bib':
        #     self.objectstore.Sort('title')
        # elif self.ListDisplay.mode == 'file':
        self.objectstore.Sort('filename')
        fill_class('piefolders')
        fill_class('pieobjects')

    # def AddExtraObject(self, obj):
    #     '''Add an object that wasn't present when the panel was
    #     initialised (i.e. when a new file is copied to the displayed
    #     folder.'''
    #     self.objectstore.Add(obj)
    #     self.AddObjects(self.objectstore)

    def GetCurrentFolder(self):
        return self.objectstore.sessiondata['containing_folder']

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
            if self.ListDisplay.mode == 'bib':
                BibListPanel.MakeMenu(self, menu, obj)
            elif self.ListDisplay.mode == 'file':
                FileListPanel.MakeMenu(self, menu, obj)

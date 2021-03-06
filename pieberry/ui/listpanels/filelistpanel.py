#GPLv3 Raif Sarcich 2011

import wx
import pieberry.pieutility

from pieberry.ui.events import *
from pieberry.ui.timers import SpinnyTimer
from pieberry.ui.listpanels.listwidgets import *
from pieberry.pieobject import *
from pieberry.ui.listpanels.baselistpanel import BaseListPanel # <-- todo

class FileListPanel(BaseListPanel):
    paneltype = 'FileListPanel'

    def _setup_data(self):
        self.objectstore = PieObjectStore()

    def _do_layout(self):
        self.sizer0 = wx.BoxSizer(wx.VERTICAL)
        self.ListDisplay = FileListCtrl(self)
        self.sizer0.Add(self.ListDisplay, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(self.sizer0)
        self.Layout()

    def _do_bindings(self):
        self.ListDisplay.Bind(wx.EVT_LIST_ITEM_ACTIVATED, 
                              self.onSelectionActivated)
        self.ListDisplay.Bind(wx.EVT_LIST_ITEM_SELECTED,
                              self.onSelectionChanged)
        self.ListDisplay.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)


    def onKeyDown(self, evt):
        keycode = evt.GetKeyCode()
        # if keycode == ord('F'):
        #     nevt = SpoofEvt(self.GetSelectedItem().StatData_FollowUpFlag)
        #     self.onFlagFollowUp(nevt)
        # elif keycode == ord('I'):
        #     nevt = SpoofEvt(self.GetSelectedItem().StatData_Favourite)
        #     self.onFlagFavourite(nevt)
        # elif keycode == ord('N'):
        #     self.onEditNotes(0)
        if keycode == 127:
            self.onDeleteObj(0)
        elif keycode == 341:
            self.onRenameFile(0)
        evt.Skip()

    def onDeleteItem(self, evt):
        print self.GetSelectedItem() 
        print 'not implemented'
        # self.objectstore.Del(self.GetSelectedItemRef())
        # self.ListDisplay.DeleteItem(self.ListDisplay.currentitem)

    def MakeMenu(self, menu, obj):
        '''Function to construct a particular context menu'''
        if obj.has_aspect('stored'):
            rcm_openfile = wx.MenuItem(menu, 1, _('Open file'))
            rcm_openfile.SetBitmap(
                wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_MENU))
            menu.AppendItem(rcm_openfile)
            self.Bind(wx.EVT_MENU, self.onOpenFile, rcm_openfile)
            rcm_opencontaining = wx.MenuItem(menu, 18, 
                                             _('Open containing folder'))
            rcm_opencontaining.SetBitmap(
                wx.ArtProvider.GetBitmap(wx.ART_FOLDER_OPEN, wx.ART_MENU))
            menu.AppendItem(rcm_opencontaining)
            self.Bind(wx.EVT_MENU, self.onOpenContainingFolder, 
                      rcm_opencontaining)
        if obj.has_aspect('saved'):
            rcm_editbibdata = wx.MenuItem(menu, 3, 
                                          _('Edit bibliographic information'))
            menu.AppendItem(rcm_editbibdata)
            self.Bind(wx.EVT_MENU, self.onEditBibData, rcm_editbibdata)
            rcm_deleteobj = wx.MenuItem(menu, 16, 
                                         _('Delete document\tDel'))
            rcm_deleteobj.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_MENU))
            menu.AppendItem(rcm_deleteobj)
            self.Bind(wx.EVT_MENU, self.onDeleteObj, rcm_deleteobj)
        if obj.aspects['encrypted'] == EC_TRUE_UNLOCKED:
            rcm_recryptfile = wx.MenuItem(menu, 28, _('Lock file'))
            rcm_recryptfile.SetBitmap(wx.Bitmap(
                    os.path.join(IMGDIR, 'ic_padlock16.png')))
            menu.AppendItem(rcm_recryptfile)
            self.Bind(wx.EVT_MENU, self.onReEncrypt, rcm_recryptfile)
        elif obj.has_aspect('hasfile'): # mutually exclusive w/ decrypted
            rcm_renamefile = wx.MenuItem(menu, 27, _('Rename file'))
            menu.AppendItem(rcm_renamefile)
            self.Bind(wx.EVT_MENU, self.onRenameFile, rcm_renamefile)


#GPLv3 Raif Sarcich 2011

import wx
import pieutility

from ui.events import *
from ui.timers import SpinnyTimer
from listwidgets import *
from pieobject import *
from baselistpanel import BaseListPanel # <-- todo

class BibListPanel(BaseListPanel):
    '''Class for displaying and working with bibliographic data'''
    paneltype = 'BibListPanel'

    def _setup_data(self):
        self.objectstore = PieObjectStore()

    def _do_layout(self):
        self.sizer0 = wx.BoxSizer(wx.VERTICAL)
        self.sizer1 = wx.BoxSizer(wx.HORIZONTAL)

        self.ListDisplay = BibListCtrl(self)
        # self.DelButton = wx.Button(self, -1, label=_("Delete"))
        # self.sizer1.Add(self.DelButton, 1, wx.ALL, 5)
        self.sizer0.Add(self.ListDisplay, 1, wx.ALL|wx.EXPAND, 5)
        self.sizer0.Add(self.sizer1)
        self.SetSizer(self.sizer0)
        # self.Layout()


    def _do_bindings(self):
        self.ListDisplay.Bind(wx.EVT_LIST_ITEM_ACTIVATED, 
                              self.onSelectionActivated)
        self.ListDisplay.Bind(wx.EVT_LIST_ITEM_SELECTED,
                              self.onSelectionChanged)
        # self.DelButton.Bind(wx.EVT_BUTTON,
        #                     self.onDeleteItem)

    def onDeleteItem(self, evt):
        print self.GetSelectedItem() 
        print 'not implemented'
        # self.objectstore.Del(self.GetSelectedItemRef())
        # self.ListDisplay.DeleteItem(self.ListDisplay.currentitem)

    def onSelectionActivated(self, evt):
        it = self.objectstore[self.ListDisplay.GetItemData(evt.GetIndex())]
        if it.FileData_FullPath:
            pieutility.open_file(it.FileData_FullPath)
            it.stats_opened()
        elif it.WebData_Url:
            pieutility.open_url(it.WebData_Url)
            it.stats_opened()
        else:
            return
        
    def MakeMenu(self, menu, obj):
        '''Function to construct a particular context menu'''
        copyMenu = wx.Menu()
        if obj.has_aspect('onweb'):
            rcm_openinbrowser = wx.MenuItem(menu, 0, _('Open in Browser'))
            rcm_openinbrowser.SetBitmap(
                wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_MENU))
            menu.AppendItem(rcm_openinbrowser)
            self.Bind(wx.EVT_MENU, self.onOpenInBrowser, rcm_openinbrowser)
            rcm_copyurl = wx.MenuItem(menu, 7, _('Copy web url'))
            copyMenu.AppendItem(rcm_copyurl)
            self.Bind(wx.EVT_MENU, self.onCopyUrl, rcm_copyurl)
        if obj.has_aspect('stored'):
            rcm_openfile = wx.MenuItem(menu, 1, _('Open file'))
            rcm_openfile.SetBitmap(
                wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_MENU))
            menu.AppendItem(rcm_openfile)
            self.Bind(wx.EVT_MENU, self.onOpenFile, rcm_openfile)
            # TODO: Deletion. This can come later, requires DB interaction
            # rcm_deletefile = wx.MenuItem(menu, 2, _('Delete'))
            # rcm_deletefile.SetBitmap(
            #     wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_MENU))
            # menu.AppendItem(rcm_deletefile)
            # self.Bind(wx.EVT_MENU, self.onDeleteOnDisk, rcm_deletefile)
        if obj.has_aspect('saved'):
            rcm_editbibdata = wx.MenuItem(menu, 3, 
                                          _('Edit bibliographic information'))
            menu.AppendItem(rcm_editbibdata)
            self.Bind(wx.EVT_MENU, self.onEditBibData, rcm_editbibdata)
            # citations
        if obj.has_aspect('bibdata'):
            rcm_copycitationplain = wx.MenuItem(copyMenu, 4,
                                                _('Copy citation (plain text)'))
            rcm_copycitationplain.SetBitmap(
                wx.ArtProvider.GetBitmap(wx.ART_COPY, wx.ART_MENU))
            copyMenu.AppendItem(rcm_copycitationplain)
            self.Bind(wx.EVT_MENU, self.onCopyCitation_PlainText, 
                      rcm_copycitationplain)
            rcm_copycitationrich = wx.MenuItem(copyMenu, 5,
                                                _('Copy citation (rich text)'))
            rcm_copycitationrich.SetBitmap(
                wx.ArtProvider.GetBitmap(wx.ART_COPY, wx.ART_MENU))
            copyMenu.AppendItem(rcm_copycitationrich)
            self.Bind(wx.EVT_MENU, self.onCopyCitation_RichText, 
                      rcm_copycitationrich)
            rcm_copycitationorg = wx.MenuItem(copyMenu, 6,
                                                _('Copy citation (org mode)'))
            rcm_copycitationorg.SetBitmap(
                wx.ArtProvider.GetBitmap(wx.ART_COPY, wx.ART_MENU))
            copyMenu.AppendItem(rcm_copycitationorg)
            self.Bind(wx.EVT_MENU, self.onCopyCitation_OrgText, 
                      rcm_copycitationorg)
        if obj.BibData_Key:
            rcm_copykey = wx.MenuItem(copyMenu, 8,
                                      _('Copy BibTeX key'))
            rcm_copykey.SetBitmap(
                wx.ArtProvider.GetBitmap(wx.ART_COPY, wx.ART_MENU))
            copyMenu.AppendItem(rcm_copykey)
            self.Bind(wx.EVT_MENU, self.onCopyBibTeXKey)
        menu.AppendMenu(20, _('Copy to clipboard ...'), copyMenu)

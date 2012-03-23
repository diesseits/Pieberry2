#GPLv3 Raif Sarcich 2011

import wx
import pieberry.pieutility

from pieberry.ui.events import *
from pieberry.ui.timers import SpinnyTimer
from pieberry.ui.listpanels.listwidgets import *
from pieberry.pieobject import *
from pieberry.ui.listpanels.baselistpanel import BaseListPanel # <-- todo
from pieberry.pieconfig.initsys import IMGDIR

WEBBMP = wx.Bitmap(os.path.join(IMGDIR, 'ic_globe16.png'))

class SpoofEvt:
    def __init__(self, checked):
        self.reverse_checked = not checked
    def Checked(self):
        return self.reverse_checked
    

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
        self.ListDisplay.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
        # self.DelButton.Bind(wx.EVT_BUTTON,
        #                     self.onDeleteItem)

    def onKeyDown(self, evt):
        keycode = evt.GetKeyCode()
        print keycode
        if evt.HasModifiers():
            evt.Skip()
            return
        if keycode == ord('F'):
            nevt = SpoofEvt(self.GetSelectedItem().StatData_FollowUpFlag)
            self.onFlagFollowUp(nevt)
        elif keycode == ord('I'):
            nevt = SpoofEvt(self.GetSelectedItem().StatData_Favourite)
            self.onFlagFavourite(nevt)
        elif keycode == ord('N'):
            self.onEditNotes(0)
        elif keycode == 127:
            self.onDeleteObj(0)
        evt.Skip()

    def onDeleteItem(self, evt):
        print self.GetSelectedItem() 
        print 'not implemented'
        # self.objectstore.Del(self.GetSelectedItemRef())
        # self.ListDisplay.DeleteItem(self.ListDisplay.currentitem)

    def MakeMenu(self, menu, obj):
        '''Function to construct a particular context menu'''
        copyMenu = wx.Menu()
        if obj.has_aspect('onweb'):
            rcm_openinbrowser = wx.MenuItem(menu, 0, _('Open in Browser'))
            rcm_openinbrowser.SetBitmap(WEBBMP)
            menu.AppendItem(rcm_openinbrowser)
            self.Bind(wx.EVT_MENU, self.onOpenInBrowser, rcm_openinbrowser)
            rcm_copyurl = wx.MenuItem(menu, 7, _('Copy web url'))
            rcm_copyurl.SetBitmap(WEBBMP)
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
            menu.AppendSeparator()
            rcm_editbibdata = wx.MenuItem(menu, 3, 
                                          _('Edit bibliographic information'))
            menu.AppendItem(rcm_editbibdata)
            self.Bind(wx.EVT_MENU, self.onEditBibData, rcm_editbibdata)
            rcm_editnotes = wx.MenuItem(menu, 18, 
                                        _('Edit notes on this item\tN'))
            menu.AppendItem(rcm_editnotes)
            self.Bind(wx.EVT_MENU, self.onEditNotes, rcm_editnotes)
            menu.AppendSeparator()
            rcm_flagfavourite = wx.MenuItem(menu, 19,
                                            _('Flag as important (star)\tI'),
                                            kind=wx.ITEM_CHECK)
            menu.AppendItem(rcm_flagfavourite)
            if obj.StatData_Favourite:
                menu.Check(rcm_flagfavourite.GetId(), True)
            wx.EVT_MENU(menu, 19, self.onFlagFavourite)
            rcm_flagfollowup = wx.MenuItem(menu, 20,
                                           _('Flag for review/follow-up\tF'),
                                           kind=wx.ITEM_CHECK)
            menu.AppendItem(rcm_flagfollowup)
            if obj.StatData_FollowUpFlag:
                menu.Check(rcm_flagfollowup.GetId(), True)
            wx.EVT_MENU(menu, 20, self.onFlagFollowUp)
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
            self.Bind(wx.EVT_MENU, self.onCopyBibTeXKey, rcm_copykey)
        if obj.has_aspect('onweb') or obj.has_aspect('bibdata'):
            menu.AppendSeparator()
            menu.AppendMenu(20, _('Copy to clipboard ...'), copyMenu)
        menu.AppendSeparator()
        rcm_deleteobj = wx.MenuItem(menu, 16, 
                                     _('Delete document\tDel'))
        rcm_deleteobj.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_MENU))
        menu.AppendItem(rcm_deleteobj)
        self.Bind(wx.EVT_MENU, self.onDeleteObj, rcm_deleteobj)
        if obj.has_aspect('hasfile'):
            rcm_renamefile = wx.MenuItem(menu, 27, _('Rename file'))
            menu.AppendItem(rcm_renamefile)
            self.Bind(wx.EVT_MENU, self.onRenameFile, rcm_renamefile)

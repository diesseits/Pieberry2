#GPLv3 Raif Sarcich 2011

import wx
from wx.lib.platebtn import PlateButton
import pieberry.pieutility

from pieberry.pieconfig.initsys import IMGDIR
from pieberry.ui.events import *
from pieberry.ui.timers import SpinnyTimer
from pieberry.ui.listpanels.listwidgets import *
from pieberry.pieobject import *
from pieberry.pieobject.folder import *
from pieberry.ui.listpanels.baselistpanel import BaseListPanel # <-- todo


class DirListCtrl(BaseListCtrl):
    '''File search/browsing control'''
    columnheads = (_('Title'), _('Location'), _('File'))
    columnwidths = (150, 150, 150)

    def __init__(self, parent):
        BaseListCtrl.__init__(self, parent)
        self.SetImageList(PieImageList, wx.IMAGE_LIST_SMALL)

    def AddObject(self, obj, ref, statusmsg=None, 
                  msgtype='success', filtertext=None):
        # print 'FileListCtrl: AddObject at %d, %s' % (self.currentitem, obj)
        if filterout(filtertext, (obj.FileData_FileName, obj.FileData_Root)):
            return
        nexidx = self.InsertImageStringItem(
            self.currentitem, 
            obj.Title(), 
            MessageType[obj.get_icon_code(window_type='filewindow')])
            # MessageType[msgtype])
        self.SetStringItem(nexidx, 1, obj.FileData_ContainingFolder)
        self.SetStringItem(nexidx, 2, obj.FileData_FileName)
        self.SetItemData(nexidx, ref)
        self.itemDataMap[ref] = (obj.Title(), 
                                 obj.FileData_ContainingFolder,
                                 obj.FileData_FileName)
        self.currentitem += 1
        self.EnsureVisible(nexidx)
        return nexidx


class BreadCrumbTrail(wx.Panel):
    '''A breadcrumb trail display'''
    def __init__(self, parent, initlvl=None, *args, **kwargs):
        wx.Panel.__init__(self, parent, root, *args, **kwargs)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)
        self.Layout()
        self.crumbs = []
        self.folders = []
        if initlvl and type(initlvl) == PieFolder:
            self.DownLevelObj(initlvl)
        elif initlvl and type(initlvl) == unicode:
            self.DownLevel(initlvl)

    def _add_crumb(self, txt):
        bt = wx.Button(self, -1, txt)
        self.sizer.Add(bt, 0, wx.ALL, 2)
        self.crumbs.append(bt)
        
    def DownLevelObj(self, piefolder):
        self._add_crumb(piefolder.EndName)

    def DownLevel(self, lvltext):
        self._add_crumb(lvltext)

    def UpLevel(self):
        assert len(self.crumbs) > 0
        havefolders = len(self.folders) == len(self.crumbs)
        if havefolders: retfolder = self.folders.pop(-1)
        else: retfolder = None
        self.sizer.Remove(self.crumbs[-1])
        self.Refresh()
        return self.crumbs.pop(-1), retfolder
        
    def OnUpLevel(self, evt):
        pass

class MtgPListPanel(BaseListPanel):
    paneltype = 'MtgPListPanel'

    def _setup_data(self):
        self.objectstore = PieObjectStore()

    def _do_layout(self):
        self.sizer0 = wx.BoxSizer(wx.VERTICAL)
        # Title display
        self.TitleLb = wx.StaticText(self, -1, 'Title')
        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.TitleLb.SetFont(font)

        # Breadcrumb trail?

        # Agenda shortcut button
        self.AgendaBt = PlateButton(
            self, -1, label='Hello', bmp=wx.Bitmap(os.path.join(IMGDIR, 'ic_blueball16.png')))
        # The List Display
        self.ListDisplay = FileDirListCtrl(self)

        # Action buttons
        self.absizer = wx.BoxSizer(wx.HORIZONTAL)
        self.NewMtgBt = wx.Button(self, -1, _('New Meeting'))
        self.absizer.Add(self.NewMtgBt, 1, wx.EXPAND|wx.ALL, 3)
        
        self.SetSizer(self.sizer0)
        self.Layout()

    def _do_layout(self):
        self.sizer0.Add(self.TitleLb, 0)
        self.sizer0.Add(self.ListDisplay, 1, wx.ALL|wx.EXPAND, 5)

    def _do_bindings(self):
        self.ListDisplay.Bind(wx.EVT_LIST_ITEM_ACTIVATED, 
                              self.onSelectionActivated)
        self.ListDisplay.Bind(wx.EVT_LIST_ITEM_SELECTED,
                              self.onSelectionChanged)
        self.ListDisplay.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)

    def _switch_to_filelist(self):
        pass
    
    def _switch_to_dirlist(self):
        pass

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
        evt.Skip()


    def onSelectionActivated(self, evt):
        it = self.objectstore[self.ListDisplay.GetItemData(evt.GetIndex())]
        if it.FileData_FullPath:
            pieberry.pieutility.open_file(it.FileData_FullPath)
            it.stats_opened()
        elif it.WebData_Url:
            pieberry.pieutility.open_url(it.WebData_Url)
            it.stats_opened()
        else:
            return

    def onDeleteItem(self, evt):
        print self.GetSelectedItem() 
        print 'not implemented'
        # self.objectstore.Del(self.GetSelectedItemRef())
        # self.ListDisplay.DeleteItem(self.ListDisplay.currentitem)

    def MakeMenu(self, menu, obj):
        '''Function to construct a particular context menu'''
        pass

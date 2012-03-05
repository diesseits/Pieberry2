import wx, sys, datetime
import wx.lib.mixins.listctrl as listmix
from pprint import pprint

from imagelist import PieImageList, MessageType

def filterout(filtertext, fields):
    '''determine whether to filter out a given term'''
    if not filtertext: return False
    to_filter_out = True
    for t in fields:
        if filtertext.lower() in t.lower(): to_filter_out = False
    if to_filter_out: 
        return True
    else:
        return False

class BaseListCtrl(wx.ListCtrl, 
                   listmix.ColumnSorterMixin,
                   listmix.ListCtrlAutoWidthMixin):
    '''Control for displaying results in the download/scraping process'''
    columnheads = ('',)
    columnwidths = (480,)

    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent=parent, id=-1, 
                             style=wx.LC_REPORT|wx.EXPAND|wx.LC_SORT_ASCENDING)
        for i in range(len(self.columnheads)):
            self.InsertColumn(i, self.columnheads[i])
            self.SetColumnWidth(i, self.columnwidths[i])

        self.itemDataMap = {}
        listmix.ColumnSorterMixin.__init__(self, len(self.columnheads))
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        self.currentitem = 0
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected)

    def GetListCtrl(self):
        '''function to support mixins'''
        return self

    def AddObject(self, pobj, ref=0, filtertext=None):
        '''Add object serially to the list view
        give also a reference to position in objectstore'''
        print 'BaseListCtrl: not implemented: AddObject'

    def onResize(self, evt):
        '''Resize columns on widget resize'''
        print 'BaseListCtrl: not implemented: onResize'
    
    def onItemSelected(self, evt):
        if evt.GetIndex() == -1: return
        self.currentitem = evt.GetIndex()
        # print 'onItemSelected:', self.currentitem

    def DeleteAllItems(self):
        self.itemDataMap = {}
        wx.ListCtrl.DeleteAllItems(self)

    def DeleteItem(self, ref):
        '''Delete an item ... ref means ... what?'''
        # self.itemDataMap.pop(ref)
        wx.ListCtrl.DeleteItem(self, ref)

    def DeleteItemByOstoreRef(self, ref):
        for i in range(self.GetItemCount()):
            if self.GetItemData(i) == ref:
                wx.ListCtrl.DeleteItem(self, i)
                break

    # TODO: Functionality yet to come for tip windows
    def onMouseEnterList(self, evt):
        self.mouseOverList = True

    def onMouseExitList(self, evt):
        self.mouseOverList = False
        if self.tipwindow and sys.platform == 'linux2': #irritating non x-platform behaviour 
            self.tipwindow.Destroy()
            self.tipwindow = None


class WebListCtrl(BaseListCtrl, listmix.CheckListCtrlMixin):
    '''Control for displaying results in the download/scraping process'''
    columnheads = ('', _('Link'), _('Url'))
    columnwidths = (20, 250, 250)

    def __init__(self, parent):
        BaseListCtrl.__init__(self, parent)
        listmix.CheckListCtrlMixin.__init__(self)

    def AddObject(self, obj, ref, 
                  statusmsg='', 
                  filtertext=None, 
                  checkstatus=False):
        '''Add an object, returning the item's current index in the ListCtrl'''
        # print 'Adding:', obj
        # print ' ... which should be checked:', checkstatus
        if filterout(filtertext, (obj.WebData_LinkText, obj.Url())):
            return
        nexidx = self.InsertStringItem(self.currentitem, statusmsg)
        self.SetStringItem(nexidx, 1, obj.WebData_LinkText)
        self.SetStringItem(nexidx, 2, obj.Url())
        self.SetItemData(nexidx, ref)
        self.itemDataMap[ref] = [checkstatus,
                                 obj.WebData_LinkText,
                                 obj.Url()]
        self.CheckItem(nexidx, checkstatus)
        self.currentitem += 1
        self.EnsureVisible(nexidx)
        return nexidx

    def OnCheckItem(self, idx, chk):
        # print 'WebListCtrl: OnCheckItem:', idx, chk
        self.itemDataMap[self.GetItemData(idx)][0] = chk

    def GetCheckedList(self):
        '''Give a tuple of indices of positively checked items'''
        return tuple([ idx for idx in self.itemDataMap.keys() if self.itemDataMap[idx][0] == True ])

class FileListCtrl(BaseListCtrl):
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

class BibListCtrl(BaseListCtrl):
    '''Control for displaying richer bibliographic search data'''
    columnheads = ('', _('Author'), _('Date'), _('Title'))
    columnwidths = (20, 160, 80, 240)

    def __init__(self, parent):
        BaseListCtrl.__init__(self, parent)
        self.SetImageList(PieImageList, wx.IMAGE_LIST_SMALL)
    
    def AddObject(self, obj, ref, filtertext=None, msgtype=None):
        # print 'BibListCtrl.AddObject at %d, %s' % (self.currentitem, obj)
        if filterout(filtertext, 
                     (obj.Author(), str(obj.ReferDate().year), obj.Title())):
            # print 'Filtered out - returning'
            return
        if not msgtype:
            msgtype = obj.get_icon_code('bibwindow')
        nexidx = self.InsertImageStringItem(
            self.currentitem, 
            '', 
            MessageType[msgtype])
        self.SetStringItem(nexidx, 1, obj.Author())
        self.SetStringItem(nexidx, 2, str(obj.ReferDate().strftime('%Y-%m-%d')))
        self.SetStringItem(nexidx, 3, obj.Title())
        self.SetItemData(nexidx, ref)
        # colorise if flagged for follow up
        if obj.StatData_FollowUpFlag:
            td = datetime.datetime.today() - obj.StatData_FollowUpDate
            if td.days == 0:
                self.SetItemTextColour(nexidx, 'blue')
            elif td.days < 4:
                self.SetItemTextColour(nexidx, 'purple')
            elif td.days > 6:
                self.SetItemTextColour(nexidx, 'red')
        self.itemDataMap[ref] = [msgtype,
                                 obj.Author(), 
                                 str(obj.ReferDate()),#.year),
                                 obj.Title()]
        self.currentitem += 1
        self.EnsureVisible(nexidx)
        return nexidx

    def GetIndexFromRef(self, ref):
        '''Get the list position of an item by its reference key'''
        for i in range(len(self.itemDataMap.keys())):
            if ref == self.GetItemData(i):
                return i
        raise ValueError, "ListCtrl does not have an item with reference %d" % ref
    
class GBListCtrl(BaseListCtrl, listmix.CheckListCtrlMixin):
    '''Control for displaying results in the download/scraping process'''
    columnheads = ('', _('Author'), _('Date'), _('Title'))
    columnwidths = (20, 160, 80, 240)

    def __init__(self, parent):
        BaseListCtrl.__init__(self, parent)
        listmix.CheckListCtrlMixin.__init__(self)

    def AddObject(self, obj, ref, 
                  statusmsg='Added', 
                  filtertext=None, 
                  checkstatus=False):
        '''Add an object, returning the item's current index in the ListCtrl'''
        # print 'Adding:', obj
        # print ' ... which should be checked:', checkstatus
        if filterout(filtertext, 
                     (obj.Author(), str(obj.ReferDate().year), obj.Title())):
            return
        nexidx = self.InsertStringItem(
            self.currentitem, 
            '')
        self.SetStringItem(nexidx, 1, obj.Author())
        self.SetStringItem(nexidx, 2, str(obj.ReferDate().strftime('%Y-%m-%d')))
        self.SetStringItem(nexidx, 3, obj.Title())
        # nexidx = self.InsertStringItem(self.currentitem, statusmsg)
        # self.SetStringItem(nexidx, 1, obj.WebData_LinkText)
        # self.SetStringItem(nexidx, 2, obj.Url())
        self.SetItemData(nexidx, ref)
        self.itemDataMap[ref] = [checkstatus,
                                 obj.Author(), 
                                 str(obj.ReferDate()),#.year),
                                 obj.Title()]
        # self.itemDataMap[ref] = [checkstatus,
        #                          obj.WebData_LinkText,
        #                          obj.Url()]
        self.CheckItem(nexidx, checkstatus)
        self.currentitem += 1
        self.EnsureVisible(nexidx)
        return nexidx

    def OnCheckItem(self, idx, chk):
        # print 'WebListCtrl: OnCheckItem:', idx, chk
        self.itemDataMap[self.GetItemData(idx)][0] = chk

    def GetCheckedList(self):
        '''Give a tuple of indices of positively checked items'''
        return tuple([ idx for idx in self.itemDataMap.keys() if self.itemDataMap[idx][0] == True ])



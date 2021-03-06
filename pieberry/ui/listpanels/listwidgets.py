import wx, sys, datetime
import wx.lib.mixins.listctrl as listmix
from pprint import pprint

from imagelist import PieImageList, MessageType
from pieberry.pieconfig.config import PIE_CONFIG
from pieberry.pieutility.date import fmtdate

ATH = False
if PIE_CONFIG.getboolean('Format', 'atom_title_hack'): ATH = True

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
        self.__init_columns()
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected)

    def __init_columns(self):
        for i in range(len(self.columnheads)):
            self.InsertColumn(i, self.columnheads[i])
            self.SetColumnWidth(i, self.columnwidths[i])

        self.itemDataMap = {}
        listmix.ColumnSorterMixin.__init__(self, len(self.columnheads))
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        self.currentitem = 0

    def GetListCtrl(self):
        '''function to support mixins'''
        return self

    def AddObject(self, pobj, ref=0, filtertext=None):
        '''Add object serially to the list view
        give also a reference to position in objectstore'''
        print 'BaseListCtrl: not implemented: AddObject'

    def EnsureVisible(self, idx):
        if sys.platform in ('win32', 'win64'):
            wx.ListCtrl.EnsureVisible(self, idx)

    def _set_columndata(self, idx, obj):
        '''Set relevant data to the column at row: idx'''
        pass

    def _set_itemdata(self, idx, ref, obj):
        '''Set relevant data in the listctrl's data stores: for row:
        idx; using ref: the reference number for the ostore; using
        obj: the object in question.'''
        pass

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

    def UpdateItem(self, ref):
        self._set_itemdata(ref)

    def UpdateItemByOstoreRef(self, ref, obj=None):
        print 'UpdateItemByOstoreRef'
        if not obj: obj = self.GetParent().objectstore[ref]
        for idx in range(self.GetItemCount()):
            if self.GetItemData(idx) == ref:
                self._set_columndata(idx, obj)
                self._set_itemdata(idx, ref, obj)
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

    def _set_columndata(self, idx, obj):
        '''Set relevant data to the column at row: idx'''
        self.SetStringItem(idx, 1, obj.WebData_LinkText)
        self.SetStringItem(idx, 2, obj.WebData_Url)

    def _set_itemdata(self, idx, ref, obj, checkstatus=False):
        '''Set relevant data in the listctrl's data stores: for row:
        idx; using ref: the reference number for the ostore; using
        obj: the object in question.'''
        self.SetItemData(idx, ref)
        self.itemDataMap[ref] = [checkstatus,
                                 obj.WebData_LinkText,
                                 obj.WebData_Url]

    def AddObject(self, obj, ref, 
                  statusmsg='', 
                  filtertext=None, 
                  checkstatus=False):
        '''Add an object, returning the item's current index in the ListCtrl'''
        # print 'Adding:', obj
        # print ' ... which should be checked:', checkstatus
        if filterout(filtertext, (obj.WebData_LinkText, obj.WebData_Url)):
            return
        nexidx = self.InsertStringItem(self.currentitem, statusmsg)
        self._set_columndata(nexidx, obj)
        self._set_itemdata(nexidx, ref, obj, checkstatus)
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
    columnwidths = (200, 150, 150)

    def __init__(self, parent):
        BaseListCtrl.__init__(self, parent)
        self.SetImageList(PieImageList, wx.IMAGE_LIST_SMALL)

    def _set_columndata(self, idx, obj):
        # print 'FileListCtrl._set_columndata'
        self.SetItemImage(idx, MessageType[obj.get_icon_code(window_type='filewindow')])
        self.SetItemText(idx, obj.Title())
        self.SetStringItem(idx, 1, obj.FileData_ContainingFolder)
        self.SetStringItem(idx, 2, obj.FileData_FileName)

    def _set_itemdata(self, idx, ref, obj):
        # print 'FileListCtrl._set_itemdata'
        self.SetItemData(idx, ref)
        self.itemDataMap[ref] = (obj.Title(), 
                                 obj.FileData_ContainingFolder,
                                 obj.FileData_FileName)
        
    def AddObject(self, obj, ref, statusmsg=None, 
                  msgtype='success', filtertext=None):
        # print 'FileListCtrl: AddObject at %d, %s' % (self.currentitem, obj)
        if filterout(filtertext, (obj.FileData_FileName, obj.FileData_Root)):
            return
        nexidx = self.InsertImageStringItem(self.currentitem, '', 0)
        self._set_columndata(nexidx, obj)
        self._set_itemdata(nexidx, ref, obj)
        self.currentitem += 1
        self.EnsureVisible(nexidx)
        return nexidx

class BibListCtrl(BaseListCtrl):
    '''Control for displaying richer bibliographic search data'''
    columnheads = ('', '', _('Author'), _('Date'), _('Title'))
    columnwidths = (20, 16, 160, 80, 240)

    def __init__(self, parent):
        BaseListCtrl.__init__(self, parent)
        self.SetImageList(PieImageList, wx.IMAGE_LIST_SMALL)

    def _set_columndata(self, idx, obj, msgtype=None):
        '''Set relevant data to the column at row: idx'''
        # print 'BibListCtrl._set_columndata'
        if not msgtype:
            msgtype = obj.get_icon_code('bibwindow')
        self.SetItemImage(idx, MessageType[msgtype])
        # self.SetItemText(idx, '')
        if obj.notes: self.SetStringItem(idx, 1, u'\u270D') # writing pen
        else: self.SetStringItem(idx, 1, '')
        self.SetStringItem(idx, 2, obj.Author())
        self.SetStringItem(idx, 3, fmtdate(obj.ReferDate()))
        self.SetStringItem(idx, 4, obj.Title(atom_title_hack=ATH))
        if obj.StatData_FollowUpFlag:
            td = datetime.datetime.today() - obj.StatData_FollowUpDate
            if td.days < PIE_CONFIG.getint('Internal', 'flagged_purpleafter'):
                self.SetItemTextColour(idx, 'blue')
            elif td.days > PIE_CONFIG.getint('Internal', 'flagged_redafter'):
                self.SetItemTextColour(idx, 'red')
            else:
                self.SetItemTextColour(idx, 'purple')
        else: self.SetItemTextColour(idx, wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT))

    def _set_itemdata(self, idx, ref, obj):
        '''Set relevant data in the listctrl's data stores: for row:
        idx; using ref: the reference number for the ostore; using
        obj: the object in question.'''
        self.SetItemData(idx, ref)
        self.itemDataMap[ref] = [obj.get_icon_code('bibwindow'),
                                 1 if obj.notes else 0,
                                 obj.Author(), 
                                 str(obj.ReferDate()),
                                 obj.Title()]
    
    def AddObject(self, obj, ref, filtertext=None, msgtype=None):
        # print 'BibListCtrl.AddObject at %d, %s' % (self.currentitem, obj)
        if filterout(filtertext, 
                     (obj.Author(), str(obj.ReferDate().year), obj.Title())):
            # print 'Filtered out - returning'
            return
        nexidx = self.InsertImageStringItem(
            self.currentitem, 
            '', 
            0)
        self._set_columndata(nexidx, obj, msgtype=msgtype)
        self._set_itemdata(nexidx, ref, obj)
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

    def _set_columndata(self, idx, obj):
        '''Set relevant data to the column at row: idx'''
        self.SetStringItem(idx, 1, obj.Author())
        self.SetStringItem(idx, 2, fmtdate(obj.ReferDate()))
        self.SetStringItem(idx, 3, obj.Title())

    def _set_itemdata(self, idx, ref, obj, checkstatus=False):
        '''Set relevant data in the listctrl's data stores: for row:
        idx; using ref: the reference number for the ostore; using
        obj: the object in question.'''
        self.SetItemData(idx, ref)
        self.itemDataMap[ref] = [checkstatus,
                                 obj.Author(), 
                                 str(obj.ReferDate()),#.year),
                                 obj.Title()]

    def AddObject(self, obj, ref, 
                  statusmsg='Added', 
                  filtertext=None, 
                  checkstatus=False,
                  msgtype=None):
        '''Add an object, returning the item's current index in the ListCtrl'''
        # print 'Adding:', obj
        # print ' ... which should be checked:', checkstatus
        if filterout(filtertext, 
                     (obj.Author(), str(obj.ReferDate().year), obj.Title())):
            return
        nexidx = self.InsertStringItem(
            self.currentitem, 
            '')
        self._set_columndata(nexidx, obj)
        self._set_itemdata(nexidx, ref, obj, checkstatus)
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


from pieberry.pieobject import PieFolder

class DirListCtrl(BibListCtrl, FileListCtrl):
    '''File search/browsing control'''
    # column setup for bib mode
    columnheads_bib = ('', '', _('Author'), _('Date'), _('Title'))
    columnwidths_bib = (20, 16, 160, 80, 240)
    # column setup for file mgmt mode
    columnheads_file = (_('Title'), _('Location'), _('File'))
    columnwidths_file = (200, 150, 150)

    columnheads = ('', '', _('Author'), _('Date'), _('Title'))
    columnwidths = (20, 16, 160, 80, 240)

    mode = 'bib'

    def __init__(self, parent):
        BaseListCtrl.__init__(self, parent)
        self.SetImageList(PieImageList, wx.IMAGE_LIST_SMALL)

    def _set_itemdata(self, idx, ref, obj):
        '''Set relevant data in the listctrl's data stores: for row:
        idx; using ref: the reference number for the ostore; using
        obj: the object in question.'''
        self.SetItemData(idx, ref)
        if type(obj) == PieFolder:
            self.SetItemData(idx, ref)
            if self.mode == 'bib':
                self.itemDataMap[ref] = ['000',
                                         0, u'< folder >', None, obj.EndName]
            elif self.mode == 'file':
                self.itemDataMap[ref] = [obj.EndName, u'< folder >', None]
            return
        if self.mode == 'bib':
            BibListCtrl._set_itemdata(self, idx, ref, obj)
        elif self.mode == 'file':
            FileListCtrl._set_itemdata(self, idx, ref, obj)
        else:
            raise Exception, 'invalid mode'

    def _set_columndata(self, idx, obj, msgtype=None):
        if type(obj) == PieFolder:
            print 'special'
            return
        if self.mode == 'bib':
            BibListCtrl._set_columndata(self, idx, obj)
        elif self.mode == 'file':
            FileListCtrl._set_columndata(self, idx, obj)
        else:
            raise Exception, 'invalid mode'

    def AddObject(self, obj, ref, statusmsg=None, 
                  msgtype='success', filtertext=None):
        # print 'FileListCtrl: AddObject at %d, %s' % (self.currentitem, obj)
        if filterout(filtertext, (obj.FileData_FileName, obj.Title(), obj.Author())):
            return
        nexidx = self.InsertImageStringItem(
            self.currentitem, 
            '', 
            0)
        self._set_columndata(nexidx, obj, msgtype=msgtype)
        self._set_itemdata(nexidx, ref, obj)
        self.currentitem += 1
        self.EnsureVisible(nexidx)
        return nexidx

    def AddFolder(self, fobj, ref):
        '''Shoehorn a folder into the list view'''
        nexidx = self.InsertImageStringItem(
            self.currentitem,
            '',
            MessageType['folder'])
        if self.mode == 'bib':
            self.SetStringItem(nexidx, 2, _('< folder >'))
            self.SetStringItem(nexidx, 3, u'...')
            self.SetStringItem(nexidx, 4, fobj.EndName)
        elif self.mode == 'file':
            self.SetStringItem(nexidx, 0, fobj.EndName)
            self.SetStringItem(nexidx, 1, fobj.path())
            self.SetStringItem(nexidx, 2, _('< folder >'))
        self._set_itemdata(nexidx, ref, fobj)
        self.currentitem += 1
        self.EnsureVisible(nexidx)
        return nexidx

    def ChangeMode(self, mode):
        '''Change the display mode between bibliographic and file
        management modes'''
        self.DeleteAllItems()
        self.DeleteAllColumns()
        if mode == 'bib':
            self.columnheads = self.columnheads_bib
            self.columnwidths = self.columnwidths_bib
            self.mode = 'bib'
        elif mode == 'file':
            self.columnheads = self.columnheads_file
            self.columnwidths = self.columnwidths_file
            self.mode = 'file'
        else:
            raise Exception, 'invalid mode %s' % mode
        # self.__init_columns()
        for i in range(len(self.columnheads)):
            self.InsertColumn(i, self.columnheads[i])
            self.SetColumnWidth(i, self.columnwidths[i])

        self.itemDataMap = {}
        self.currentitem = 0
        # BaseListCtrl.__init_columns(self)

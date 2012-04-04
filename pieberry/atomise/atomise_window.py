# GNU GPLv3, Raif Sarcich 2012

import wx
import traceback
import os, string, time, sys, datetime
from pieberry.pieconfig.paths import IMGDIR
from pieberry.pieobject import PieObjectStore
from pieberry.ui.events import *
from wx.lib.buttons import ThemedGenBitmapToggleButton 
from pieberry.atomise.atomise_imagelist import *

if sys.platform == 'win32':
    class atomIcon(wx.StaticBitmap):
        def __init__(self, parent, rowid, *args, **kwargs):
            wx.StaticBitmap.__init__(self, parent, -1, size=(22, 22))
            self.rowid = rowid
            
        def getRowId(self):
            return self.rowid
else:
    class atomIcon(wx.Panel):
        def __init__(self, parent, rowid, bmp, *args, **kwargs):
            wx.Panel.__init__(self, parent, -1, size=(22, 22))#(bmp.GetWidth(), bmp.GetHeight))
            self._bmp = bmp
            self.rowid = rowid
            self.Bind(wx.EVT_PAINT, self.OnPaint)
        def OnPaint(self, event):
            dc = wx.AutoBufferedPaintDC(self)
            dc.DrawBitmap(self._bmp, 0, 0)
        def getRowId(self):
            return self.rowid

class atomButton(wx.Button):
    def __init__(self, parent, rowid, id=wx.ID_ANY, label=''):
        wx.Button.__init__(self, parent, id, label)
        self.rowid = rowid

    def getRowId(self):
        return self.rowid

class atomBmpButton(wx.BitmapButton):
    def __init__(self, parent, rowid, id=wx.ID_ANY, bitmap=None):
        wx.BitmapButton.__init__(self, parent, id, bitmap)
        self.rowid = rowid

    def getRowId(self):
        return self.rowid

class FlagBitmapButton(ThemedGenBitmapToggleButton):
    image = os.path.join(IMGDIR, 'ic_flag16.png')
    
    def __init__(self, parent, rowid, id=wx.ID_ANY, bitmap=None, *args, **kwds):
        theimage = wx.Image(self.image, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        wx.lib.buttons.ThemedGenBitmapToggleButton.__init__(
            self, parent, id, theimage, size=(25,25))
        self.rowid  = rowid

    def getRowId(self):
        return self.rowid

class atomActionWindow(wx.ScrolledWindow):
    '''a window with a dynamic scrolled layout to allow the
    organisation of files'''
    defaultchoices = ('choice1', 'choice2')
    def __init__(self, parent, *args, **kwargs):
        wx.ScrolledWindow.__init__(self, parent, -1, style=wx.RAISED_BORDER)
        self.__do_layout()
        self.__init_data()
        self.parent = parent
        
    def __do_layout(self):
        self.flexsizer = wx.FlexGridSizer(0, 8, 5, 10)
        self.flexsizer.AddGrowableCol(1, 2)
        # self.flexsizer.AddGrowableCol(3, 3)
        font =  wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        for i in ('    ', 'File name', 'Destination folder', '', '', '', '', ''):
            txt = wx.StaticText(self, -1, i, style=wx.ALIGN_CENTER|wx.EXPAND)
            txt.SetFont(font)
            self.flexsizer.Add(txt)

        self.SetSizer(self.flexsizer)
        self.SetScrollbars(0, 20, 0, 50)

    def __init_data(self):
        self.rowlist = []
        self.rowdata = PieObjectStore()
        self.maxrow = -1
        self.currentrow = -1

    def _on_createbib(self, evt):
        ob = evt.GetEventObject()
        self.currentrow = ob.getRowId()
        # self.currentrow = self.rowdata[ob.getRowId()]
        self.parent.onCreateBib(self.currentrow)

    def _on_gofile(self, evt):
        ob = evt.GetEventObject()
        # self.currentrow = self.rowdata[ob.getRowId()]
        self.currentrow = ob.getRowId()
        self.parent.onGoFile(self.currentrow)

    def _on_delfile(self, evt):
        ob = evt.GetEventObject()
        self.currentrow = ob.getRowId()
        self.parent.onDelFile(self.currentrow)

    def _on_openfile(self, evt):
        ob = evt.GetEventObject()
        self.currentrow = ob.getRowId()
        self.parent.onOpenFile(self.currentrow)

    def _on_flag(self, evt):
        ob = evt.GetEventObject()
        self.currentrow = ob.getRowId()
        bt = getattr(self, 'flagbutton%d' % self.currentrow)
        val = bt.GetValue()
        # bt.SetBackgroundColour('pink')
        self.parent.onFlag(self.currentrow, val)

    def onFileAll(self):
        pass

    def onMouseOverBmp(self, evt):
        print evt.GetEventObject().getRowId()
        mob = evt.GetEventObject().getRowId()
        self.mouseoverbmp = mob
        wx.FutureCall(500, self.onMouseStillOverBmp, mob)

    def onMouseStillOverBmp(self, rowid):
        if self.mouseoverbmp == rowid:
            obj = self.rowdata[rowid]
            ttdata = string.join([
                    u'Author: %s' % obj.Author(),
                    u'Title: %s' % obj.Title(),
                    u'Date: %s' % obj.ReferDate().ctime(),
                    u'File type: %s' % obj.FileData_FileType,
                    u'File size: %dkb' % (obj.FileData_Size / 1000),
                    ], u'\n')
            self.tw = wx.TipWindow(self, ttdata, maxLength=300)
    
    def onMouseOffBmp(self, evt):
        self.mouseoverbmp = -1
        # self.tw.Close()
        # self.tw.Destroy()

    def AddObject(self, obj, recommended_dir=None, suggested_fn=None):
        # Todo - customisable attenuation, (also in web scraping)
        def attenuate(f):
            if f == None: return u''
            if len(f) > 40:
                return f[:36] + ' ...'
            else:
                return f
        
        self.maxrow += 1
        # setattr(self, 'icon%d' % self.maxrow, atomIcon(self, self.maxrow, -1, size=(22, 22)))
        print 'File type', obj.FileData_FileType
        iconcode = obj.get_icon_code(window_type='filewindow')
        icon = AtomImageList.GetBitmap(IconType[iconcode])
        setattr(self, 
                'icon%d' % self.maxrow, 
                atomIcon(self, self.maxrow, icon))

        bm = getattr(self, 'icon%d' % self.maxrow)
        if sys.platform == 'win32':
            bm.SetBitmap(icon)

        bm.Bind(wx.EVT_ENTER_WINDOW, self.onMouseOverBmp)
        bm.Bind(wx.EVT_LEAVE_WINDOW, self.onMouseOffBmp)

        setattr( #TODO need a validator to exclude filesystem chars
            self, 
            'suggesttc%d' % self.maxrow, 
            wx.TextCtrl(self, -1)
            )
        tc = getattr(
            self,
            'suggesttc%d' % self.maxrow)
        tctt = wx.ToolTip(_('You may set the desired filename for this document when it is filed'))
        tc.SetToolTip(tctt)
                         
        setattr(self, 'choice%d' % self.maxrow, wx.Choice(self, -1, choices=self.defaultchoices))
        ch = getattr(self, 'choice%d' % self.maxrow)
        chtt = wx.ToolTip(_('Select a destination project folder here'))
        ch.SetToolTip(chtt)

        setattr(self, 'bibbutton%d' % self.maxrow, atomButton(self, self.maxrow, id=-1, label='To Library'))
        bt = getattr(self, 'bibbutton%d' % self.maxrow)
        bttt = wx.ToolTip(_('Fill out bibliographic data and send to the Library'))
        bt.SetToolTip(bttt)
        # if obj.FileData_FileType != 'pdf':
        #     bt.Enable(False)

        setattr(
            self, 
            'delbutton%d' % self.maxrow, 
            atomBmpButton(self, self.maxrow, id=-1, bitmap=wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_TOOLBAR, (16, 16)))
            )
        delbt = getattr(self, 'delbutton%d' % self.maxrow)
        delbttt = wx.ToolTip(_('Delete'))
        delbt.SetToolTip(delbttt)

        setattr(
            self,
            'openbutton%d' % self.maxrow,
            atomBmpButton(self, self.maxrow, id=-1, bitmap=wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, (16, 16)))
            )
        openbt = getattr(self, 'openbutton%d' % self.maxrow)
        openbttt = wx.ToolTip(_('Open file'))
        openbt.SetToolTip(openbttt)

        setattr(self, 'flagbutton%d' % self.maxrow, FlagBitmapButton(self, self.maxrow, id=-1)#, bitmap=wx.Bitmap(os.path.join(IMGDIR, 'ic_flag16.png')))
                )
        flagbt = getattr(self, 'flagbutton%d' % self.maxrow)
        flagbttt = wx.ToolTip(_('Flag document for follow up'))
        flagbt.SetToolTip(flagbttt)

        if obj.StatData_FollowUpFlag:
            flagbt.SetBackgroundColour('pink')
        setattr(self, 'gobutton%d' % self.maxrow, atomButton(self, self.maxrow, id=-1, label='File it'))
        gobt = getattr(self, 'gobutton%d' % self.maxrow)
        gobttt = wx.ToolTip(_('File this document'))
        gobt.SetToolTip(gobttt)

        self.Bind(wx.EVT_BUTTON, self._on_createbib, bt)
        self.Bind(wx.EVT_BUTTON, self._on_gofile, gobt)
        self.Bind(wx.EVT_BUTTON, self._on_delfile, delbt)
        self.Bind(wx.EVT_BUTTON, self._on_openfile, openbt)
        self.Bind(wx.EVT_BUTTON, self._on_flag, flagbt)
        self.flexsizer.Add(bm)
        self.flexsizer.Add(tc, flag=wx.EXPAND)
        self.flexsizer.Add(ch, flag=wx.EXPAND)
        self.flexsizer.Add(bt)
        self.flexsizer.Add(delbt)
        self.flexsizer.Add(openbt)
        self.flexsizer.Add(flagbt)
        self.flexsizer.Add(gobt)
        self.SetScrollbars(0, 20, 0, 50)
        try:
            ch.SetSelection(self.defaultchoices.index(recommended_dir))
        except:
            ch.SetSelection(0)
        if suggested_fn:
            tc.SetValue(suggested_fn)
        else:
            tc.SetValue(obj.FileData_FileName)
        self.Layout()
        self.rowdata.Add(obj)

    def addTestRow(self, evt):
        testdat = {'initial_fn': 'Test row %d' % (self.maxrow + 1)}
        self.addRow(testdat)

    def removeRow(self, row):
        bm = getattr(self, 'icon%d' % row, None)
        ch = getattr(self, 'choice%d' % row, None)
        bt = getattr(self, 'bibbutton%d' % row, None)
        gobt = getattr(self, 'gobutton%d' % row, None)
        delbt = getattr(self, 'delbutton%d' % row, None)
        opbt = getattr(self, 'openbutton%d' % row, None)
        flbt = getattr(self, 'flagbutton%d' % row, None)
        tc = getattr(self, 'suggesttc%d' % row, None)

        self.flexsizer.Remove(bm)
        self.flexsizer.Remove(ch)
        self.flexsizer.Remove(bt)
        self.flexsizer.Remove(tc)
        self.flexsizer.Remove(delbt)
        self.flexsizer.Remove(opbt)
        self.flexsizer.Remove(flbt)
        self.flexsizer.Remove(gobt)
        bm.Destroy()
        ch.Destroy()
        bt.Destroy()
        tc.Destroy()
        delbt.Destroy()
        opbt.Destroy()
        flbt.Destroy()
        gobt.Destroy()
        self.Layout()
        self.rowdata.Del(row)

    def clearAll(self, evt=1):
        for i in range(0, self.maxrow + 1):
            try:
                self.removeRow(i)
            except:
                continue
        self.maxrow = -1
        self.currentrow = -1
        self.rowdata = PieObjectStore()
        
    def refresh(self):
        pass

    def getCurrentItem(self):
        return self.currentrow

    def getCurrentItemData(self):
        return self.rowdata[self.currentrow]

    def setDestinations(self, dests):
        dests.sort()
        td = ['None']
        td.extend(dests)
        self.defaultchoices = td
        if self.maxrow == -1: return
        for i in range(0, self.maxrow + 1):
            try:
                ch = getattr(self, 'choice%d' % i)
                ch.Clear()
            except:
                continue
            [ch.Append(j) for j in td]
            ch.SetSelection(0)
            

if __name__ == "__main__":
    pass

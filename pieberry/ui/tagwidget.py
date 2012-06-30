# A widget for displaying and editing tags attached to a PieObject

import wx
from wx.lib.platebtn import *

tagnames = ['foo', 'bar', 'hoopla']

class PieTagButton(PlateButton):
    def __init__(self, parent, id, tag, *args, **kwargs):
        PlateButton.__init__(self, parent, id, tag, *args, **kwargs)
        self.tag = tag
    def GetTag(self):
        return self.tag

class PieTagWidget(wx.Panel):
    '''A tag display/editing widget'''
    def __init__(self, parent, id, mode="horizontal", columns=3):
        wx.Panel.__init__(self, parent, id, size=(28,28))
        self.menubtn = None
        self.tags = []
        self.tagbuttons = []
        self.__do_layout(mode, columns)

    def __build_menu(self):
        self.tagmenu = wx.Menu()
        for tn in tagnames:
            if not tn in self.tags:
                self.tagmenu.Append(-1, tn)
        self.tagmenu.Append(-1, "New Tag")
        self.tagmenu.Bind(wx.EVT_MENU, self.onMenuChoice)

    def __append_menubutton(self):
        if not self.menubtn:
            self.menubtn = PlateButton(
                self, -1, 
                # label="Add",
                bmp=wx.ArtProvider.GetBitmap(wx.ART_ADD_BOOKMARK, wx.ART_MENU),
                style=PB_STYLE_SQUARE
                )
            self.menubtn.Bind(wx.EVT_BUTTON, self.onMenuButtonPress)
        self.__build_menu()
        self.menubtn.SetMenu(self.tagmenu)
        self._sizer.Add(self.menubtn, 0)
        self.menubtn.Show()

    def __do_layout(self, mode, columns):
        if mode == "horizontal":
            self._sizer = wx.BoxSizer(wx.HORIZONTAL)
        elif mode == "vertical":
            self._sizer = wx.BoxSizer(wx.VERTICAL)
        else:
            self._sizer = wx.FlexGridSizer(1, columns, 0, 0)
            [ self._sizer.AddGrowableCol(idx) for idx in range(columns) ]
        self._sizer.Add((5,5))
        self.__append_menubutton()
        self.SetSizer(self._sizer)
        self._sizer.Layout()
        self.Layout()

    def onMenuChoice(self, evt):
        tagtxtchosen = self.tagmenu.FindItemById(evt.GetId()).GetLabel()
        if tagtxtchosen == "New Tag":
            self.onCreateNewTag()
        else:
            self.AddTag(tagtxtchosen)

    def onTagPress(self, evt):
        print evt.GetEventObject().GetTag()

    def onMenuButtonPress(self, evt):
        self.menubtn.ShowMenu()

    def onCreateNewTag(self):
        tdia = wx.TextEntryDialog(self, "Name of new tag:", "Create new tag")
        ans = tdia.ShowModal()
        if ans == wx.ID_CANCEL: return
        if len(tdia.GetValue()) == 0: return
        print "Creating new tag: %s" % tdia.GetValue()
        newtag = tdia.GetValue()
        tagnames.append(newtag)
        self.AddTag(newtag)

    def AddTag(self, tag):
        self.tags.append(tag)
        btn = PieTagButton(
            self, -1, 
            tag,
            # bmp=wx.ArtProvider.GetBitmap(wx.ART_FIND, wx.ART_MENU),
            style=PB_STYLE_SQUARE
            )
        self.tagbuttons.append(btn)
        self._sizer.Add(btn, 0)
        btn.Bind(wx.EVT_BUTTON, self.onTagPress)
        self.menubtn.Hide()
        self._sizer.Remove(self.menubtn)
        self.__append_menubutton()
        self._sizer.Layout()
        self.Layout()
        newevt = PieTagAddedEvent(tag = tag)
        wx.PostEvent(self, newevt)

PieTagAddedEvent, EVT_PIE_TAG_ADDED = wx.lib.newevent.NewEvent()
# attributes - tag - the tag added

class PieTagDialog(wx.Dialog):
    def __init__(self, parent):
        title = 'Add tags'
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        super(PieTagDialog, self).__init__(parent, -1, title, 
                                         size=(300,300),style=style)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.ptw = PieTagWidget(self, 1, mode="horizontal")
        buttons = self.CreateButtonSizer(wx.OK|wx.CANCEL)
        self.sizer.Add(wx.StaticText(self, -1, "Add Tags to Document:"), 
                       0, wx.ALL|wx.EXPAND, 5)
        self.sizer.Add(wx.StaticLine(self, -1), 0, wx.ALL|wx.EXPAND, 5)
        self.sizer.Add(self.ptw, 1, wx.EXPAND)
        self.sizer.Add(wx.StaticLine(self, -1), 0, wx.ALL|wx.EXPAND, 5)
        self.sizer.Add(buttons, 0, wx.ALL|wx.EXPAND, 5)

        self.SetSizerAndFit(self.sizer)
        self.ptw.Bind(EVT_PIE_TAG_ADDED, self.onTagAdded)
        
    def onTagAdded(self, evt):
        wx.CallAfter(self.doRefresh())

    def doRefresh(self):
        win = wx.GetTopLevelParent(self) 
        win.sizer.SetSizeHints(win) 
        win.Fit() 
        win.Layout()         

class testdialog(wx.Dialog):
    def __init__(self, parent):
        title = 'nt'
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        super(testdialog, self).__init__(parent, -1, title, 
                                         size=(300,300),style=style)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.ptw = PieTagWidget(self, 1, mode="grid")
        sizer.Add(self.ptw, 1, wx.EXPAND|wx.ALL, 5)
        self.ptw.AddTag("A tag")
        self.ptw.AddTag("Another tag")
        self.SetSizerAndFit(sizer)


if __name__ == '__main__':
    app = wx.PySimpleApp(0)
    ted = PieTagDialog(None)
    ted.Show()
    app.MainLoop()



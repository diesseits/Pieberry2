# A widget for displaying and editing tags attached to a PieObject

import wx
from wx.lib.platebtn import *
from pieberry.ui.events import PieTagAddedEvent, EVT_PIE_TAG_ADDED
from pieberry.ui.events import PieTagClickedEvent, EVT_PIE_TAG_CLICKED
from pieberry.pieobject.tags import fn_add_tag

tagnames = ['foo', 'bar', 'hoopla']

class PieTagButton(PlateButton):
    def __init__(self, parent, id, tag, *args, **kwargs):
        PlateButton.__init__(self, parent, id, tag, *args, **kwargs)
        self.tag = tag
    def GetTag(self):
        return self.tag

class PieTagWidget(wx.Panel):
    '''A tag display/editing widget'''
    def __init__(self, parent, id, mode="horizontal", columns=4):
        wx.Panel.__init__(self, parent, id, size=(28,28))
        self.menubtn = None
        self.tags = []
        self.tagbuttons = []
        self.mode = mode
        self.taglist = tagnames
        self.taglist.sort()
        self.__do_layout(mode, columns)

    def __build_menu(self):
        self.tagmenu = wx.Menu()
        for tn in self.taglist:
            if not tn in self.tags:
                self.tagmenu.Append(-1, tn)
        self.tagmenu.Append(-1, _("[ New Tag ]"))
        self.tagmenu.Bind(wx.EVT_MENU, self.onMenuChoice)

    def __add_to_sizer(self, widget, *params):
        '''Add things to the sizer, with various modes'''
        def addrow():
            '''Add a row for multiline mode'''
            newrow = wx.BoxSizer(wx.HORIZONTAL)
            self._sizer.Add(newrow, 0)
            self._rows.append(newrow)
            self._rowcount += 1
            return newrow
        if self.mode == "multiline":
            if self._rowcount == -1:
                row = addrow()
            elif self._colcount == self._columns:
                self._colcount = 0
                row = addrow()
            else: 
                row = self._rows[self._rowcount]
            row.Add(widget, *params)
            self._colcount += 1
            self._sizer.Layout()
            self.Layout()
        else:
            self._sizer.Add(widget, *params)

    def __remove_from_sizer(self, widget):
        for row in self._rows:
            try: 
                row.Remove(widget)
            except:
                pass

    def __append_menubutton(self):
        if not self.menubtn:
            self.menubtn = PlateButton(
                self, -1, 
                # label="Add",
                bmp=wx.ArtProvider.GetBitmap(wx.ART_ADD_BOOKMARK, wx.ART_MENU),
                style=PB_STYLE_SQUARE
                )
            self.menubtn.Bind(wx.EVT_BUTTON, self.onMenuButtonPress)
        tt = wx.ToolTip("Tags")
        self.menubtn.SetToolTip(tt)
        self.__refresh_menu()
        # if not self.mode == "lhorizontal":
        self.__add_to_sizer(self.menubtn, 0)
        print "MENUBUTTON INVOKED"
        self.menubtn.Show()

    def __refresh_menu(self):
        self.taglist.sort()
        self.__build_menu()
        self.menubtn.SetMenu(self.tagmenu)

    def __do_layout(self, mode, columns):
        if mode == "rhorizontal": # button at right
            self._sizer = wx.BoxSizer(wx.HORIZONTAL)
        elif mode == "lhorizontal": # button at left
            self._sizer = wx.BoxSizer(wx.HORIZONTAL)
        elif mode == "lvertical": 
            self._sizer = wx.BoxSizer(wx.VERTICAL)
        elif mode == "multiline":
            self._sizer = wx.BoxSizer(wx.VERTICAL)
        else:
            self._sizer = wx.FlexGridSizer(1, columns, 0, 0)
            [ self._sizer.AddGrowableCol(idx) for idx in range(columns) ]
        self._columns = columns
        self._colcount = 0
        self._rowcount = -1
        self._rows = []
        # self._sizer.Add((5,5))
        self.__append_menubutton()
        self.SetSizer(self._sizer)
        self._sizer.Layout()
        self.Layout()

    def setTagList(self, taglist):
        '''Sets the available tags (list of strings, not PieTags)'''
        self.taglist = taglist
        self.taglist.sort()
        self.__refresh_menu()

    def onMenuChoice(self, evt):
        '''The user chose one of the tag menu options'''
        tagtxtchosen = self.tagmenu.FindItemById(evt.GetId()).GetLabel()
        if tagtxtchosen == _("[ New Tag ]"):
            self.onCreateNewTag()
        else:
            self.UserAddTag(tagtxtchosen)

    def onTagPress(self, evt):
        '''The user clicked a tag platebutton '''
        newevt = PieTagClickedEvent(
            tag = evt.GetEventObject().GetTag()
            )
        wx.PostEvent(self, newevt)
        # print evt.GetEventObject().GetTag()

    def onMenuButtonPress(self, evt):
        '''Show the menu when menu button pressed'''
        self.menubtn.ShowMenu()

    def onCreateNewTag(self):
        '''The user opts to create a non-preexisting tag'''
        tdia = wx.TextEntryDialog(self, "Name of new tag:", "Create new tag")
        ans = tdia.ShowModal()
        if ans == wx.ID_CANCEL: return
        if len(tdia.GetValue()) == 0: return
        if tdia.GetValue in self.taglist: return
        print "Creating new tag: %s" % tdia.GetValue()
        newtag = tdia.GetValue()
        fn_add_tag(tdia.GetValue())
        self.taglist.append(newtag)
        self.UserAddTag(newtag)

    def Clear(self):
        irange = range(len(self.tags))
        irange.reverse()
        if self.mode == "multiline":
            print self._rows
            [ self._sizer.Remove(row) for row in self._rows ] 
        self._colcount = 0
        self._rowcount = -1
        self._rows = []
        for i in irange:
            self.tags.pop(i)
            if self.mode != "multiline":
                self._sizer.Remove(self.tagbuttons[i])
            self.tagbuttons[i].Destroy()
            self.tagbuttons.pop(i)
        if self.mode == 'multiline':
            self.__append_menubutton()
        self.__refresh_menu()
        self._sizer.Layout()
        self.Layout()

    def AddTags(self, tags):
        '''Add a list of tags (strings)'''
        for tag in tags: self.AddTag(tag)

    def UserAddTag(self, tag):
        '''The user has added a tag'''
        self.AddTag(tag)
        newevt = PieTagAddedEvent(tag = tag)
        wx.PostEvent(self, newevt)

    def AddTag(self, tag):
        '''A tag is added by any means'''
        self.tags.append(tag)
        btn = PieTagButton(
            self, -1, 
            tag,
            # bmp=wx.ArtProvider.GetBitmap(wx.ART_FIND, wx.ART_MENU),
            style=PB_STYLE_SQUARE
            )
        self.tagbuttons.append(btn)
        self.__add_to_sizer(btn, 0)
        btn.Bind(wx.EVT_BUTTON, self.onTagPress)
        if not self.mode in ('lhorizontal', 'multiline'):
            self.menubtn.Hide()
            self._sizer.Remove(self.menubtn)
            self.__append_menubutton()
        else:
            self.__refresh_menu()
        self._sizer.Layout()
        self.Layout()
        wx.Panel.SetSize(self, self._sizer.GetMinSize())

    def GetTags(self):
        '''Return list of tags applicable'''
        return self.tags

class PieSpecialSizer(wx.BoxSizer):
    def __init__(self, columns):
        wx.BoxSizer.__init__(self, wx.VERTICAL)
        self._maxcolumn = columns
        self.hsizers = []
        self.__add_hsizer()
        # self.Layout()

    def __add_hsizer(self):
        self.runningcount = 0
        hs0 = wx.BoxSizer(wx.HORIZONTAL)
        self.hsizers.append(hs0)
        self.Add(hs0, 1, wx.EXPAND)

    def Add(self, widget, size=0, flags=0, padding=0):
        if self.runningcount == self._maxcolumn:
            self.__add_hsizer()
        sa = self.hsizers[-1]
        self.hsizers[-1].Add(widget, size, flags, padding)
        self.runningcount += 1

class PieTagDialog(wx.Dialog):
    def __init__(self, parent, taglist=[], existingtags=[]):
        title = _('Add tags')
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        super(PieTagDialog, self).__init__(parent, -1, title, 
                                         size=(300,300),style=style)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.ptw = PieTagWidget(self, 1, mode="standard")
        buttons = self.CreateButtonSizer(wx.OK|wx.CANCEL)
        self.sizer.Add(wx.StaticText(self, -1, _("Add Tags to Document:")), 
                       0, wx.ALL|wx.EXPAND, 5)
        self.sizer.Add(wx.StaticLine(self, -1), 0, wx.ALL|wx.EXPAND, 5)
        self.sizer.Add(self.ptw, 1, wx.EXPAND)
        self.sizer.Add(wx.StaticLine(self, -1), 0, wx.ALL|wx.EXPAND, 5)
        self.sizer.Add(buttons, 0, wx.ALL|wx.EXPAND, 5)

        self.SetSizerAndFit(self.sizer)
        self.ptw.Bind(EVT_PIE_TAG_ADDED, self.onTagAdded)

        self.ptw.setTagList(taglist)
        self.ptw.AddTags(existingtags)
        
    def onTagAdded(self, evt):
        wx.CallAfter(self.doRefresh())

    def doRefresh(self):
        win = wx.GetTopLevelParent(self) 
        win.sizer.SetSizeHints(win) 
        win.Fit() 
        win.Layout()         

    def GetTags(self):
        return self.ptw.GetTags()

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



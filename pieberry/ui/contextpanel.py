import wx

class BaseContextPanel(wx.Panel):
    '''Class for generic forms of context'''
    changed=0

    def __init__(self, parent, id=-1, style=wx.EXPAND|wx.TAB_TRAVERSAL):
        wx.Panel.__init__(
            self, parent=parent, id=id, style=style)
        self._do_layout()

    def _do_layout(self):
        print '_do_layout'

    def SetMode(self, mode='default'):
        '''Set the context view mode'''
        print 'SetMode'

    def SetObject(self, obj):
        '''Set the object to show context for'''
        print 'SetObject'

    
class SimpleContextPanel(BaseContextPanel):
    #widgetlist = []

    def _create_field(self, label, display):
        #widgetlist.append((label, display))
        self.sizer0.Add(label, 0, wx.ALL, 5)
        self.sizer0.Add(display, 0, wx.ALL, 5)

    def _do_layout(self):
        self.sizer0 = wx.BoxSizer(wx.VERTICAL)
        idlabel = wx.StaticText(self, -1, 'ID:')
        self.iddisplay = wx.StaticText(self, -1, '')
        self._create_field(idlabel, self.iddisplay)
        titlelabel = wx.StaticText(self, -1, 'Title:', style=wx.TE_MULTILINE)
        self.titledisplay = wx.StaticText(self, -1, '')
        self._create_field(titlelabel, self.titledisplay)
        authorlabel = wx.StaticText(self, -1, 'Author:')
        self.authordisplay = wx.StaticText(self, -1, '')
        self._create_field(authorlabel, self.authordisplay)
        fileloclabel = wx.StaticText(self, -1, 'File location:')
        self.filelocdisplay = wx.StaticText(self, -1, '')
        self._create_field(fileloclabel, self.filelocdisplay)
        collectlabel = wx.StaticText(self, -1, 'Collection:')
        self.collectiondisplay = wx.StaticText(self, -1, '')
        self._create_field(collectlabel, self.collectiondisplay)
        self.SetSizer(self.sizer0)
        self.Layout()
                                     
    def SetObject(self, obj):
        self.iddisplay.SetLabel(unicode(obj.GetId()))
        self.titledisplay.SetLabel(obj.Title())
        self.authordisplay.SetLabel(obj.Author())
        self.filelocdisplay.SetLabel(unicode(obj.FileData_FullPath))
        self.collectiondisplay.SetLabel(unicode(obj.collection))

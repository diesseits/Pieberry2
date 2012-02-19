import wx, wx.html, os.path
import wx.lib.agw.foldpanelbar as fpb
from wx.lib.buttons import ThemedGenBitmapToggleButton 
from wx.lib import wordwrap


from pieconfig.paths import IMGDIR
from string import join
from ui.events import PieContextPanelUpdateEvent
from urlparse import urlsplit

html_fundamental = _('''
<body bgcolor="%(color)s">
<p>
<font size=-1>
<b>Author:</b> %(author)s<br>
<b>Date:</b> %(date)s<br>
<b>Tags:</b> %(tags)s
</p>
</font>
</body>
''')

html_colors = {'kde': "#F0EBE2"}

class BetterContextPanel(wx.Panel):
    '''Class for generic forms of context'''
    changed=0

    def __init__(self, parent, id=-1, style=wx.EXPAND|wx.TAB_TRAVERSAL):
        wx.Panel.__init__(self, parent=parent, id=id, style=style)
        self.bar = fpb.FoldPanelBar(self, -1, style=fpb.FPB_HORIZONTAL) 
        self.fund_fp = self.bar.AddFoldPanel(_('Information'))
        self.bib_fp = self.bar.AddFoldPanel(_('Bibliographic Info'))
        self.web_fp = self.bar.AddFoldPanel(_('Web Info'))
        self.file_fp = self.bar.AddFoldPanel(_('File Info'))

        self.fund_win = FundInfoPanel(self.fund_fp, -1, bigparent=self)
        self.web_win = WebInfoPanel(self.web_fp, -1)
        self.bib_win = BibInfoPanel(self.bib_fp, -1)
        self.file_win = FileInfoPanel(self.file_fp, -1)
        self.bar.AddFoldPanelWindow(self.fund_fp, self.fund_win)
        self.bar.AddFoldPanelWindow(self.web_fp, self.web_win)
        self.bar.AddFoldPanelWindow(self.bib_fp, self.bib_win)
        self.bar.AddFoldPanelWindow(self.file_fp, self.file_win)
        self._do_layout()
        self._do_bindings()

    def onCaptionBar(self, event):
        event.Skip()
        wx.CallAfter(self.ResizeFPB)

    def ResizeFPB(self):
        sizeNeeded = self.bar.GetPanelsLength(0, 0)[2]
        self.bar.SetMinSize((sizeNeeded, self.bar.GetSize()[1]))
        self.Fit()

    def _do_bindings(self):
        # self.bar.Bind(fpb.EVT_CAPTIONBAR, self.onCaptionBar)
        pass

    def _do_layout(self):
        self.sizer_1 = wx.BoxSizer(wx.VERTICAL)
        self.sizer_1.Add(self.bar, 1, wx.EXPAND)
        self.SetSizer(self.sizer_1)
        self.Layout()
  	self.bar.Expand(self.fund_fp) 
  	self.bar.Collapse(self.web_fp) 
        self.bar.Collapse(self.bib_fp)
        self.bar.Collapse(self.file_fp)

        # self.ResizeFPB()

    def SetMode(self, mode='default'):
        '''Set the context view mode'''
        print 'SetMode'

    def SetObject(self, obj):
        '''Set the object to show context for'''
        self.obj = obj
        self.fund_win.SetObject(obj)
        self.web_win.SetObject(obj)
        self.bib_win.SetObject(obj)
        self.file_win.SetObject(obj)

    def EmitUpdate(self, evt=0):
        newevt = PieContextPanelUpdateEvent(
            obj=self.obj,
            favourite=self.fund_win.GetFavourite())
        wx.PostEvent(self, newevt)

bibhtml = _('''
<body bgcolor="%(color)s">
<font size=-1>
<p>
<b>BibTeX Type:</b> %(bibtex_type)s<br>
<b>Publication Date:</b> %(date)s<br>
</p>
</font>
</body>
''')


class BibInfoPanel(wx.Panel):
    def __init__(self, parent, id, *args, **kwargs):
        kwargs['size'] = (80,60)
        wx.Panel.__init__(self, parent, id, *args, **kwargs)
        self.Html = wx.html.HtmlWindow(self, -1)
        self._do_layout()

    def _do_layout(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.Html, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(self.sizer)
        self.Layout()

    def SetObject(self, obj):
        self.sizer.Remove(self.Html)
        self.Html.Destroy()
        self.Html = wx.html.HtmlWindow(self, -1)
        self.sizer.Add(self.Html, 1, wx.EXPAND|wx.ALL, 5)
        self.Layout()
        info = {'color': html_colors['kde']}
        info['bibtex_type'] = unicode(obj.BibData_Type)
        if obj.BibData_DatePublished:
            info['date'] = obj.BibData_DatePublished.strftime('%d %B %Y')
        else: info['date'] = 'None'
        self.Html.AppendToPage(bibhtml % info)

filehtml = _('''
<body bgcolor="%(color)s">
<font size=-1>
<p>
<b>Type:</b> %(type)s<br>
<b>Size:</b> %(size)s<br>
</p>
</font>
</body>
''')

class FileInfoPanel(wx.Panel):
    def __init__(self, parent, id, *args, **kwargs):
        kwargs['size'] = (80,160)
        wx.Panel.__init__(self, parent, id, *args, **kwargs)
        self.locte = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_CHARWRAP)
        self.Html = wx.html.HtmlWindow(self, -1)
        self._do_layout()

    def _do_layout(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(wx.StaticText(self, -1, _('File location:')), 0, wx.ALL, 5)
        self.sizer.Add(self.locte, 1, wx.ALL|wx.EXPAND, 5)
        self.sizer.Add(self.Html, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(self.sizer)
        self.Layout()

    def SetObject(self, obj):
        self.locte.SetValue(obj.FileData_FullPath)
        self.sizer.Remove(self.Html)
        self.Html.Destroy()
        self.Html = wx.html.HtmlWindow(self, -1, size=(80,80))
        self.sizer.Add(self.Html, 1, wx.EXPAND|wx.ALL, 5)
        self.Layout()
        info = {'color': html_colors['kde']}
        info['path'] = unicode(obj.FileData_FullPath)
        info['type'] = unicode(obj.FileData_FileType)
        info['size'] = unicode(obj.FileData_Size)
        self.Html.AppendToPage(filehtml % info)

class WebInfoPanel(wx.Panel):
    def __init__(self, parent, id, *args, **kwargs):
        kwargs['size'] = (80,30)
        wx.Panel.__init__(self, parent, id, *args, **kwargs)

        self.urlDisplay = wx.HyperlinkCtrl(self, -1, '', '')
        self._do_layout()

    def _do_layout(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.urlDisplay, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(self.sizer)
        self.Layout()
        
    def SetObject(self, obj):
        if not obj.Url():
            self.urlDisplay.SetURL('')
            self.urlDisplay.SetLabel(_('No Url'))
            return
        self.urlDisplay.SetURL(obj.Url())
        if obj.website:
            self.urlDisplay.SetLabel(_('From %s') % obj.website.Domain)
        else:
            self.urlDisplay.SetLabel(_('From %s') % urlsplit(obj.Url())[1])
        self.urlDisplay.Refresh()

class FundInfoPanel(wx.Panel):
    def __init__(self, parent, id, bigparent, *args, **kwargs):
        kwargs['size'] = (80,140)
        wx.Panel.__init__(self, parent, id, *args, **kwargs)
        self.bigparent = bigparent
        self.favpanel = FBBPanel(self, -1, bigparent=bigparent)
        self.sizer0 = wx.BoxSizer(wx.VERTICAL)
        self.sizer0.Add(self.favpanel, 0)
        self.fundHtml = wx.html.HtmlWindow(self, -1)
        self.sizer0.Add(self.fundHtml, 1, wx.EXPAND|wx.ALL, 0)
        # self.favpanel.BMB.Bind(wx.EVT_BUTTON, self.GetParent().GetParent().EmitUpdate)
        self.SetSizer(self.sizer0)
        self.Layout()

    def SetObject(self, obj):
        self.favpanel.SetValue(obj.StatData_Favourite)
        self.favpanel.SetTitleWidth(int(self.GetSize()[0] * 0.66))
        self.favpanel.SetTitle(obj.Title())
        self.sizer0.Remove(self.fundHtml)
        self.fundHtml.Destroy()
        self.fundHtml = wx.html.HtmlWindow(self, -1)
        self.sizer0.Add(self.fundHtml, 1, wx.EXPAND|wx.ALL, 0)
        self.fundHtml.AppendToPage(html_fundamental % {
                'author': obj.Author(),
                'title': obj.Title(),
                'date': obj.ReferDate().strftime('%d %B %Y'),
                'color': html_colors['kde'],
                'tags': join([unicode(t) for t in obj.tags], ' | ')
                })
        # self.SetClientSize(self.sizer0.GetMinSizeTuple())
        self.Layout()

    def GetFavourite(self):
        return self.favpanel.BMB.GetValue()
        
class FavBitmapButton(ThemedGenBitmapToggleButton):
    image_up = os.path.join(IMGDIR, 'ic_silverstar22.png')
    image_down = os.path.join(IMGDIR, 'ic_goldstar22.png')
    
    def __init__(self, parent, id):

        imageup = wx.Image(self.image_up, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        imagedown = wx.Image(self.image_down, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        wx.lib.buttons.ThemedGenBitmapToggleButton.__init__(self, parent, id, imageup)
        self.SetBitmapSelected(imagedown)


class FBBPanel(wx.Panel):
    '''Panel to mount the favourite button on'''
    def __init__(self, parent, id, bigparent):
        wx.Panel.__init__(self, parent, id)
        self.bigparent = bigparent
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.BMB = FavBitmapButton(self, -1)
        self.sizer.Add(self.BMB, 0, wx.ALL, 5)
        self.title = wx.StaticText(self, -1, '')
        # self.title = wx.TextCtrl(self, -1, style=wx.TE_READONLY)
        # self.title = wx.WindowDC(self)
        font = wx.Font(10, wx.FONTFAMILY_ROMAN, -1, wx.FONTWEIGHT_BOLD)
        self.title.SetFont(font)
        self.sizer.Add(self.title, 1, wx.EXPAND)
        # self.sizer.Add((22,22), 1)
        self.SetSizer(self.sizer)
        self.Layout()
        self.w = 80
        self.BMB.Bind(wx.EVT_BUTTON, self.bigparent.EmitUpdate)

    def GetValue(self):
        return self.BMB.GetValue()

    def SetValue(self, val):
        return self.BMB.SetValue(val)
    
    def SetTitleWidth(self, w):
        self.w = w

    def SetTitle(self, ttl):
        # self.title.SetLabel(ttl)
        dc = wx.WindowDC(self.title)
        self.title.SetLabel(wordwrap.wordwrap(ttl, self.w, dc))

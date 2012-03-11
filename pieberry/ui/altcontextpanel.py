import wx, wx.html, os.path, sys
import wx.lib.agw.foldpanelbar as fpb
from wx.lib.buttons import ThemedGenBitmapToggleButton 
from wx.lib import wordwrap

from pieberry.pieconfig.paths import IMGDIR
from string import join
from pieberry.ui.events import PieContextPanelUpdateEvent
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

    def OnFieldEdit(self, evt):
        self.EmitUpdate(otherargs=((evt.objattr, evt.objattrval),))

    def EmitUpdate(self, evt=0, ttltext=None, otherargs=()):
        newevt = PieContextPanelUpdateEvent(
            obj=self.obj,
            favourite=self.fund_win.GetFavourite(),
            ttltext=ttltext)
        [ setattr(newevt, attrname, attrval) for attrname, attrval in otherargs ] 
        wx.PostEvent(self, newevt)

bibhtml = _('''
<body bgcolor="%(color)s">
<font size=-1>
<p>
<b>BibTeX Type:</b> %(bibtex_type)s<br>
<b>BibTeX Key:</b> %(bibtex_key)s<br>
<b>Publication Date:</b> %(date)s<br>
</p>
</font>
</body>
''')


class BibInfoPanel(wx.Panel):
    def __init__(self, parent, id, *args, **kwargs):
        kwargs['size'] = (80,80)
        wx.Panel.__init__(self, parent, id, *args, **kwargs)
        self.Html = wx.html.HtmlWindow(self, -1)
        self._do_layout()

    def _do_layout(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.Html, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Layout()

    def SetObject(self, obj):
        self.sizer.Remove(self.Html)
        self.Html.Destroy()
        self.Html = wx.html.HtmlWindow(self, -1)
        self.sizer.Add(self.Html, 1, wx.EXPAND|wx.ALL)
        self.Layout()
        info = {'color': html_colors['kde']}
        info['bibtex_type'] = unicode(obj.BibData_Type)
        info['bibtex_key'] = unicode(obj.BibData_Key)
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
        self.sizer.Add(self.Html, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Layout()

    def SetObject(self, obj):
        self.locte.SetValue(unicode(obj.FileData_FullPath))
        self.sizer.Remove(self.Html)
        self.Html.Destroy()
        self.Html = wx.html.HtmlWindow(self, -1, size=(80,80))
        self.sizer.Add(self.Html, 1, wx.EXPAND)
        self.Layout()
        if obj.FileData_Size: fsize = unicode(obj.FileData_Size / 1000) + 'kb'
        else: fsize = _('Nil')
        info = {'color': html_colors['kde']}
        info['path'] = unicode(obj.FileData_FullPath)
        info['type'] = unicode(obj.FileData_FileType)
        info['size'] = fsize
        self.Html.AppendToPage(filehtml % info)

class WebInfoPanel(wx.Panel):
    def __init__(self, parent, id, *args, **kwargs):
        kwargs['size'] = (80,30)
        wx.Panel.__init__(self, parent, id, *args, **kwargs)

        self.urlDisplay = wx.HyperlinkCtrl(self, -1, 'empty', 'empty')
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


boldfont = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
normalfont = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

from pieberry.ui.events import PieContextPanelFieldEvent, EVT_PIE_CONTEXT_PANEL_FIELD

# class StaticWrapText(wx.PyControl):
#     def __init__(self, parent, id=wx.ID_ANY, label='', pos=wx.DefaultPosition,
#                  size=wx.DefaultSize, style=wx.NO_BORDER,
#                  validator=wx.DefaultValidator, name='StaticWrapText'):
#         wx.PyControl.__init__(self, parent, id, pos, size, style, validator, name)
#         self.statictext = wx.StaticText(self, wx.ID_ANY, label, style=style)
#         self.wraplabel = label
#       #self.wrap()
#     def wrap(self):
#         self.Freeze()
#         self.statictext.SetLabel(self.wraplabel)
#         self.statictext.Wrap(self.GetSize().width)
#         self.Thaw()
#     def DoGetBestSize(self):
#         self.wrap()
#       #print self.statictext.GetSize()
#         self.SetSize(self.statictext.GetSize())
#         return self.GetSize()

class EditableText(wx.Panel):
    '''A thing that will flip from a static text to a textctrl on a
    mouse click to allow editing of a displayed field'''
    def __init__(self, parent, id, label, objattr, *args, **kwargs):
        wx.Panel.__init__(self, parent, id, *args, **kwargs)
        self.stext = wx.StaticText(self, -1, label)
        self.dtext = wx.TextCtrl(self, -1, label, size=(110,-1))#, style=wx.TE_MULTILINE|wx.EXPAND)
    
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.stext, 1, wx.EXPAND)
        self.sizer.Add(self.dtext, 1, wx.EXPAND)
        self.dtext.Hide()

        self.stext.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.dtext.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.dtext.Bind(wx.EVT_KILL_FOCUS, self.OnLoseFocus)

        self._objattr = objattr

    def OnLeftUp(self, evt):
        self.stext.Hide()
        self.dtext.Show()
        self.dtext.SetFocus()
        self.Layout()
        self.GetParent().Layout()

    def OnKeyUp(self, evt):
        if evt.GetKeyCode() in (wx.WXK_ESCAPE, wx.WXK_RETURN): 
            self._exit_edit()
        else: 
            evt.Skip() 

    def OnLoseFocus(self, evt):
        self._exit_edit()

    def SetFont(self, font):
        self.stext.SetFont(font)

    def _exit_edit(self):
        self.dtext.Hide()
        self.stext.Show()
        self.SetValue(self.dtext.GetValue())
        self.Layout()
        self.GetParent().Layout()
        newevt = PieContextPanelFieldEvent(
            objattr=self._objattr,
            objattrval=self.GetValue())
        wx.PostEvent(self, newevt)

    def SetValue(self, txt):
        dc = wx.WindowDC(self.stext)
        self.stext.SetLabel(wordwrap.wordwrap(txt, self.w, dc))
        # self.stext.SetLabel(txt)
        self.dtext.SetValue(txt)

    def SetWrapWidth(self, w):
        self.w = w

    def GetValue(self):
        return self.dtext.GetValue()

class FundInfoPanel(wx.Panel):
    def __init__(self, parent, id, bigparent, *args, **kwargs):
        kwargs['size'] = (80,140)
        wx.Panel.__init__(self, parent, id, *args, **kwargs)
        self.bigparent = bigparent
        self.favpanel = FBBPanel(self, -1, bigparent=bigparent)
        self.sizer0 = wx.BoxSizer(wx.VERTICAL)
        self.sizer0.Add(self.favpanel, 0)
        
        self.fgsizer = wx.FlexGridSizer(0, 2, 5, 5)
        self.fgsizer.AddGrowableCol(1)

        self.auth_lb = wx.StaticText(self, -1, _('Author:'))
        self.auth_lb.SetFont(boldfont)
        self.auth_ct = EditableText(self, -1, '', objattr='author')
        self.auth_ct.SetFont(normalfont)
        self.date_lb = wx.StaticText(self, -1, _('Date:'))
        self.date_lb.SetFont(boldfont)
        self.date_ct = wx.StaticText(self, -1, '')
        self.date_ct.SetFont(normalfont)
        
        self.auth_ct.Bind(EVT_PIE_CONTEXT_PANEL_FIELD, self.bigparent.OnFieldEdit)

        self.fgsizer.Add(self.auth_lb)
        self.fgsizer.Add(self.auth_ct, 1, wx.EXPAND)
        self.fgsizer.Add(self.date_lb)
        self.fgsizer.Add(self.date_ct)

        self.sizer0.Add((5,5))
        self.sizer0.Add(self.fgsizer, 1, wx.EXPAND)
        self.SetSizer(self.sizer0)
        self.Layout()

    def SetObject(self, obj):
        self.auth_ct.SetWrapWidth(self.fgsizer.GetColWidths()[1])
        self.favpanel.SetValue(obj.StatData_Favourite)
        if sys.platform == 'win32':
            self.favpanel.SetTitleWidth(int(self.GetSize()[0] * 1))
        else:
            self.favpanel.SetTitleWidth(int(self.GetSize()[0] * 0.66))
        self.favpanel.SetTitle(obj.Title())
        self.auth_ct.SetValue(obj.Author())
        # self.auth_ct.SetLabel(obj.Author())
        self.date_ct.SetLabel(obj.ReferDate().strftime('%d %B %Y'))
        self.fgsizer.Layout()
        self.sizer0.Layout()
        self.Layout()

    def GetFavourite(self):
        return self.favpanel.BMB.GetValue()


class OldFundInfoPanel(wx.Panel):
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
        if sys.platform == 'win32':
            self.favpanel.SetTitleWidth(int(self.GetSize()[0] * 1))
        else:
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
        self.topsizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.BMB = FavBitmapButton(self, -1)
        self.sizer.Add(self.BMB, 0, wx.ALL, 5)
        self.title = wx.StaticText(self, -1, '')
        self.titleedit = wx.TextCtrl(self, -1, '', style=wx.TE_MULTILINE)
        # self.title = wx.TextCtrl(self, -1, style=wx.TE_READONLY)
        # self.title = wx.WindowDC(self)
        if not sys.platform == 'win32':
            font = wx.Font(10, wx.FONTFAMILY_ROMAN, -1, wx.FONTWEIGHT_BOLD)
            self.title.SetFont(font)
        self.sizer.Add(self.title, 1, wx.EXPAND)
        self.sizer.Add(self.titleedit, 1, wx.EXPAND)
        self.titleedit.Hide()
        # self.sizer.Add((22,22), 1)
        self.SetSizer(self.sizer)
        self.Layout()
        self.w = 80
        self.BMB.Bind(wx.EVT_BUTTON, self.bigparent.EmitUpdate)
        self.title.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.titleedit.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.titleedit.Bind(wx.EVT_KILL_FOCUS, self.OnTtlKillFocus)

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
        self.titleedit.SetValue(ttl)

    def OnLeftUp(self, evt):
        self.title.Hide()
        self.titleedit.Show()
        self.titleedit.SetFocus()
        self.Layout()

    def OnKeyUp(self, evt): 
        if evt.GetKeyCode() in (wx.WXK_ESCAPE, wx.WXK_RETURN): 
            self._exit_titleedit()
        else: 
            evt.Skip() 

    def OnTtlKillFocus(self, evt):
        self._exit_titleedit()

    def _exit_titleedit(self):
        self.titleedit.Hide()
        self.title.Show() 
        self.SetTitle(self.titleedit.GetValue())
        self.Layout() 
        self.GetParent().Layout()
        self.bigparent.EmitUpdate(ttltext = self.titleedit.GetValue())
        

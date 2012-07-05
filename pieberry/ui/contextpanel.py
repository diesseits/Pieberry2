import wx, wx.html, os.path, sys
import wx.lib.agw.foldpanelbar as fpb
from wx.lib.buttons import ThemedGenBitmapToggleButton 
from wx.lib import wordwrap

from pieberry.pieconfig.paths import IMGDIR
from string import join
from pieberry.ui.events import PieContextPanelUpdateEvent
from urlparse import urlsplit
from pieberry.ui.events import *
from pieberry.ui.tagwidget import *
from pieberry.pieutility.date import fmtdate
from pieberry.pieobject.folder import SECURITY_CLASSES
from pieberry.pieobject.tags import get_all_tags, get_tag

boldfont = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
normalfont = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
itfont = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL)

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
        self.bib_win = BibInfoPanel(self.bib_fp, -1, bigparent=self)
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

        self.ResizeFPB()

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
        self.bar.RedisplayFoldPanelItems()
        self.bar.RefreshPanelsFrom(self.fund_fp)

    def OnFieldEdit(self, evt):
        self.EmitUpdate(otherargs=((evt.objattr, evt.objattrval),))

    def OnTagAdded(self, evt):
        if self.obj.has_aspect('saved'):
            self.obj.add_tag(evt.tag)
        else:
            self.obj.add_tags_queued(evt.tag)

    def OnTagClicked(self, evt):
        relparent = self.GetParent()
        relparent.OpenTagsPane()
        pan = relparent.GetCurrentPane()
        pan.SelectTag(evt.tag)

    def EmitUpdate(self, evt=0, ttltext=None, otherargs=()):
        newevt = PieContextPanelUpdateEvent(
            obj=self.obj,
            favourite=self.fund_win.GetFavourite(),
            ttltext=ttltext)
        [ setattr(newevt, attrname, attrval) for attrname, attrval in otherargs ] 
        wx.PostEvent(self, newevt)

class BibInfoPanel(wx.Panel):
    def __init__(self, parent, id, bigparent, *args, **kwargs):
        kwargs['size'] = (80,50)
        wx.Panel.__init__(self, parent, id, *args, **kwargs)
        self.bigparent = bigparent
        self._do_layout()

    def _do_layout(self):
        self.fgsizer = wx.FlexGridSizer(0, 2, 5, 5)
        self.fgsizer.AddGrowableCol(1)
        self.type_lb = wx.StaticText(self, -1, _('Type:'))
        self.type_ct = wx.StaticText(self, -1, u'')
        self.key_lb = wx.StaticText(self, -1, _('Key:'))
        self.key_ct = wx.StaticText(self, -1, u'')
        self.date_lb = wx.StaticText(self, -1, _('Published:'))
        self.date_ct = wx.StaticText(self, -1, u'')
        self.abst_lb = wx.StaticText(self, -1, _('Abstract:'))
        self.abst_ct = EditableText(self, -1, '', objattr='abstract')

        self.date_lb.SetFont(boldfont)
        self.type_lb.SetFont(boldfont)
        self.key_lb.SetFont(boldfont)
        self.abst_lb.SetFont(boldfont)

        self.fgsizer.Add(self.type_lb, 0, wx.LEFT|wx.RIGHT, 3)
        self.fgsizer.Add(self.type_ct, 0, wx.LEFT|wx.RIGHT, 3)
        self.fgsizer.Add(self.key_lb, 0, wx.LEFT|wx.RIGHT, 3)
        self.fgsizer.Add(self.key_ct, 0, wx.LEFT|wx.RIGHT, 3)
        self.fgsizer.Add(self.date_lb, 0, wx.LEFT|wx.RIGHT, 3)
        self.fgsizer.Add(self.date_ct, 0, wx.LEFT|wx.RIGHT, 3)
        self.fgsizer.Add(self.abst_lb, 0, wx.LEFT|wx.RIGHT, 3)
        self.fgsizer.Add(self.abst_ct, 0, wx.LEFT|wx.RIGHT, 3)
        self.fgsizer.Add((3,3))

        self.abst_ct.Bind(EVT_PIE_CONTEXT_PANEL_FIELD, self.bigparent.OnFieldEdit)
        
        self.SetSizer(self.fgsizer)
        wx.Panel.SetSize(self, self.fgsizer.GetMinSize())
        self.Layout()

    def SetObject(self, obj):

        self.abst_ct.SetWrapWidth(self.fgsizer.GetColWidths()[1])
        self.abst_ct.SetValue(obj.BibData_Abstract if obj.BibData_Abstract else '')
        self.type_ct.SetLabel(unicode(obj.BibData_Type))
        self.key_ct.SetLabel(unicode(obj.BibData_Key))
        if obj.BibData_DatePublished: 
            date = obj.BibData_DatePublished.strftime('%d %B %Y') if obj.BibData_DatePublished.year >= 1900 else fmtdate(obj.BibData_DatePublished)
        else:
            date = u'N/A'
        self.date_ct.SetLabel(date)
        wx.Panel.SetSize(self, self.fgsizer.GetMinSize())


class FileInfoPanel(wx.Panel):
    def __init__(self, parent, id, *args, **kwargs):
        kwargs['size'] = (80,120)
        wx.Panel.__init__(self, parent, id, *args, **kwargs)
        self._do_layout()

    def _do_layout(self):
        self.locte = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_CHARWRAP, size=(20,50))
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(wx.StaticText(self, -1, _('File location:')), 0, wx.ALL, 5)
        self.sizer.Add(self.locte, 1, wx.ALL|wx.EXPAND, 5)
        self.fgsizer = wx.FlexGridSizer(0, 2, 5, 5)
        self.fgsizer.AddGrowableCol(1)

        self.type_lb = wx.StaticText(self, -1, _('Type:'))
        self.type_ct = wx.StaticText(self, -1, u'')
        self.size_lb = wx.StaticText(self, -1, _('Size:'))
        self.size_ct = wx.StaticText(self, -1, u'')
        self.record_lb = wx.StaticText(self, -1, _('Record:'))
        self.record_ct = wx.StaticText(self, -1, u'')
        self.sec_lb = wx.StaticText(self, -1, _('Security:'))
        self.sec_ct = wx.StaticText(self, -1, u'')

        self.fgsizer.Add(self.type_lb, 0, wx.LEFT|wx.RIGHT, 3)
        self.fgsizer.Add(self.type_ct, 0, wx.LEFT|wx.RIGHT, 3)
        self.fgsizer.Add(self.size_lb, 0, wx.LEFT|wx.RIGHT, 3)
        self.fgsizer.Add(self.size_ct, 0, wx.LEFT|wx.RIGHT, 3)
        self.fgsizer.Add(self.record_lb, 0, wx.LEFT|wx.RIGHT, 3)
        self.fgsizer.Add(self.record_ct, 0, wx.LEFT|wx.RIGHT, 3)
        self.fgsizer.Add(self.sec_lb, 0, wx.LEFT|wx.RIGHT, 3)
        self.fgsizer.Add(self.sec_ct, 0, wx.LEFT|wx.RIGHT, 3)

        self.type_lb.SetFont(boldfont)
        self.size_lb.SetFont(boldfont)
        self.record_lb.SetFont(boldfont)
        self.sec_lb.SetFont(boldfont)
        
        self.sizer.Add(self.fgsizer)
        self.SetSizer(self.sizer)
        wx.Panel.SetSize(self, self.sizer.GetMinSize())
        self.Layout()

    def SetObject(self, obj):
        if obj.FileData_Size: fsize = unicode(obj.FileData_Size / 1000) + 'kb'
        else: fsize = _('Nil')
        self.locte.SetValue(unicode(obj.FileData_FullPath))
        self.type_ct.SetLabel(unicode(obj.FileData_FileType))
        self.size_ct.SetLabel(unicode(fsize))
        self.record_ct.SetLabel(obj.FileData_FolderAdv.RecordFile if obj.FileData_FolderAdv else '')
        self.sec_ct.SetLabel(SECURITY_CLASSES[obj.FileData_FolderAdv.SecurityLevel] if obj.FileData_FolderAdv else _('N/A'))
        self.Layout()
        wx.Panel.SetSize(self, self.sizer.GetMinSize())

class WebInfoPanel(wx.Panel):
    def __init__(self, parent, id, *args, **kwargs):
        wx.Panel.__init__(self, parent, id, *args, **kwargs)

        self.urlDisplay = wx.HyperlinkCtrl(self, -1, 'empty', 'empty')
        self._do_layout()

    def _do_layout(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.urlDisplay, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(self.sizer)
        self.Layout()
        wx.Panel.SetSize(self, self.sizer.GetMinSize())
        
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
        wx.Panel.SetSize(self, self.sizer.GetMinSize())


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
        self.settext = None

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

    def SetMinSize(self, size):
        self.dtext.SetMinSize(size)

    def _exit_edit(self):
        self.dtext.Hide()
        self.stext.Show()
        self.Layout()
        self.GetParent().Layout()
        if self.dtext.GetValue() == self.settext: 
            return
        self.SetValue(self.dtext.GetValue())
        newevt = PieContextPanelFieldEvent(
            objattr=self._objattr,
            objattrval=self.GetValue())
        wx.PostEvent(self, newevt)
        print 'EditableText._exit_edit : event emitted'

    def SetValue(self, txt):
        '''Set the text to be displayed'''
        def trunc(t):
            '''truncate some text with ... at the end if necessary'''
            if len(t) > 200:
                return t[:200] + u' ...'
            else:
                return t
        if len(txt) == 0: txt = _(u'[click to edit]')
        dc = wx.WindowDC(self.stext)
        self.stext.SetLabel(wordwrap.wordwrap(trunc(txt), self.w, dc))
        self.dtext.SetValue(txt)
        self.settext = txt

    def SetWrapWidth(self, w):
        if sys.platform == 'win32': w = w * 1.3
        self.w = w

    def GetValue(self):
        r = self.dtext.GetValue()
        if r == _('[click to edit]'): r = u''
        return r

MAP_LOCNS = {
    'cachedir': _('Cached'),
    'meetingpaperdir': _('Meeting Papers'),
    'librarydir': _('Library'),
    'projectdir': _('Projects')
    }

class FundInfoPanel(wx.Panel):
    def __init__(self, parent, id, bigparent, *args, **kwargs):
        # kwargs['size'] = (80,140)
        wx.Panel.__init__(self, parent, id, *args, **kwargs)
        self.bigparent = bigparent
        self.favpanel = FBBPanel(self, -1, bigparent=bigparent)
        self.sizer0 = wx.BoxSizer(wx.VERTICAL)
        
        self.fgsizer = wx.FlexGridSizer(0, 2, 5, 5)
        self.fgsizer.AddGrowableCol(1)

        self.title_ct = EditableText(self, -1, '', objattr='title')
        # self.title_ct.SetFont(itfont)
        self.dings_ct = wx.StaticText(self, -1, u'')
        self.auth_lb = wx.StaticText(self, -1, _('Author:'))
        self.auth_lb.SetFont(boldfont)
        self.auth_ct = EditableText(self, -1, '', objattr='author')
        self.auth_ct.SetFont(normalfont)
        self.date_lb = wx.StaticText(self, -1, _('Date:'))
        self.date_lb.SetFont(boldfont)
        self.date_ct = wx.StaticText(self, -1, '')
        self.date_ct.SetFont(normalfont)
        self.locn_lb = wx.StaticText(self, -1, _('Location:'))
        self.locn_lb.SetFont(boldfont)
        self.locn_ct = wx.StaticText(self, -1, '')
        self.locn_ct.SetFont(normalfont)
        self.tagedit = PieTagWidget(self, -1, mode="lhorizontal")
        self.tagedit.setTagList(get_all_tags().keys())

        self.tagedit.Bind(EVT_PIE_TAG_ADDED, self.bigparent.OnTagAdded)
        self.tagedit.Bind(EVT_PIE_TAG_CLICKED, self.bigparent.OnTagClicked)
        self.auth_ct.Bind(EVT_PIE_CONTEXT_PANEL_FIELD, self.bigparent.OnFieldEdit)
        self.title_ct.Bind(EVT_PIE_CONTEXT_PANEL_FIELD, self.bigparent.OnFieldEdit)

        self.fgsizer.Add(self.favpanel)
        self.fgsizer.Add(self.title_ct, 1, wx.ALL, 3)
        self.fgsizer.Add((5,5))
        self.fgsizer.Add(self.dings_ct, 0, wx.LEFT|wx.RIGHT, 3)
        self.fgsizer.Add(self.auth_lb, 0, wx.LEFT|wx.RIGHT, 3)
        self.fgsizer.Add(self.auth_ct, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 3)
        self.fgsizer.Add(self.date_lb, 0, wx.LEFT|wx.RIGHT, 3)
        self.fgsizer.Add(self.date_ct, 0, wx.LEFT|wx.RIGHT, 3)
        self.fgsizer.Add(self.locn_lb, 0, wx.LEFT|wx.RIGHT, 3)
        self.fgsizer.Add(self.locn_ct, 0, wx.LEFT|wx.RIGHT, 3)
        self.fgsizer.Add((5,5))

        self.sizer0.Add(self.fgsizer, 1, wx.EXPAND)
        self.sizer0.Add(self.tagedit, 0)
        self.SetSizer(self.sizer0)
        # self.SetSizer(self.fgsizer)
        self.Layout()
        wx.Panel.SetSize(self, self.sizer0.GetMinSize())

    def SetObject(self, obj):
        # print 'COLWIDTHS', self.fgsizer.GetColWidths()
        self.auth_ct.SetWrapWidth(self.fgsizer.GetColWidths()[1])
        self.title_ct.SetWrapWidth(self.fgsizer.GetColWidths()[1])
        self.favpanel.SetValue(obj.StatData_Favourite)
        # if sys.platform == 'win32':
        #     self.favpanel.SetTitleWidth(int(self.GetSize()[0] * 1))
        # else:
        #     self.favpanel.SetTitleWidth(int(self.GetSize()[0] * 0.66))
        # print 'Setting title'
        self.title_ct.SetValue(obj.Title())
        # self.favpanel.SetTitle(obj.Title())
        # print 'Setting author'
        self.dings_ct.SetLabel(compile_infostring(obj))
        self.auth_ct.SetValue(obj.Author())
        # self.auth_ct.SetLabel(obj.Author())
        self.date_ct.SetLabel(
            obj.ReferDate().strftime('%d %B %Y') if obj.ReferDate().year >= 1900 else fmtdate(obj.ReferDate()))
        if obj.FileData_Root in MAP_LOCNS.keys():
            self.locn_ct.SetLabel(MAP_LOCNS[obj.FileData_Root])
        else:
            self.locn_ct.SetLabel(_('Library'))
        self.tagedit.Clear()
        if obj.has_aspect('saved'):
            self.tagedit.AddTags(obj.get_taglist())
        else:
            self.tagedit.AddTags(obj.get_queued_tags())
        # if not obj.has_aspect('saved'):
        #     self.tagedit.Disable()
        # else:
        #     self.tagedit.Enable()
        self.fgsizer.Layout()
        wx.Panel.SetSize(self, self.sizer0.GetMinSize())
        # self.sizer0.Layout()
        # self.Layout()

    def GetFavourite(self):
        return self.favpanel.BMB.GetValue()
    
aspectmap = {
    'onweb': u'\u2706',
    'ondesktop': u'',
    'cached': u'',
    'saved': u'',
    'stored': u'',
    'hasfile': u'\u2707',
    'failed_dl': u'',
    'bibdata': u'\u2711',
    'physical': u'\u267E'
    }

othermap = {
    'notes': u'\u270D',
    'encrypted': u'\u26BF',
    'flagged': u'\u2691',
    'starred': u'\u2729',
    }

def compile_infostring(obj):
    '''Compile a string of dingbats indicating info about the
    shown item'''
    rs = u''
    for asp in aspectmap.keys():
        if obj.has_aspect(asp): rs = rs + aspectmap[asp]
    if obj.notes: rs = rs + othermap['notes']
    if obj.StatData_FollowUpFlag: rs = rs + othermap['flagged']
    if obj.StatData_Favourite: rs = rs + othermap['starred']
    if obj.aspects['encrypted'] > 0: rs = rs + othermap['encrypted']
    return rs
        
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
        # self.sizer = wx.FlexGridSizer(0, 2, 3, 3)
        # self.sizer.AddGrowableCol(1)
        self.BMB = FavBitmapButton(self, -1)
        self.sizer.Add(self.BMB, 0, wx.ALL, 5)
        # self.title = EditableText(self, -1, '', objattr='title')
        # self.title.Bind(EVT_PIE_CONTEXT_PANEL_FIELD, self.bigparent.OnFieldEdit)
        # if not sys.platform == 'win32':
        #     font = wx.Font(10, wx.FONTFAMILY_ROMAN, -1, wx.FONTWEIGHT_BOLD)
        #     self.title.SetFont(font)
        # self.sizer.Add(self.title, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Layout()
        self.BMB.Bind(wx.EVT_BUTTON, self.bigparent.EmitUpdate)

    def GetValue(self):
        return self.BMB.GetValue()

    def SetValue(self, val):
        return self.BMB.SetValue(val)
    
    # def SetTitle(self, ttl):
    #     print 'Setting title wrapwidth', self.sizer.GetColWidths()[1]
    #     print self.sizer.GetColWidths()
    #     self.title.SetWrapWidth(self.sizer.GetColWidths()[1])
    #     self.title.SetMinSize((self.sizer.GetColWidths()[1], -1))
    #     self.title.SetValue(ttl)

        

import wx, wx.html
from string import join

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

html_fundamental = '''
<body bgcolor="%(color)s">
<i><b>%(title)s</b></i>
<p>
<font size=-1>
<b>Author:</b> %(author)s.<br>
<b>Date:</b> %(date)s<br>
<b>Tags:</b> %(tags)s
</p>
</font>
</body>
'''

html_colors = {'kde': "#F0EBE2"}

from urlparse import urlsplit

class BetterContextPanel(BaseContextPanel):

    def _do_layout(self):
        self.sizer0 = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer0)
        self.Layout()
        self.cleared = True

    def _add_section_onweb(self, obj):
        if obj.website:
            self.urlDisplay = wx.HyperlinkCtrl(
                self, -1, 
                'From %s' % obj.website.Domain, 
                obj.Url())
        else:
            self.urlDisplay = wx.HyperlinkCtrl(
                self, -1, 
                'From %s' % urlsplit(obj.Url())[1], 
                obj.Url())
        self.sizer0.Add(self.urlDisplay, 0, wx.EXPAND|wx.ALL, 3)
        # self.urlDisplay.SetURL(obj.Url())
    
    def _add_section_saved(self, obj):
        pass

    def _add_section_fundamental(self, obj):
        self.fundHtml = wx.html.HtmlWindow(self, -1)
        self.sizer0.Add(self.fundHtml, 1, wx.EXPAND|wx.ALL, 0)
        self.fundHtml.AppendToPage(html_fundamental % {
                'author': obj.Author(),
                'title': obj.Title(),
                'date': obj.ReferDate().strftime('%d %B %Y'),
                'color': html_colors['kde'],
                'tags': join(obj.tags, ' | ')
                })
        

    def SetObject(self, obj):
        self.Clear()
        self._add_section_fundamental(obj)
        if obj.has_aspect('onweb'):
            self._add_section_onweb(obj)
        self.Layout()
        self.cleared = False

    def Clear(self):
        if self.cleared: return
        if self.fundHtml:
            self.sizer0.Remove(self.fundHtml)
            self.fundHtml.Destroy()
        if self.urlDisplay:
            self.sizer0.Remove(self.urlDisplay)
            self.urlDisplay.Destroy()
        self.cleared = True
    
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
        websitelabel = wx.StaticText(self, -1, 'Website:')
        self.websitedisplay = wx.StaticText(self, -1, '')
        self._create_field(websitelabel, self.websitedisplay)
        self.SetSizer(self.sizer0)
        self.Layout()
                                     
    def SetObject(self, obj):
        self.iddisplay.SetLabel(unicode(obj.GetId()))
        self.titledisplay.SetLabel(obj.Title())
        self.authordisplay.SetLabel(obj.Author())
        self.filelocdisplay.SetLabel(unicode(obj.FileData_FullPath))
        self.collectiondisplay.SetLabel(unicode(obj.collection))
        self.websitedisplay.SetLabel(unicode(obj.website))


class FavButton(wx.PyControl):
    '''Custom button for marking entries as favourite'''
    # TODO - yet to implement
    def __init__(self, parent, id, bmp, text, **kwargs):
        wx.PyControl.__init__(self,parent, id, **kwargs)

        self.Bind(wx.EVT_LEFT_DOWN, self._onMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self._onMouseUp)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._onMouseLeave)
        self.Bind(wx.EVT_ENTER_WINDOW, self._onMouseEnter)
        self.Bind(wx.EVT_ERASE_BACKGROUND,self._onEraseBackground)
        self.Bind(wx.EVT_PAINT,self._onPaint)

        self._mouseIn = self._mouseDown = False

    def _onMouseEnter(self, event):
        self._mouseIn = True

    def _onMouseLeave(self, event):
        self._mouseIn = False

    def _onMouseDown(self, event):
        self._mouseDown = True

    def _onMouseUp(self, event):
        self._mouseDown = False
        self.sendButtonEvent()

    def sendButtonEvent(self):
        event = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, self.GetId())
        event.SetInt(0)
        event.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(event)

    def _onEraseBackground(self,event):
        # reduce flicker
        pass

    def _onPaint(self, event):
        dc = wx.BufferedPaintDC(self)
        dc.SetFont(self.GetFont())
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        # draw whatever you want to draw
        # draw glossy bitmaps e.g. dc.DrawBitmap
        if self._mouseIn:
            pass# on mouserover may be draw different bitmap
        if self._mouseDown:
            pass # draw different image text

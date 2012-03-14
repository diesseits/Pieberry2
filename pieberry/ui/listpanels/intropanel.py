import sys, os, os.path, wx

from pieberry.pieconfig.identity import *
from pieberry.pieconfig.initsys import IMGDIR

import pieberry.ui.stdlines as stdlines

from wx.lib import wordwrap

bigfont = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)


class IntroPanel(wx.Panel):
    '''Intro panel so that new users don't boot up a blank screen'''
    paneltype = 'IntroPanel'

    def __init__(self, parent, id=-1, style=wx.EXPAND):
        wx.Panel.__init__(self, parent, id=id, style=style)
        
        title = wx.StaticText(self, -1, stdlines.SLOGAN)
        title.SetFont(bigfont)
        icon = wx.StaticBitmap(
            self, -1, wx.Bitmap(os.path.join(IMGDIR, 'pie_48.png')))
        desc = wx.StaticText(self, -1, '')
        dc = wx.WindowDC(desc)
        desc.SetLabel(wordwrap.wordwrap(stdlines.DESCRIPTION, 300, dc))
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add((20,20), 1)
        sizer.Add(title, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        sizer.Add(icon, 0, wx.ALL|wx.ALIGN_CENTRE, 5)
        sizer.Add(desc, 0, wx.ALL|wx.ALIGN_CENTRE, 5)
        sizer.Add((20,20), 3)
        
        self.SetSizer(sizer)
        self.Layout()
    


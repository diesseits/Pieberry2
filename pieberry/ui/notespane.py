import sys, wx
import wx.richtext as rt
from pieberry.pieconfig.initsys import *

class RichTextPanel(wx.Panel):
    paneltype = 'notespanel'
    
    def __init__(self, *args, **kw):
        
        wx.Panel.__init__(self, *args, **kw)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.toolbar = wx.ToolBar(self, -1)

        # tb_undo = self.toolbar.AddTool(
        #     wx.ID_UNDO, wx.ArtProvider.GetBitmap(wx.ART_UNDO, wx.ART_TOOLBAR),
        #     shortHelpString=_("Undo"))

        # tb_redo = self.toolbar.AddTool(
        #     wx.ID_REDO, wx.ArtProvider.GetBitmap(wx.ART_REDO, wx.ART_TOOLBAR),
        #     shortHelpString=_('Redo'))


        # self.toolbar.Realize()
        self.MakeToolBar()
        
        self.rtc = rt.RichTextCtrl(self, style=wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER|wx.WANTS_CHARS)
        sizer.Add(self.toolbar, 0, wx.EXPAND)
        sizer.Add(self.rtc, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(sizer)
        self.Layout()
        wx.CallAfter(self.rtc.SetFocus)
        self.rtc.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

    def OnKeyDown(self, evt):
        print evt.GetKeyCode()
        keycode = evt.GetKeyCode()

        if evt.ControlDown():
            if (keycode == ord('B') ):
                self.rtc.ApplyBoldToSelection()
            elif (keycode == ord('I')):
                self.rtc.ApplyItalicToSelection()
            elif (keycode == ord('U')):
                self.rtc.ApplyUnderlineToSelection()

        evt.Skip()


    def OnURL(self, evt):

        wx.MessageBox(evt.GetString(), "URL Clicked")


    def OnFileOpen(self, evt):

        # This gives us a string suitable for the file dialog based on
        # the file handlers that are loaded
        wildcard, types = rt.RichTextBuffer.GetExtWildcard(save=False)
        dlg = wx.FileDialog(self, "Choose a filename",
                            wildcard=wildcard,
                            style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if path:
                fileType = types[dlg.GetFilterIndex()]
                self.rtc.LoadFile(path, fileType)
        dlg.Destroy()


    def OnFileSave(self, evt):

        if not self.rtc.GetFilename():
            self.OnFileSaveAs(evt)
            return

        self.rtc.SaveFile()


    def OnFileSaveAs(self, evt):

        wildcard, types = rt.RichTextBuffer.GetExtWildcard(save=True)

        dlg = wx.FileDialog(self, "Choose a filename",
                            wildcard=wildcard,
                            style=wx.SAVE)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if path:
                fileType = types[dlg.GetFilterIndex()]
                ext = rt.RichTextBuffer.FindHandlerByType(fileType).GetExtension()
                if not path.endswith(ext):
                    path += '.' + ext
                self.rtc.SaveFile(path, fileType)

        dlg.Destroy()


    def OnFileViewHTML(self, evt):

        # Get an instance of the html file handler, use it to save the
        # document to a StringIO stream, and then display the
        # resulting html text in a dialog with a HtmlWindow.
        handler = rt.RichTextHTMLHandler()
        handler.SetFlags(rt.RICHTEXT_HANDLER_SAVE_IMAGES_TO_MEMORY)
        handler.SetFontSizeMapping([7,9,11,12,14,22,100])

        import cStringIO
        stream = cStringIO.StringIO()
        if not handler.SaveStream(self.rtc.GetBuffer(), stream):
            return

        import wx.html
        dlg = wx.Dialog(self, title="HTML", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        html = wx.html.HtmlWindow(dlg, size=(500,400), style=wx.BORDER_SUNKEN)
        html.SetPage(stream.getvalue())
        btn = wx.Button(dlg, wx.ID_CANCEL)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(html, 1, wx.ALL|wx.EXPAND, 5)
        sizer.Add(btn, 0, wx.ALL|wx.CENTER, 10)
        dlg.SetSizer(sizer)
        sizer.Fit(dlg)

        dlg.ShowModal()

        handler.DeleteTemporaryImages()


    def OnFileExit(self, evt):

        self.Close(True)


    def OnBold(self, evt):

        self.rtc.ApplyBoldToSelection()


    def OnItalic(self, evt):

        self.rtc.ApplyItalicToSelection()


    def OnUnderline(self, evt):

        self.rtc.ApplyUnderlineToSelection()


    def OnAlignLeft(self, evt):

        self.rtc.ApplyAlignmentToSelection(rt.TEXT_ALIGNMENT_LEFT)


    def OnAlignRight(self, evt):

        self.rtc.ApplyAlignmentToSelection(rt.TEXT_ALIGNMENT_RIGHT)


    def OnAlignCenter(self, evt):

        self.rtc.ApplyAlignmentToSelection(rt.TEXT_ALIGNMENT_CENTRE)


    def OnIndentMore(self, evt):

        attr = rt.TextAttrEx()
        attr.SetFlags(rt.TEXT_ATTR_LEFT_INDENT)
        ip = self.rtc.GetInsertionPoint()
        if self.rtc.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rtc.HasSelection():
                r = self.rtc.GetSelectionRange()

            attr.SetLeftIndent(attr.GetLeftIndent() + 100)
            attr.SetFlags(rt.TEXT_ATTR_LEFT_INDENT)
            self.rtc.SetStyle(r, attr)


    def OnIndentLess(self, evt):

        attr = rt.TextAttrEx()
        attr.SetFlags(rt.TEXT_ATTR_LEFT_INDENT)
        ip = self.rtc.GetInsertionPoint()
        if self.rtc.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rtc.HasSelection():
                r = self.rtc.GetSelectionRange()

        if attr.GetLeftIndent() >= 100:
            attr.SetLeftIndent(attr.GetLeftIndent() - 100)
            attr.SetFlags(rt.TEXT_ATTR_LEFT_INDENT)
            self.rtc.SetStyle(r, attr)


    def OnParagraphSpacingMore(self, evt):

        attr = rt.TextAttrEx()
        attr.SetFlags(rt.TEXT_ATTR_PARA_SPACING_AFTER)
        ip = self.rtc.GetInsertionPoint()
        if self.rtc.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rtc.HasSelection():
                r = self.rtc.GetSelectionRange()

            attr.SetParagraphSpacingAfter(attr.GetParagraphSpacingAfter() + 20);
            attr.SetFlags(rt.TEXT_ATTR_PARA_SPACING_AFTER)
            self.rtc.SetStyle(r, attr)


    def OnParagraphSpacingLess(self, evt):

        attr = rt.TextAttrEx()
        attr.SetFlags(rt.TEXT_ATTR_PARA_SPACING_AFTER)
        ip = self.rtc.GetInsertionPoint()
        if self.rtc.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rtc.HasSelection():
                r = self.rtc.GetSelectionRange()

            if attr.GetParagraphSpacingAfter() >= 20:
                attr.SetParagraphSpacingAfter(attr.GetParagraphSpacingAfter() - 20);
                attr.SetFlags(rt.TEXT_ATTR_PARA_SPACING_AFTER)
                self.rtc.SetStyle(r, attr)


    def OnLineSpacingSingle(self, evt):

        attr = rt.TextAttrEx()
        attr.SetFlags(rt.TEXT_ATTR_LINE_SPACING)
        ip = self.rtc.GetInsertionPoint()
        if self.rtc.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rtc.HasSelection():
                r = self.rtc.GetSelectionRange()

            attr.SetFlags(rt.TEXT_ATTR_LINE_SPACING)
            attr.SetLineSpacing(10)
            self.rtc.SetStyle(r, attr)


    def OnLineSpacingHalf(self, evt):

        attr = rt.TextAttrEx()
        attr.SetFlags(rt.TEXT_ATTR_LINE_SPACING)
        ip = self.rtc.GetInsertionPoint()
        if self.rtc.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rtc.HasSelection():
                r = self.rtc.GetSelectionRange()

            attr.SetFlags(rt.TEXT_ATTR_LINE_SPACING)
            attr.SetLineSpacing(15)
            self.rtc.SetStyle(r, attr)


    def OnLineSpacingDouble(self, evt):

        attr = rt.TextAttrEx()
        attr.SetFlags(rt.TEXT_ATTR_LINE_SPACING)
        ip = self.rtc.GetInsertionPoint()
        if self.rtc.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rtc.HasSelection():
                r = self.rtc.GetSelectionRange()

            attr.SetFlags(rt.TEXT_ATTR_LINE_SPACING)
            attr.SetLineSpacing(20)
            self.rtc.SetStyle(r, attr)


    def OnFont(self, evt):

        if not self.rtc.HasSelection():
            return

        r = self.rtc.GetSelectionRange()
        fontData = wx.FontData()
        fontData.EnableEffects(False)
        attr = rt.TextAttrEx()
        attr.SetFlags(rt.TEXT_ATTR_FONT)
        if self.rtc.GetStyle(self.rtc.GetInsertionPoint(), attr):
            fontData.SetInitialFont(attr.GetFont())

        dlg = wx.FontDialog(self, fontData)
        if dlg.ShowModal() == wx.ID_OK:
            fontData = dlg.GetFontData()
            font = fontData.GetChosenFont()
            if font:
                attr.SetFlags(rt.TEXT_ATTR_FONT)
                attr.SetFont(font)
                self.rtc.SetStyle(r, attr)
        dlg.Destroy()


    def OnColour(self, evt):

        colourData = wx.ColourData()
        attr = rt.TextAttrEx()
        attr.SetFlags(rt.TEXT_ATTR_TEXT_COLOUR)
        if self.rtc.GetStyle(self.rtc.GetInsertionPoint(), attr):
            colourData.SetColour(attr.GetTextColour())

        dlg = wx.ColourDialog(self, colourData)
        if dlg.ShowModal() == wx.ID_OK:
            colourData = dlg.GetColourData()
            colour = colourData.GetColour()
            if colour:
                if not self.rtc.HasSelection():
                    self.rtc.BeginTextColour(colour)
                else:
                    r = self.rtc.GetSelectionRange()
                    attr.SetFlags(rt.TEXT_ATTR_TEXT_COLOUR)
                    attr.SetTextColour(colour)
                    self.rtc.SetStyle(r, attr)
        dlg.Destroy()



    def OnUpdateBold(self, evt):

        evt.Check(self.rtc.IsSelectionBold())


    def OnUpdateItalic(self, evt):

        evt.Check(self.rtc.IsSelectionItalics())


    def OnUpdateUnderline(self, evt):

        evt.Check(self.rtc.IsSelectionUnderlined())


    def OnUpdateAlignLeft(self, evt):

        evt.Check(self.rtc.IsSelectionAligned(rt.TEXT_ALIGNMENT_LEFT))


    def OnUpdateAlignCenter(self, evt):

        evt.Check(self.rtc.IsSelectionAligned(rt.TEXT_ALIGNMENT_CENTRE))


    def OnUpdateAlignRight(self, evt):

        evt.Check(self.rtc.IsSelectionAligned(rt.TEXT_ALIGNMENT_RIGHT))


    def ForwardEvent(self, evt):

        # The RichTextCtrl can handle menu and update events for undo,
        # redo, cut, copy, paste, delete, and select all, so just
        # forward the event to it.
        self.rtc.ProcessEvent(evt)

    def MakeToolBar(self):


        def doBind(item, handler, updateUI=None):

            self.Bind(wx.EVT_TOOL, handler, item)
            if updateUI is not None:
                self.Bind(wx.EVT_UPDATE_UI, updateUI, item)

        tbar = self.toolbar
        # doBind( tbar.AddTool(-1, images._rt_open.GetBitmap(),
        #                       shortHelpString="Open"), self.OnFileOpen)
        # doBind( tbar.AddTool(-1, images._rt_save.GetBitmap(),
        #                       shortHelpString="Save"), self.OnFileSave)
        # tbar.AddSeparator()
        doBind( tbar.AddTool(wx.ID_CUT, wx.ArtProvider.GetBitmap(wx.ART_CUT, wx.ART_TOOLBAR),
                             shortHelpString="Cut"), self.ForwardEvent, self.ForwardEvent)
        doBind( tbar.AddTool(wx.ID_COPY, wx.ArtProvider.GetBitmap(wx.ART_COPY, wx.ART_TOOLBAR),
                             shortHelpString="Copy"), self.ForwardEvent, self.ForwardEvent)
        doBind( tbar.AddTool(wx.ID_PASTE, wx.ArtProvider.GetBitmap(wx.ART_PASTE, wx.ART_TOOLBAR),
                             shortHelpString="Paste"), self.ForwardEvent, self.ForwardEvent)
        tbar.AddSeparator()
        doBind( tbar.AddTool(wx.ID_UNDO, wx.ArtProvider.GetBitmap(wx.ART_UNDO, wx.ART_TOOLBAR),
                             shortHelpString="Undo"), self.ForwardEvent, self.ForwardEvent)
        doBind( tbar.AddTool(wx.ID_REDO, wx.ArtProvider.GetBitmap(wx.ART_REDO, wx.ART_TOOLBAR),
                             shortHelpString="Redo"), self.ForwardEvent, self.ForwardEvent)
        tbar.AddSeparator()
        # doBind( tbar.AddTool(-1, images._rt_bold.GetBitmap(), isToggle=True,
        #                       shortHelpString="Bold"), self.OnBold, self.OnUpdateBold)
        # doBind( tbar.AddTool(-1, images._rt_italic.GetBitmap(), isToggle=True,
        #                       shortHelpString="Italic"), self.OnItalic, self.OnUpdateItalic)
        # doBind( tbar.AddTool(-1, images._rt_underline.GetBitmap(), isToggle=True,
        #                       shortHelpString="Underline"), self.OnUnderline, self.OnUpdateUnderline)
        # tbar.AddSeparator()
        # doBind( tbar.AddTool(-1, images._rt_alignleft.GetBitmap(), isToggle=True,
        #                       shortHelpString="Align Left"), self.OnAlignLeft, self.OnUpdateAlignLeft)
        # doBind( tbar.AddTool(-1, images._rt_centre.GetBitmap(), isToggle=True,
        #                       shortHelpString="Center"), self.OnAlignCenter, self.OnUpdateAlignCenter)
        # doBind( tbar.AddTool(-1, images._rt_alignright.GetBitmap(), isToggle=True,
        #                       shortHelpString="Align Right"), self.OnAlignRight, self.OnUpdateAlignRight)
        # tbar.AddSeparator()
        # doBind( tbar.AddTool(-1, images._rt_indentless.GetBitmap(),
        #                       shortHelpString="Indent Less"), self.OnIndentLess)
        # doBind( tbar.AddTool(-1, images._rt_indentmore.GetBitmap(),
        #                       shortHelpString="Indent More"), self.OnIndentMore)
        # tbar.AddSeparator()
        # doBind( tbar.AddTool(-1, images._rt_font.GetBitmap(),
        #                       shortHelpString="Font"), self.OnFont)
        # doBind( tbar.AddTool(-1, images._rt_colour.GetBitmap(),
        #                       shortHelpString="Font Colour"), self.OnColour)
        tbar.Realize()

    

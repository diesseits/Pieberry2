import wx, os.path

from pieberry.piemeta import get_metadata_object
from pieberry.atomise.atomise_imagelist import *

class BibtexEntryDialog(wx.Dialog):
    '''A class to allow the direct cut & pasting in of bibtex
    information and an associated file'''
    def __init__(self, parent, title, caption):
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        super(BibtexEntryDialog, self).__init__(parent, -1, title, style=style)
        text = wx.StaticText(self, -1, caption)
        input = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE)
        input.SetInitialSize((400, 300))
        tt2 = wx.ToolTip(_('You may paste in BibTeX formatted database entries directly here, as provided by sites like JSTOR as a citation format.'))
        input.SetToolTip(tt2)
        # dt = FileDropTarget(self.fntext, icon)
        # self.fntext.SetDropTarget(dt)
        self.icon = wx.StaticBitmap(self, -1, size=(22,22))
        # self.fntext = wx.TextCtrl(self, -1, style=wx.TE_READONLY)
        self.fntext = wx.FilePickerCtrl(
            self, -1,
            wildcard = "Known file types (*.pdf;*.doc;*.docx;*.txt;*.xls;*.xlsx;*.ppt;*.pptx;*.odf;*.ods;*.odp)|*.pdf;*.doc;*.docx;*.txt;*.xls;*.xlsx;*.ppt;*.pptx;*.odf;*.ods;*.odp|All files (*.*)|*.*",
            style = wx.FLP_USE_TEXTCTRL|wx.FLP_SAVE)
        tt = wx.ToolTip(_('A file selected here will be attached to the first record drawn from the bibtex entries above when they are put in the staging pane'))
        self.fntext.SetToolTip(tt)
        buttons = self.CreateButtonSizer(wx.OK|wx.CANCEL)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(self.icon, 0, wx.ALL, 5)
        sizer1.Add(self.fntext, 1, wx.ALL, 5)
        sizer.Add(text, 0, wx.ALL, 5)
        sizer.Add(input, 1, wx.EXPAND|wx.ALL, 5)
        sizer.Add(wx.StaticText(self, -1, 'File to attach'), #_('File to attach: (drag and drop)')),
                  0, wx.ALL, 5)
        sizer.Add(sizer1, 0, wx.EXPAND)
        sizer.Add(buttons, 0, wx.EXPAND|wx.ALL, 5)
        self.SetSizerAndFit(sizer)
        self.input = input
        self.fntext.Bind(wx.EVT_FILEPICKER_CHANGED, self.OnFilePicked)
        self.input.SetFocus()
        
    def OnFilePicked(self, evt):
        thepath = evt.GetPath()[5:] if evt.GetPath()[:5] == 'file:' else evt.GetPath()
        if not os.path.isfile(thepath): 
            print 'Error reading path'
            self.fntext.SetPath('')
            return
        obj = get_metadata_object(thepath, fakeonly=True)
        if not obj: 
            print 'Unrecognised file type'
            self.fntext.SetPath('')
            return
        self.fntext.SetPath(thepath)
        iconcode = obj.get_icon_code(window_type='filewindow')
        iconp = AtomImageList.GetBitmap(IconType[iconcode])
        self.icon.SetBitmap(iconp)
        self.input.SetFocus()

    def SetValue(self, value):
        self.input.SetValue(value)
    def GetValue(self):
        return self.input.GetValue()
    def GetAttachedFile(self):
        if self.fntext.GetPath():
            return self.fntext.GetPath()
        else: return None
        

# class FileDropTarget(wx.FileDropTarget):
#     """ This object implements Drop Target functionality for Files """
#     def __init__(self, parent, icon):
#         """ Initialize the Drop Target, passing in the Object Reference to
#         indicate what should receive the dropped files """
#         # Initialize the wxFileDropTarget Object
#         wx.FileDropTarget.__init__(self)
#         # Store the Object Reference for dropped files
#         self.parent = parent
#         self.icon = icon
 
#     def OnDropFiles(self, x, y, filenames):
#         """ Implement File Drop """
#         print filenames
#         if len(filenames) > 1:
#             return
#         else:
#             self.parent.SetPath(filenames[0])
#             obj = get_metadata_object(filenames[0], fakeonly=True)
#             print obj
#             iconcode = obj.get_icon_code(window_type='filewindow')
#             iconp = AtomImageList.GetBitmap(IconType[iconcode])
#             self.icon.SetBitmap(iconp)

if __name__ == '__main__':
    app = wx.PySimpleApp(0)
    ted = BibtexEntryDialog(None, 'Hello', 'Thingy')
    ted.Show()
    app.MainLoop()

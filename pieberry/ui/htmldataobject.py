# Source:
# http://groups.google.com/group/wxPython-users/browse_thread/thread/5c66b0d1b1d438a2
# Robin Dunn 
# Software Craftsman 
# http://wxPython.org 

# [   htmldataobj.py 2K ] 

import wx 

class HTMLDataObject(wx.PyDataObjectSimple): 
    header = """Version:0.9 
StartHTML:%08d 
EndHTML:%08d 
StartFragment:%08d 
EndFragment:%08d 
SourceURL:%s 
""" 
    startFrag = """<html><body> 
<!--StartFragment-->""" 
    endFrag = """<!--EndFragment--> 
</body> 
</html> 
""" 
    def __init__(self): 
        fmt = wx.CustomDataFormat("HTML Format") 
        wx.PyDataObjectSimple.__init__(self, fmt) 
        self.value = None 
        self.fmt = fmt 
    def SetValue(self, html, srcURL=""): 
        if isinstance(html, unicode): 
            fragment = html.encode('utf-8') 
        else: 
            # This assumes that it's already utf-8 or plain ascii and 
            # not some other encoding 
            fragment = html 
        # Assemble the text using the templates above, and the html 
        # fragment given to us.  First calculate the sizes that will 
        # be put in the header. 
        startHtml = len(self.header) + 4*4 + len(srcURL) 
        # 4*4 is the number of extra digits that will be substituted 
        # for all the %08d items in the header 
        startFragment = startHtml + len(self.startFrag) 
        endFragment = startFragment + len(fragment) 
        endHtml = endFragment + len(self.endFrag) 
        value = self.header % (startHtml, endHtml, startFragment, endFragment, srcURL) 
        value += self.startFrag + fragment + self.endFrag 
        self.value = value 
    def GetValue(self): 
        # TODO: This should extract just the fragment from the whole 
        # value and return that, in order to be consistent with how 
        # SetValue works. 
        return self.value 
    # Overridden base class methods that implement the data transfer 
    def GetDataSize(self): 
        print 'GetDataSize' 
        return len(self.value) 
    def GetDataHere(self): 
        print 'GetDataHere' 
        return self.value 
    def SetData(self, buf): 
        print 'SetData' 
        self.value = buf 


if __name__ == '__main__': 
    def copy(evt): 
        do = HTMLDataObject() 
        do.SetValue("<b>hello world</b>") 
        wx.TheClipboard.Open() 
        wx.TheClipboard.SetData(do) 
        wx.TheClipboard.Close() 
    def paste(evt): 
        do = HTMLDataObject() 
        wx.TheClipboard.Open() 
        if not wx.TheClipboard.IsSupported(do.fmt): 
            print "expected format not in the clipboard" 
        else: 
            wx.TheClipboard.GetData(do) 
        wx.TheClipboard.Close() 
        print do.GetValue() 
    app = wx.App(False) 
    frm = wx.Frame(None) 
    cbtn = wx.Button(frm, -1, "copy") 
    cbtn.Bind(wx.EVT_BUTTON, copy) 
    pbtn = wx.Button(frm, -1, "paste") 
    pbtn.Bind(wx.EVT_BUTTON, paste) 
    sizer = wx.BoxSizer() 
    sizer.Add(cbtn, 0, wx.ALL, 5) 
    sizer.Add(pbtn, 0, wx.ALL, 5) 
    frm.SetSizer(sizer) 
    frm.Fit() 
    frm.Show() 
    app.MainLoop() 


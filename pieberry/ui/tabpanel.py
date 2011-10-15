import wx 

class TestTabPanel(wx.Panel):
    """
    This will be the first notebook tab
    """
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """"""

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        sizer = wx.BoxSizer(wx.VERTICAL)
        txtOne = wx.TextCtrl(self, wx.ID_ANY, "")
        txtTwo = wx.TextCtrl(self, wx.ID_ANY, "")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(txtOne, 0, wx.ALL, 5)
        sizer.Add(txtTwo, 0, wx.ALL, 5)

        self.SetSizer(sizer)


class AddablePanel(wx.Panel):
    '''Generic Panel with some stuff'''
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY, size=(100,100),
                          style=wx.EXPAND)

        sizer = wx.BoxSizer(wx.VERTICAL)
        
        lb = wx.StaticText(self, -1, "This thing:")
        tc = wx.TextCtrl(self, -1, "Hello", size=(100,100), style=wx.EXPAND)
        
        sizer.Add(lb, 0, wx.ALL, 5)
        sizer.Add(tc, 1, wx.ALL, 5)

        self.SetSizer(sizer)

class ManagedTabPanel(wx.Panel):
    '''Tab panel managed by aui manager'''
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self._mgr = wx.aui.AuiManager(self)
        
        txtOne = wx.TextCtrl(self, wx.ID_ANY, "Hey")
        # txtTwo = wx.TextCtrl(self, wx.ID_ANY, "You")
        pan = AddablePanel(self)
        

        self._mgr.AddPane(txtOne, wx.aui.AuiPaneInfo().Top().BestSize((150,50)), 'Top Pane')
        # self._mgr.AddPane(txtTwo, wx.BOTTOM, 'Bottom Pane')
        self._mgr.AddPane(pan, wx.aui.AuiPaneInfo().Fixed(), 'Bottom pane')

        self._mgr.Update()



class GeneralRedrawablePanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY, style=wx.EXPAND)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        tx = wx.TextCtrl(self, -1, style=wx.EXPAND)
        bt1 = wx.Button(self, -1, style=wx.EXPAND, label="Create")
        
        self.sizer.Add(tx, 1, wx.ALL, 5)
        self.sizer.Add(bt1, 1, wx.ALL, 5)

        self.SetSizer(self.sizer)
        self.sizer.Layout()
        
        bt1.Bind(wx.EVT_BUTTON, self.onBt1)

    def onBt1(self, evt):
        self.bt2 = wx.Button(self, -1, label="Destroy")
        self.bt2.Bind(wx.EVT_BUTTON, self.onBt2)

        self.sizer.Add(self.bt2, 1, wx.ALL, 5)
        self.sizer.Layout()

    def onBt2(self, evt):
        self.sizer.Remove(self.bt2)
        self.bt2.Destroy()
        # self.Refresh()
        self.sizer.Layout()

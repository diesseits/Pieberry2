import wx, time
from pieberry.pieconfig.config import PIE_CONFIG


class WebPanelUiTimer(wx.Timer):
    '''timer class that updates web panel (triggers prefetch)'''
    def __init__(self, parent, *args, **kwargs):
        wx.Timer.__init__(self, *args, **kwargs)
        self._last_iteration = time.time()
        self._f = parent
 
    def Notify(self):
        self._last_iteration = time.time()
        self._f.onPrefetchTag(self._last_iteration)

class TooltipUiTimer(wx.Timer):
    '''timer class that updates tooltips in list views'''
    def __init__(self, parent, *args, **kwargs):
        wx.Timer.__init__(self, *args, **kwargs)
        self._last_iteration = time.time()
        self._f = parent
 
    def Notify(self):
        self._last_iteration = time.time()
        self._f.onMouseUpdateList()
        self._f.onPrefetchTag(self._last_iteration)

class SpinnyTimer(wx.Timer):
    def __init__(self, parent, *args, **kwargs):
        wx.Timer.__init__(self, *args, **kwargs)
        self._f = parent

    def Notify(self):
        self._f.spinnerTick()

class FileIndexTimer(wx.Timer):
    def __init__(self, parent, *args, **kwargs):
        wx.Timer.__init__(self, *args, **kwargs)
        self._f = parent

    def Notify(self):
        self._f.OnStartIndexer()
        

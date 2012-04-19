# A breadcrumb-trail widget

import wx

from pieberry.ui.events import PieCrumbClickedEvent, EVT_PIE_CRUMB_CLICKED

class PieBreadcrumb(wx.Button):
    '''An individual breadcrumb'''
    def __init__(self, parent, id, folder, ordinal):
        wx.Button.__init__(self, parent, id, label=u'> %s' % folder.EndName)
        self.folder = folder
        self.ordinal = ordinal # the sequence number of the current crumb

    def GetFolder(self):
        return self.folder

class PieBreadcrumbTrail(wx.Panel):
    '''A breadcrumb trail widget'''
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id, size=(28,28))
        self._crumbs = []
        self._parent = parent
        self._no_crumbs = 0
        self.__do_layout()

    def __do_layout(self):
        self._sizer = wx.BoxSizer(wx.HORIZONTAL)

    def SetRoot(self, folder):
        self.AddCrumb(folder)

    def AddCrumb(self, folder):
        # self._no_crumbs += 1
        crumb = PieBreadcrumb(self, -1, folder, len(self._crumbs)+1)#, self._no_crumbs)
        self._sizer.Add(crumb, 0, wx.ALL, 2)
        self._crumbs.append(crumb)
        crumb.Bind(wx.EVT_BUTTON, self.onCrumbClicked)
        self._sizer.Layout()
        self.Layout()
        print 'crumbs:', self._no_crumbs

    def onCrumbClicked(self, evt):
        ordinal = evt.GetEventObject().ordinal
        print ordinal, len(self._crumbs)
        print range(ordinal, len(self._crumbs))
        print self._crumbs
        irange = range(ordinal, len(self._crumbs))
        irange.reverse()
        for i in irange:
            print 'removing', i
            self._crumbs[i].Destroy()
            # self._sizer.Remove(self._crumbs[i])
            self._crumbs.pop(i)
        # self._no_crumbs == ordinal
        self._sizer.Layout()
        self.Layout()
        newevt = PieCrumbClickedEvent(
            fobj = evt.GetEventObject().GetFolder(),
            notify_window = self._parent)
        wx.PostEvent(self._parent, newevt)
        

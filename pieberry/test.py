#!/usr/bin/python

import wx
import sys, os
# sys.path.append(os.path.abspath('pieobject'))
# print os.path.abspath('.')

from pieconfig.globals import *

if __name__ == '__main__':
    import gettext
    gettext.install('pietest')
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()

from pieobject import *
from piescrape import *
#from ui import BaseMainWindow
from functionwindow import FunctionMainWindow
from spoofgeneration import *

def test():
    print sqlalchemy.__version__
    for i in range(3):
        o = spoof_pieobject()
        print o

if __name__ == '__main__':
    frame_1 = FunctionMainWindow(None, -1, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    for i in range(5):
        o = spoof_pieobject('normal')
        p = spoof_pieobject('web')
        pan = frame_1.GetCurrentPane()
        pan.AddObject(p)
        # frame_1.tab0.AddObject(o)
        # frame_1.tab1.AddObject(p)
        # frame_1.tab2.AddObject(o)
        # print frame_1.tab0.objectstore
        # print frame_1.tab1.objectstore
    app.MainLoop()


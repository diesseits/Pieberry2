#!/usr/bin/python

import wx
import sys, os, shutil
# sys.path.append(os.path.abspath('pieobject'))
# print os.path.abspath('.')

from pieconfig.globals import *
from pieconfig.paths import *
from spoofgeneration import fill_desktopdir

if __name__ == '__main__':
    # use gettext
    import gettext
    gettext.install('pietest')
    # instantiate app
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    # clear out the directories if debugging
    if DEBUG:
        nuke_directories()
        create_directories()
        fill_desktopdir()

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

from pieobject.website import make_spoof_websites

if __name__ == '__main__':
    SQLABase.metadata.create_all(engine)
    make_spoof_websites()
    frame_1 = FunctionMainWindow(None, -1, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    # frame_1.DebugAddWebPane()
    # frame_1.DebugAddDownloadedPane()
    # for i in range(5):
    #     o = spoof_pieobject('normal')
    #     p = spoof_pieobject('web')
    #     pan = frame_1.GetCurrentPane()
    #     pan.AddObject(p)
        # frame_1.tab0.AddObject(o)
        # frame_1.tab1.AddObject(p)
        # frame_1.tab2.AddObject(o)
        # print frame_1.tab0.objectstore
        # print frame_1.tab1.objectstore
    app.MainLoop()


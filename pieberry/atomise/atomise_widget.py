#!/bin/python

import sys, os, time, subprocess
import traceback
import wx
import pprint
import shutil

# from atomise_exec import *
from atomise_window import *
from pieconfig.paths import *

class atomWidget(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.__do_layout()
        self.Bind(wx.EVT_BUTTON, self.atomDisplay.onFileAll, self.procbt)

        # cf = open(os.path.join(SYSDIR, 'criteria.pickle'), 'r')
        # self.criteria = cPickle.load(cf)
        # cf.close()
        # self.setDestinations(self.criteria.keys())
        # self.Bind(wx.EVT_BUTTON, self.onOpenTemp, self.openbt)
    
    def __do_layout(self):
        self.atomDisplay = atomActionWindow(self, -1)
        self.openbt = wx.Button(self, -1, label='Open temp directory')
        self.procbt = wx.Button(self, -1, label='Process all')
        self.donebt = wx.Button(self, -1, label='Done')

        s2 = wx.BoxSizer(wx.VERTICAL)
        s3 = wx.BoxSizer(wx.HORIZONTAL)

        s2.Add(self.atomDisplay, 1, wx.EXPAND|wx.ALL, 3)

        s3.Add((20, 20), 1)
        s3.Add(self.openbt, 0, wx.EXPAND|wx.ALL, 3)
        s3.Add(self.procbt, 0, wx.EXPAND|wx.ALL, 3)
        s3.Add(self.donebt, 0, wx.EXPAND|wx.ALL, 3)

        s2.Add(s3, 0, wx.EXPAND)
        self.SetSizer(s2)
        self.Layout()

    def addRow(self, filedata):
        return self.atomDisplay.addRow(filedata)

    def setDestinations(self, dests):
        return self.atomDisplay.setDestinations(dests)

    def setData(self, listofdicts):
        self.atomDisplay.clearAll()
        for item in listofdicts:
            self.addRow(item)

    def onOpenTemp(self, evt):
        '''Probably redundant now'''
        # if sys.platform == 'linux2':
        #     subprocess.call(('xdg-open', CACHEDIR))
        # elif sys.platform == 'win32':
        #     os.startfile(CACHEDIR))
        # elif sys.platform == 'darwin':
        #     subprocess.call(('open', CACHEDIR))
        pass

            
if __name__ == "__main__":
    pass

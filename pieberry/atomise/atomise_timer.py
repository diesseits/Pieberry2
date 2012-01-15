#!/bin/python

import wx
from atomise_exec import periodic_sweep

class atomTimer(wx.Timer):
    '''timer class that updates outputList's tooltip'''
    def __init__(self, parent, *args, **kwargs):
        wx.Timer.__init__(self, *args, **kwargs)
        self._f = parent
        self.collected_data = []
 
    def Notify(self):
        self.CollectData()

    def CollectData(self):
        print 'COLLECTED', self.collected_data
        self.collected_data = periodic_sweep()

    def GetCollectedData(self):
        return self.collected_data
        

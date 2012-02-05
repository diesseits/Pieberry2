#!/bin/python

import sys, os, time
import traceback
import wx
import pprint
import shutil
import pieutility

# from atomise_exec import *
from ui.events import *
from atomise_utility import *
from atomise_window import *
from pieconfig.paths import *
from pieobject.folder import FOLDER_LOOKUP, PieFolder

class atomWidget(wx.Panel):
    '''A ui class for displaying files grabbed from the user's desktop'''

    paneltype = 'AtomPanel'

    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.__do_layout()
        self.Bind(wx.EVT_BUTTON, self.atomDisplay.onFileAll, self.procbt)
        self.donebt.Bind(wx.EVT_BUTTON, self.onCloseSelf)
        self.SetDestinations([f.name() for f in FOLDER_LOOKUP['projectdir']])
    
    def __do_layout(self):
        self.atomDisplay = atomActionWindow(self, -1)
        # self.openbt = wx.Button(self, -1, label='Open temp directory')
        self.procbt = wx.Button(self, -1, label='Process all')
        self.donebt = wx.Button(self, -1, label='Done')

        s2 = wx.BoxSizer(wx.VERTICAL)
        s3 = wx.BoxSizer(wx.HORIZONTAL)

        s2.Add(self.atomDisplay, 1, wx.EXPAND|wx.ALL, 3)

        s3.Add((20, 20), 1)
        # s3.Add(self.openbt, 0, wx.EXPAND|wx.ALL, 3)
        s3.Add(self.procbt, 0, wx.EXPAND|wx.ALL, 3)
        s3.Add(self.donebt, 0, wx.EXPAND|wx.ALL, 3)

        s2.Add(s3, 0, wx.EXPAND)
        self.SetSizer(s2)
        self.Layout()

    def AddObject(self, obj):
        return self.atomDisplay.AddObject(
            obj,
            suggested_fn=suggest_initial_fn(obj))

    def SetDestinations(self, dests):
        return self.atomDisplay.setDestinations(dests)

    def AddObjects(self, ostore):
        self.atomDisplay.clearAll()
        for obj in ostore:
            self.AddObject(obj)

    def onDelFile(self, currentrow):
        '''Delete a file in the staging area. Probably shouldn't be 
        handling this in a GUI module but hey'''
        obj = self.atomDisplay.rowdata[currentrow]
        dia = wx.MessageDialog(self, 'Delete %s?' % obj.FileData_FileName,
                               'Delete File', style=wx.YES_NO|wx.ICON_QUESTION)
        ans = dia.ShowModal()
        if ans == wx.ID_YES:
            try: 
                os.remove(obj.FileData_FullPath)
            except:
                traceback.print_exc()
                wx.MessageBox('Prevented from deleting this file')
                return
            newevt = AtomDelFileEvent(obj=obj, rowid=currentrow)
            wx.PostEvent(self, newevt) 
            self.atomDisplay.removeRow(currentrow)

    def onCreateBib(self, row):
        '''override for bib entry creation implementation'''
        pass

    def onGoFile(self, row):
        '''override for filing action implementation'''
        obj = self.atomDisplay.rowdata[row]
        ch = getattr(self.atomDisplay, 'choice%d' % self.atomDisplay.currentrow)
        if ch.GetSelection() == 0:
            wx.MessageBox('No selected destination for this file')
            return
        tc = getattr(self.atomDisplay, 'suggesttc%d' % self.atomDisplay.currentrow)
        newevt = AtomFileFileEvent(
            obj=obj, 
            rowid=row,
            dest_folder=ch.GetStringSelection(),
            new_fn=tc.GetValue(),
            notify_window=self)
        wx.PostEvent(self, newevt)

    def Callback_onGoFile(self, rowid):
        '''finish up with filing'''
        self.atomDisplay.removeRow(rowid)

    def onFileAll(self):
        pass

    def onOpenFile(self, rowid):
        pieutility.open_file(self.atomDisplay.rowdata[rowid].FileData_FullPath)

    def onFilterView(self, evt=0):
        '''Does nothing for this widget'''
        pass

    def onCloseSelf(self, evt=0):
        newevt = PieClosePaneEvent()
        wx.PostEvent(self, newevt)
            
if __name__ == "__main__":
    pass

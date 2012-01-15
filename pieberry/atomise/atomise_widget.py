#!/bin/python

import sys, os, time, subprocess
import traceback
import wx
import pprint
import shutil

from atomise_exec import *
from atomise_window import *
from pieberry.pieberry_config import *

class atomNewActionWindow(atomActionWindow):
    def __init__(self, *args, **kwargs):
        atomActionWindow.__init__(self, *args, **kwargs)

    def onGoFile(self):
        idat = self.getCurrentItemData()
        ch = getattr(self, 'choice%d' % self.currentrow)
        if ch.GetSelection() == 0:
            wx.MessageBox('No selected destination for this file')
            return
        tc = getattr(self, 'suggesttc%d' % self.currentrow)
        idat['final_fn'] = os.path.join(
            config.get('AToptions', 'filing_directory'),
            self.defaultchoices[ch.GetSelection()],
            tc.GetValue() 
            )
        print idat['final_fn']
        if os.path.exists(idat['final_fn']):
            wx.MessageBox('File already exists.', 'Error')
            return
        try:
            os.renames(
                os.path.join(
                    config.get('AToptions', 'temp_directory'),
                    idat['initial_fn']
                    ),
                idat['final_fn']
                )
        except Exception, exc:
            traceback.print_exc()
            wx.MessageBox('%s' % exc, 'Error')
            return
            
        self.removeRow(self.currentrow)

    def onFileAll(self, evt=1):
        print 'MAXROW ', self.maxrow
        for i in range(0, self.maxrow + 1):
            idat = self.rowdata[i]
            ch = getattr(self, 'choice%d' % i)
            if ch.GetSelection() == 0:
                continue
            tc = getattr(self, 'suggesttc%d' % i)
            idat['final_fn'] = os.path.join(
                config.get('AToptions', 'filing_directory'),
                self.defaultchoices[ch.GetSelection()],
                tc.GetValue() 
                )
            if os.path.exists(idat['final_fn']):
                wx.MessageBox('File already exists.', 'Error')
                continue
            try:
                os.renames(
                    os.path.join(
                        config.get('AToptions', 'temp_directory'),
                        idat['initial_fn']
                        ),
                    idat['final_fn']
                    )
            except:
                traceback.print_exc()
                continue
            self.removeRow(i)

    def onCreateBib(self, evt=1):
        pwindow = self.GetParent().GetParent().GetParent()
        pwindow.onAddFile(os.path.join(config.get('AToptions', 'temp_directory'), self.getCurrentItemData()['initial_fn']))

    def onDelFile(self, evt=1):
        idat = self.getCurrentItemData()
        dia = wx.MessageDialog(self, 'Delete %s?' % idat['initial_fn'], 'Delete file', style=wx.YES_NO|wx.ICON_QUESTION)
        ans = dia.ShowModal()
        if ans == wx.ID_YES:
            try:
                os.remove(os.path.join(config.get('AToptions', 'temp_directory'), idat['initial_fn']))
                self.removeRow(self.currentrow)
            except Exception, exc:
                traceback.print_exc()
                wx.MessageBox('Prevented from deleting this file (%s)' % unicode(exc))

    def onOpenFile(self, evt=1):
        idat = self.getCurrentItemData()
        if sys.platform == 'linux2':
            subprocess.call(('xdg-open', os.path.join(config.get('AToptions', 'temp_directory'), idat['initial_fn'])))
        elif sys.platform == 'win32':
            os.startfile(os.path.join(config.get('AToptions', 'temp_directory'), idat['initial_fn']))


class atomWidget(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.__do_layout()

        # self.Bind(wx.EVT_BUTTON, self.atomDisplay.clearAll, self.clearbt)
        self.Bind(wx.EVT_BUTTON, self.atomDisplay.onFileAll, self.procbt)

        cf = open(os.path.join(sysdir, 'criteria.pickle'), 'r')
        self.criteria = cPickle.load(cf)
        cf.close()
        self.setDestinations(self.criteria.keys())
        self.Bind(wx.EVT_BUTTON, self.onOpenTemp, self.openbt)
    
    def __do_layout(self):
        self.atomDisplay = atomNewActionWindow(self, -1)
        self.openbt = wx.Button(self, -1, label='Open temp directory')
        self.procbt = wx.Button(self, -1, label='Process all')
        # self.clearbt = wx.Button(self, -1, label='Clear all')
        self.donebt = wx.Button(self, -1, label='Done')

        s2 = wx.BoxSizer(wx.VERTICAL)
        s3 = wx.BoxSizer(wx.HORIZONTAL)

        s2.Add(self.atomDisplay, 1, wx.EXPAND|wx.ALL, 3)

        s3.Add((20, 20), 1)
        s3.Add(self.openbt, 0, wx.EXPAND|wx.ALL, 3)
        s3.Add(self.procbt, 0, wx.EXPAND|wx.ALL, 3)
        # s3.Add(self.clearbt, 0, wx.EXPAND|wx.ALL, 3)
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
        if sys.platform == 'linux2':
            subprocess.call(('xdg-open', config.get('AToptions', 'temp_directory')))
        elif sys.platform == 'win32':
            os.startfile(config.get('AToptions', 'temp_directory'))
        elif sys.platform == 'darwin':
            subprocess.call(('open', config.get('AToptions', 'temp_directory')))

            

class atomBasicFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        # _icon = wx.EmptyIcon()
        # _icon.CopyFromBitmap(wx.Bitmap(os.path.join(IMGDIR, 'pie_16.png')))
        # self.SetIcon(_icon)
        kwargs['size'] = (1000, 600)
        kwargs['title'] = 'Clean-up desktop files'
        wx.Frame.__init__(self, *args, **kwargs)
        self.atomWidget = atomWidget(self, -1)
        s1 = wx.BoxSizer(wx.VERTICAL)
        s1.Add(self.atomWidget, 1, wx.EXPAND|wx.ALL, 3)
        self.SetSizer(s1)
        self.Layout()
        self.Bind(wx.EVT_BUTTON, self.onClose, self.atomWidget.donebt)

    def onClose(self, evt):
        self.Destroy()

    def setData(self, data):
        self.atomWidget.setData(data)

if __name__ == "__main__":
    sweepdata = periodic_sweep()
    pprint.pprint( sweepdata )
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    w = atomBasicFrame()
    app.SetTopWindow(w)
    w.Show()
    w.atomWidget.setDestinations(criteria.keys())
    w.atomWidget.setData(sweepdata)
    app.MainLoop()

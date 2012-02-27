import wx
import os
from pieberry.pieconfig.paths import *

# ### For test purposes only
# if TEST:
#     IMGDIR = os.path.join(os.getcwd(), 'ui')
# ### 

PieImageList = wx.ImageList(16, 16)

PieImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_blueball16.png')))
PieImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_redsquare16.png')))
PieImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_yellowex16.png')))
PieImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_greensquare16.png')))
PieImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_greentick16.png')))
PieImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_blueex16.png')))
PieImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'al00.png')))
PieImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'al01.png')))
PieImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'al02.png')))
PieImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'al03.png')))
PieImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'al04.png')))
PieImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'al05.png')))
PieImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_pdf16.png')))
PieImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_doc16.png')))
PieImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_goldstar16.png')))

MessageType = {
    'start': 'spin',
    'spin': 6,
    'blank': None,
    'success': 0,
    'fail': 1,
    'warn': 2,
    'pass': 3,
    'tick': 4,
    'exclude': 5,
    'pdf': 12,
    'doc': 13,
    'star': 14
    }

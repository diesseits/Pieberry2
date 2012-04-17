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
PieImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_flag16.png')))
PieImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_flagstar16.png')))
PieImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_text16.png')))
PieImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_yellowball16.png')))
PieImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_redball16.png')))
PieImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_greenball16.png')))
PieImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_greenballlocked16.png')))
PieImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_greenballunlocked16.png')))
PieImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_greenballneverlocked16.png')))
PieImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_docx16.png')))
PieImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_odf16.png')))
PieImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_html16.png')))
PieImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_locked16.png')))
PieImageList.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER_OPEN, wx.ART_MENU))

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
    'star': 14,
    'flag': 15,
    'flagstar': 16,
    'text': 17,
    'blueball': 0,
    'yellowball': 18,
    'redball': 19,
    'greenball': 20,
    'locked': 21,
    'unlocked': 22,
    'neverlocked': 23,
    'docx': 24,
    'odf': 25,
    'html': 26,
    'filelocked': 27,
    'folder': 28
    }

import wx
import os, os.path

from pieberry.pieconfig.paths import IMGDIR

AtomImageList = wx.ImageList(22, 22)

AtomImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_doc22.png')))
AtomImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_docx22.png')))
AtomImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_pdf22.png')))
AtomImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_text22.png')))
AtomImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_html22.png')))
AtomImageList.Add(wx.Bitmap(os.path.join(IMGDIR, 'ic_odf22.png')))

IconType = {
    'doc': 0,
    'docx': 1,
    'oxml_doc': 1,
    'pdf': 2,
    'text': 3,
    'plaintext': 3,
    'html': 4,
    'odf': 5
    }



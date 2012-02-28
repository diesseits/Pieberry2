import pieberry.pieutility
import os, os.path, wx
import traceback

from pieberry.ui.editdialog import PieBibEditDialog
from pieberry.ui.events import EVT_PIE_BIB_EDIT

from pieberry.pieconfig.identity import PIE_APPNAME
from pieberry.pieconfig.paths import IMGDIR
from pieberry.pieconfig.globalvars import PYNOTIFY
from pieberry.pieoutput.bibtex import *

if PYNOTIFY:
    import pynotify

class MenuFunctionsMixin:
    '''Set of generic functions for context menu operations in listwindows'''
    def __init__(self):
        pass
    
    def onOpenInBrowser(self, evt):
        obj = self.GetSelectedItem()
        # obj = self.objectstore[self._last_item_right_clicked]
        assert hasattr(obj, 'WebData_Url')
        pieberry.pieutility.open_web_file(obj.WebData_Url)
        obj.stats_opened()
        
    def onOpenFile(self, evt):
        obj = self.GetSelectedItem()
        # obj = self.objectstore[self._last_item_right_clicked]
        assert hasattr(obj, 'FileData_FullPath')
        pieberry.pieutility.open_file(obj.FileData_FullPath)
        obj.stats_opened()

    def onOpenContainingFolder(self, evt):
        obj = self.GetSelectedItem()
        assert hasattr(obj, 'FileData_FullPath')
        pieberry.pieutility.open_file(obj.FileData_ContainingFolder)

    def onDeleteOnDisk(self, evt):
        # obj = self.objectstore[self._last_item_right_clicked]
        obj = self.GetSelectedItem()
        assert hasattr(obj, 'FileData_FullPath')
        print 'deleting', obj.FileData_FullPath
        try:
            os.remove(obj.FileData_FullPath)
        except:
            traceback.print_exc()
            wx.MessageBox(_('Could not delete file - do you have it open?'), 
                       style=wx.ICON_ERROR)
            return
        self.objectstore.Del(self.GetSelectedItemRef())
        self.ListDisplay.DeleteItem(self.ListDisplay.currentitem)
        #TODO implement deletion from database
        
    def onNotImplemented(self, evt):
        wx.MessageBox(_('Function not implemented.'))
        
    def onEditBibData(self, evt):
        print 'onEditBibData'
        obj = self.GetSelectedItem()
        # NB: segfaults if we make the parent this window
        edwin = PieBibEditDialog(obj, self.GetParent().GetParent())
        edwin.Bind(
            EVT_PIE_BIB_EDIT, self.onEditedBibData)
        res = edwin.ShowModal()
        if res == wx.ID_OK:
            pass
        if res == wx.ID_CANCEL:
            pass

    def onEditedBibData(self, evt):
        self.GetParent().GetParent().OnEditedBibData(evt)

    def onEditNotes(self, evt):
        obj = self.GetSelectedItem()
        self.GetParent().GetParent().OpenNotesPane(obj=obj)

    def onCopyCitation_PlainText(self, evt):
        print 'onCopyCitiation_PlainText'
        obj = self.GetSelectedItem()
        fmt = PIE_CONFIG.get('Format', 'plaintext_citation_format')
        try:
            bobj = get_pybtex_object(obj)
            cite = get_formatted_citation(bobj, format=fmt)
        except Exception, exc:
            traceback.print_exc()
            wx.MessageBox(unicode(exc), "Error")
            return
        clipdata = wx.TextDataObject()
        clipdata.SetText(cite)        
        if PYNOTIFY:
            n = pynotify.Notification(
                _("Citation"), 
                cite, 
                os.path.join(IMGDIR, 'pie_48.png'))
            n.show()
        else:
            print cite
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(clipdata)
        wx.TheClipboard.Close()

    def onCopyCitation_RichText(self, evt):
        print 'onCopyCitiation_PlainText'
        obj = self.GetSelectedItem()
        try:
            bobj = get_pybtex_object(obj)
            cite = get_formatted_citation(
                bobj, 
                format=PIE_CONFIG.get('Format', 'richtext_citation_format'))
        except Exception, exc:
            traceback.print_exc()
            wx.MessageBox(unicode(exc), "Error")
            return
        clipdata = wx.TextDataObject()
        clipdata.SetText(cite)        
        if PYNOTIFY:
            n = pynotify.Notification(
                "Citation", 
                get_formatted_citation(bobj, format='plaintext'),
                os.path.join(IMGDIR, 'pie_48.png'))
            n.show()
        else:
            print cite
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(clipdata)
        wx.TheClipboard.Close()

    def onCopyCitation_OrgText(self, evt):
        print 'onCopyCitiation_PlainText'
        obj = self.GetSelectedItem()
        try:
            bobj = get_pybtex_object(obj)
            cite = get_formatted_citation(bobj, format='org')
        except Exception, exc:
            traceback.print_exc()
            wx.MessageBox(unicode(exc), "Error")
            return
        clipdata = wx.TextDataObject()
        clipdata.SetText(cite)        
        if PYNOTIFY:
            n = pynotify.Notification(
                "Citation", 
                get_formatted_citation(bobj, format='plaintext'),
                os.path.join(IMGDIR, 'pie_48.png'))
            n.show()
        else:
            print cite
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(clipdata)
        wx.TheClipboard.Close()

    def onCopyUrl(self, evt):
        obj = self.GetSelectedItem()
        clipdata = wx.TextDataObject()
        clipdata.SetText(obj.Url())        
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(clipdata)
        wx.TheClipboard.Close()

    def onCopyBibTeXKey(self, evt):
        obj = self.GetSelectedItem()
        clipdata = wx.TextDataObject()
        clipdata.SetText(obj.BibData_Key)        
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(clipdata)
        wx.TheClipboard.Close()
        


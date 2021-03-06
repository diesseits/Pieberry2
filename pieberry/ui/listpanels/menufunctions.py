import pieberry.pieutility
import os, os.path, wx, sys, shutil
import traceback

from pieberry.pieobject import *
from pieberry.pieobject.paths import *
from pieberry.pieobject.folder import contribute_folder
from pieberry.piefiles.encryption import *
from pieberry.ui.editdialog import PieBibEditDialog
from pieberry.ui.events import *
from pieberry.ui.htmldataobject import HTMLDataObject
from pieberry.ui.validators import PiePlainTextValidator

from pieberry.pieconfig.identity import PIE_APPNAME
from pieberry.pieconfig.paths import IMGDIR
from pieberry.pieconfig.globalvars import PYNOTIFY
from pieberry.pieoutput.bibtex import *
from pieberry.pieoutput.pieslice import *
from pieberry.pieutility.decoding import translate_non_alphanumerics

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
        if obj.aspects['encrypted'] == EC_TRUE_LOCKED:
            # get md5 hash of user password from config
            enckey = PIE_CONFIG.get('Security', 'file_key')
            if enckey == None: 
                wx.MessageBox(_('You have not set a password yet'), _('Error'))
                return
            # test whether that's the correct key for this Pieberry archive
            if not PIE_INTERNALS.verify_encryption_hash(enckey):
                wx.MessageBox(_("You don't have the right password"), _('Error'))
                return
            decrypt_file(
                enckey,
                obj.FileData_FullPath,
                decrypted_path(obj))
            fp = decrypted_path(obj)
            obj.aspects['encrypted'] = EC_TRUE_UNLOCKED
            self.UpdateObject(obj)
        elif obj.aspects['encrypted'] == EC_TRUE_UNLOCKED:
            fp = decrypted_path(obj)
        else:
            fp = obj.FileData_FullPath
        pieberry.pieutility.open_file(fp)
        obj.stats_opened()

    def onReEncrypt(self, evt):
        '''Re-encrypt (lock) a file that is encrypted but opened
        (decrypted) in the decrypted files cache'''
        obj = self.GetSelectedItem()
        tmpfile = os.path.join(obj.FileData_ContainingFolder,
                               u're-enc.tmp')
        # get md5 hash of user password from config
        enckey = PIE_CONFIG.get('Security', 'file_key')
        if enckey == None: 
            wx.MessageBox(_('You have not set a password yet'), _('Error'))
            return
        # test whether that's the correct key for this Pieberry archive
        if not PIE_INTERNALS.verify_encryption_hash(enckey):
            wx.MessageBox(_("You don't have the right password"), _('Error'))
            return
        try:
            encrypt_file(enckey, 
                         decrypted_path(obj),
                         tmpfile)
            os.remove(obj.FileData_FullPath)
            os.rename(tmpfile, obj.FileData_FullPath)
            os.remove(decrypted_path(obj))
        except Exception, exc:
            wx.MessageBox(unicode(exc), _('Error'))
            try:
                os.remove(tmpfile)
            except: pass
            return
        obj.aspects['encrypted'] = EC_TRUE_LOCKED
        self.UpdateObject(obj)

    def onOpenContainingFolder(self, evt):
        obj = self.GetSelectedItem()
        assert hasattr(obj, 'FileData_FullPath')
        pieberry.pieutility.open_file(obj.FileData_ContainingFolder)

    def onDeleteObj(self, evt):
        '''Delete an object. Special handling for library documents -
        the first time delete is called on an object which has a file
        in the library directory, only the file will be deleted, not
        the database object. The user must delete it again to remove
        the database object. This is because the user may still want
        the bibliographic information for the deleted document.'''
        # obj = self.objectstore[self._last_item_right_clicked]
        obj = self.GetSelectedItem()
        if obj.has_aspect('hasfile') and obj.FileData_Root == 'librarydir':
            islib = True
            msg = _('Do you want to delete this document? The file on disk will be deleted but the database entry will not.')
        elif obj.has_aspect('hasfile'):
            islib = False
            msg = _('Do you want to delete this document? Both the file on disk and the database entry will be deleted.')
        else:
            islib = False
            msg = _('Do you want to delete this document? The database entry will be deleted.')
        dia = wx.MessageDialog(self, msg, style=wx.YES|wx.NO|wx.NO_DEFAULT)
        ans = dia.ShowModal()
        if not ans == wx.ID_YES: return
        if obj.has_aspect('hasfile'):
            print 'deleting', obj.FileData_FullPath
            try:
                if obj.aspects['encrypted'] == EC_TRUE_UNLOCKED:
                    os.remove(decrypted_path(obj))
                if os.path.isdir(obj.FileData_FullPath):
                    shutil.rmtree(obj.FileData_FullPath)
                else:
                    os.remove(obj.FileData_FullPath)
                obj.clear_file()
            except:
                traceback.print_exc()
                wx.MessageBox(_('Could not delete file - do you have it open?'), 
                              style=wx.ICON_ERROR)
                return
        if not islib:
            self.objectstore.Del(self.GetSelectedItemRef())
            self.ListDisplay.DeleteItem(self.ListDisplay.currentitem)
            from pieberry.functionwindow import session
            session.delete(obj)
            session.commit()

    def onRenameFile(self, evt):
        obj = self.GetSelectedItem()
        if obj.aspects['encrypted'] == EC_TRUE_UNLOCKED:
            wx.MessageBox(_('Can\'t rename encrypted files in use'))
            return
        fn = obj.FileData_FileName
        dia = wx.TextEntryDialog(
            self, _('New filename:'), _('Rename file'), defaultValue=fn)
        # txtCtrl = dia.FindWindowById(3000) # text entry dialog id
        # txtCtrl.Validator = PiePlainTextValidator()
        ans = dia.ShowModal()
        if ans == wx.ID_CANCEL: return
        newpath = os.path.join(
            obj.FileData_ContainingFolder, 
            translate_non_alphanumerics(dia.GetValue()))
        try: 
            os.rename(obj.FileData_FullPath, newpath)
        except Exception, exc:
            wx.MessageBox(unicode(exc), 'Error')
            return
        obj.set_file(newpath)
        self.UpdateObject(obj)
        
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
        obj.stats_opened()
        self.GetParent().GetParent().OpenNotesPane(obj=obj)

    def onFlagFavourite(self, evt=0):
        obj = self.GetSelectedItem()
        newevt = PieFlagCheckedEvent(flagkey='StatData_Favourite',
                                     flagval=evt.Checked(),
                                     obj=obj)
        wx.PostEvent(self, newevt)
        self.ListDisplay.SetFocus()

    def onFlagFollowUp(self, evt=0):
        print 'ee'
        obj = self.GetSelectedItem()
        newevt = PieFlagCheckedEvent(flagkey='StatData_FollowUpFlag',
                                     flagval=evt.Checked(),
                                     obj=obj)
        wx.PostEvent(self, newevt)
        self.ListDisplay.SetFocus()

    def onCopyCitation_PlainText(self, evt):
        print 'onCopyCitiation_PlainText'
        obj = self.GetSelectedItem()
        fmt = PIE_CONFIG.get('Format', 'plaintext_citation_format')
        try:
            bobj = get_pybtex_object(obj, texify=False)
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
        if sys.platform == 'win32':
            clipdata = HTMLDataObject()
            clipdata.SetValue(cite)
        else:
            clipdata = wx.TextDataObject()
            clipdata.SetText(cite)
            fmt = wx.DataFormat(wx.DF_INVALID)
            fmt.SetId('text/html')
            clipdata.SetFormat(fmt)
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
            bobj = get_pybtex_object(obj, texify=False)
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
        if PYNOTIFY:
            n = pynotify.Notification(
                "BibTeX Key", 
                obj.BibData_Key,
                os.path.join(IMGDIR, 'pie_48.png'))
            n.show()
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(clipdata)
        wx.TheClipboard.Close()

    def onCopyPieSlice(self, evt):
        '''Make available a pieslice glob file to the clipboard'''
        obj = self.GetSelectedItem()
        pieslice = PieSlice(obj = obj)
        clipdata = wx.FileDataObject()
        clipdata.AddFile(pieslice.GetSlice())
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(clipdata)
        wx.TheClipboard.Close()
        if PYNOTIFY:
            n = pynotify.Notification(
                _("Exported file to clipboard"), 
                pieslice.GetSlice(), 
                os.path.join(IMGDIR, 'pie_48.png'))
            n.show()


    def onAttachFile(self, evt):
        '''Attach a file to a record (at the staging point)'''
        obj = self.GetSelectedItem()
        if obj.has_aspect('hasfile'):
            print 'Warning: object already has a file'
            return
        fdia = wx.FileDialog(self, message="Select file to attach to record", wildcard="Known file types (*.pdf;*.doc;*.docx;*.txt;*.xls;*.xlsx;*.ppt;*.pptx;*.odf;*.ods;*.odp)|*.pdf;*.doc;*.docx;*.txt;*.xls;*.xlsx;*.ppt;*.pptx;*.odf;*.ods;*.odp|All files (*.*)|*.*", style=wx.FD_OPEN, defaultDir=PIE_CONFIG.get('Profile', 'rootdir'))
        res = fdia.ShowModal()
        if res == wx.ID_CANCEL: return
        fpath = fdia.GetPath()
        assert os.path.exists(fpath)
        if not hasattr(obj, 'session'):
            obj.set_session(get_session())
        dpath, components = suggest_path_cache_fromother(obj, fpath)
        contribute_folder(os.path.dirname(dpath), components)
        shutil.copyfile(fpath, dpath)
        obj.add_aspect_cached(dpath)
        print obj.FileData_FullPath
        print obj.aspects
        print 'onAttachFile: success'


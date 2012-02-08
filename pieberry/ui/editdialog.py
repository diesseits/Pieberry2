import wx
import datetime, time

from pprint import pprint
from ui.validators import *
from ui.events import PieBibEditEvent

from pieconfig.schemas import *
from pieutility.date import wxdate2pydate
from pieutility.bibtex import *
from pieobject.database import Session

class PieFieldPanel(wx.ScrolledWindow):
    def __init__(self, parent, entry_type, fieldlist):
        '''initialise with a string for the type of entry in question,
        and a tuple containing two tuples - (1) strings representing
        compulsory fields for that article type and (2) representing
        optional fields.'''
        wx.ScrolledWindow.__init__(self, parent)
        sizer1 = wx.FlexGridSizer(0, 2, 3, 3)
        sizer1.AddGrowableCol(1)

        # Compulsory fields
        for opt_field in fieldlist[0]:
            # Create a label and control dynamically
            setattr(self, 
                    '%sLabel' % opt_field, 
                    wx.StaticText(self, -1, opt_field.capitalize() + ':'))
            setattr(self, 
                    '%sCtrl' % opt_field, 
                    wx.TextCtrl(self, -1, style=wx.EXPAND, 
                                validator=pieBibtexValidator(compulsory=True)))
            a = getattr(self, '%sCtrl' % opt_field)
            a.Bind(wx.EVT_TEXT, 
                   parent.GetParent().GetParent().onFieldValidate)
            # Add to sizer
            sizer1.Add(getattr(self, '%sLabel' % opt_field), 0, wx.EXPAND)
            sizer1.Add(a, 1, wx.EXPAND)

        # Optional fields
        for opt_field in fieldlist[1]:
            setattr(self, 
                    '%sLabel' % opt_field, 
                    wx.StaticText(self, -1, opt_field.capitalize() + ':'))
            setattr(self, 
                    '%sCtrl' % opt_field, 
                    wx.TextCtrl(self, -1, style=wx.EXPAND, 
                                validator=pieBibtexValidator(compulsory=False)))
            a = getattr(self, '%sCtrl' % opt_field)
            a.SetBackgroundColour('yellow')
            a.Bind(wx.EVT_TEXT, parent.GetParent().GetParent().onFieldValidate)
            sizer1.Add(getattr(self, '%sLabel' % opt_field), 0, wx.EXPAND)
            sizer1.Add(a, 1, wx.EXPAND)

        self.SetSizer(sizer1)
        self.entry_type = entry_type
        self.SetScrollbars(0, 20, 0, 50)
        self.fieldlist = fieldlist

    def getData(self):
        ret = {}
        for it in self.fieldlist[0]:
            f = getattr(self, '%sCtrl' % it)
            if not f.GetValidator().Validate():
                raise Exception, 'Value in %s is inappropriate for BibTeX' % it
            ret[bibtexmap[it]] = f.GetValue()
        for it in self.fieldlist[1]:
            f = getattr(self, '%sCtrl' % it)
            if not f.GetValidator().Validate():
                raise Exception, 'Value in %s is inappropriate for BibTeX' % it
            if len(f.GetValue()) > 0:
                ret[bibtexmap[it]] = f.GetValue()
        return self.entry_type, ret

    def setData(self, data):
        for it, val in data.items():
            f = getattr(self, '%sCtrl' % it, None)
            if f and val:
                f.SetValue(val)



class PieBibEditDialog(wx.Dialog):
    '''A multifunction dialog for editing bibliographic data associated with 
    database items'''
    def __init__(self, obj, *args, **kwargs):
        kwargs['style'] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwargs)

        # Panels
        self.panelx = wx.Panel(self, -1)

        # Principal Controls
        self.keyCtrl = wx.TextCtrl(
            self.panelx, -1, "", validator=pieBibtexValidator(compulsory=True))
        self.keyAutoCb = wx.CheckBox(self.panelx, -1, label="Auto-generate")
        self.authorIsCorporateCb = wx.CheckBox(
            self.panelx, -1, label="Author is corporate entity")
        self.authorCtrl = wx.TextCtrl(
            self.panelx, -1, "", style=wx.TE_PROCESS_ENTER, 
            validator=pieBibtexValidator(compulsory=True))
        self.authorSwapButton = wx.BitmapButton(
            self.panelx, -1, 
            wx.ArtProvider.GetBitmap(wx.ART_GO_BACK, wx.ART_TOOLBAR, (16, 16)))
        self.authorAltCtrl = wx.TextCtrl(
            self.panelx, -1, "", style=wx.TE_READONLY)
        self.titleCtrl = wx.TextCtrl(
            self.panelx, -1, "", style=wx.TE_PROCESS_ENTER|wx.EXPAND, 
            validator=pieBibtexValidator(compulsory=True))
        self.titleSwapButton = wx.BitmapButton(
            self.panelx, -1, 
            wx.ArtProvider.GetBitmap(wx.ART_GO_BACK, wx.ART_TOOLBAR, (16, 16)))
        self.titleAltCtrl = wx.TextCtrl(
            self.panelx, -1, "", style=wx.TE_READONLY)
        self.datePicker = wx.DatePickerCtrl(self.panelx, -1)

        
        # Dialog controls

        self.btCancel = wx.Button(self.panelx, wx.ID_CANCEL, "Cancel")
        self.btOk = wx.Button(self.panelx, -1, "Ok")

        # The dynamic panel - construction
        self.choiceBook = wx.Choicebook(self.panelx, -1)
        self.panelref = []
        for k, v in bibtexfields.items():
            pan = PieFieldPanel(self.choiceBook, k, v)
            self.choiceBook.AddPage(pan, k.capitalize())
            self.panelref.append(k)

        # Finish initialisation

        self.__set_properties()
        self.__do_layout()
        self.__fill_fields(obj)
        self.__do_bindings()

    def __do_bindings(self):
        self.Bind(wx.EVT_BUTTON, self.onCancel, self.btCancel)
        self.Bind(wx.EVT_BUTTON, self.onOk, self.btOk)
        self.authorCtrl.Bind(wx.EVT_TEXT_ENTER, self.onOk)
        self.authorCtrl.Bind(wx.EVT_TEXT, self.onFieldValidate)
        self.titleCtrl.Bind(wx.EVT_TEXT_ENTER, self.onOk)
        self.titleCtrl.Bind(wx.EVT_TEXT, self.onFieldValidate)
        self.keyCtrl.Bind(wx.EVT_TEXT, self.onFieldValidate)
        self.keyAutoCb.Bind(wx.EVT_CHECKBOX, self.onKeygenToggle)
        self.authorSwapButton.Bind(wx.EVT_BUTTON, self.onAuthorSwap)
        self.titleSwapButton.Bind(wx.EVT_BUTTON, self.onTitleSwap)

    def __set_properties(self):
        self.SetTitle("Edit Bibliography Entry")
        self.SetSize((547, 558))

    def __do_layout(self):
        sizer1 = wx.BoxSizer(wx.VERTICAL)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer3 = wx.BoxSizer(wx.VERTICAL)
        sizer4 = wx.BoxSizer(wx.VERTICAL)

        sizerA = wx.BoxSizer(wx.HORIZONTAL)
        sizerB = wx.BoxSizer(wx.HORIZONTAL)
        sizerC = wx.BoxSizer(wx.HORIZONTAL)
        sizerD = wx.BoxSizer(wx.HORIZONTAL)
        sizerE = wx.BoxSizer(wx.HORIZONTAL)
        sizerF = wx.BoxSizer(wx.HORIZONTAL)


        sizerE.Add(self.keyCtrl, 1, wx.ALL, 3)
        sizerE.Add((22,22), 0, wx.ALL, 3)
        sizerE.Add(self.keyAutoCb, 1, wx.ALL, 3)

        sizerC.Add(wx.StaticText(self.panelx, -1, 'Author:'), 1, wx.ALL, 3)
        sizerC.Add((22,22), 0, wx.ALL, 3)
        sizerC.Add(self.authorIsCorporateCb, 1, wx.ALL, 3)

        sizerA.Add(self.authorCtrl, 1, wx.ALL, 3)
        sizerA.Add(self.authorSwapButton, 0, wx.ALL, 3)
        sizerA.Add(self.authorAltCtrl, 1, wx.ALL, 3)

        sizerB.Add(self.titleCtrl, 1, wx.ALL, 3)
        sizerB.Add(self.titleSwapButton, 0, wx.ALL, 3)
        sizerB.Add(self.titleAltCtrl, 1, wx.ALL, 3)

        sizerD.Add(wx.StaticText(
                self.panelx, -1, 'Date of publication:'), 1, wx.ALL, 3)
        sizerD.Add((22,22), 0, wx.ALL, 3)
        sizerD.Add(self.datePicker, 1, wx.ALL, 3)

        sizerF.Add((20, 20), 3, wx.EXPAND, 0)
        sizerF.Add(self.btCancel, 0, wx.ALL, 3)
        sizerF.Add(self.btOk, 0, wx.ALL, 3)

        sizer1.Add(wx.StaticText(self.panelx, -1, 'BibTeX key:'), 0, wx.ALL, 3)
        sizer1.Add(sizerE, 0, wx.EXPAND)
        sizer1.Add(sizerC, 0, wx.EXPAND)
        sizer1.Add(sizerA, 0, wx.EXPAND)
        sizer1.Add(wx.StaticText(self.panelx, -1, 'Title:'), 0, wx.ALL, 3)
        sizer1.Add(sizerB, 0, wx.EXPAND)
        sizer1.Add(sizerD, 0, wx.EXPAND)
        sizer2.Add(self.choiceBook, 1, wx.ALL|wx.EXPAND, 3)

        sizer3.Add(sizer1, 0, wx.EXPAND)
        sizer3.Add(sizer2, 1, wx.EXPAND)
        sizer3.Add(sizerF, 0, wx.EXPAND)
        self.panelx.SetSizer(sizer3)
        self.panelx.Layout()
        
        sizer4.Add(self.panelx, 1, wx.EXPAND)
        
        self.SetSizer(sizer4)
        self.Layout()
        self.Refresh()

    def __fill_fields(self, obj):
        '''Preload data'''
        self.obj = obj
        if obj.BibData_Key:
            self.keyAutoCb.SetValue(False)
            self.keyCtrl.SetValue(obj.BibData_Key)
        else:
            self.keyAutoCb.SetValue(True)
            self.keyCtrl.SetValue('Autogen')#autogen_bibtex_key(bibdata))
            self.keyCtrl.Enable(False)
        if obj.BibData_Type:
            self.choiceBook.ChangeSelection(
                self.panelref.index(obj.BibData_Type.lower()))
        self.authorCtrl.SetValue(obj.Author())
        if obj.AuthorIsCorporate():
            self.authorIsCorporateCb.SetValue(wx.CHK_CHECKED)
        if obj.filemetadata.has_key('author'):
            self.authorAltCtrl.SetValue(obj.filemetadata['author'])
        self.titleCtrl.SetValue(obj.Title())
        if obj.filemetadata.has_key('title'):
            self.titleAltCtrl.SetValue(obj.filemetadata['title'])
        self.datePicker.SetValue(
            wx.DateTimeFromTimeT(time.mktime(obj.ReferDate().timetuple())))
        self.authorCtrl.SetFocus()
        
        bibdata = {}
        for bibtexkey, objkey in bibtexmap.items():
            bibdata[bibtexkey] = getattr(obj, objkey)
        self.choiceBook.GetCurrentPage().setData(bibdata)
        
# datetime.datetime.fromtimestamp(wx.DateTime.Now().GetTicks())
# wx.DateTimeFromTimeT(time.mktime(datetime.datetime.now().timetuple())) 

    def onKeygenToggle(self, evt):
        if self.keyAutoCb.IsChecked():
            self.keyCtrl.Enable(False)
        else:
            self.keyCtrl.Enable(True)

    def getData(self):
        # return self._bibdata
        pass
    
    def onOk(self, evt=1):
        for ctrl in (self.keyCtrl, self.authorCtrl, self.titleCtrl):
            if not ctrl.GetValidator().Validate():
                wx.MessageBox(
                    '''One or more of these fields has problematic
                    syntax for BibTeX - please remedy'''
                    )
                return
        ret = {}
        ret['title'] = self.titleCtrl.GetValue()
        ret['BibData_DatePublished'] = wxdate2pydate(
            self.datePicker.GetValue())
        if not self.keyAutoCb.IsChecked():
            ret['BibData_Key'] = self.keyCtrl.GetValue()
        else:
            ret['BibData_Key'] = None
        if self.authorIsCorporateCb.IsChecked() == True:
            ret['corpauthor'] = self.authorCtrl.GetValue()
            ret['author'] = None
        else:
            ret['author'] = self.authorCtrl.GetValue()
        cbp = self.choiceBook.GetCurrentPage()
        try:
            et, moredata = cbp.getData()
        except Exception, exc:
            wx.MessageBox(unicode(exc))
            return
        ret['BibData_Type'] = et
        ret.update(moredata)
        self.obj.add_aspect_bibdata(**ret)
        newevt = PieBibEditEvent(obj=self.obj)
        wx.PostEvent(self, newevt)
        self.EndModal(wx.ID_OK)

    def onCancel(self, evt=1):
        self.EndModal(wx.ID_CANCEL)

    def onTitleSwap(self, evt):
        t = self.titleCtrl.GetValue()
        self.titleCtrl.SetValue(self.titleAltCtrl.GetValue())
        self.titleAltCtrl.SetValue(t)

    def onAuthorSwap(self, evt):
        t = self.authorCtrl.GetValue()
        self.authorCtrl.SetValue(self.authorAltCtrl.GetValue())
        self.authorAltCtrl.SetValue(t)

    def onFieldValidate(self, evt):
        obj = evt.GetEventObject()
        obj.GetValidator().Validate()

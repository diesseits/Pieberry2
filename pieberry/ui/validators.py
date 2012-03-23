### Validators for text inputs
import wx, re, string

class pieUrlValidator(wx.PyValidator):
     """ This validator is used to ensure that the user has entered something
         into the text object editor dialog's text field.
     """
     def __init__(self):
         """ Standard constructor.
         """
         wx.PyValidator.__init__(self)
         # self.regexp = re.compile(r'^http://', re.IGNORECASE)
         self.regexp_long = re.compile("([0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}|(((news|telnet|nttp|file|http|ftp|https)://)|(www|ftp)[-A-Za-z0-9]*\\.)[-A-Za-z0-9\\.]+)(:[0-9]*)?/*[-A-Za-z0-9_\\$\\.\\+\\!\\*\\(\\),;:@&=\\?/~\\#\\%]*[^]'\\.}>\\),\\\"]")
         self.regexp_short = re.compile("([0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}|(((news|telnet|nttp|file|http|ftp|https)://)|(www|ftp)[-A-Za-z0-9]*\\.)[-A-Za-z0-9\\.]+)(:[0-9]*)?")
         self.invalid_urls = []

     def Clone(self):
         """ Standard cloner.
             Note that every validator must implement the Clone() method.
         """
         return pieUrlValidator()

     def AddInvalidUrl(self, url):
          if not url in self.invalid_urls:
               self.invalid_urls.append(url)

     def inValidate(self):
         textCtrl = self.GetWindow()
         textCtrl.SetBackgroundColour("pink")
         textCtrl.SetFocus()
         textCtrl.Refresh()

     def Validate(self, win=None):
         """ Validate the contents of the given text control.
         """
         textCtrl = self.GetWindow()
         text = textCtrl.GetValue()
         if len(text) == 0:
              self.inValidate()
              return False
         if text in self.invalid_urls:
              self.inValidate()
              return False
         elif self.regexp_long.match(text) is None:
              self.inValidate()
              return False
         else:
              textCtrl.SetBackgroundColour(
                   wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
              textCtrl.Refresh()
              return True

     def TransferToWindow(self):
         """ Transfer data from validator to window.

             The default implementation returns False, indicating that an error
             occurred.  We simply return True, as we don't do any data transfer.
         """
         return True # Prevent wxDialog from complaining.

     def TransferFromWindow(self):
         """ Transfer data from window to validator.

             The default implementation returns False, indicating that an error
             occurred.  We simply return True, as we don't do any data transfer.
         """
         return True # Prevent wxDialog from complaining.

class PiePlainTextValidator(wx.PyValidator):
     def __init__(self):
         wx.PyValidator.__init__(self)
         self.invalidchars = (':', ';', '/', '\\', '>', '<', '|', '@', '!', '*', '^', '`')

     def Clone(self):
         return PiePlainTextValidator()

     def Validate(self, win=None):
         """ Validate the contents of the given text control.
         """
         textCtrl = self.GetWindow()
         text = textCtrl.GetValue()
         for ch in self.invalidchars:
             if ch in text: 
                 textCtrl.SetBackgroundColour("pink")
                 textCtrl.SetFocus()
                 textCtrl.Refresh()
                 return False
         textCtrl.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
         textCtrl.Refresh()
         return True

     def TransferToWindow(self):
         return True # Prevent wxDialog from complaining.

     def TransferFromWindow(self):
         return True # Prevent wxDialog from complaining.

     def OnChar(self, evt):
          pass

class pieBibtexValidator(wx.PyValidator):
     def __init__(self, compulsory=False):
         wx.PyValidator.__init__(self)
         self.invalidchars = (r'#', r'$', r'%', r'&') # , r'_') #, '{', '}'
         self.valid_escapes = (r'\#', r'\$', r'\%', r'\&') # , r'\_')
         self.compulsory = compulsory
         # self.re_invalidchars = re.compile()
     def Clone(self):
         return pieBibtexValidator(compulsory=self.compulsory)

     def Validate(self, win=None):
         """ Validate the contents of the given text control.
         """
         textCtrl = self.GetWindow()
         text = textCtrl.GetValue()
         fbrack = text.count('{')
         rbrack = text.count('}')
         if fbrack != rbrack:
              textCtrl.SetBackgroundColour("pink")
              return False
         if len(text) == 0 and self.compulsory == True:
              textCtrl.SetBackgroundColour("pink")
              return False
         # unescaped chars are no longer detected ... this is done automatically
         # at the time of saving. 
         # still look for unbalanced brackets though
         # for ch in self.valid_escapes:
         #      text = string.replace(text, ch, '')
         # for ch in self.invalidchars:
         #     if ch in text: 
         #         textCtrl.SetBackgroundColour("lightblue")
         #         # textCtrl.SetFocus()
         #         # textCtrl.Refresh()
         #         return False
         if self.compulsory:
              textCtrl.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
         else:
              textCtrl.SetBackgroundColour("yellow")
         textCtrl.Refresh()
         return True

     def TransferToWindow(self):
         return True # Prevent wxDialog from complaining.

     def TransferFromWindow(self):
         return True # Prevent wxDialog from complaining.


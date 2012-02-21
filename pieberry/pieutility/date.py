import wx, datetime

def wxdate2pydate(date): 
     assert isinstance(date, wx.DateTime) 
     if date.IsValid(): 
         ymd = map(int, date.FormatISODate().split('-')) 
         return datetime.date(*ymd) 
     else: 
         return None 


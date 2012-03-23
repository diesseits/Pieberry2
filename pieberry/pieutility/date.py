import wx, datetime

def wxdate2pydate(date): 
     assert isinstance(date, wx.DateTime) 
     if date.IsValid(): 
         ymd = map(int, date.FormatISODate().split('-')) 
         return datetime.date(*ymd) 
     else: 
         return None 

def pydate2wxdate(date):
     assert isinstance(date, (datetime.datetime, datetime.date))
     tt = date.timetuple()
     dmy = (tt[2], tt[1]-1, tt[0])
     return wx.DateTimeFromDMY(*dmy) 

def fmtdate(date):
    '''Hack for ui - work around the fact that datetime's strftime
    shits itself at dates prior to 1900'''
    d = str(date.day) if date.day > 9 else '0%d' % date.day
    m = str(date.month) if date.month > 9 else '0%d' % date.month
    return '%d-%s-%s' % (date.year, m, d)


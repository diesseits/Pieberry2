# utility functions to help get various things in unproblematic formats
import wx, time, string, re, locale
from htmlentitydefs import name2codepoint as n2cp

def filesystem_decode(st):
    '''try to read a file name to unicode. Generally these are either
    utf-8 or ANSI'''
    if type(st) == unicode:
        return st
    try:
        return st.decode(locale.getpreferredencoding())
    except:
        pass
    try:
        return st.decode('utf-8')
    except:
        pass
    try:
        return st.decode('iso-8859-1')
    except:
        raise UnicodeDecodeError, 'decode failed in filesystem_decode'

def wxdate2pydate(date): 
     import datetime 
     assert isinstance(date, wx.DateTime) 
     if date.IsValid(): 
         ymd = map(int, date.FormatISODate().split('-')) 
         return datetime.date(*ymd) 
     else: 
         return None 

def substitute_entity(match):
    ent = match.group(2)
    if match.group(1) == "#":
        return unichr(int(ent))
    else:
        cp = n2cp.get(ent)

        if cp:
            return unichr(cp)
        else:
            return match.group()

def decode_htmlentities(string):
    entity_re = re.compile("&(#?)(\d{1,5}|\w{1,8});")
    return entity_re.subn(substitute_entity, string)[0]

def translate_non_alphanumerics(to_translate, translate_to=u'_'):
    not_letters_or_digits = u'!"#%\'()*+,-./:;<=>?@[\]^_`{|}~'
    if isinstance(to_translate, unicode):
        translate_table = dict((ord(char), unicode(translate_to))
                               for char in not_letters_or_digits)
    else:
        assert isinstance(to_translate, str)
        translate_table = string.maketrans(not_letters_or_digits,
                                           translate_to
                                              *len(not_letters_or_digits))
    # split & join whitespace to ensure that we only have single spacing
    return string.join(to_translate.translate(translate_table).split()) 



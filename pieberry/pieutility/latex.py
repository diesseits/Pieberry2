import string, re

def escape_bad_latex_chars(texstring):
    '''ensure that LaTeX-unsafe characters are escaped'''
    invalidchars = (r'#', r'$', r'%', r'&', r'_') #, '{', '}'
    valid_escapes = (r'\#', r'\$', r'\%', r'\&', r'\_')
    replace_chars = ('LATEXHASH', 'LATEXDOLLAR', 'LATEXPERCENT', 'LATEXAMPERSAND', 'LATEXUNDERSCORE')
    for k in range(len(invalidchars)):
        ch = valid_escapes[k]
        texstring = string.replace(texstring, ch, replace_chars[k])
    for k in range(len(invalidchars)):
        ch = invalidchars[k]
        texstring = string.replace(texstring, ch, valid_escapes[k])
    for k in range(len(invalidchars)):
        texstring = string.replace(texstring, replace_chars[k], valid_escapes[k])
    return texstring

def unescape_bad_latex_chars(texstring):
    '''get rid of LaTeX-friendly escaping'''
    invalidchars = (r'#', r'$', r'%', r'&', r'_') #, '{', '}'
    valid_escapes = (r'\#', r'\$', r'\%', r'\&', r'\_')
    for k in range(len(invalidchars)):
        texstring = string.replace(texstring, valid_escapes[k], invalidchars[k])
    return texstring

re_tex = re.compile(r'\\.+?\{(.+)\}')
def untexify(texstring):
    '''remove curly braces and other tex-related stuff'''
    # TODO this is unlikely to work if there's more than one latex macro
    tex_match = re_tex.search(texstring)
    if tex_match:
        texstring = re_tex.sub(tex_match.group(1), texstring)
    texstring = unescape_bad_latex_chars(texstring)
    transtbl = {ord('{'): None, ord('}'): None}
    texstring = texstring.translate(transtbl)
    return texstring

preceders = (u':', u'-', u'.', u'\u2014', u'\u2e3b', u'\ufe58', u'\u2e3a')
ignorers = (u'\u0022',u'\u0027',u'\u00AB',u'\u00BB',u'\u2018', u'\u2019', u'\u201A', u'\u201B', u'\u201C', u'\u201D', u'\u201E', u'\u201F', u'\u2039', u'\u203A', u'(', u')', u'[', u']')
whitespacers =  (u'u\0009',u'u\000A',u'u\000B',u'u\000C',u'u\000D',u'u\0020',u'u\0085',u'u\00A0',u'u\1680',u'u\180E',u'u\2000',u'u\2001',u'u\2002',u'u\2003',u'u\2004',u'u\2005',u'u\2006',u'u\2007',u'u\2008',u'u\2009',u'u\200A',u'u\2028',u'u\2029',u'u\202F',u'u\205F',u'u\3000')

class AwareChar:
    '''A Unicode char that is aware of its place in a string'''
    idx = -1
    str_firstchar = False
    starts_word = False
    pre_char = None
    pre_char2 = None
    following_char = None

    def __init__(self, idx, charstr):
        assert type(charstr) == unicode
        self.char = charstr[idx]
        self.idx = idx
        if not idx == 0:
            self.pre_char = charstr[idx-1]
        if not idx < 2: 
            self.pre_char2 = charstr[idx-2]
        if not idx == len(charstr)-1:
            self.following_char = charstr[idx+1]
        self._set_startsword()

    def _set_startsword(self):
        if not self.isalpha(): return
        if self.idx == 0:
            self.starts_word = True
            return
        if self.idx == 1:
            if self.pre_char.isspace():
                self.starts_word = True
                return
            if self.pre_char in ignorers:
                self.starts_word = True
                return
        if self.idx > 1:
            if self.pre_char.isspace():
                self.starts_word = True
                return
            if self.pre_char in ignorers and self.pre_char2.isspace():
                self.starts_word = True
                return

    def isignore(self):
        if self.char in ignorers:
            return True
        else: return False
            
    def isalpha(self):
        return self.char.isalpha()

    def isupper(self):
        return self.char.isupper()

    def isspace(self):
        return self.char.isspace()

    def ic(self):
        return self.idx, self.char

    def startsword(self):
        return self.starts_word

    def endsword(self):
        if self.following_char == None:
            if self.isalpha(): 
                print self.char, 'wtf', self.following_char
                return True
            else: return False
        if self.following_char in ignorers:
            # print self.char, 'returning true because next char in ignorers'
            return True
        if self.following_char.isspace(): 
            # print self.char, 'returning true because next char is whitespace'
            return True
        return False

    def startssentence(self, strictness=0):
        if strictness == 2:
            if self.idx == 0 and self.startsword(): return True
            else: return False
        if strictness == 1:
            if not self.startsword(): return False
            if self.idx == 0: return True
            if self.pre_char in (u'(', u'[') or self.pre_char2 == u':':
                return True
            return False
        if strictness == 0:
            if not self.startsword(): return False
            if self.idx == 0: return True
            if self.pre_char.isspace() and self.pre_char2 in preceders:
                return True
            if self.pre_char in (u'(', u'['):
                return True
            return False
        return False

def protect_caps(plainstring, save_all=False):
    '''Place curly braces around caps to protect them when formatting
    citations.
    save_all = protect all caps'''
    def get_contiguous(startidx, charstr):
        endidx = startidx
        while endidx < len(charstr)-1 and charstr[endidx+1].isupper():
            endidx += 1
        return startidx, endidx

    assert type(plainstring) == unicode

    awarestr = []
    for i in range(len(plainstring)):
        awarestr.append(AwareChar(i, plainstring))
    
    preserves = []
    pa_end, pa_st = -1, -1
    for ch in awarestr:
        if ch.isupper():
            if ch.idx <= pa_end: continue #fast forward to end of acronyms
            pa_st, pa_end = get_contiguous(ch.idx, plainstring)
            # if there's a contiguous set of caps, assess if it looks
            # like an acronym and append it to the preservation list
            if pa_end > pa_st:
                if (ch.startsword() and awarestr[pa_end].endsword()) or save_all:
                    # print awarestr[pa_end].char, 'ENDS WORD'
                    preserves.append((pa_st, pa_end))
            elif save_all: preserves.append((ch.idx, ch.idx))
            elif ch.startssentence(1): preserves.append((ch.idx, ch.idx))
            # elif ch.startsword(): preserves.append((ch.idx, ch.idx))

    print preserves
    st_blocks = []
    endlast = 0
    for st, end in preserves:
        if endlast < st:
            st_blocks.append(plainstring[endlast:st])
        st_blocks.append(u"{%s}" % plainstring[st:end+1])
        endlast = end+1
    st_blocks.append(plainstring[endlast:])
    r = u''.join(st_blocks)
    return r

if __name__ == '__main__':
    thestr = u'The {QUICK} Brown fOx "Jumped" ov{ERZ} {t}he LAzI2000 d0G'
    print thestr
    print protect_caps(thestr, False)

            
        
        
    
    

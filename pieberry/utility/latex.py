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

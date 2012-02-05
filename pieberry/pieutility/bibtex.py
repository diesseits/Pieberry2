import string, re
from latex import escape_bad_latex_chars

bibtex_fields = ('title', 'howpublished', 'month', 'year', 'annote', 'note', 'url', 'volume', 'number', 'pages', 'journal', 'edition', 'series', 'publisher', 'chapter', 'type', 'address', 'institution')
person_fields = ('author', 'editor')

def format_bibtex_entry(bibdict):
    '''format a single bibtex entry'''
    if bibdict.has_key('bibtex_key'):
        key = bibdict['bibtex_key']
    else:
        key = autogen_bibtex_key(bibdict)
    author = bibdict['author']
    if bibdict.has_key('corporate_author'):
        if bibdict['corporate_author']:
            author = "{%s}" % bibdict['author']
    ent = """
@%s{%s,
  author = {%s},
  title = {%s},
  howpublished = {\href{%s}{On the web}},
  month = {%s},
  year = %s,
  annote = {%s}}

""" % (
        bibdict['bibtex_type'].encode('utf-8'),
        key,
        escape_bad_latex_chars(author).encode('utf-8'),
        escape_bad_latex_chars(bibdict['title']).encode('utf-8'),
        escape_bad_latex_chars(bibdict['howpublished']).encode('utf-8'),
        bibdict['month'].encode('utf-8'),
        bibdict['year'].encode('utf-8'),
        escape_bad_latex_chars(bibdict['annote']).encode('utf-8')
        )
    return ent

def autogen_bibtex_key(bibdict):
    keytitlecompact = string.join([i[:3] for i in string.split(bibdict['title'].encode("utf-8").translate(string.maketrans("",""), string.punctuation)) if len(i) > 3], '') #ouch ... this compacts the first three letters of each word in the title together, to make a dependably unique key
    keyauthorcompact = string.join([i[:1] for i in string.split(bibdict['author'].encode("utf-8").translate(string.maketrans("",""), string.punctuation))], '') #same for authors, but just initials
    key = "%s%s_%s" % (
        keyauthorcompact,
        bibdict['year'].encode('utf-8'), 
        keytitlecompact
        )
    return key

def increment_bibtex_key(keytext):
     '''add digits to end of key to try to avoid identical keys'''
     try:
         last_digit = int(keytext[-1])
         if last_digit == 9:
             key_base = keytext
             last_digit = -1
         else:
             key_base = keytext[:-1]
     except:
         last_digit = -1
         key_base = keytext
     last_digit += 1
     print 'generated key %s%d' % (key_base, last_digit)
     return '%s%d' % (key_base, last_digit)

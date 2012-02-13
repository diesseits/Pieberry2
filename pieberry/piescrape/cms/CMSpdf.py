import re, string
from urlparse import urlsplit, parse_qs
from urllib import unquote
from pieutility.decoding import translate_non_alphanumerics as tr_nan

re_cd_filename = re.compile('^.*filename="(.*\.(pdf|Pdf|PDF))')

def diagnose(uobj):
    '''not implemented for this CMS'''
    # diagnosis handled in __init__ by looking at the type
    pass

def get_context_object(uobj):
    retobj = PDFContextObject(uobj)
    return retobj

class PDFContextObject:
    def __init__(self, uobj):
        self._url = uobj.url
        self.titlesuggestions = {}
        header = uobj.headers.getheader('Content-Disposition')
        if header and re_cd_filename.match(header):
            self.titlesuggestions['content-disposition'] = re_cd_filename.match(
                header).group(1)
        query = parse_qs(urlsplit(uobj.geturl())[3])
        self.titlesuggestions['filename'] = unquote(urlsplit(uobj.url)[2])
        if 'fn' in query.keys():
            self.titlesuggestions['filename'] = unquote(query['fn'][0])

    def get_links(self, *args, **kwargs):
        linkdata = {'Url': unicode(self._url),
                    'LastHeading': '',
                    'LinkText': self.get_context_title(),
                    'SuggestedTitle': self.get_context_title(),
                    'Tags': []}
        ret = [linkdata,]
        return ret

    def get_context_title(self):
        ret = ''
        if self.titlesuggestions.has_key('content-disposition'):
            ret = self.titlesuggestions['content-disposition']
        else:
            ret = self.titlesuggestions['filename']
        if ret[-4:] in ('.pdf', '.Pdf', '.PDF'):
            return tr_nan(unicode(ret[:-4]))
        else:
            return tr_nan(unicode(ret))

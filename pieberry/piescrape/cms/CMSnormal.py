from BeautifulSoup import BeautifulSoup
import re, urlparse, os.path
from pieutility.decoding import translate_non_alphanumerics as tr_nan
from pieutility.decoding import decode_htmlentities
from pieconfig.schemas import PIE_TYPES_DOCUMENTS, PIE_TYPES_ALL, FEXTENSIONS


head_re = re.compile('[hH][1-7]')
re_submission = re.compile(r'^(.+?)(\'s)?( -)? [sS]ubmission')
sub_re = re.compile('[Ss]ubmission')

def make_linktest_re_str(filetype, exts):
    '''Make an all-purpose link location regex out of file extensions'''
    ext_str = ''
    for ext in exts:
        ext_str = ext_str + '|'
        ext_str = ext_str + "%s|%s|%s" % (ext.lower(), 
                                          '.' + ext[1:].capitalize(), 
                                          ext.upper())
    ret_str = "^.*(%s)" % ext_str[1:]
    print 'Making re out of', ret_str
    return re.compile(ret_str)

LINKTESTS = {}
for filetype, exts in FEXTENSIONS.items():
    LINKTESTS[filetype] = [make_linktest_re_str(filetype, exts),]

RE_SPECIAL_DOCS = (re.compile(r'.*DownloadPublication.aspx.*'),)

def diagnose(obj):
    '''not implemented for this cms'''
    pass

def get_context_object(obj):
    '''receive a urlopener object, return a context object'''
    retobj = NormalContextObject(obj)
    return retobj

class NormalContextObject:
    '''let this be the first of its type'''
    def __init__(self, obj):
        '''receive a urlopener object'''
        thehtml = obj.read()
        self._bs = BeautifulSoup(thehtml)

    def get_links(self, types=('pdf',), baseurl=''):
        '''receive a tuple of link types to seek
        return a list of dicts containing information on the various
        links'''
        links = []
        ret = []
        listofallfileextensions = []
        for i in types:
            listofallfileextensions.extend(FEXTENSIONS[i])
        print 'types = ', types
        if types == PIE_TYPES_ALL:
            links.extend(self._bs.findAll('a'))
        else:
            for linktype in types:
                if linktype in LINKTESTS.keys():
                    for linkre in LINKTESTS[linktype]:
                        links.extend(self._bs.findAll('a', href=linkre))
            if types == PIE_TYPES_DOCUMENTS:
                # handle regexs that will find "documents" but might
                # not know their exact type
                for linkre in RE_SPECIAL_DOCS:
                    links.extend(self._bs.findAll('a', href=linkre))
        for link in links:
            linkdata = {}
            linkdata['Url'] = urlparse.urljoin(
                baseurl, link['href'].encode('utf-8'))
            linkdata['Url'] = unicode(linkdata['Url'])
            if link.findPrevious(head_re):
                linkdata['LastHeading'] = unicode(
                    link.findPrevious(head_re).text)
            if hasattr(link, 'text'):
                linkdata['LinkText'] = decode_htmlentities(unicode(link.text))
                st = link.text.strip(' -_')
                if os.path.splitext(st)[1] in listofallfileextensions: 
                    st = os.path.splitext(st)[0]
                st = tr_nan(st)
                linkdata['SuggestedTitle'] = decode_htmlentities(unicode(st))
            else:
                linkdata['LinkText'] = unicode(linkdata['Url'])
                linkdata['SuggestedTitle'] = unicode(linkdata['Url'])
            linkdata['PageTitle'] = self.get_context_title()
            linkdata['Tags'] = tag_by_data(linkdata)
            ret.append(linkdata)
        return ret

    def get_context_title(self):
        return unicode(decode_htmlentities(self._bs.title.string))

TESTS = {
    'Submissions': (
        ('submission', 'in', 'SuggestedTitle'),
        ('submission', 'in', 'LastHeading'),
        ('submission', 'in', 'PageTitle')
        ),
    'Presentations': (
        ('presentation', 'in', 'SuggestedTitle'),
        ('.ppt', 'in', 'Url'),
        ('slides', 'in', 'SuggestedTitle'),
        ('powerpoint', 'in', 'SuggestedTitle')
        ),
    'Trololo': (
        ('submission', 'in', 'PageTitle'),
        )
    }

def apply_test(retdata, string, test, field):
    '''utility function to tag_by_data'''
    print ' ..', string
    assert type(retdata[field]) == unicode
    assert test in ('in', 'equals')
    if not retdata.has_key(field):
        return False
    if test == 'in':
        if string in retdata[field].lower(): 
            return True
        else:
            return False
    if test == 'equals':
        if string == retdata[field].lower():
            return True
        else:
            return False

def tag_by_data(linkdata):
    '''Try to add some automatic tags according to link data provided'''
    retdata = []
    for tag, tests in TESTS.items():
        match = False
        for test in tests:
            match = apply_test(linkdata, *test)
        if match: retdata.append(tag)
    return retdata
    
def text_t(node):
     '''return last substantial (> 5 chars) bit of text before the
     current BS node'''
     rettext = ''
     counter = 0
     while not len(rettext) > 5 and counter < 10000:
          node = node.findPrevious(text=True)
          rettext = unicode(node)
          counter += 1
     return rettext

# Download from CiteseerX.com

from BeautifulSoup import BeautifulSoup
import re, urlparse, os.path, traceback
from pieberry.pieconfig.paths import CACHEDIR
from pieberry.pieutility.decoding import translate_non_alphanumerics as tr_nan
from pieberry.pieutility.decoding import decode_htmlentities
from pieberry.pieconfig.schemas import PIE_TYPES_DOCUMENTS, PIE_TYPES_ALL, FEXTENSIONS
from pieberry.pieinput.bibtex import *

def diagnose(uobj):
    '''not implemented for this cms'''
    if urlparse.urlparse(uobj.url).netloc == 'citeseerx.ist.psu.edu':
        return True
    else: return False

def get_context_object(uobj):
    retobj = CSXContextObject(uobj)
    return retobj

class CSXContextObject:
    def __init__(self, uobj):
        self._url = uobj.url
        self._bs = BeautifulSoup(uobj.read())

    def get_links(self, types=('pdf,'), baseurl=''):
        '''receive a tuple of link types to seek return a list of
        dicts containing information on the various links'''
        ret = self._get_dl_links()
        ret.append(self._get_cache_link())
        return ret

    def get_context_title(self):
        return unicode(decode_htmlentities(self._bs.title.string))

    def _get_cache_link(self):
        cachestub = self._bs.find('ul', id='clinks').li.a['href']
        if not cachestub: raise Exception, 'Seemingly invalid page'
        scheme = urlparse.urlparse(self._url).scheme
        netloc = urlparse.urlparse(self._url).netloc
        fulllink = urlparse.urlunparse((
                scheme, netloc, cachestub, '', '', ''))
        metadata = self._get_metadata()
        metadata['Url'] = fulllink
        return metadata

    def _get_dl_links(self):
        links = [ a['href'] 
                  for a in self._bs.find('ul', id='dlinks').findAll('a') ]
        metadata = self._get_metadata()
        rlist = []
        for link in links:
            rmeta = dict(metadata)
            rmeta['Url'] = link
            rlist.append(rmeta)
        return rlist

    def _get_metadata(self):
        # ret = []
        linkdata = {}
        # bibtexdata = self._bs.find('div', id='bibtex').p.prettify()
        # print bibtexdata.split('\n') 
        # A fairly brute force of coercing the bit of html containing
        # the bibtex into a useable format
        linkdata['LastHeading'] = u''
        linkdata['LinkText'] = unicode(self._bs.find('ul', id='clinks').li.a['title'])
        linkdata['SuggestedTitle'] = self.get_context_title()
        linkdata['PageTitle'] = self.get_context_title()
        linkdata['InferredFileType'] = u'pdf'
        linkdata['Tags'] = []
        try:
            bibtexdata = [ 
                unicode(decode_htmlentities(l.replace('&nbsp;', '')))
                for l in self._bs.find('div', id='bibtex').p.prettify().split('\n') 
                if len(l) > 0 and l[0] != '<' 
                ]
            bibtexdata = u'\n'.join(bibtexdata)
            f = open(os.path.join(CACHEDIR, 'bibtexsc.bib'), 'w')
            # f.write(bibtexdata)
            f.write(unicode(decode_htmlentities(bibtexdata)))
            f.close()
            btread = pybtex_entries_from_file(os.path.join(CACHEDIR, 'bibtexsc.bib'))
            for ky, vl in btread.items(): print pybtex_to_pieberry(ky, vl)
            
            linkdata['BibTeX'] = btread.items()[0]
            linkdata['SuggestedTitle'] = btread.items()[0].fields['title']
        except Exception, exc:
            traceback.print_exc()
            

        return linkdata

        # bs.find('div', id='bibtex').p.prettify().replace('&nbsp;', '').replace('<br />', '')


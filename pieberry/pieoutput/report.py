# (c) Raif Sarcich 2012 GPLv3

from pieberry.pieobject import PieObjectStore
from pieberry.pieoutput import bibtex

import xml.dom.minidom

ORDERS = {
    _('Order by Author'): 'author', 
    _('Order by Title'): 'title', 
    _('Order by Date of Publication'): 'date', 
    _('Order by File Name'): 'filename'
    }
HEADER_FORMATS = ('citation', 'title', 'authortitle', 'filename')

report_xml_header = '<?xml version="1.0" encoding="UTF-8"?><richtext version="1.0.0.0" xmlns="http://www.wxwidgets.org">'
report_xml_footer = '</richtext>'

cite_xml_header = '<paragraphlayout textcolor="#000000" fontsize="14" fontstyle="90" fontweight="90" fontunderlined="0" fontface="serif" alignment="1" parspacingafter="10" parspacingbefore="10" linespacing="10">'
cite_xml_footer = '</paragraphlayout>'

class ReportFormatter:
    '''A class to prepare wxXML formatted reports for the user'''
    def __init__(self, header_format='authortitle'):
        self.ostore = PieObjectStore()
        self.header_format = header_format
        self.basedom = xml.dom.minidom.parseString(report_xml_header+report_xml_footer)
        self.title = _('Report')

    def _get_header(self, obj):
        if self.header_format == 'authortitle':
            ret = u"%s (%d) \u2014 %s" % (
                obj.Author(),
                obj.ReferDate().year,
                obj.Title()
                )
            return ret
        else:
            raise Exception, 'header style not implemented'

    def _get_title(self):
        return self.title

    def AddObject(self, obj):
        self.ostore.Add(obj)

    def AddObjects(self, ostore):
        self.ostore = ostore

    def Sort(self, order='date'):
        self.ostore.Sort(order)

    def SetTitle(self, title):
        '''Set an overall title for the report'''
        assert type(title) in (str, unicode)
        self.title = title

    def SetSubject(self, subject, fromcontext=None):
        '''Set a relevant subject for the report
        fromcontext can be a 'tag', 'searchterm' '''
        self.subject = subject
        self.title = _('Report: ') + subject

    def _get_node_paragraphlayout(self):
        '''just boilerplate for wxXML'''
        header = self.basedom.createElement('paragraphlayout')
        header.setAttribute('textcolor', "#000000")
        header.setAttribute('fontsize', "12")
        header.setAttribute('fontstyle', '90')
        header.setAttribute('fontweight', '90')
        header.setAttribute('fontunderlined', '0')
        header.setAttribute('fontface', 'serif')
        header.setAttribute('alignment', '1')
        header.setAttribute('parspacingafter', '10')
        header.setAttribute('parspacingbefore', '20')
        header.setAttribute('linespacing', '10')
        return header

    def GenerateReport(self):
        # title the report
        pl = self._get_node_paragraphlayout()
        p = self.basedom.createElement('paragraph')
        p.setAttribute('alignment', '2')
        p.setAttribute('parspacingafter', '15')
        titlenode = self.basedom.createElement('text')
        titlenode.setAttribute('fontsize', '18')
        titlenode.setAttribute('fontface', 'serif')
        titlenode.setAttribute('fontunderlined', '1')
        titletextnode = self.basedom.createTextNode(self._get_title())
        titlenode.appendChild(titletextnode)
        p.appendChild(titlenode)
        pl.appendChild(p)
        self.basedom.childNodes[0].appendChild(pl)

        for obj in self.ostore:
            # create overall header
            headerpara = self.basedom.createElement('paragraph')
            headerpara.setAttribute('parspacingafter', '20')
            dummypara = self.basedom.createElement('paragraph')
            headertext = self.basedom.createElement('text')
            headertext.setAttribute('fontface', 'sansserif')
            headertext.setAttribute('fontsize', '14')
            headertext.setAttribute('fontweight', '92')
            # headertext.setAttribute('fontunderlined', '1')
            headertextnode = self.basedom.createTextNode(self._get_header(obj))

            # pin it to the DOM tree
            headertext.appendChild(headertextnode)
            headerpara.appendChild(headertext)
            self.basedom.childNodes[0].childNodes[0].appendChild(dummypara)
            self.basedom.childNodes[0].childNodes[0].appendChild(headerpara)

            if obj.notes:
                # pull the xml payload out of the notes page
                xparse = xml.dom.minidom.parseString(obj.notes)
                payload = xparse.getElementsByTagName('paragraphlayout')[0]
                newnode = self.basedom.importNode(payload, True)
                self.basedom.childNodes[0].childNodes[0].appendChild(newnode)
            else:
                standinpara = self.basedom.createElement('paragraph')
                standintextnode = self.basedom.createElement('text')
                standintext = self.basedom.createTextNode(_('[ no notes ]'))
                standintextnode.appendChild(standintext)
                standinpara.appendChild(standintextnode)
                self.basedom.childNodes[0].childNodes[0].appendChild(standinpara)
            
        # print self.basedom.toprettyxml(encoding="UTF-8", indent="  ")

        return self.basedom.toprettyxml(encoding="UTF-8", indent="  ")

    

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

testxml = '''<?xml version="1.0" encoding="UTF-8"?>
<richtext version="1.0.0.0" xmlns="http://www.wxwidgets.org">
  <paragraphlayout textcolor="#000000" fontsize="12" fontstyle="90" fontweight="90" fontunderlined="0" fontface="serif" alignment="1" parspacingafter="10" parspacingbefore="0" linespacing="10">
    <paragraph>
      <text>Spradley 1979:</text>
    </paragraph>
    <paragraph>
      <text></text>
    </paragraph>
    <paragraph>
      <text>"Ethnographic research techniques: "</text>
    </paragraph>
    <paragraph>
      <text>- Informants: discuss and frame issues themselves for the researcher</text>
    </paragraph>
    <paragraph>
      <text>- Respondents: answer questions framed by and put by the researcher</text>
    </paragraph>
    <paragraph>
      <text>- Subjects: used to test hypotheses</text>
    </paragraph>
    <paragraph>
      <text>- Actors: are observed</text>
    </paragraph>
  </paragraphlayout>
</richtext>
'''


def _fmt_obj(obj):
    '''spit out an object citation + notes in wxXML format'''
    basedom = xml.dom.minidom.parseString(report_xml_header+report_xml_footer)
    
    if obj.notes:
        # pull the xml payload out of the notes page
        xparse = xml.dom.minidom.parseString(obj.notes)
        payload = xparse.getElementsByTagName('paragraphlayout')[0]

    newnode = basedom.importNode(payload, True)
    basedom.childNodes[0].appendChild(newnode)
    print basedom.toxml()
        

class Dummy:
    def __init__(self):
        self.notes = testxml

if __name__ == '__main__':
    obj = Dummy()
    _fmt_obj(obj)

class ReportFormatter:
    '''A class to prepare wxXML formatted reports for the user'''
    def __init__(self, header_format='authortitle'):
        self.ostore = PieObjectStore()
        self.header_format = header_format
        self.basedom = xml.dom.minidom.parseString(report_xml_header+report_xml_footer)

    def _get_header(self, obj):
        if self.header_format == 'authortitle':
            return obj.Author() + u' \u2014 ' + obj.Title()
        else:
            raise Exception, 'header style not implemented'

    def AddObject(self, obj):
        self.ostore.Add(obj)

    def AddObjects(self, ostore):
        self.ostore = ostore

    def Sort(self, order='date'):
        self.ostore.Sort(order)

    def GenerateReport(self):
        for obj in self.ostore:
            # create overall header
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
            headerpara = self.basedom.createElement('paragraph')
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
            header.appendChild(dummypara)
            header.appendChild(headerpara)
            self.basedom.childNodes[0].appendChild(header)

            if obj.notes:
                # pull the xml payload out of the notes page
                xparse = xml.dom.minidom.parseString(obj.notes)
                payload = xparse.getElementsByTagName('paragraphlayout')[0]
                newnode = self.basedom.importNode(payload, True)
                self.basedom.childNodes[0].appendChild(newnode)
            
        # print self.basedom.toprettyxml(encoding="UTF-8", indent="  ")

        return self.basedom.toprettyxml(encoding="UTF-8", indent="  ")

    

import re

from pybtex.style.formatting import BaseStyle, toplevel
from pybtex.style.formatting.unsrt import *
from pybtex.style.template import (
    join, words, field, optional, first_of,
    names, sentence, tag, optional_field
)
from pybtex.richtext import Text, Symbol

class Formatter(Style):
    default_name_style = 'lastfirst'

    def format_people(self, e):
        template = toplevel [ 
            self.format_author_or_editor(e)
            ]
        return template.format_data(e)

    def format_online(self, e):
        return self.format_misc(e)

    def unmung_hrefs(self, field):
        import re
        print type(field)
        re_href = re.compile(r'\href\{(.*)\}\{Web [sS]ite\}')
        m = re_href.match(field)
        if m:
            return m.group(1)
        return field

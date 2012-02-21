# Copyright (C) 2006, 2007, 2008, 2009  Andrey Golovizin
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re

from pybtex.style.formatting import FormatterBase, toplevel
from pybtex.style.template import (
    join, words, field, optional, first_of,
    names, sentence, tag, optional_field
)
from pybtex.richtext import Text, Symbol

def dashify(text):
    dash_re = re.compile(r'-+')
    return Text(Symbol('ndash')).join(dash_re.split(text))

pages = field('pages', apply_func=dashify)

date = words [optional_field('month'), field('year')]

class Formatter(FormatterBase):
    def format_names(self, role):
        return sentence(capfirst=False) [names(role, sep=', ', sep2 = ' and ', last_sep=', and ')]

    def format_article(self, e):
        volume_and_pages = first_of [
            join [field('volume'), optional [':', pages]],
            words ['pages', optional [pages]]
        ]
        template = toplevel [
            self.format_names('author'),
            sentence [field('title')],
            sentence [
                tag('emph') [field('journal')], optional [ volume_and_pages ], date],
        ]
        return template.format_data(e)
        
    def format_author_or_editor(self, e):
        if e.persons['author']:
            return self.format_names('author')
        else:
            editors = self.format_names('editors')
            if len(e.persons['editors']) > 1:
                word = 'editors'
            else:
                word = 'editor'
            return words [editors, word]
    
    def format_volume_and_series(self, e):
        volume_and_series = optional [
            sentence(capfirst=False, sep=' ') [
                'Volume', field('volume'), optional [
                    words ['of', field('series')]
                ]
            ]
        ]
        number_and_series = optional [
            sentence(capfirst=False, sep=' ') [
                join(sep=Symbol('nbsp')) ['Number', field('number')],
                optional [
                    words ['in', field('series')]
                ]
            ]
        ]
        series = optional [ sentence(capfirst=False) [field('series')] ]
        return first_of [
                volume_and_series,
                number_and_series,
                series,
            ]
    
    def format_chapter_and_pages(self, e):
        return join(sep=', ') [
            optional [words ['chapter', field('chapter')]],
            optional [words ['pages', pages]],
        ]

    def format_people(self, e):
        template = toplevel [ 
            self.format_author_or_editor(e)
            ]
        return template.format_data(e)

    def format_book(self, e):
        template = toplevel [
            self.format_author_or_editor(e),
            tag('emph') [sentence [field('title')]],
            self.format_volume_and_series(e),
            sentence [field('publisher'), date],
        ]
        return template.format_data(e)

    def format_booklet(self, e):
        template = toplevel [
            sentence [self.format_names('author')],
            sentence [tag('emph') [field('title')]],
            sentence [
                optional_field('howpublished'),
                optional_field('address'),
                date,
                optional_field('note'),
            ]
        ]
        return template.format_data(e)

    def format_misc(self, e):
        return self.format_booklet(e)

    def format_Misc(self, e):
        return self.format_booklet(e)

    def format_other(self, e):
        return self.format_booklet(e)

    def format_booklet_with_url(self, e):
        template = toplevel [
            sentence [self.format_names('author')],
            sentence [tag('emph') [field('title')]],
            sentence [
                optional_field('howpublished'),
                optional_field('address'),
                date,
                optional_field('note'),
            ],
            optional_field('url')
        ]
        return template.format_data(e)

    def unmung_hrefs(self, field):
        import re
        print type(field)
        re_href = re.compile(r'\href\{(.*)\}\{Web [sS]ite\}')
        m = re_href.match(field)
        if m:
            return m.group(1)
        return field

    def format_incollection(self, e):
        template = toplevel [
            sentence [self.format_names('author')],
            sentence [
                tag('emph') [field('title')],
                self.format_chapter_and_pages(e),
            ],
            sentence [
                words [
                    'in', 
                    words [
                        optional [ field('editors'), '(eds.)'], #hack alert
                        ],
                    field('booktitle')
                    ],
                ],
            
            self.format_volume_and_series(e),
            sentence [
                field('publisher'),
                optional_field('address'),
                optional [
                    words [field('edition'), 'edition']
                ],
                date,
                optional_field('note'),
            ]
        ]
        return template.format_data(e)


    def format_inbook(self, e):
        template = toplevel [
            sentence [self.format_names('author')],
            sentence [
                tag('emph') [field('title')],
                self.format_chapter_and_pages(e),
            ],
            self.format_volume_and_series(e),
            sentence [
                field('publisher'),
                optional_field('address'),
                optional [
                    words [field('edition'), 'edition']
                ],
                date,
                optional_field('note'),
            ]
        ]
        return template.format_data(e)

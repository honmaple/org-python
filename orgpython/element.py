#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ********************************************************************************
# Copyright © 2018 jianglin
# File Name: element.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2018-02-26 11:44:43 (CST)
# Last Update: Monday 2018-03-19 14:49:21 (CST)
#          By:
# Description:
# ********************************************************************************
import re
from time import time
from textwrap import dedent
from collections import OrderedDict

from .inline import Text
from .regex import Regex


class NotBeginError(Exception):
    pass


class Element(object):
    label = '{text}'
    regex = None

    def __init__(self, text, escape=False):
        self.text = text
        self.children = []
        self.parent = self
        self.escape = escape

    def append(self, child):
        if self.children or child:
            if isinstance(child, str):
                child = Text(child, escape=self.escape)
            self.children.append(child)

    def to_html(self):
        if isinstance(self.children, list):
            text = '\n'.join([child.to_html() for child in self.children])
        else:
            text = self.children.to_html()
        text = dedent(text)
        return self.label.format(text=text)

    def __str__(self):
        str_children = [str(child) for child in self.children]
        return self.__class__.__name__ + '(' + ','.join(str_children) + ')'

    def __repr__(self):
        return self.__str__()


class Heading(Element):
    label = '<h{level}>{title}</h{level}>'
    label1 = '<h{level} id="{tid}">{title}</h{level}>'
    regex = Regex.heading

    def __init__(self, text, offset=0, toc=False):
        self.text = text
        self.offset = offset
        self.toc = toc
        self.children = []

    def to_html(self):
        m = self.regex.match(self.text)
        level = len(m.group('level')) + self.offset
        title = m.group('title')
        text = self.label.format(level=level, title=title)
        if self.toc:
            tid = self.heading_id(text)
            text = self.label1.format(level=level, tid=tid, title=title)
            self.toc.append('{}- <a href="#{}">{}</a>'.format(' ' * level, tid,
                                                              title))
        return text

    def heading_id(self, text):
        return 'org-{}'.format(int(time() * 10000))


class OutlineElement(object):
    def __init__(self, text, escape=False):
        self.text = text
        self.parent = self
        self.children = Org("", escape=escape)
        self.escape = escape
        self.init()

    def init(self):
        '''
        cover default params.
        '''

    def append(self, child):
        self.children.append(child)

    def to_html(self):
        if isinstance(self.children, list):
            text = '\n'.join([child.to_html() for child in self.children])
        else:
            text = self.children.to_html()
        return self.label.format(text=text)

    def end(self, text):
        return not self.regex.match(text)

    def __str__(self):
        return self.__class__.__name__ + '(' + str(self.children) + ')'

    def __repr__(self):
        return self.__str__()


class Src(OutlineElement):
    label = '<pre class="{lang}">\n{text}\n</pre>'
    regex = Regex.begin_src

    def init(self):
        self.children = []
        self.lang = self.regex.match(self.text).group('lang')

    def append(self, child):
        self.children.append(Text(child, False))

    def to_html(self):
        text = '\n'.join([child.to_html() for child in self.children])
        text = dedent(text)
        return self.label.format(lang=self.lang, text=text)

    def end(self, text):
        return Regex.end_src.match(text)


class Example(OutlineElement):
    label = '<pre class="example">\n{text}\n</pre>'
    regex = Regex.begin_example

    def init(self):
        self.children = []

    def append(self, child):
        self.children.append(Text(child, False))

    def end(self, text):
        return Regex.end_example.match(text)


class Export(OutlineElement):
    label = '{text}'
    regex = Regex.begin_export

    def init(self):
        self.children = []

    def append(self, child):
        self.children.append(Text(child, True))

    def end(self, text):
        return Regex.end_export.match(text)


class Verse(OutlineElement):
    label = '<p class="org-verse">\n{text}\n</p>'
    regex = Regex.begin_verse

    def init(self):
        self.children = []

    def append(self, child):
        self.children.append(Text(child, True))

    def to_html(self):
        text = '<br/>'.join([child.to_html() for child in self.children])
        return self.label.format(text=text)

    def end(self, text):
        return Regex.end_verse.match(text)


class Center(OutlineElement):
    label = '<div class="org-center">\n{text}\n</div>'
    regex = Regex.begin_center

    def end(self, text):
        return Regex.end_center.match(text)


class BlockQuote(OutlineElement):
    label = '<blockquote>\n{text}\n</blockquote>'
    regex = Regex.begin_quote

    def end(self, text):
        return Regex.end_quote.match(text)


class CheckBox(Element):
    label = '<input type="checkbox" />{text}'
    label1 = '<input type="checkbox" checked="checked" />{text}'
    regex = Regex.checkbox

    def to_html(self):
        m = self.regex.match(self.text)
        label = self.label
        if m.group("check") == 'X':
            label = self.label1
        text = label.format(text=Text(
            m.group("title"),
            escape=self.escape, ).to_html())
        return text


class ListItem(OutlineElement):
    label = '<li>{text}</li>'

    def init(self):
        '''
        first line
        '''
        if CheckBox.regex.match(self.text):
            self.text = CheckBox(self.text, escape=self.escape)
        self.append(self.text)

    def append(self, child):
        if not self.children.children and isinstance(child, str):
            child = Text(child, escape=self.escape)
        self.children.append(child)


class List(OutlineElement):
    regex = None

    def init(self):
        self.depth = len(self.regex.match(self.text).group('depth'))
        self.children = []
        self.append(self.text)

    def append(self, child):
        m = self.regex.match(child)
        if m is not None:
            depth = len(m.group('depth'))
            title = m.group('title')

            if depth == self.depth:
                element = ListItem(title, escape=self.escape)
                self.children.append(element)
            elif depth > self.depth:
                self.children[-1].append(child)
        else:
            self.children[-1].append(child)

    def end(self, text):
        if not text:
            return False
        m = Regex.any_depth.match(text)
        depth = len(m.group('depth'))
        if not self.regex.match(text) and depth == self.depth:
            return True
        if m and (depth >= self.depth):
            return False
        return True


class UnorderList(List):
    label = '<ul>\n{text}\n</ul>'
    regex = Regex.unorder_list


class OrderList(List):
    label = '<ol>\n{text}\n</ol>'
    regex = Regex.order_list


class TableCell(Element):
    label = '<td>{text}</td>'


class TableRow(Element):
    label = '<tr>\n{text}\n</tr>'
    regex = Regex.table

    def to_html(self):
        m = self.regex.match(self.text)
        cells = [c for c in m.group('cells').split('|') if c]
        for cell in cells:
            child = TableCell(cell, escape=self.escape)
            child.append(cell.strip())
            self.children.append(child)
        text = ''.join([child.to_html() for child in self.children])
        return self.label.format(text=text)


class Table(OutlineElement):
    label = '<table>\n{text}\n</table>'
    regex = Regex.table

    def init(self):
        self.children = []
        self.append(self.text)

    def append(self, child):
        if Regex.table_sep.match(child):
            # th instead of td only once
            td = re.compile(r'<td>(.*?)</td>')
            text = '\n'.join([ch.to_html() for ch in self.children])
            text = td.sub(lambda match: match.group(0).replace('td', 'th'),
                          text)
            self.children = [Text(text, False, False)]
        else:
            self.children.append(TableRow(child, escape=self.escape))

    def to_html(self):
        text = '\n'.join([child.to_html() for child in self.children])
        return self.label.format(text=text)

    def end(self, text):
        return not self.regex.match(text)


class Toc(Element):
    def append(self, child):
        self.children.append(child)

    def to_html(self):
        text = '\n'.join(self.children)
        if text:
            text = ('<div id="table-of-contents">'
                    '<h2>Table of Contents</h2>'
                    '<div id="text-table-of-contents">{}\n</div></div>\n\n'
                    ).format(Org(text, escape=False).to_html())
        return text


class Hr(Element):
    regex = Regex.hr

    def to_html(self):
        return '<hr/>'


class Paragraph(Element):
    label = '<p>{text}</p>'


class BlankLine(Element):
    regex = Regex.blankline

    def to_html(self):
        return ''


class Attr(Element):
    regex = Regex.attr


class Org(object):
    regex = OrderedDict([
        ('heading', Heading),
        ('unorderlist', UnorderList),
        ('orderlist', OrderList),
        ('table', Table),
        ('quote', BlockQuote),
        ('verse', Verse),
        ('center', Center),
        ('example', Example),
        ('src', Src),
        ('export', Export),
        ('hr', Hr),
        ('attr', Attr),
        ('blankline', BlankLine),
    ])

    def __init__(self, text, offset=0, toc=False, escape=False):
        self.text = text
        self.children = []
        self.parent = self
        self.current = self
        self.offset = offset
        self.escape = escape
        # startswith #+
        self.attr = {'property': {}}
        self.toc = Toc(self) if toc else None

    def parse_blankline(self, text, element):
        while isinstance(self.current, Paragraph):
            self.current = self.current.parent
        element = element(text)
        element.parent = self
        return element

    def parse_heading(self, text, element):
        element = element(text, self.offset, self.toc)
        element.parent = self
        return element

    def parse_hr(self, text, element):
        element = element(text)
        element.parent = self
        return element

    def parse_attr(self, text, element):
        m = element.regex.match(text)
        if not m.group(1):
            key, value = m.group(2), m.group(3)
            r = self.attr
            if key == "PROPERTY":
                r = self.attr['property']
                value = value.split(" ", 1)
                value.append("")
                key, value = value[0], value[1]
            r.update(**{key.lower(): value})

    def parse_paragraph(self, text):
        element = Paragraph(text, escape=self.escape)
        element.append(text)
        element.parent = self
        self.current = element
        return element

    def parse_outline(self, text, element):
        element = element(text, escape=self.escape)
        element.parent = self
        self.current = element
        return element

    def parse_end(self, text):
        if not self.current.end(text):
            return self.current.append(text)

        current = self.current
        while not isinstance(self.current, self.current.__class__):
            self.current = self.current.parent
        self.current = self.current.parent
        # List , Table need parse last line
        if isinstance(current, (List, Table)):
            return self.parse(text)

    def parse(self, text):
        for name, element in self.regex.items():
            if isinstance(self.current, OutlineElement):
                return self.parse_end(text)
            if element.regex.match(text):
                name = "parse_" + name
                return getattr(self, name)(text, element) if hasattr(
                    self, name) else self.parse_outline(text, element)

        if isinstance(self.current, Paragraph):
            self.current.append(text)
            return
        while isinstance(self.current, Paragraph):
            self.current = self.current.parent
        return self.parse_paragraph(text)

    def append(self, child):
        if isinstance(child, str):
            child = self.parse(child)
        if child and (not self.children or child != self.children[-1]):
            self.children.append(child)

    def to_html(self):
        [self.append(line.rstrip()) for line in self.text.splitlines()]
        text = '\n'.join([child.to_html() for child in self.children])
        if self.toc:
            text = self.toc.to_html() + text
        return text

    def __str__(self):
        return 'Org(' + ','.join([str(child) for child in self.children]) + ')'

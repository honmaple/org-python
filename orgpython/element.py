#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ********************************************************************************
# Copyright © 2018 jianglin
# File Name: element.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2018-02-26 11:44:43 (CST)
# Last Update: Tuesday 2018-02-27 10:12:06 (CST)
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

    def __init__(self, parent):
        self.parent = parent
        self.children = []

    def append(self, child):
        if self.children or child:
            if isinstance(child, str):
                child = Text(child)
            self.children.append(child)

    def to_html(self):
        text = '\n'.join([child.to_html() for child in self.children])
        return self.label.format(text=text)

    def __str__(self):
        str_children = [str(child) for child in self.children]
        return self.__class__.__name__ + '(' + ','.join(str_children) + ')'


class Heading(Element):
    label = '<h{level}>{title}</h{level}>'
    label1 = '<h{level} id="{tid}">{title}</h{level}>'
    regex = Regex.heading

    def __init__(self, text, offset=0, toc=False):
        self.text = text
        self.offset = offset
        self._toc = toc
        self.children = []

    def to_html(self):
        m = self.regex.match(self.text)
        level = len(m.group('level')) + self.offset
        title = m.group('title')
        text = self.label.format(level=level, title=title)
        if self._toc:
            tid = self.heading_id(text)
            text = self.label1.format(level=level, tid=tid, title=title)
            self.toc = '{}- <a href="#{}">{}</a>'.format(' ' * level, tid,
                                                         title)
        return text

    def heading_id(self, text):
        return 'org-{}'.format(int(time() * 10000))


class Src(Element):
    label = '<pre class="{lang}">\n{text}\n</pre>'

    def __init__(self, parent, lang='example'):
        self.parent = parent
        self.lang = lang
        self.flag = False
        self.children = []

    def append(self, child):
        if self.children or child:
            if isinstance(child, str):
                child = Text(child, False)
            self.children.append(child)

    def to_html(self):
        text = '\n'.join([child.to_html() for child in self.children])
        text = dedent(text)
        return self.label.format(lang=self.lang, text=text)

    def end(self, text):
        return Regex.end_src.match(text)


class Example(Src):
    def end(self, text):
        return Regex.end_example.match(text)


class Export(Src):
    label = '{text}'

    def __init__(self, parent):
        self.parent = parent
        self.flag = False
        self.children = []

    def to_html(self):
        text = '\n'.join([child.to_html() for child in self.children])
        return self.label.format(text=text)

    def end(self, text):
        return Regex.end_export.match(text)


class Verse(Element):
    label = '<p class="org-verse">\n{text}\n</p>'

    def __init__(self, parent):
        self.parent = parent
        self.flag = False
        self.children = []

    def to_html(self):
        text = '<br/>\n'.join([child.to_html() for child in self.children])
        return self.label.format(text=text)

    def end(self, text):
        return Regex.end_verse.match(text)


class Center(Element):
    label = '<div class="org-center">\n{text}\n</div>'

    def __init__(self, parent):
        self.parent = parent
        self.flag = False
        self.children = [Org('', parse=False)]

    def append(self, child):
        self.children[0].parse(child)

    def end(self, text):
        return Regex.end_center.match(text)


class BlockQuote(Element):
    label = '<blockquote>\n{text}\n</blockquote>'

    def __init__(self, parent):
        self.parent = parent
        self.flag = False
        self.children = [Org('', parse=False)]

    def append(self, child):
        self.children[0].parse(child)

    def end(self, text):
        return Regex.end_quote.match(text)


class ListItem(Element):
    label = '<li>{text}</li>'

    def __init__(self, parent, depth):
        self.parent = parent
        self.depth = depth
        self.flag = False
        self.children = [Org('', parse=False)]

    def append(self, child):
        if not self.children[0].children:
            self.children[0].append(Text(child))
        else:
            self.children[0].parse(child)


class List(Element):
    regex = None

    def __init__(self, parent, depth):
        self.parent = parent
        self.depth = depth
        self.flag = False
        self.children = []
        self.current = ListItem(self, depth)

    def append(self, child):
        if self.regex.match(child):
            m = self.regex.match(child)
            depth = len(m.group('depth'))
            title = m.group('title')
            checkbox = Regex.checkbox.match(title)
            if checkbox:
                title = '<input type="checkbox" />{}'
                if checkbox.group('check') == 'X':
                    title = '<input type="checkbox" checked="checked" />{}'
                title = title.format(checkbox.group('title'))
            if depth == self.depth:
                element = ListItem(self.current, depth)
                element.append(title)
                self.children.append(element)
                self.current = element
            elif depth > self.depth:
                self.current.append(child)
        else:
            self.current.append(child)

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


class TableRow(Element):
    label = '<tr>\n{text}\n</tr>'

    def append(self, child):
        m = Regex.table.match(child)
        cells = [c for c in m.group('cells').split('|') if c]
        child = ''
        for cell in cells:
            child += '<td>{text}</td>'.format(text=cell.strip())
        child = Text(child)
        self.children.append(child)


class Table(Element):
    label = '<table>\n{text}\n</table>'

    def __init__(self, parent):
        self.parent = parent
        self.flag = False
        self.children = []

    def append(self, child):
        if Regex.table_sep.match(child):
            # th instead of td only once
            td = re.compile(r'<td>(.*?)</td>')
            text = '\n'.join([ch.to_html() for ch in self.children])
            text = td.sub(lambda match: match.group(0).replace('td', 'th'),
                          text)
            self.children = [Text(text)]
        else:
            row = TableRow(self)
            row.append(child)
            self.children.append(row)

    def end(self, text):
        return not Regex.table.match(text)


class Toc(Element):
    def __init__(self, parent):
        self.parent = parent
        self.flag = False
        self.children = []

    def append(self, child):
        self.children.append(child)

    def to_html(self):
        text = '\n'.join([child.toc for child in self.children])
        if text:
            text = ('<div id="table-of-contents">'
                    '<h2>Table of Contents</h2>'
                    '<div id="text-table-of-contents">{}\n</div></div>\n\n'
                    ).format(Org(text).to_html())
        return text


class Hr(Element):
    def to_html(self):
        return '<hr/>'


class Paragraph(Element):
    label = '<p>{text}</p>'


class Org(object):
    class _end:
        def __init__(self, _self):
            self._self = _self

        def match(self, text):
            _self = self._self
            return hasattr(_self.current, 'flag') and _self.current.flag

    regex = OrderedDict([
        ('end', _end),
        ('heading', Regex.heading),
        ('unorderlist', Regex.unorder_list),
        ('orderlist', Regex.order_list),
        ('table', Regex.table),
        ('quote', Regex.begin_quote),
        ('verse', Regex.begin_verse),
        ('center', Regex.begin_center),
        ('example', Regex.begin_example),
        ('src', Regex.begin_src),
        ('export', Regex.begin_export),
        ('hr', Regex.hr),
        ('attr', Regex.attr),
        ('blankline', Regex.blankline),
    ])
    del _end

    def __init__(self, text, offset=0, toc=False, parse=True):
        self.text = text
        self.children = []
        self.parent = self
        self.current = self
        self.offset = offset
        self.toc = Toc(self)
        self.toc.flag = toc
        if parse:
            self._parse(text)

    def _parse(self, text):
        for line in text.splitlines():
            self.parse(line.rstrip())

    def parse(self, text):
        for parse, regex in self.regex.items():
            if callable(regex):
                regex = regex(self)
            if regex.match(text):
                return getattr(self, 'parse_' + parse)(text)
        if isinstance(self.current, Paragraph):
            self.current.append(text.strip())
        else:
            while isinstance(self.current, Paragraph):
                self.current = self.current.parent
            element = Paragraph(self.current)
            element.append(text.strip())
            self.children.append(element)
            self.current = element

    def begin_init(self, element):
        self.current.append(element)
        self.current = element
        self.current.flag = True

    def end_init(self, element):
        if not self.current.flag:
            raise NotBeginError
        self.current.flag = False
        while not isinstance(self.current, element):
            if isinstance(self.current, Org):
                raise NotBeginError
            self.current = self.current.parent
        self.current = self.current.parent

    def parse_end(self, text):
        if not self.current.end(text):
            self.current.append(text)
        else:
            e = self.current
            self.end_init(self.current.__class__)
            if isinstance(e, (UnorderList, OrderList)):
                self.parse(text)

    def parse_blankline(self, text):
        while isinstance(self.current, Paragraph):
            self.current = self.current.parent
        self.children.append(Text(''))

    def parse_heading(self, text):
        element = Heading(text, self.offset, self.toc.flag)
        self.toc.append(element)
        self.children.append(element)

    def parse_hr(self, text):
        element = Hr(self)
        self.children.append(element)

    def parse_unorderlist(self, text):
        while isinstance(self.current, Paragraph):
            self.current = self.current.parent
        m = Regex.unorder_list.match(text)
        depth = len(m.group('depth'))
        element = UnorderList(self.current, depth)
        element.append(text)
        self.begin_init(element)

    def parse_orderlist(self, text):
        while isinstance(self.current, Paragraph):
            self.current = self.current.parent
        m = Regex.order_list.match(text)
        depth = len(m.group('depth'))
        element = OrderList(self.current, depth)
        element.append(text)
        self.begin_init(element)

    def parse_table(self, text):
        element = Table(self.current)
        element.append(text)
        self.begin_init(element)

    def parse_src(self, text):
        lang = Regex.begin_src.match(text).group('lang')
        element = Src(self.current, lang)
        self.begin_init(element)

    def parse_example(self, text):
        element = Example(self.current)
        self.begin_init(element)

    def parse_quote(self, text):
        element = BlockQuote(self.current)
        self.begin_init(element)

    def parse_center(self, text):
        element = Center(self.current)
        self.begin_init(element)

    def parse_verse(self, text):
        element = Verse(self.current)
        self.begin_init(element)

    def parse_export(self, text):
        element = Export(self.current)
        self.begin_init(element)

    def parse_attr(self, text):
        pass

    def append(self, child):
        if isinstance(child, str):
            child = Text(child)
        self.children.append(child)
        child.parent = self

    def to_html(self):
        text = '\n'.join([child.to_html() for child in self.children])
        if self.toc.flag:
            text = self.toc.to_html() + text
        return text

    def __str__(self):
        return 'Org(' + ','.join([str(child) for child in self.children]) + ')'

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: orgpython.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-07-12 21:21:00 (CST)
# Last Update:星期五 2017-7-21 9:23:27 (CST)
#          By:
# Description:
# **************************************************************************
import re
from time import time


class Regex(object):
    newline = re.compile(r'^$')
    heading = re.compile(r'^(?P<level>\*+)\s+(?P<title>.+)$')
    comment = re.compile(r'^(\s*)#(.*)$')
    bold = re.compile(r'( |^)\*(?P<text>[\S]+)\*')
    # italic = re.compile(r'(\*\*|/)(?P<text>[\S]+?)(\*\*|/)')
    italic = re.compile(r'( |^)\*\*(?P<text>[\S]+)\*\*')
    underlined = re.compile(r'( |^)_(?P<text>[\S]+)_')
    code = re.compile(r'( |^)=(?P<text>[\S]+)=')
    delete = re.compile(r'( |^)\+(?P<text>[\S]+)\+')
    verbatim = re.compile(r'( |^)~(?P<text>[\S]+)~')
    image = re.compile(r'\[\[(?P<src>.+?)\](?:\[(?P<alt>.+?)\])?\]')
    link = re.compile(r'\[\[(?P<href>https?://.+?)\](?:\[(?P<text>.+?)\])?\]')
    fn = re.compile(r'\[fn:(?P<text>.+?)\]')

    begin_example = re.compile(r'\s*#\+BEGIN_EXAMPLE$')
    end_example = re.compile(r'\s*#\+END_EXAMPLE$')

    begin_quote = re.compile(r'\s*#\+BEGIN_QUOTE$')
    end_quote = re.compile(r'\s*#\+END_QUOTE$')

    begin_src = re.compile(r'\s*#\+BEGIN_SRC\s+(?P<lang>.+)$')
    end_src = re.compile(r'\s*#\+END_SRC$')

    any_depth = re.compile(r'(?P<depth>\s*)(?P<title>.+)$')
    order_list = re.compile(r'(?P<depth>\s*)\d+(\.|\))\s+(?P<title>.+)$')
    unorder_list = re.compile(r'(?P<depth>\s*)(-|\+)\s+(?P<title>.+)$')
    checkbox = re.compile(r'[[](?P<check>.+)[]]\s+(?P<title>.+)$')

    table = re.compile(r'\s*\|(?P<cells>(.+\|)+)s*$')
    table_sep = re.compile(r'^(\s*)\|((?:\+|-)*?)\|?$')
    table_setting = re.compile(r'\s*#\+ATTR_HTML:\s*:class\s*(?P<cls>.+)$')

    attr = re.compile(r'^(\s*)#\+(.*)$')


class NotBeginError(Exception):
    pass


class InlineElement(object):
    label = '{text}'
    regex = None

    def __init__(self, text):
        self.text = text
        self.children = []

    def to_html(self):
        return self.parse(self.text)

    def parse(self, text):
        return self.regex.sub(
            lambda match: self.label.format(text=match.group('text')), text)

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, self.text.strip())


class Fn(InlineElement):
    '''
    <sup><a id="fnr.1" class="footref" href="#fn.1">1</a></sup>
    '''
    label = '<sup><a id="fnr:{text}" class="footref" href="#fn.{text}">{text}</a></sup>'
    regex = Regex.fn


class Underlined(InlineElement):
    label = '<span style="text-decoration:underline">{text}</span>'
    regex = Regex.underlined


class Bold(InlineElement):
    label = '<b>{text}</b>'
    regex = Regex.bold


class Italic(InlineElement):
    label = '<i>{text}</i>'
    regex = Regex.italic


class Code(InlineElement):
    label = '<code>{text}</code>'
    regex = Regex.code


class Delete(InlineElement):
    label = '<del>{text}</del>'
    regex = Regex.delete


class Verbatim(InlineElement):
    label = '<code>{text}</code>'
    regex = Regex.verbatim


class Image(InlineElement):
    label = '<img alt="{alt}" src="{src}"/>'
    label1 = '<img src="{src}"/>'
    regex = Regex.image

    def parse(self, text):
        # return self.regex.sub(
        #     lambda match: self.label.format(text=match.group('text'))
        #     if not match.group('alt') else
        #     self.label.format(src=match.group('src'),
        #                       alt=match.group('alt')), text)
        for t in self.regex.finditer(text):
            if not t.group('alt'):
                string = self.label1.format(src=t.group('src'))
            else:
                string = self.label.format(
                    src=t.group('src'), alt=t.group('alt'))
            text = self.regex.sub(string, text, 1)
        return text


class Link(InlineElement):
    label = '<a href="{href}">{text}</a>'
    regex = Regex.link

    def parse(self, text):
        return self.regex.sub(
            lambda match: self.label.format(href=match.group('href'),
                                       text=match.group('text')), text)
        # for t in self.regex.finditer(text):
        #     string = self.label.format(
        #         href=t.group('href'), text=t.group('text'))
        #     text = self.regex.sub(string, text, 1)
        # return text


class Heading(InlineElement):
    label = '<h{level}>{title}</h{level}>'
    label1 = '<h{level} id="{tid}">{title}</h{level}>'
    regex = Regex.heading

    def __init__(self, text, offset=0, toc=False):
        self.text = text
        self.offset = offset
        self._toc = toc
        self.children = []

    def parse(self, text):
        m = Regex.heading.match(text)
        level = len(m.group('level')) + self.offset
        title = m.group('title')
        text = self.label.format(level=level, title=title)
        if self._toc:
            tid = 'org-{}'.format(int(time() * 10000))
            text = self.label1.format(level=level, tid=tid, title=title)
            self.toc = '{}- <a href="#{}">{}</a>'.format(' ' * level, tid,
                                                         title)
        return text


class Text(InlineElement):
    def __init__(self, text, no_parse=False):
        self.text = text
        self.no_parse = no_parse

    def parse(self, text):
        if not isinstance(text, str):
            text = text.to_html()
        if Regex.comment.search(text) or self.no_parse:
            return text
        elif Regex.italic.search(text):
            return self.parse(Italic(text))
        elif Regex.bold.search(text):
            return self.parse(Bold(text))
        elif Regex.underlined.search(text):
            return self.parse(Underlined(text))
        elif Regex.code.search(text):
            return self.parse(Code(text))
        elif Regex.delete.search(text):
            return self.parse(Delete(text))
        elif Regex.verbatim.search(text):
            return self.parse(Verbatim(text))
        elif Regex.fn.search(text):
            return self.parse(Fn(text))
        else:
            return self.parse_other(text)

    def parse_other(self, text):
        if Regex.link.search(text):
            text = Link(text).to_html()
        elif Regex.image.search(text):
            text = Image(text).to_html()
        return text

    def to_html(self):
        return self.parse(self.text)


class Element(object):
    label = '{text}'
    regex = None

    def __init__(self, parent):
        self.parent = parent
        self.children = []

    def append(self, child):
        if isinstance(child, str):
            child = Text(child)
        self.children.append(child)

    def to_html(self):
        text = '\n'.join([child.to_html() for child in self.children])
        return self.label.format(text=text)

    def __str__(self):
        str_children = [str(child) for child in self.children]
        return self.__class__.__name__ + '(' + ','.join(str_children) + ')'


class Example(Element):
    label = '\n<pre class="example"><code>\n{text}\n</code></pre>\n'

    def __init__(self, parent):
        self.parent = parent
        self.flag = False
        self.children = []

    def append(self, child):
        if isinstance(child, str):
            child = Text(child, True)
        self.children.append(child)

    def end(self, text):
        return Regex.end_example.match(text)


class Src(Element):
    label = '<pre class="{lang}"><code>\n{text}\n</code></pre>'

    def __init__(self, parent, lang='python'):
        self.parent = parent
        self.lang = lang
        self.flag = False
        self.children = []

    def append(self, child):
        if isinstance(child, str):
            child = Text(child, True)
        self.children.append(child)

    def to_html(self):
        text = '\n'.join([child.to_html() for child in self.children])
        return self.label.format(lang=self.lang, text=text)

    def end(self, text):
        return Regex.end_src.match(text)


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


class Paragraph(Element):
    label = '<p>{text}</p>'


class Org(object):
    def __init__(self, text, offset=0, toc=False, parse=True):
        self.text = text
        self.children = []
        self.parent = self
        self.current = self
        self.offset = offset
        self.toc = Toc(self)
        self.toc.flag = toc
        if parse:
            for line in text.splitlines():
                self.parse(line.rstrip())

    def parse(self, text):
        if hasattr(self.current, 'flag') and self.current.flag:
            self.parse_end(text)
        elif Regex.heading.match(text):
            self.parse_heading(text)
        elif Regex.unorder_list.match(text):
            self.parse_unorderlist(text)
        elif Regex.order_list.match(text):
            self.parse_orderlist(text)
        elif Regex.table.match(text):
            self.parse_table(text)
        elif Regex.begin_quote.match(text):
            self.parse_quote(text)
        elif Regex.begin_example.match(text):
            self.parse_example(text)
        elif Regex.begin_src.match(text):
            self.parse_src(text)
        elif Regex.attr.match(text):
            pass
        elif not text.strip():
            while isinstance(self.current, Paragraph):
                self.current = self.current.parent
            self.children.append(Text(''))
        elif isinstance(self.current, Paragraph):
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

    def parse_heading(self, text):
        element = Heading(text, self.offset, self.toc.flag)
        self.toc.append(element)
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


def org_to_html(text, offset=0, toc=True):
    return Org(text, offset, toc).to_html()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: org.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-03-15 14:48:01 (CST)
# Last Update:星期四 2017-3-16 16:45:37 (CST)
#          By:
# Description:
# **************************************************************************
import re
from html import escape


class Regex(object):
    header = re.compile(r'^(?P<level>\*+)\s+(?P<title>.+)$')
    bold = re.compile(r'\*(?P<text>[\S]+?)\*')
    # italic = re.compile(r'(\*\*|/)(?P<text>[\S]+?)(\*\*|/)')
    italic = re.compile(r'\*\*(?P<text>[\S]+?)\*\*')
    underlined = re.compile(r'_(?P<text>[\S]+?)_')
    code = re.compile(r'=(?P<text>[\S]+?)=')
    delete = re.compile(r'\+(?P<text>[\S]+?)\+')
    verbatim = re.compile(r'~(?P<text>[\S]+?)~')
    image = re.compile(r'\[\[(?P<src>.+?)\](?:\[(?P<alt>.+?)\])?\]')
    link = re.compile(r'\[\[(?P<href>https?://.+?)\](?:\[(?P<text>.+?)\])?\]')

    begin_example = re.compile(r'^#\+BEGIN_EXAMPLE$')
    end_example = re.compile(r'^#\+END_EXAMPLE$')

    begin_quote = re.compile(r'^#\+BEGIN_QUOTE$')
    end_quote = re.compile(r'^#\+END_QUOTE$')

    begin_src = re.compile(r'#\+BEGIN_SRC\s*(?P<lang>.+)$')
    end_src = re.compile(r'^#\+END_SRC$')

    order_list = re.compile(r'(?P<depth>\s*)\d+(\.|\))\s+(?P<item>.+)$')
    unorder_list = re.compile(r'(?P<depth>\s*)(-|\+)\s+(?P<item>.+)$')

    table = re.compile(r'\s*\|(?P<cells>(.+\|)+)s*$')


class Element(object):
    def __init__(self, regex):
        self.regex = regex


class Node(object):
    label = ''

    def __init__(self, text):
        self.text = text

    @property
    def html(self):
        return '<{label}>{text}</{label}>'.format(
            label=self.label, text=self.text)


class Header(Element):
    def __init__(self, regex, offset=1):
        self.offset = offset
        self.regex = regex

    def parse(self, text):
        m = self.regex.match(text)
        level = len(m.group('level')) + (self.offset - 1)
        title = m.group('title')
        return '<h{level}>{title}</h{level}>'.format(
            level=level, title=title)


class Table(Element):
    def __init__(self, regex):
        self.regex = regex

    def parse(self, text):
        m = self.regex.match(text)
        cells = [c for c in m.group('cells').split('|') if c != '']
        strings = ''
        for cell in cells:
            strings += '<td>{text}</td>'.format(text=cell.strip())
        return '<tr>{text}</tr>'.format(text=strings)


class UnorderList(Element):
    def __init__(self, regex, depth):
        self.regex = regex
        self.depth = depth
        self.times = 0

    def parse(self, text):
        m = self.regex.match(text)
        depth = len(m.group('depth')) + 1
        item = m.group('item')
        if depth > self.depth:
            string = '<ul><li>{item}'.format(item=item)
            self.times += 1
        elif depth < self.depth:
            string = '</li></ul></li><li>{item}'.format(item=item)
            self.times -= 1
        else:
            string = '</li><li>{item}'.format(item=item)
        self.depth = depth
        return string


class OrderList(Element):
    def __init__(self, regex, depth):
        self.regex = regex
        self.depth = depth
        self.times = 0

    def parse(self, text):
        m = self.regex.match(text)
        depth = len(m.group('depth')) + 1
        item = m.group('item')
        if depth > self.depth:
            string = '<ol><li>{item}'.format(item=item)
            self.times += 1
        elif depth < self.depth:
            string = '</li></ol></li><li>{item}'.format(item=item)
            self.times -= 1
        else:
            string = '</li><li>{item}'.format(item=item)
        self.depth = depth
        return string


class Src(object):
    def __init__(self, lang='example'):
        self.lang = lang

    def parse(self, text):
        return '<pre class="{lang}"><code>{text}</code></pre>'.format(
            text=text, lang=self.lang)


class BlockQuote(object):
    def parse(self, text):
        return '<blockquote>{text}</blockquote>'.format(text=text)


class TextNode(object):
    label = '<span>{text}</span>'

    def __init__(self, regex):
        self.regex = regex

    def parse(self, text):
        for t in self.regex.finditer(text):
            string = self.label.format(text=t.group('text'))
            text = self.regex.sub(string, text)
        return text


class Underlined(TextNode):
    label = '<span style="text-decoration:underline">{text}</span>'


class Bold(TextNode):
    label = '<b>{text}</b>'


class Italic(TextNode):
    label = '<i>{text}</i>'


class Code(TextNode):
    label = '<code>{text}</code>'


class Delete(TextNode):
    label = '<del>{text}</del>'


class Verbatim(TextNode):
    label = '<code>{text}</code>'


class Image(TextNode):
    label = '<img alt="{alt}" src="{src}"/>'

    def parse(self, text):
        for t in self.regex.finditer(text):
            string = self.label.format(src=t.group('src'), alt=t.group('alt'))
            text = self.regex.sub(string, text)
        return text


class Link(TextNode):
    label = '<a href="{href}">{text}</a>'

    def parse(self, text):
        for t in self.regex.finditer(text):
            string = self.label.format(
                href=t.group('href'), text=t.group('text'))
            text = self.regex.sub(string, text)
        return text


class Text(object):
    def __init__(self, line):
        self._html = ''
        self.flag = False
        self.parse(line)

    def parse(self, text):
        if self.flag:
            return self._html
        if Regex.italic.search(text):
            text = Italic(Regex.italic).parse(text)
            return self.parse(text)
        elif Regex.bold.search(text):
            text = Bold(Regex.bold).parse(text)
            return self.parse(text)
        elif Regex.underlined.search(text):
            text = Underlined(Regex.underlined).parse(text)
            return self.parse(text)
        elif Regex.code.search(text):
            text = Code(Regex.code).parse(text)
            return self.parse(text)
        elif Regex.delete.search(text):
            text = Delete(Regex.delete).parse(text)
            return self.parse(text)
        elif Regex.verbatim.search(text):
            text = Verbatim(Regex.verbatim).parse(text)
            return self.parse(text)
        else:
            self._html += self.parse_other(text)
            self.flag = True

    def parse_other(self, text):
        if Regex.link.search(text):
            text = Link(Regex.link).parse(text)
        elif Regex.image.search(text):
            text = Image(Regex.image).parse(text)
        return text

    @property
    def html(self):
        return self._html


class OrgMode(object):
    def __init__(self):
        self.regex = Regex
        self._html = ''
        self._headers = []
        self._example_flag = False
        self._quote_flag = False
        self._src_flag = False
        self._table_flag = False
        self._src_lang = 'python'
        self._begin_buffer = ''
        self.elements = []
        self.current = self
        self._order_list_times = 0
        self._order_list_depth = -1
        self._order_list_flag = False
        self._unorder_list_times = 0
        self._unorder_list_depth = -1
        self._unorder_list_flag = False

    def close_order_list(self, force=False):
        if force or (self._order_list_flag and self._order_list_times == 1):
            self.current.append('</li></ol>' * self._order_list_times)
            self._order_list_flag = False
            self._order_list_times = 0
            self._order_list_depth = -1

    def close_unorder_list(self, force=False):
        if force or (self._unorder_list_flag and
                     self._unorder_list_times == 1):
            self.current.append('</li></ul>' * self._unorder_list_times)
            self._unorder_list_flag = False
            self._unorder_list_times = 0
            self._unorder_list_depth = -1

    def close_table(self, force=False):
        if force or self._table_flag:
            self.current.append('</tbody></table>')
            self._table_flag = False

    def close(self):
        self.close_order_list()
        self.close_unorder_list()
        self.close_table()

    def parse(self, text):
        text = text.splitlines()
        for line in text:
            line = escape(line.strip(), True)
            if Regex.unorder_list.match(line):
                self.parse_unorder_list(line)
            elif Regex.order_list.match(line):
                self.parse_order_list(line)
            elif Regex.table.match(line):
                self.parse_table(line)
            else:
                self.close()
                self._parse(line)

    def _parse(self, text):
        if self._example_flag:
            self.parse_example(text)
        elif self._quote_flag:
            self.parse_quote(text)
        elif self._src_flag:
            self.parse_src(text)
        elif Regex.header.match(text):
            self.parse_header(text)
        elif Regex.begin_example.match(text):
            self._example_flag = True
        elif Regex.begin_quote.match(text):
            self._quote_flag = True
        elif Regex.begin_src.match(text):
            self._src_flag = True
            self._src_lang = Regex.begin_src.match(text).group('lang')
        else:
            text = Text(text).html
            self._html += text

    def parse_unorder_list(self, text):
        l = UnorderList(Regex.unorder_list, self._unorder_list_depth)
        string = l.parse(text)
        self._unorder_list_times += l.times
        self._unorder_list_depth = l.depth
        self._unorder_list_flag = True
        if self._order_list_flag and (
                self._unorder_list_depth < self._order_list_depth):
            self.close_order_list(True)
        self.current.append(string)

    def parse_order_list(self, text):
        l = OrderList(Regex.order_list, self._order_list_depth)
        string = l.parse(text)
        self._order_list_times += l.times
        self._order_list_depth = l.depth
        self._order_list_flag = True
        if self._unorder_list_flag and (
                self._order_list_depth < self._unorder_list_depth):
            self.close_unorder_list(True)
        self.current.append(string)

    def parse_table(self, text):
        if not self._table_flag:
            self.current.append('<table><tbody>')
            self._table_flag = True
        table = Table(Regex.table)
        self.elements.append(table)
        self.current.append(table.parse(text))

    def parse_header(self, text):
        header = Header(Regex.header)
        self.elements.append(header)
        self._html += header.parse(text)

    def parse_example(self, text):
        if Regex.end_example.match(text):
            if not self._example_flag:
                raise ValueError('ssss')
            string = Src('example').parse(self._begin_buffer)
            self.current.append(string)
            self._example_flag = False
            self._begin_buffer = ''
        else:
            self._begin_buffer += text

    def parse_src(self, text):
        if Regex.end_src.match(text):
            if not self._src_flag:
                raise ValueError('ssss')
            string = Src(self._src_lang).parse(self._begin_buffer)
            self.current.append(string)
            self._src_flag = False
            self._begin_buffer = ''
        else:
            self._begin_buffer += text

    def parse_quote(self, text):
        if Regex.end_quote.match(text):
            if not self._quote_flag:
                raise ValueError('ssss')
            string = BlockQuote().parse(self._begin_buffer)
            self.current.append(string)
            self._quote_flag = False
            self._begin_buffer = ''
        else:
            text = Text(text).html
            self._begin_buffer += text

    def append(self, text):
        self._html += text

    def to_html(self):
        self.close()
        return self._html


def orgmode(text):
    org = OrgMode()
    org.parse(text)
    return org

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: org.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-03-15 14:48:01 (CST)
# Last Update:星期六 2017-3-18 23:39:12 (CST)
#          By:
# Description:
# **************************************************************************
import re
from time import time


class Regex(object):
    heading = re.compile(r'^(?P<level>\*+)\s+(?P<title>.+)$')
    bold = re.compile(r'\*(?P<text>[\S]+?)\*')
    # italic = re.compile(r'(\*\*|/)(?P<text>[\S]+?)(\*\*|/)')
    italic = re.compile(r'\*\*(?P<text>[\S]+?)\*\*')
    underlined = re.compile(r'_(?P<text>[\S]+?)_')
    code = re.compile(r'=(?P<text>[\S]+?)=')
    delete = re.compile(r'\+(?P<text>[\S]+?)\+')
    verbatim = re.compile(r'~(?P<text>[\S]+?)~')
    image = re.compile(r'\[\[(?P<src>.+?)\](?:\[(?P<alt>.+?)\])?\]')
    link = re.compile(r'\[\[(?P<href>https?://.+?)\](?:\[(?P<text>.+?)\])?\]')
    fn = re.compile(r'\[fn:(?P<text>.+?)\]')
    begin_example = re.compile(r'\s*#\+BEGIN_EXAMPLE$')
    end_example = re.compile(r'\s*#\+END_EXAMPLE$')

    begin_quote = re.compile(r'\s*#\+BEGIN_QUOTE$')
    end_quote = re.compile(r'\s*#\+END_QUOTE$')

    begin_src = re.compile(r'\s*#\+BEGIN_SRC\s*(?P<lang>.+)$')
    end_src = re.compile(r'\s*#\+END_SRC$')

    order_list = re.compile(r'(?P<depth>\s*)\d+(\.|\))\s+(?P<item>.+)$')
    unorder_list = re.compile(r'(?P<depth>\s*)(-|\+)\s+(?P<item>.+)$')

    table = re.compile(r'\s*\|(?P<cells>(.+\|)+)s*$')
    table_setting = re.compile(r'\s*#\+ATTR_HTML:\s*:class\s*(?P<cls>.+)$')


class Element(object):
    label = '<span>{text}</span>'

    def __init__(self, regex):
        self.regex = regex

    def parse(self, text):
        for t in self.regex.finditer(text):
            string = self.label.format(text=t.group('text'))
            text = self.regex.sub(string, text)
        return text


class Fn(Element):
    '''
    <sup><a id="fnr.1" class="footref" href="#fn.1">1</a></sup>
    '''
    label = '<sup><a id="fnr:{text}" class="footref" href="#fn.{text}">{text}</a></sup>'


class Underlined(Element):
    label = '<span style="text-decoration:underline">{text}</span>'


class Bold(Element):
    label = '<b>{text}</b>'


class Italic(Element):
    label = '<i>{text}</i>'


class Code(Element):
    label = '<code>{text}</code>'


class Delete(Element):
    label = '<del>{text}</del>'


class Verbatim(Element):
    label = '<code>{text}</code>'


class Image(Element):
    label = '<img alt="{alt}" src="{src}"/>'

    def parse(self, text):
        for t in self.regex.finditer(text):
            string = self.label.format(src=t.group('src'), alt=t.group('alt'))
            text = self.regex.sub(string, text)
        return text


class Link(Element):
    label = '<a href="{href}">{text}</a>'

    def parse(self, text):
        for t in self.regex.finditer(text):
            string = self.label.format(
                href=t.group('href'), text=t.group('text'))
            text = self.regex.sub(string, text)
        return text


class Heading(Element):
    def __init__(self, to_toc=True):
        self.to_toc = to_toc
        self.toc = ''
        self.init()

    def init(self):
        self.string = ''
        self.offset = 1

    def append(self, text):
        m = Regex.heading.match(text)
        level = len(m.group('level')) + (self.offset - 1)
        title = m.group('title')
        html_id = int(time() * 10000)
        self.string = '<h{level} id="{id}">{title}</h{level}>'.format(
            level=level, title=title, id=html_id)
        if self.to_toc:
            self.toc += ' ' * level + '- <a href="#{id}">{title}</a>\n'.format(
                title=title, id=html_id)

    def to_html(self):
        text = self.string
        self.init()
        return text


class Table(Element):
    def __init__(self):
        self.init()

    def init(self):
        self.flag = False
        self.has_th = False
        self.string = ''

    def append(self, text):
        if not self.flag:
            self.flag = True
        m = Regex.table.match(text)
        has_th = m.group('cells').replace('-', '').replace('+', '').replace(
            '|', '')
        if not self.has_th and not has_th and self.string:
            self.has_th = True
            td = re.compile(r'<td>(.*?)</td>')
            self.string = td.sub(
                lambda match: match.group(0).replace('td', 'th'), self.string)
        if has_th:
            cells = [c for c in m.group('cells').split('|') if c]
            strings = ''
            for cell in cells:
                strings += '<td>{text}</td>'.format(text=cell.strip())
            self.string += '<tr>{text}</tr>'.format(text=strings)

    def to_html(self):
        text = '<table class="table table-bordered table-hover"><tbody>{text}</tbody></table>'.format(
            text=self.string)
        self.init()
        return text


class Text(object):
    def __init__(self, no_parse=False):
        self.no_parse = no_parse
        self.init()

    def init(self):
        self.string = ''

    def append(self, text):
        if self.no_parse:
            self.string += (text + '\n')
        else:
            self.string += (self.parse(text) + '\n')

    def parse(self, text):
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
        elif Regex.fn.search(text):
            text = Fn(Regex.fn).parse(text)
            return self.parse(text)
        else:
            return self.parse_other(text)

    def parse_other(self, text):
        if Regex.link.search(text):
            text = Link(Regex.link).parse(text)
        elif Regex.image.search(text):
            text = Image(Regex.image).parse(text)
        return text

    def to_html(self):
        return self.string


class Src(Element):
    def __init__(self):
        self.children = Text(no_parse=True)
        self.init()

    def init(self):
        self.flag = False
        self.lang = 'example'
        self.children.init()

    def append(self, text):
        if not self.flag:
            self.flag = True
        self.lang = Regex.begin_src.match(text).group('lang')

    def to_html(self):
        text = '<pre class="{lang}"><code>{text}</code></pre>'.format(
            text=self.children.to_html(), lang=self.lang)
        self.init()
        return text


class Example(Element):
    def __init__(self):
        self.children = Text(no_parse=True)
        self.init()

    def init(self):
        self.flag = False
        self.lang = 'example'
        self.children.init()

    def append(self, text):
        if not self.flag:
            self.flag = True

    def to_html(self):
        text = '<pre class="{lang}"><code>{text}</code></pre>'.format(
            text=self.children.to_html(), lang=self.lang)
        self.init()
        return text


class BlockQuote(object):
    def __init__(self):
        self.children = Text()
        self.init()

    def init(self):
        self.flag = False
        self.children.init()

    def append(self, text):
        if not self.flag:
            self.flag = True

    def to_html(self):
        text = '<blockquote>{text}</blockquote>'.format(
            text=self.children.to_html())
        self.init()
        return text


class UnderedList1(object):
    def __init__(self):
        self.children = Text()
        self.init()

    def init(self):
        self.flag = False
        self.string = ''
        self.depth = -1
        self.times = 0

    def append(self, text):
        if not self.flag:
            self.flag = True
        m = Regex.unorder_list.match(text)
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
        self.string = string

    def to_html(self):
        return self.string


class OrderedList1(object):
    def __init__(self):
        self.children = Text()
        self.init()

    def init(self):
        self.flag = False
        self.string = ''
        self.depth = -1
        self.times = 0

    def append(self, text):
        if not self.flag:
            self.flag = True
        m = Regex.order_list.match(text)
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
        self.string = string

    def to_html(self):
        return self.string


class OrgContent(object):
    def __init__(self):
        self.string = ''

    def append(self, text):
        self.string += (text + '\n')

    def to_html(self):
        return self.string


class OrgMode(object):
    def __init__(self, toc=True, offset=1):
        self.heading_offset = offset
        self.heading_toc = toc
        self.content = OrgContent()
        self.src = Src()
        self.example = Example()
        self.blockquote = BlockQuote()
        self.table = Table()
        self.heading = Heading()
        self.text = Text()
        self.unordered_list = UnderedList1()
        self.ordered_list = OrderedList1()

    def close_order_list(self, force=False):
        if force or (self.ordered_list.flag and self.ordered_list.times >= 1):
            self.content.append('</li></ol>' * self.ordered_list.times)
            self.ordered_list.init()

    def close_unorder_list(self, force=False):
        if force or (self.unordered_list.flag and
                     self.unordered_list.times >= 1):
            self.content.append('</li></ul>' * self.unordered_list.times)
            self.unordered_list.init()

    def close(self):
        self.close_unorder_list()
        self.close_order_list()

    def parse_unordered_list(self, text):
        self.unordered_list.append(text)
        if self.ordered_list.flag and (
                self.unordered_list.depth < self.ordered_list.depth):
            self.close_order_list(True)
        self.content.append(self.unordered_list.to_html())

    def parse_ordered_list(self, text):
        self.ordered_list.append(text)
        if self.unordered_list.flag and (
                self.ordered_list.depth < self.unordered_list.depth):
            self.close_unorder_list(True)
        self.content.append(self.ordered_list.to_html())

    def parse_text(self, text):
        self.text.append(text)
        self.content.append(self.text.to_html())
        self.text.init()

    def parse_table(self, text):
        self.table.append(text)

    def parse_heading(self, text):
        self.heading.append(text)
        self.content.append(self.heading.to_html())

    def parse_example(self, text):
        if Regex.end_example.match(text):
            if not self.example.flag:
                raise ValueError('ssss')
            self.content.append(self.example.to_html())
        else:
            self.example.children.append(text)

    def parse_src(self, text):
        if Regex.end_src.match(text):
            if not self.src.flag:
                raise ValueError('ssss')
            self.content.append(self.src.to_html())
        else:
            self.src.children.append(text)

    def parse_quote(self, text):
        if Regex.end_quote.match(text):
            if not self.blockquote.flag:
                raise ValueError('ssss')
            self.content.append(self.blockquote.to_html())
        else:
            self.blockquote.children.append(text)

    def parse_toc(self, text):
        return '''
        <div id="table-of-contents">
        <h2>Table of Contents</h2>
        <div id="text-table-of-contents">
        {text}
        </div>
        </div>
        '''.format(text=text)

    def append(self, text):
        if Regex.unorder_list.match(text):
            self.parse_unordered_list(text)
        elif Regex.order_list.match(text):
            self.parse_ordered_list(text)
        else:
            if len(text) == len(text.lstrip()):
                self.close()
            self.parse(text)

    def parse(self, text):
        if Regex.table.match(text):
            self.parse_table(text)
        elif self.table.flag:
            self.content.append(self.table.to_html())
        elif self.example.flag:
            self.parse_example(text)
        elif self.src.flag:
            self.parse_src(text)
        elif self.blockquote.flag:
            self.parse_quote(text)
        elif Regex.heading.match(text):
            self.parse_heading(text)
        elif Regex.begin_example.match(text):
            self.example.flag = True
        elif Regex.begin_src.match(text):
            self.src.append(text)
        elif Regex.begin_quote.match(text):
            self.blockquote.flag = True
        else:
            self.parse_text(text)

    def to_html(self):
        if self.heading_toc and self.heading.toc:
            t = self.heading.toc.splitlines()
            org = OrgMode(False, self.heading_offset)
            for i in t:
                org.append(i)
            org.close_unorder_list(True)
            toc = self.parse_toc(org.to_html())
            return toc + self.content.to_html()
        return self.content.to_html()


def org_to_html(text, toc=True, heading_offset=1):
    org = OrgMode(toc, heading_offset)
    text = text.splitlines()
    for t in text:
        org.append(t)
    return org

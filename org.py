#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: org.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-03-15 14:48:01 (CST)
# Last Update:星期三 2017-3-15 23:54:19 (CST)
#          By:
# Description:
# **************************************************************************
import re


class Regex(object):
    header = re.compile(r'^(?P<level>\*+)\s+(?P<title>.+)$')
    bold = re.compile(r'\*(?P<text>[\S]+?)\*')
    italic = re.compile(r'\*\*(?P<text>[\S]+?)\*\*')
    italic2 = re.compile(r'/(?P<text>[\S]+?)/')
    underlined = re.compile(r'_(?P<text>[\S]+?)_')
    code = re.compile(r'=(?P<text>[\S]+?)=')
    delete = re.compile(r'\+(?P<text>[\S]+?)\+')
    verbatim = re.compile(r'~(?P<text>[\S]+?)~')
    image = re.compile(r'\[\[(?P<src>.+?)\](?:\[(?P<alt>.+?)\])?\]')

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
    def __init__(self):
        pass


class Node(object):
    label = ''

    def __init__(self, text):
        self.text = text

    @property
    def html(self):
        return '<{label}>{text}</{label}>'.format(
            label=self.label, text=self.text)


class Header(object):
    def __init__(self, level, title, offset=1):
        self.level = level + (offset - 1)
        self.title = title
        self.offset = offset

    @property
    def html(self):
        return '<h{level}>{title}</h{level}>'.format(
            level=self.level, title=self.title)


class TextNode(object):
    label = '<span>{text}</span>'

    def __init__(self, regex):
        self.regex = regex

    def parse(self, text):
        for t in self.regex.finditer(text):
            string = self.label.format(text=t.group('text'))
            text = self.regex.sub(string, text)
        return text + '\n'


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
        return text + '\n'


class Text(object):
    # regex = {
    #     'bold': {
    #         'regex': Regex.bold,
    #         'parse': Bold
    #     },
    #     'italic': {
    #         'regex': Regex.italic,
    #         'parse': Italic
    #     },
    #     'delete': {
    #         'regex': Regex.delete,
    #         'parse': Delete
    #     },
    #     'code': {
    #         'regex': Regex.code,
    #         'parse': Code
    #     },
    #     'underlined': {
    #         'regex': Regex.underlined,
    #         'parse': Underlined
    #     },
    #     'verbatim': {
    #         'regex': Regex.verbatim,
    #         'parse': Verbatim
    #     },
    # }

    # regex = [Regex.bold, Regex.italic, Regex.underlined, Regex.code,
    #          Regex.verbatim, Regex.delete]

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
        elif Regex.italic2.search(text):
            text = Italic(Regex.italic2).parse(text)
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
        elif Regex.image.search(text):
            text = Image(Regex.image).parse(text)
            return self.parse(text)
        else:
            self._html += text
            self.flag = True

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
        self._begin_buffer = ''
        self._src_lang = 'python'
        self._list_buffer = {'depth': -1, 'ul': 1}
        self._list_flag = False
        self._table_flag = False

    def end_list(self):
        if self._list_flag:
            self._html += '</li></ul>' * self._list_buffer['ul']
            self._list_flag = False
        if self._table_flag:
            self._html += '</tbody></table>'
            self._table_flag = False

    def parse(self, text):
        text = text.splitlines()
        for line in text:
            if Regex.unorder_list.match(line):
                self.parse_list(line)
            elif Regex.table.match(line):
                self.parse_table(line)
            else:
                self._parse(line)
                self.end_list()

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

    def parse_table(self, text):
        if not self._table_flag:
            self._html += '<table><tbody>'
        self._table_flag = True
        m = Regex.table.match(text)
        cells = [c for c in m.group('cells').split('|') if c != '']
        strings = ''
        for cell in cells:
            strings += '<td>{text}</td>'.format(text=cell)
        self._html += '<tr>{text}</tr>'.format(text=strings)

    def parse_header(self, text):
        m = Regex.header.match(text)
        header = Header(len(m.group('level')), m.group('title')).html + '\n'
        self._headers.append(header)
        self._html += header

    def parse_list(self, text):
        self._list_flag = True
        m = Regex.unorder_list.match(text)
        depth = len(m.group('depth')) + 1
        item = m.group('item')
        buffer_depth = self._list_buffer['depth']
        if buffer_depth == -1:
            string = '<ul><li>{item}'.format(item=item)
        elif depth > buffer_depth:
            string = '<ul><li>{item}'.format(item=item)
            self._list_buffer['ul'] += 1
        elif depth < buffer_depth:
            string = '</li></ul></li><li>{item}'.format(item=item)
            self._list_buffer['ul'] -= 1
        else:
            string = '</li><li>{item}'.format(item=item)
        self._list_buffer['depth'] = depth
        self._html += string

    def parse_example(self, text):
        if Regex.end_example.match(text):
            if not self._example_flag:
                raise ValueError('ssss')
            self._html += '<pre class="example"><code>{text}</code></pre>'.format(
                text=self._begin_buffer)
            self._example_flag = False
            self._begin_buffer = ''
        else:
            self._begin_buffer += text

    def parse_quote(self, text):
        if Regex.end_quote.match(text):
            if not self._quote_flag:
                raise ValueError('ssss')
            self._html += '<blockquote><p>{text}</p></blockquote>'.format(
                text=self._begin_buffer)
            self._quote_flag = False
            self._begin_buffer = ''
        else:
            text = Text(text).html
            self._begin_buffer += text

    def parse_src(self, text):
        if Regex.end_src.match(text):
            if not self._src_flag:
                raise ValueError('ssss')
            self._html += '<pre class="{lang}"><code>{text}</code></pre>'.format(
                text=self._begin_buffer, lang=self._src_lang)
            self._src_flag = False
            self._begin_buffer = ''
        else:
            # text = Text(text).html
            self._begin_buffer += text

    def html(self):
        self.end_list()
        return self._html


def orgmode(text):
    org = OrgMode()
    org.parse(text)
    return org


if __name__ == '__main__':
    text = '''
#+BEGIN_SRC python
import a
#+END_SRC

    - adasd
    - 1
    - 2
        - 3
    - asasdasd

1. 111
2. 222
3. 333

[[adsad][asdad]]
| asda  | asdad | asd | ads | sdad |
|-------+-------+-----+-----+------|
| dasda | adsd  | asd | ads | ads  |
'''
    org = orgmode(text)
    print(org.html())
    print(org._headers)

    # bold = re.compile(r'\*(?P<text>[\S]+?)\*')
    # content = "adasdsa * *aaaa* adad *vvvv*"
    # # print(bold.split(content, 1))
    # a = bold.finditer(content)
    # c = content
    # for i in a:
    #     string = '<b>{text}</b>'.format(text=i.group('text'))
    #     c = bold.sub(string, c)
    # print(c)

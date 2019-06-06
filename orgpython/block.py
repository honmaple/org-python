#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ********************************************************************************
# Copyright © 2018-2019 jianglin
# File Name: block.py
# Author: jianglin
# Email: mail@honmaple.com
# Created: 2018-02-26 11:44:43 (CST)
# Last Update: Thursday 2019-06-06 21:15:23 (CST)
#          By:
# Description:
# ********************************************************************************
from hashlib import sha1
from textwrap import dedent

from . import regex as R
from .inline import InlineText

try:
    import pygments
    from pygments import lexers
    from pygments import formatters
except ImportError:
    pygments = None


class Block(object):
    def __init__(self, text=""):
        self.lines = text.splitlines()
        self.escape = True
        self.needparse = True
        self.inlineparse = False
        self.children = []
        self.offset = 0
        self.ispair = True
        self.current = self
        self.parent = None
        self.toc = True
        self.attrs = {'property': {}}
        self.blocks = [
            Heading,
            UnorderList,
            OrderList,
            Table,
            Src,
            Example,
            Quote,
            Center,
            Export,
            Verse,
        ]

    @classmethod
    def new(cls, text):
        return cls()

    @classmethod
    def match(cls, text):
        return False

    def matchend(self, text):
        return False

    def add_child(self, child):
        child.parent = self
        child.toc = self.toc
        child.escape = self.escape
        child.offset = self.offset
        child.init()

        self.children.append(child)

    def attr(self, text):
        match = R.attr.match(text)
        key, value = match.group(2), match.group(3)
        if key == "PROPERTY":
            value = value.split(" ", 1)
            value.append("")
            key, value = value[0], value[1]
            self.attrs['property'].setdefault(key.lower(), value)
            return
        self.attrs.setdefault(key.lower(), value)

    def inlinetext(self, text):
        return InlineText(text, self.needparse, self.escape)

    def heading(self, text):
        return Heading.new(text)

    def quote(self, text):
        return Quote.new(text)

    def src(self, text):
        return Src.new(text)

    def example(self, text):
        return Example.new(text)

    def export(self, text):
        return Export.new(text)

    def verse(self, text):
        return Verse.new(text)

    def center(self, text):
        return Center.new(text)

    def paragraph(self, text):
        return Paragraph.new(text)

    def table(self, text):
        return Table.new(text)

    def unorderlist(self, text):
        return UnorderList.new(text)

    def orderlist(self, text):
        return OrderList.new(text)

    def append(self, text):
        # TODO: unclose block
        b = self.current
        while b.parent is not None:
            if b.matchend(text) and b.ispair:
                # if b.ispair:
                #     unclose = b.children.pop()
                #     b.children.append(b.inlinetext(unclose.firstline))
                #     b.children.extend(unclose.children)
                self.current = b
                break
            b = b.parent

        current = self.current
        while isinstance(self.current, Paragraph):
            self.current = self.current.parent

        if self.current.matchend(text):
            if self.current.ispair:
                self.current = self.current.parent
                return
            self.current = self.current.parent
            return self.append(text)

        if not self.current.needparse or self.current.inlineparse:
            self.current.add_child(self.current.inlinetext(text))
            return

        if not self.current.ispair:
            self.current.append(text)
            return

        for block in self.blocks:
            if block.match(text):
                name = block.__name__.lower()
                current = getattr(self.current, name)(text)
                self.current.add_child(current)
                self.current = current
                return

        if R.attr.match(text):
            self.current.attr(text)
            return

        if R.blankline.match(text):
            self.current.add_child(self.current.inlinetext(""))
            return

        if isinstance(current, Paragraph):
            current.add_child(current.inlinetext(text))
            self.current = current
            return

        current = self.paragraph(text)
        current.needparse = self.current.needparse
        self.current.add_child(current)
        self.current = current
        return

    def init(self):
        self.children = []
        [self.append(line.rstrip()) for line in self.lines]

    def _to_html(self):
        text = '\n'.join([child.to_html() for child in self.children])
        return dedent(text)

    def to_html(self, init=False):
        if init: self.init()
        text = self._to_html()
        if hasattr(self, "label") and self.needparse:
            return self.label.format(text)
        return text

    def __str__(self):
        return "{0}({1})".format(
            self.__class__.__name__,
            ', '.join([str(child) for child in self.children]))


class Toc(Block):
    def to_html(self):
        text = '\n'.join([child.to_html() for child in self.children])
        if text:
            text = ('<div id="table-of-contents">'
                    '<h2>Table of Contents</h2>'
                    '<div id="text-table-of-contents">\n{}\n</div></div>\n\n'
                    ).format(text)
        return text


class Heading(Block):
    def __init__(self, title, level=1, offset=0, toc=False):
        super(Heading, self).__init__(title)
        self.title = title
        self.level = level
        self.offset = offset
        self.toc = toc

    def hid(self):
        return 'org-{0}'.format(sha1(self.title.encode()).hexdigest()[:10])

    @classmethod
    def new(cls, text):
        match = R.heading.match(text)
        level = len(match.group(1))
        title = match.group(2)
        return cls(title, level=level)

    @classmethod
    def match(cls, text):
        return R.heading.match(text)

    def matchend(self, text):
        match = R.heading.match(text)
        if match and len(match.group(1)) <= self.level:
            return True
        return False

    def to_html(self):
        text = "<h{0}>{1}</h{0}>".format(
            self.level + self.offset,
            self.title,
        )
        if self.toc:
            hid = self.hid()
            text = '<h{0} id="{2}">{1}</h{0}>'.format(self.level + self.offset,
                                                      self.title, hid)
            self.toc.append('{0}- [[#{1}][{2}]]'.format(
                ' ' * self.level, hid, self.title))
        return text + '\n'.join([child.to_html() for child in self.children])


class Src(Block):
    def __init__(self, text="", language="language"):
        super(Src, self).__init__(text)
        self.needparse = False
        self.inlineparse = True
        self.language = language
        self.label = "<pre class=\"src src-{0}\">\n{1}\n</pre>"

    @classmethod
    def new(cls, text):
        match = R.begin_src.match(text)
        language = match.group(2)
        return cls(language=language)

    @classmethod
    def match(cls, text):
        return R.begin_src.match(text)

    def matchend(self, text):
        return R.end_src.match(text)

    def to_html(self, init=False):
        if init: self.init()
        text = self._to_html()
        if pygments is not None:
            return self.highlight(text)
        return self.label.format(self.language, text)

    def highlight(self, text):
        try:
            lexer = lexers.get_lexer_by_name(self.language)
        except pygments.util.ClassNotFound:
            lexer = lexers.guess_lexer(text)
        formatter = formatters.HtmlFormatter()
        return pygments.highlight(text, lexer, formatter)


class Example(Src):
    def __init__(self, text=""):
        super(Example, self).__init__(text)
        self.language = "example"
        self.label = "<pre class=\"{0}\">\n{1}\n</pre>"

    @classmethod
    def new(cls, text):
        return cls()

    @classmethod
    def match(cls, text):
        return R.begin_example.match(text)

    def matchend(self, text):
        return R.end_example.match(text)

    def highlight(self, text):
        lexer = pygments.lexers.guess_lexer(text)
        formatter = pygments.formatters.HtmlFormatter()
        return pygments.highlight(text, lexer, formatter)


class Export(Block):
    def __init__(self, text="", language="HTML"):
        super(Export, self).__init__(text)
        self.language = language
        self.needparse = True
        self.inlineparse = True

    def init(self):
        if self.language.upper() == "HTML": self.escape = False
        return super(Export, self).init()

    @classmethod
    def new(cls, text):
        match = R.begin_export.match(text)
        language = match.group(2)
        return cls(language=language)

    @classmethod
    def match(cls, text):
        return R.begin_export.match(text)

    def matchend(self, text):
        return R.end_export.match(text)


class Verse(Block):
    def __init__(self, text=""):
        super(Verse, self).__init__(text)
        self.needparse = True
        self.inlineparse = True
        self.label = "<p class=\"verse\">\n{0}\n</p>"

    @classmethod
    def match(cls, text):
        return R.begin_verse.match(text)

    def matchend(self, text):
        return R.end_verse.match(text)

    def to_html(self, init=False):
        if init: self.init()
        text = '<br/>'.join([child.to_html() for child in self.children])
        if hasattr(self, "label") and self.needparse:
            return self.label.format(text)
        return text


class Center(Block):
    def __init__(self, text=""):
        super(Center, self).__init__(text)
        self.label = '<div style="text-align: center;">\n{0}\n</div>'

    @classmethod
    def match(cls, text):
        return R.begin_center.match(text)

    def matchend(self, text):
        return R.end_center.match(text)


class Quote(Block):
    def __init__(self, text=""):
        super(Quote, self).__init__(text)
        self.label = '<blockquote>\n{0}\n</blockquote>'

    @classmethod
    def match(cls, text):
        return R.begin_quote.match(text)

    def matchend(self, text):
        return R.end_quote.match(text)


class Paragraph(Block):
    def __init__(self, text=""):
        super(Paragraph, self).__init__(text)
        self.label = "<p>{0}</p>"

    @classmethod
    def new(cls, text):
        return cls(text)


class ListItemLine(Block):
    def __init__(self, title=""):
        super(ListItemLine, self).__init__("")
        self.inlineparse = True
        self.title = title

    @classmethod
    def new(cls, text):
        return cls(text)

    def to_html(self):
        match = R.checkbox.match(self.title)
        if not match:
            return self.inlinetext(self.title).to_html()
        checkbox = '<input type="checkbox" />{0}'
        if match.group(1) == "X":
            checkbox = '<input type="checkbox" checked="checked" />{0}'
        return checkbox.format(self.inlinetext(match.group(2)).to_html())


class ListItem(Block):
    def __init__(self, title=""):
        super(ListItem, self).__init__("")
        self.title = title
        self.label = "<li>{0}</li>"

    def listitemline(self, text):
        return ListItemLine.new(text)

    @classmethod
    def new(cls, text):
        return cls(text)

    def init(self):
        self.children = []
        self.add_child(self.listitemline(self.title))


class UnorderList(Block):
    regex = R.unorderlist

    def __init__(self, title="", depth=0):
        super(UnorderList, self).__init__("")
        self.title = title
        self.depth = depth
        self.ispair = False
        self.label = "<ul>\n{0}\n</ul>"

    def listitem(self, text):
        return ListItem.new(text)

    def append(self, text):
        match = self.regex.match(text)
        if match and len(match.group(1)) == self.depth:
            return self.add_child(self.listitem(match.group(3)))
        self.children[-1].append(text)

    @classmethod
    def new(cls, text):
        match = cls.regex.match(text)
        depth = len(match.group(1))
        title = match.group(3)
        return cls(title, depth)

    @classmethod
    def match(cls, text):
        return cls.regex.match(text)

    def matchend(self, text):
        if not text.strip():
            return False

        match = R.depth.match(text)
        depth = len(match.group(1))
        if self.regex.match(text):
            return depth < self.depth
        return depth <= self.depth

    def init(self):
        self.children = []
        self.add_child(self.listitem(self.title))


class OrderList(UnorderList):
    regex = R.orderlist

    def __init__(self, title="", depth=0):
        super(OrderList, self).__init__(title, depth)
        self.label = "<ol>\n{0}\n<ol>"


class TableCell(Block):
    def __init__(self, text=""):
        super(TableCell, self).__init__(text)
        self.inlineparse = True
        self.label = "<td>{0}</td>"

    @classmethod
    def new(cls, text):
        return cls(text)


class TableHeader(Block):
    def __init__(self, text=""):
        super(TableHeader, self).__init__(text)
        self.label = "<th>{0}</th>"

    def tablecell(self, text):
        return TableCell.new(text)

    @classmethod
    def new(cls, text):
        return cls(text)

    def append(self, text):
        match = R.table.match(text)
        for i in match.group(1).split("|"):
            self.add_child(self.tablecell(i.strip()))


class TableRow(TableHeader):
    def __init__(self, text=""):
        super(TableRow, self).__init__(text)
        self.label = "<tr>\n{0}\n</tr>"


class Table(Block):
    def __init__(self, text=""):
        super(Table, self).__init__(text)
        self.ispair = False
        self.label = "<table>\n{0}\n</table>"

    def tablerow(self, text):
        return TableRow.new(text)

    @classmethod
    def new(cls, text):
        return cls(text)

    def append(self, text):
        if R.tablesep.match(text):
            for child in self.children:
                child.label = "<th>\n{0}\n</th>"
            return
        self.add_child(self.tablerow(text))

    @classmethod
    def match(cls, text):
        return R.table.match(text)

    def matchend(self, text):
        return not R.table.match(text)

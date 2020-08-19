#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ********************************************************************************
# Copyright © 2017-2020 jianglin
# File Name: document.py
# Author: jianglin
# Email: mail@honmaple.com
# Created: 2018-02-26 11:44:43 (CST)
# Last Update: Wednesday 2020-08-19 12:00:03 (CST)
# Description:
# ********************************************************************************
import re
from hashlib import sha1
from textwrap import dedent

from .inline import Blankline, Hr, InlineText
from .src import highlight as src_highlight

DRAWER_BEGIN_REGEXP = re.compile(r"^(\s*):(\S+):\s*$")
DRAWER_END_REGEXP = re.compile(r"^(\s*):END:\s*$")
DRAWER_PROPERTY_REGEXP = re.compile(r"^(\s*):(\S+):(\s+(.*)$|$)")

BLOCK_BEGIN_REGEXP = re.compile(r"(?i)^(\s*)#\+BEGIN_(\w+)(.*)")
BLOCK_END_REGEXP = re.compile(r"(?i)^(\s*)#\+END_(\w+)")
BLOCK_RESULT_REGEXP = re.compile(r"(?i)^(\s*)#\+RESULTS:")
BLOCK_RESULT_CONTENT_REGEXP = re.compile(r"(?:^|\s+):(\s+(.*)|$)")

TABLE_SEP_REGEXP = re.compile(r"^(\s*)(\|[+-|]*)\s*$")
TABLE_ROW_REGEXP = re.compile(r"^(\s*)(\|.*)")
TABLE_ALIGN_REGEXP = re.compile(r"^<(l|c|r)>$")

LIST_DESCRIPTIVE_REGEXP = re.compile(r"^(\s*)([+*-])\s+(.*)::(\s|$)")
LIST_UNORDER_REGEXP = re.compile(r"^(\s*)([+*-])(\s+(.*)|$)")
LIST_ORDER_REGEXP = re.compile(r"^(\s*)(([0-9]+|[a-zA-Z])[.)])(\s+(.*)|$)")
LIST_STATUS_REGEXP = re.compile(r"\[( |X|-)\]\s")
LIST_LEVEL_REGEXP = re.compile(r"(\s*)(.+)$")

HEADLINE_REGEXP = re.compile(
    r"^(\*+)(?:\s+(.+?))?(?:\s+\[#(.+)\])?(\s+.*?)(?:\s+:(.+):)?$")
KEYWORD_REGEXP = re.compile(r"^(\s*)#\+([^:]+):(\s+(.*)|$)")
COMMENT_REGEXP = re.compile(r"^(\s*)#(.*)")
ATTRIBUTE_REGEXP = re.compile(r"(?:^|\s+)(:[-\w]+)\s+(.*)$")

TODO_KEYWORDS = ("DONE", "TODO")


def string_split(s, sep):
    if not s:
        return []
    return s.split(sep)


class Parser(object):
    def __init__(self, content=""):
        self.lines = content.splitlines()
        self.level = 0
        self.element = ""
        self.children = []
        self.escape = True
        self.needparse = True
        self.parsed_nodes = (
            "blankline",
            "headline",
            "table",
            "list",
            "drawer",
            "block",
            "block_result",
            "keyword",
            "hr",
        )

    def first_child(self):
        if len(self.children) == 0:
            return
        return self.children[0]

    def last_child(self):
        if len(self.children) == 0:
            return
        return self.children[-1]

    def add_child(self, node):
        last = self.last_child()
        if self.is_headline(last):
            if self.is_properties(node):
                last.properties = node
                return

            if not self.is_headline(node):
                last.add_child(node)
                return

            if self.is_headline(node) and node.stars > last.stars:
                last.add_child(node)
                return

        if self.is_table(last):
            if self.is_table(node):
                last.add_child(node)
                return

        if self.is_list(last):
            if self.is_blankline(node):
                last.add_child(node)
                return

            if node.level > last.level:
                last.add_child(node)
                return

            if self.is_list(node) and node.level == last.level:
                last.add_child(node)
                return

        if self.is_keyword(last):
            if self.is_table(node):
                node.keyword = last

        if self.is_paragraph(last):
            if self.is_inlinetext(node):
                last.add_child(node)
                return

        if self.is_inlinetext(node):
            self.children.append(self.paragraph(node))
            return

        self.children.append(node)

    def is_keyword(self, child):
        return child and isinstance(child, Keyword)

    def is_headline(self, child):
        return child and isinstance(child, Headline)

    def is_list(self, child):
        return child and isinstance(child, List)

    def is_table(self, child):
        return child and isinstance(child, Table)

    def is_src(self, child):
        return child and isinstance(child, (Src, Example))

    def is_inlinetext(self, child):
        return child and isinstance(child, InlineText)

    def is_blankline(self, child):
        return child and isinstance(child, Blankline)

    def is_paragraph(self, child):
        return child and isinstance(child, Paragraph)

    def is_properties(self, child):
        return child and isinstance(child, Properties)

    def inlinetext(self, text):
        return InlineText(text, self.needparse, self.escape)

    def paragraph(self, node):
        n = Paragraph()
        n.add_child(node)
        return n

    def _parse_paired(self, cls, index, lines):
        node = cls.match(lines[index])
        if not node:
            return None, index

        end = len(lines)
        num = index + 1
        while num < end:
            if node.matchend(num, lines):
                node.preparse(lines[index + 1:num])
                return node, num
            num += 1
        return None, index

    def _parse_nopaired(self, cls, index, lines):
        node = cls.match(lines[index])
        if not node:
            return None, index

        end = len(lines)
        num = index + 1
        while num < end:
            if node.matchend(num, lines):
                break
            num += 1
        node.preparse(lines[index + 1:num])
        return node, num

    def parse_headline(self, index, lines):
        return Headline.match(lines[index]), index

    def parse_list(self, index, lines):
        return List.match(lines[index]), index

    def parse_table(self, index, lines):
        return self._parse_nopaired(Table, index, lines)

    def parse_drawer(self, index, lines):
        return self._parse_paired(Drawer, index, lines)

    def parse_block(self, index, lines):
        return self._parse_paired(Block, index, lines)

    def parse_block_result(self, index, lines):
        return self._parse_paired(BlockResult, index, lines)

    def parse_blankline(self, index, lines):
        return Blankline.match(lines[index]), index

    def parse_keyword(self, index, lines):
        return Keyword.match(lines[index]), index

    def parse_hr(self, index, lines):
        return Hr.match(lines[index]), index

    def parse_inlinetext(self, index, lines):
        return self.inlinetext(lines[index]), index

    def parse(self, index, lines):
        for b in self.parsed_nodes:
            func = "parse_" + b
            if not hasattr(self, func):
                continue
            block, num = getattr(self, func)(index, lines)
            if not block:
                continue
            return block, num

        return self.parse_inlinetext(index, lines)

    def preparse(self, lines):
        index = 0
        while index < len(lines):
            line = lines[index]
            node, index = self.parse(index, lines)
            if node:
                node.level = len(line) - len(line.strip())
                self.add_child(node)
            index += 1

    def to_html(self):
        if len(self.children) == 0 and len(self.lines) > 0:
            self.preparse(self.lines)

        children = []
        for child in self.children:
            content = child.to_html()
            if not content:
                continue
            children.append(content)
        text = "\n".join(children)
        if self.element:
            return self.element.format(text)
        return text

    def __str__(self):
        str_children = [str(child) for child in self.children]
        return self.__class__.__name__ + '(' + ','.join(str_children) + ')'

    def __repr__(self):
        return self.__str__()


class Headline(Parser):
    def __init__(
            self,
            title,
            stars=1,
            keyword=None,
            priority=None,
            tags=[],
            todo_keywords=TODO_KEYWORDS):
        super(Headline, self).__init__()
        self.title = title
        self.stars = stars
        self.keyword = keyword
        self.priority = priority
        self.tags = tags
        self.properties = None
        self.todo_keywords = todo_keywords

    @classmethod
    def match(cls, line):
        match = HEADLINE_REGEXP.match(line)
        if not match:
            return

        stars = len(match[1])
        keyword = match[2] or ""
        priority = match[3] or ""

        if keyword and not priority:
            if len(keyword) >= 4 and keyword[0:2] == "[#":
                priority = keyword[2:-1]
                keyword = ""

        title = keyword + match[4]
        keyword = ""

        return cls(
            title,
            stars,
            keyword,
            priority,
            string_split(match[5], ":"),
        )

    def id(self):
        hid = 'org-{0}'.format(sha1(self.title.encode()).hexdigest()[:10])
        if self.properties:
            return self.properties.get("CUSTOM_ID", hid)
        return hid

    def toc(self):
        b = ""
        if self.keyword:
            b = b + "<span class=\"todo\">{0}</span>".format(self.keyword)
        if self.priority:
            b = b + "<span class=\"priority\">{0}</span>".format(self.priority)

        b = b + self.inlinetext(self.title).to_html()

        for tag in self.tags:
            b = b + "<span class=\"tag\">{0}</span>".format(tag)
        return b.strip()

    def to_html(self):
        b = "<h{0} id=\"{1}\">{2}</h{0}>".format(
            self.stars,
            self.id(),
            self.toc(),
        )
        return b + super(Headline, self).to_html()


class Drawer(Parser):
    def __init__(self, name):
        super(Drawer, self).__init__()
        self.name = name

    @classmethod
    def match(cls, line):
        match = DRAWER_BEGIN_REGEXP.match(line)
        if not match:
            return
        name = match[2]
        if name.upper() == "PROPERTIES":
            return Properties(name)
        return Drawer(name)

    def matchend(self, index, lines):
        return DRAWER_END_REGEXP.match(lines[index])

    def to_html(self):
        return ""


class Properties(Drawer):
    def __init__(self, name):
        super(Properties, self).__init__(name)
        self.properties = {}

    def parse(self, index, lines):
        match = DRAWER_PROPERTY_REGEXP.match(lines[index])
        if match:
            self.properties[match[2].upper()] = match[4]
        return None, index

    def get(self, key, default=None):
        return self.properties.get(key, default)

    def to_html(self):
        return ""


class Block(Parser):
    def __init__(self, name, params=""):
        super(Block, self).__init__()
        self.name = name
        self.params = params

    @classmethod
    def match(cls, line):
        match = BLOCK_BEGIN_REGEXP.match(line)
        if not match:
            return

        name = match[2].lower()
        if name == "src":
            return Src(*match[3].strip().split(" ", 1))
        if name == "example":
            return Example(match[3])
        if name == "center":
            return Center(match[3])
        if name == "verse":
            return Verse(match[3])
        if name == "quote":
            return Quote(match[3])
        if name == "export":
            return Export(*match[3].strip().split(" ", 1))
        return cls(name, match[3])

    def matchend(self, index, lines):
        match = BLOCK_END_REGEXP.match(lines[index])
        return match and match[2].lower() == self.name


class Center(Block):
    def __init__(self, params=""):
        super(Center, self).__init__("center", params)
        self.element = "<div style=\"text-align: center;\">\n{0}\n</div>"


class Verse(Block):
    def __init__(self, params=""):
        super(Verse, self).__init__("verse", params)
        self.element = "<p class=\"verse\">\n{0}\n</p>"

    def add_child(self, node):
        self.children.append(node)

    def to_html(self):
        children = [child.to_html() for child in self.children]
        return self.element.format("<br />".join(children))


class Quote(Block):
    def __init__(self, params=""):
        super(Quote, self).__init__("quote", params)
        self.element = "<blockquote>\n{0}\n</blockquote>"


class Export(Block):
    def __init__(self, language="", params=""):
        super(Export, self).__init__("export", params)
        self.language = language
        self.escape = self.language.upper() != "HTML"
        self.parsed_nodes = ()

    def to_html(self):
        if not self.escape:
            return super(Export, self).to_html()
        return ""


class Src(Block):
    def __init__(self, language="", params="", highlight=False):
        super(Src, self).__init__("src", params)
        self.language = language
        self.highlight_code = highlight
        self.element = "<pre class=\"src src-{0}\">\n{1}\n</pre>"
        self.needparse = False
        self.escape = False
        self.parsed_nodes = ()

    def add_child(self, node):
        self.children.append(node)

    def highlight(self, language, text):
        return src_highlight(language, text)

    def to_html(self):
        text = "\n".join([child.to_html() for child in self.children])
        if self.highlight_code:
            return self.highlight(self.language, dedent(text))
        if not self.language:
            return "<pre>\n{0}\n</pre>".format(dedent(text))
        return self.element.format(self.language, dedent(text))


class Example(Src):
    def __init__(self, params="", highlight=False):
        super(Example, self).__init__("example", params, highlight)
        self.name = "example"


class BlockResult(Parser):
    def __init__(self):
        super(BlockResult, self).__init__()
        self.element = "<pre class=\"example\">\n{0}\n</pre>"

    @classmethod
    def match(cls, line):
        match = BLOCK_RESULT_REGEXP.match(line)
        if not match:
            return
        return cls()

    def matchend(self, index, lines):
        return not BLOCK_RESULT_CONTENT_REGEXP.match(lines[index])

    def parse(self, index, lines):
        match = BLOCK_RESULT_CONTENT_REGEXP.match(lines[index])
        return self.inlinetext(match[2]), index


class ListItem(Parser):
    def __init__(self, status=None, checkbox="HTML"):
        super(ListItem, self).__init__()
        self.status = status
        self.checkbox = checkbox
        self.element = "<li>\n{0}\n</li>"

    @classmethod
    def match(cls, line):
        status = None
        content = line
        status_match = LIST_STATUS_REGEXP.match(line)
        if status_match:
            status, content = status_match[1], content[len("[ ] "):]

        node = cls(status)
        node.add_child(node.inlinetext(content))
        return node

    def set_status(self):
        if not self.checkbox:
            return

        if self.checkbox == "HTML":
            if self.status == "X":
                node = self.inlinetext(
                    '<input type="checkbox" checked="checked" />')
            else:
                node = self.inlinetext('<input type="checkbox" />')
            node.needparse = False
            node.escape = False
        else:
            node = self.inlinetext("=[{0}]=".format(self.status))

        if not self.children:
            self.children.append(node)
            return

        self.children[0].children = [node] + self.children[0].children

    def to_html(self):
        if self.status is not None:
            self.set_status()
        return super(ListItem, self).to_html()


class DescriptiveItem(ListItem):
    def __init__(self, title="", status=""):
        super(DescriptiveItem, self).__init__(title, status)
        self.element = "<dt>\n{0}\n</dt>"


class List(Parser):
    def __init__(self, items=[]):
        super(List, self).__init__()
        self.children = items

    @classmethod
    def match(cls, line):
        match = UnorderList.match(line)
        if match:
            return match

        match = OrderList.match(line)
        if match:
            return match

        return Descriptive.match(line)

    def add_child(self, node):
        if self.is_list(node) and node.level == self.level:
            self.children.append(node.children[0])
            return
        last = self.last_child()
        last.add_child(node)


class Descriptive(List):
    def __init__(self, items=[]):
        super(Descriptive, self).__init__(items)
        self.element = "<dd>\n{0}\n</dd>"

    @classmethod
    def match(cls, line):
        match = LIST_DESCRIPTIVE_REGEXP.match(line)
        if not match:
            return
        title = DescriptiveItem.match(match[3])
        return cls([title])


class UnorderList(List):
    def __init__(self, items=[]):
        super(UnorderList, self).__init__(items)
        self.element = "<ul>\n{0}\n</ul>"

    @classmethod
    def match(cls, line):
        match = LIST_UNORDER_REGEXP.match(line)
        if not match:
            return
        title = ListItem.match(match[4])
        return cls([title])


class OrderList(List):
    def __init__(self, items=[]):
        super(OrderList, self).__init__(items)
        self.element = "<ol>\n{0}\n</ol>"

    @classmethod
    def match(cls, line):
        match = LIST_ORDER_REGEXP.match(line)
        if not match:
            return
        title = ListItem.match(match[4])
        return cls([title])


class TableColumn(Parser):
    def __init__(self, content="", header=False):
        super(TableColumn, self).__init__(content)
        self.header = header
        self.parsed_nodes = ()

    def add_child(self, child):
        self.children.append(child)

    def reset(self):
        self.header = True

    def to_html(self):
        self.element = "<th>{0}</th>" if self.header else "<td>{0}</td>"
        return super(TableColumn, self).to_html()


class TableRow(Parser):
    def __init__(self, header=False):
        super(TableRow, self).__init__()
        self.is_sep = False
        self.header = header
        self.element = "<tr>\n{0}\n</tr>"
        self.parsed_nodes = ("tablecolumn", )

    @classmethod
    def match(cls, line):
        match = TABLE_ROW_REGEXP.match(line)
        if not match:
            return

        row = cls()
        row.is_sep = bool(TABLE_SEP_REGEXP.match(line))
        row.preparse(match[2].strip("|").split("|"))
        return row

    def add_child(self, child):
        self.children.append(child)

    def parse_tablecolumn(self, index, lines):
        return TableColumn(lines[index].strip(), self.header), index

    def reset(self):
        self.header = True
        for column in self.children:
            column.reset()


class Table(Parser):
    def __init__(self, keyword=None):
        super(Table, self).__init__()
        self.element = "<table>\n{0}\n</table>"
        self.keyword = keyword
        self.parsed_nodes = ("tablerow", )

    @classmethod
    def match(cls, line):
        row = TableRow.match(line)
        if not row:
            return

        table = cls()
        if row.is_sep:
            return table
        table.add_child(row)
        return table

    def matchend(self, index, lines):
        return not TABLE_ROW_REGEXP.match(lines[index])

    def reset(self):
        first = self.first_child()
        if first and first.header:
            return
        for row in self.children:
            row.reset()

    def add_child(self, child):
        if child.is_sep:
            return self.reset()
        self.children.append(child)

    def parse_tablerow(self, index, lines):
        return TableRow.match(lines[index]), index


class Keyword(Parser):
    def __init__(self, key, value=""):
        super(Keyword, self).__init__()
        self.key = key
        self.value = value

    def options(self):
        results = {}
        for line in self.value.split(" "):
            if not line:
                continue
            m = line.split(":", 1)
            k = m[0]
            if not k:
                continue
            results[k] = "" if len(m) == 1 else m[1]
        return results

    def properties(self):
        results = {}
        line = self.value.strip()
        if not line:
            return results
        m = line.split(" ", 1)
        k = m[0]
        if not k:
            return results
        results[k] = "" if len(m) == 1 else m[1]
        return results

    @classmethod
    def match(cls, line):
        match = KEYWORD_REGEXP.match(line)
        if not match:
            return
        return cls(match[2], match[4])

    def to_html(self):
        return ""


class Paragraph(Parser):
    def __init__(self, content=""):
        super(Paragraph, self).__init__(content)
        self.element = "<p>\n{0}\n</p>"
        self.parsed_nodes = ()

    def add_child(self, node):
        self.children.append(node)


class Section(Parser):
    def __init__(self, headline):
        super(Section, self).__init__()
        self.headline = headline

    @property
    def stars(self):
        return self.headline.stars

    def add_child(self, node):
        last = self.last_child()
        if not last:
            self.children.append(node)
            return

        if node.stars > last.stars:
            last.add_child(node)
            return
        self.children.append(node)

    def to_html(self):
        text = "<li>"
        text += "<a href=\"#{0}\">{1}</a>".format(
            self.headline.id(),
            self.headline.toc(),
        )
        if not self.children:
            return text + "</li>"

        text += "\n<ul>\n{0}\n</ul>\n</li>".format(
            "\n".join([child.to_html() for child in self.children]))
        return text


class Toc(Parser):
    def __init__(self):
        super(Toc, self).__init__()
        self.element = (
            '<div id="table-of-contents">'
            '<h2>Table of Contents</h2>'
            '<div id="text-table-of-contents">'
            '\n<ul>\n{0}\n</ul>\n</div></div>')

    def add_child(self, node):
        last = self.last_child()
        if not last:
            self.children.append(node)
            return

        if node.stars > last.stars:
            last.add_child(node)
            return

        if node.stars < last.stars:
            last.add_child(node)
            return

        self.children.append(node)

    def to_html(self):
        if not self.children:
            return ""
        return super(Toc, self).to_html()


class Document(Parser):
    def __init__(self, content, offset=0, highlight=False, **options):
        super(Document, self).__init__(content)
        self.offset = offset
        self.highlight = highlight
        self.options = options
        self.properties = {}
        self.toc = Toc()

    def _is_true(self, value):
        return value in ("true", "t", "1", True, 1)

    def section(self, node):
        return Section(node)

    def parse_keyword(self, index, lines):
        block, index = super(Document, self).parse_keyword(index, lines)
        if not block:
            return block, index

        if block.key == "OPTIONS":
            self.options.update(**block.options())
        elif block.key == "PROPERTY":
            self.properties.update(**block.properties())
        else:
            self.properties[block.key] = block.value
        return block, index

    def parse_headline(self, index, lines):
        block, index = super(Document, self).parse_headline(index, lines)
        if not block:
            return block, index
        block.stars = block.stars + self.offset

        todo_keywords = self.properties.get("TODO")
        if todo_keywords:
            block.todo_keywords = todo_keywords.split(" ")
        s = block.title.split(" ", 1)
        if len(s) > 1 and s[0] in block.todo_keywords:
            block.keyword = s[0]
            block.title = s[1]
        self.toc.add_child(self.section(block))
        return block, index

    def parse_block(self, index, lines):
        block, index = super(Document, self).parse_block(index, lines)
        if not block:
            return block, index
        if self.is_src(block):
            block.highlight_code = self.highlight
        return block, index

    def to_html(self):
        text = super(Document, self).to_html()
        if self._is_true(self.options.get("toc")):
            return self.toc.to_html() + "\n" + text
        return text

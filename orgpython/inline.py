#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ********************************************************************************
# Copyright © 2017-2020 jianglin
# File Name: inline.py
# Author: jianglin
# Email: mail@honmaple.com
# Created: 2018-02-26 11:41:22 (CST)
# Last Update: Tuesday 2020-08-18 17:21:40 (CST)
#          By:
# Description:
# ********************************************************************************
import re
import os

# _inline_regexp = r"(^|.*?(?<![/\\])){0}(.+?(?<![/\\])){0}(.*?|$)"
_inline_regexp = r"(^|.*?(?<![/\\])){0}(.+?(?<![/\\])){0}(.*?|$)"

BOLD_REGEXP = re.compile(_inline_regexp.format('\\*'))
CODE_REGEXP = re.compile(_inline_regexp.format('(?:\\=|`)'))
ITALIC_REGEXP = re.compile(_inline_regexp.format('(?:\\*\\*|\\/)'))
DELETE_REGEXP = re.compile(_inline_regexp.format('\\+'))
VERBATIM_REGEXP = re.compile(_inline_regexp.format('~'))
UNDERLINE_REGEXP = re.compile(_inline_regexp.format('_'))

PERCENT_REGEXP = re.compile(r"\[(\d+/\d+|\d+%)\]")

HR_REGEXP = re.compile(r"^\s*\-{5,}\s*")
FN_REGEXP = re.compile(r"(^|.*?(?<![/\\]))(\[fn:(.+?)\])(.*?|$)")
IMG_REGEXP = re.compile(r"^[.](png|gif|jpe?g|svg|tiff?)$")
LINK_REGEXP = re.compile(r'\[\[(.+?)\](?:\[(.+?)\])?\]')
VIDEO_REGEXP = re.compile(r"^[.](webm|mp4)$")

NEWLINE_REGEXP = re.compile(r"(^|.*?(?<![/\\]))(\\\\(\s*)$)")
BLANKLINE_REGEXP = re.compile(r"^(\s*)$")

TIMESTAMP_REGEXP = re.compile(
    r"^<(\d{4}-\d{2}-\d{2})( [A-Za-z]+)?( \d{2}:\d{2})?( \+\d+[dwmy])?>")

_html_escape = (
    ("&", "&amp;"),
    ("'", "&#39;"),
    ("<", "&lt;"),
    (">", "&gt;"),
    ("\"", "&#34;"),
)

# https://github.com/tsroten/zhon/blob/develop/zhon/hanzi.py
_chinese_non_stops = (
    # Fullwidth ASCII variants
    '\uFF02\uFF03\uFF04\uFF05\uFF06\uFF07\uFF08\uFF09\uFF0A\uFF0B\uFF0C\uFF0D'
    '\uFF0F\uFF1A\uFF1B\uFF1C\uFF1D\uFF1E\uFF20\uFF3B\uFF3C\uFF3D\uFF3E\uFF3F'
    '\uFF40\uFF5B\uFF5C\uFF5D\uFF5E\uFF5F\uFF60'

    # Halfwidth CJK punctuation
    '\uFF62\uFF63\uFF64'

    # CJK symbols and punctuation
    '\u3000\u3001\u3003'

    # CJK angle and corner brackets
    '\u3008\u3009\u300A\u300B\u300C\u300D\u300E\u300F\u3010\u3011'

    # CJK brackets and symbols/punctuation
    '\u3014\u3015\u3016\u3017\u3018\u3019\u301A\u301B\u301C\u301D\u301E\u301F'

    # Other CJK symbols
    '\u3030'

    # Special CJK indicators
    '\u303E\u303F'

    # Dashes
    '\u2013\u2014'

    # Quotation marks and apostrophe
    '\u2018\u2019\u201B\u201C\u201D\u201E\u201F'

    # General punctuation
    '\u2026\u2027'

    # Overscores and underscores
    '\uFE4F'

    # Small form variants
    '\uFE51\uFE54'

    # Latin punctuation
    '\u00B7')

_chinese_stops = (
    '\uFF01'  # Fullwidth exclamation mark
    '\uFF1F'  # Fullwidth question mark
    '\uFF61'  # Halfwidth ideographic full stop
    '\u3002'  # Ideographic full stop
)


def html_escape(text):
    for e in _html_escape:
        text = text.replace(e[0], e[1])
    return text


def match_chinese(ch):
    if '\u4e00' <= ch <= '\u9fff':
        return True
    if ch in _chinese_stops:
        return True
    return ch in _chinese_non_stops


def match_emphasis(cls, regexp, line, index):
    match = regexp.match(line, index)
    if not match:
        return None, index

    end = match.end()

    if index != 0:
        prechar = line[index - 1]
        border = prechar != " " and prechar not in "-({'\""
        if border and not match_chinese(prechar):
            return None, index

    if end < len(line):
        endchar = line[end]
        border = endchar != " " and endchar not in "-.,:!?;'\")}["
        if border and not match_chinese(endchar):
            return None, index
    return cls(match[2]), end - 1


class InlineParser(object):
    def __init__(self, content=""):
        self.content = content
        self.children = []
        self.element = ""

    def add_child(self, child):
        self.children.append(child)

    def parse_code(self, index, lines):
        return Code.match(lines, index)

    def parse_bold(self, index, lines):
        return Bold.match(lines, index)

    def parse_italic(self, index, lines):
        return Italic.match(lines, index)

    def parse_delete(self, index, lines):
        return Delete.match(lines, index)

    def parse_verbatim(self, index, lines):
        return Verbatim.match(lines, index)

    def parse_underline(self, index, lines):
        return Underline.match(lines, index)

    def parse_percent(self, index, lines):
        return Percent.match(lines, index)

    def parse_link(self, index, lines):
        return Link.match(lines, index)

    def parse_fn(self, index, lines):
        return Fn.match(lines, index)

    def parse_newline(self, index, lines):
        return Newline.match(lines, index)

    def parse(self, index, lines):
        chars = (
            ("=", "code"),
            ("`", "code"),
            ("~", "verbatim"),
            ("_", "underline"),
            ("+", "delete"),
            ("/", "italic"),
            ("**", "italic"),
            ("*", "bold"),
            ("[[", "link"),
            ("[", "percent"),
            ("\\", "newline"),
        )
        char_map = dict(chars)
        single_char = lines[index]
        double_char = lines[index:index + 2]
        for char in chars:
            c1 = len(char[0]) == 1 and char[0] == single_char
            c2 = len(char[0]) == 2 and char[0] == double_char

            if c1 or c2:
                node, num = getattr(self, "parse_" + char_map[char[0]])(
                    index, lines)
                if node:
                    return node, num

        if lines[index:index + 3] == "[fn":
            node, num = self.parse_fn(index, lines)
            if node:
                return node, num

        child = self.last_child()
        if child and isinstance(child, Text):
            child.content += single_char
            return None, index
        return Text(single_char), index

    def last_child(self):
        if len(self.children) == 0:
            return
        return self.children[-1]

    def preparse(self, lines):
        index = 0
        while index < len(lines):
            block, index = self.parse(index, lines)
            index += 1
            if not block:
                continue
            self.add_child(block)

    def to_html(self):
        if len(self.children) == 0 and self.content:
            self.preparse(self.content)

        text = "".join([child.to_html() for child in self.children])
        if self.element:
            return self.element.format(text)
        return text

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, self.content.strip())

    def __repr__(self):
        return self.__str__()


class Text(InlineParser):
    def to_html(self):
        return self.content


class Newline(InlineParser):
    @classmethod
    def match(cls, line, index):
        match = NEWLINE_REGEXP.match(line, index)
        if not match:
            return None, index
        return cls(), match.end() - 1

    def to_html(self):
        return "<br/>"


class Bold(InlineParser):
    def __init__(self, content):
        super(Bold, self).__init__(content)
        self.element = "<b>{0}</b>"

    @classmethod
    def match(cls, line, index):
        return match_emphasis(cls, BOLD_REGEXP, line, index)


class Code(InlineParser):
    def __init__(self, content):
        super(Code, self).__init__(content)
        self.element = "<code>{0}</code>"

    @classmethod
    def match(cls, line, index):
        return match_emphasis(cls, CODE_REGEXP, line, index)


class Italic(InlineParser):
    def __init__(self, content):
        super(Italic, self).__init__(content)
        self.element = "<i>{0}</i>"

    @classmethod
    def match(cls, line, index):
        return match_emphasis(cls, ITALIC_REGEXP, line, index)


class Delete(InlineParser):
    def __init__(self, content):
        super(Delete, self).__init__(content)
        self.element = "<del>{0}</del>"

    @classmethod
    def match(cls, line, index):
        return match_emphasis(cls, DELETE_REGEXP, line, index)


class Verbatim(InlineParser):
    def __init__(self, content):
        super(Verbatim, self).__init__(content)
        self.element = "<code>{0}</code>"

    @classmethod
    def match(cls, line, index):
        return match_emphasis(cls, VERBATIM_REGEXP, line, index)


class Underline(InlineParser):
    def __init__(self, content):
        super(Underline, self).__init__(content)
        self.element = "<span style=\"text-decoration:underline\">{0}</span>"

    @classmethod
    def match(cls, line, index):
        return match_emphasis(cls, UNDERLINE_REGEXP, line, index)


class Percent(InlineParser):
    def __init__(self, content):
        super(Percent, self).__init__(content)
        self.element = "<code>[{0}]</code>"

    @classmethod
    def match(cls, line, index):
        match = PERCENT_REGEXP.match(line, index)
        if not match:
            return None, index
        return cls(match[1]), match.end()


class Link(InlineParser):
    def __init__(self, url, desc=None):
        super(Link, self).__init__(url)
        self.desc = desc

    @classmethod
    def match(cls, line, index):
        match = LINK_REGEXP.match(line, index)
        if not match:
            return None, index
        return cls(match[1], match[2]), match.end()

    def is_img(self):
        _, ext = os.path.splitext(self.content)
        return not self.desc and IMG_REGEXP.match(ext)

    def is_vedio(self):
        _, ext = os.path.splitext(self.content)
        return not self.desc and VIDEO_REGEXP.match(ext)

    def to_html(self):
        if self.is_img():
            return "<img src=\"{0}\"/>".format(self.content)
        if self.is_vedio():
            return "<video src=\"{0}\">{0}</video>".format(self.content)
        if self.desc:
            return '<a href="{0}">{1}</a>'.format(self.content, self.desc)
        return '<a href="{0}">{1}</a>'.format(self.content, self.content)


class Fn(InlineParser):
    def __init__(self, content):
        super(Fn, self).__init__(content)
        self.element = '<sup><a id="fnr:{0}" class="footref" href="#fn.{0}">{0}</a></sup>'

    @classmethod
    def match(cls, line, index):
        match = FN_REGEXP.match(line, index)
        if not match:
            return None, index
        return cls(match[3]), match.end()

    def to_html(self):
        return self.element.format(self.content)


class Timestamp(InlineParser):
    def __init__(self, date="", time="", interval=None):
        super(Timestamp, self).__init__()
        self.date = date
        self.time = time
        self.interval = interval

    @classmethod
    def match(cls, line, index):
        match = TIMESTAMP_REGEXP.match(line, index)
        if not match:
            return None, index
        return cls(match[1], match[3], match[4]), match.end()


class Blankline(InlineParser):
    def __init__(self):
        super(Blankline, self).__init__()

    @classmethod
    def match(cls, line):
        match = BLANKLINE_REGEXP.match(line)
        if not match:
            return
        return cls()

    def to_html(self):
        return ""


class Hr(InlineParser):
    def __init__(self):
        super(Hr, self).__init__()

    @classmethod
    def match(cls, line):
        if HR_REGEXP.match(line):
            return cls()
        return

    def to_html(self):
        return ""


class InlineText(InlineParser):
    def __init__(self, content="", needparse=True, escape=True):
        super(InlineText, self).__init__(content)
        self.needparse = needparse
        self.escape = escape

    def to_html(self):
        if self.escape:
            self.content = html_escape(self.content)
        if not self.needparse:
            return self.content
        return super(InlineText, self).to_html()

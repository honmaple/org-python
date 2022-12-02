#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os

# _inline_regexp = r"(^|.*?(?<![/\\])){0}(.+?(?<![/\\])){0}(.*?|$)"
_inline_regexp = r"(^|.*?(?<![/\\])){0}(.+?(?<![/\\])){0}(.*?|$)"

NEWLINE_REGEXP = re.compile(r"(^|.*?(?<![/\\]))(\\\\(\s*)$)")
BLANKLINE_REGEXP = re.compile(r"^(\s*)$")

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


def _valid_pre_border(line, index):
    pass


def _valid_end_border(line, index):
    pass


def _is_span(line, index):
    pass


class Text(object):
    def __init__(self, content):
        self.content = content

    @classmethod
    def match(cls, document, line, index):
        beg, end = index + 1, len(line)
        while beg < end:
            next_obj, n = document.parse_object(line, beg)
            if next_obj:
                return cls(line[index:beg]), next_obj, beg - index + n
            beg = beg + 1
        return cls(line[index:beg]), None, beg - index


class Link(object):
    REGEXP = re.compile(r'\[\[(.+?)\](?:\[(.+?)\])?\]')
    IMG_REGEXP = re.compile(r"^[.](png|gif|jpe?g|svg|tiff?)$")
    VIDEO_REGEXP = re.compile(r"^[.](webm|mp4)$")

    def __init__(self, url, desc):
        self.url = url
        self.desc = desc

    def is_image(self):
        _, ext = os.path.splitext(self.url)
        return ext in ["png", "jpg", "jepg", "gif", "svg"]

    def is_video(self):
        _, ext = os.path.splitext(self.url)
        return ext in ["mp4", "webm"]

    @classmethod
    def match(cls, document, line, index):
        match = cls.REGEXP.match(line[index:])
        if not match:
            return None, 0
        return cls(match[1], match[2]), len(match[0])


class Percent(object):
    REGEXP = re.compile(r"\[(\d+/\d+|\d+%)\]")

    def __init__(self, num):
        self.num = num

    @classmethod
    def match(cls, document, line, index):
        match = cls.REGEXP.match(line[index:])
        if not match:
            return None, 0
        return cls(match[1]), len(match[0])


class Emphasis(object):
    def __init__(self, marker, children=[]):
        self.marker = marker
        self.children = children

    @classmethod
    def match(cls, document, line, index):
        marker = line[index]

        needparse = True
        if marker in ["*", "/", "+", "_"]:
            needparse = True
        elif marker in ["=", "~", "`"]:
            needparse = False
        else:
            return None, 0

        if _valid_pre_border(line, index - 1):
            return None, 0
        idx, end = index + 1, len(line)
        while idx < end:
            if line[idx] == marker and idx != index + 1 and _valid_end_border(
                    line, idx + 1):
                b = cls(marker=marker,
                        children=document.parse_objects(
                            line[index + 1:idx],
                            not needparse,
                        ))
                if _is_span(line, idx + 1):
                    return b, idx - index + 2
                return b, idx - index + 1
            idx = idx + 1
        return None, 0


class Timestamp(object):
    REGEXP = re.compile(
        r"^<(\d{4}-\d{2}-\d{2})( [A-Za-z]+)?( \d{2}:\d{2})?( \+\d+[dwmy])?>")

    def __init__(self, date="", time="", interval=None):
        self.date = date
        self.time = time
        self.interval = interval

    @classmethod
    def match(cls, document, line, index):
        match = cls.REGEXP.match(line[index:])
        if not match:
            return None, 0
        date, time, interval = match[1], match[3], match[4]
        return cls(date, time, interval), len(match[0])


class Footnote(object):
    REGEXP = re.compile(r"(^|.*?(?<![/\\]))(\[fn:(.+?)\])(.*?|$)")

    def __init__(self, content):
        self.content = content

    @classmethod
    def match(cls, document, line, index):
        match = cls.REGEXP.match(line[index:])
        if not match:
            return None, 0
        return None, 0


class LineBreak(object):
    def __init__(self, count):
        self.count = count

    @classmethod
    def match(cls, document, line, index):
        beg, end = index, len(line)
        while beg < end:
            if line[beg] != "\n":
                break
            beg = beg + 1
        count = beg - index
        if count > 0:
            return cls(count), count
        return None, 0

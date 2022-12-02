#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re


def string_split(s, sep):
    if not s:
        return []
    return s.split(sep)


def is_blankline(line):
    return line.strip() == ""


class Section(object):
    def __init__(self):
        self.idx = ""
        self.last = None
        self.parent = None
        self.children = []
        self.heading = None

    @property
    def stars(self):
        return self.heading.stars

    def add(self, n):
        parent = None
        if self.last is None:
            parent = self
        elif n.stars > self.last.stars:
            parent = self.last
        elif n.stars == self.last.stars:
            parent = self.last.parent
        else:
            parent = self.last.parent
            while parent.heading and n.stars <= parent.stars:
                parent = parent.parent
        b = Section()
        b.heading = n
        b.parent = parent
        parent.children.append(b)
        if parent.heading is None:
            b.idx = str(len(parent.children))
        else:
            b.idx = f"{parent.idx}.{len(parent.children)}"
        self.last = b
        return b.idx


class Heading(object):
    '''
    STARS KEYWORD PRIORITY TITLE TAGS
    '''
    REGEXP = re.compile(r"^(\*+)\s+(.*?)(?:\r?\n|$)")
    TITLE_REGEXP = re.compile(r"^(?:\[#([A-C])\])?\s*(.+?)(?:\s+:(.+?):)?$")

    def __init__(self,
                 title=[],
                 stars=1,
                 keyword=None,
                 priority=None,
                 tags=[],
                 properties=None,
                 children=[]):
        self.index = ""
        self.title = title
        self.stars = stars
        self.keyword = keyword
        self.priority = priority
        self.tags = tags
        self.properties = properties
        self.children = children

    def id(self):
        if self.properties:
            custom_id = self.properties.get("CUSTOM_ID")
            if custom_id:
                return custom_id
        return f"heading-{self.index}"

    @classmethod
    def match(cls, document, lines):
        match = cls.REGEXP.match(lines[0])
        if not match:
            return None, 0

        keyword = ""
        title = match[2]

        titles = title.split(" ", 1)
        if len(titles) > 1 and document.is_todo(titles[0]):
            keyword = titles[0]
            title = titles[1]

        tmatch = cls.TITLE_REGEXP.match(title)
        b = cls(stars=len(match[1]),
                keyword=keyword,
                priority=tmatch[1],
                tags=string_split(tmatch[3], ":"))
        b.title = document.parse_objects(tmatch[2])
        b.index = document.sections.add(b)

        idx, end = 1, len(lines)
        while idx < end:
            m = cls.REGEXP.match(lines[idx])
            if m and len(m[1]) <= b.stars:
                break
            idx = idx + 1

        children = document.parse_all(lines[1:idx])
        if len(children) > 0 and isinstance(children[0], PropertyDrawer):
            b.properties = children[0]
            children = children[1:]
        b.children = children
        return b, idx


class Block(object):
    BEGIN_REGEXP = re.compile(r"(?i)^(\s*)#\+BEGIN_(\w+)(.*)")
    END_REGEXP = re.compile(r"(?i)^(\s*)#\+END_(\w+)")
    DYNAMIC_BEGIN_REGEXP = re.compile(r"(?i)^(\s*)#\+BEGIN:\s*(.*)")
    DYNAMIC_END_REGEXP = re.compile(r"(?i)^(\s*)#\+END:\s*$")

    def __init__(self, block_type, parameters=[], result=None, children=[]):
        self.block_type = block_type
        self.parameters = parameters
        self.result = result
        self.children = children

    @classmethod
    def match(cls, document, lines):
        match = cls.BEGIN_REGEXP.match(lines[0])
        if not match:
            return None, 0

        block_type = match[2].upper()
        idx, end = 1, len(lines)
        while idx < end:
            m = cls.END_REGEXP.match(lines[idx])
            if m and m[2].upper() == block_type:
                b = cls(
                    block_type=block_type,
                    parameters=match[3].strip().split(" "),
                )
                if block_type == "VERSE":
                    b.children = document.parse_objects("\n".join(
                        lines[1:idx]), )
                elif block_type in ["SRC", "EXAMPLE"]:
                    b.children = document.parse_all(lines[1:idx], True)
                else:
                    b.children = document.parse_all(lines[1:idx])
                return b, idx + 1
            idx = idx + 1
        return None, 0


class BlockResult(object):
    REGEXP = re.compile(r"(?i)^(\s*)#\+RESULTS:")
    CONTENT_REGEXP = re.compile(r"(?:^|\s+):(\s+(.*)|$)")

    def __init__(self, children=[]):
        self.children = children

    @classmethod
    def match(cls, document, lines):
        match = cls.REGEXP.match(lines[0])
        if not match:
            return None, 0
        idx, end = 1, len(lines)
        while idx < end:
            m = cls.REGEXP.match(lines[idx])
            if not m:
                return cls(document.parse_all(lines[1:idx])), idx + 1
            idx = idx + 1
        return None, 0


class Drawer(object):
    BEGIN_REGEXP = re.compile(r"^(\s*):(\S+):\s*$")
    END_REGEXP = re.compile(r"^(\s*):END:\s*$")

    def __init__(self, drawer_type, children=[]):
        self.drawer_type = drawer_type
        self.children = children

    @classmethod
    def match(cls, document, lines):
        match = cls.BEGIN_REGEXP.match(lines[0])
        if not match:
            return None, 0
        idx, end = 1, len(lines)
        while idx < end:
            m = cls.END_REGEXP.match(lines[idx])
            if not m:
                idx = idx + 1
                continue
            if match[2].upper() == "PROPERTIES":
                n, _ = document.parse_proerty_drawer(lines[1:idx])
                return n, idx
            n = cls(
                drawer_type=match[2],
                children=document.parse_all(lines[1:idx]),
            )
            return n, idx
        return None, 0


class PropertyDrawer(object):
    REGEXP = re.compile(r"^(\s*):(\S+):(\s+(.*)$|$)")

    def __init__(self, properties=dict()):
        self.properties = properties

    def get(self, key):
        return self.properties.get(key)

    @classmethod
    def match(cls, document, lines):
        properties = dict()
        for line in lines:
            match = cls.REGEXP.match(line)
            if not match:
                continue
            properties[match[2]] = match[4]
        return cls(properties), len(lines)


class Hr(object):
    REGEXP = re.compile(r"^\s*\-{5,}\s*")

    @classmethod
    def match(cls, document, lines):
        match = cls.REGEXP.match(lines[0])
        if not match:
            return None, 0
        return cls(), 1


class Blankline(object):
    def __init__(self, count=0):
        self.count = count

    @classmethod
    def match(cls, document, lines):
        idx, end = 0, len(lines)
        while idx < end:
            if not is_blankline(lines[idx]):
                break
            idx = idx + 1
        if idx > 0:
            return cls(idx), idx
        return None, 0


class Pargraph(object):
    def __init__(self, children=[]):
        self.children = children

    @classmethod
    def match(cls, document, lines):
        idx, end = 1, len(lines)
        while idx < end:
            next_node, n = document.parse(lines[idx:])
            if next_node:
                return cls(), next_node, idx + n
            idx = idx + 1
        return cls(), None, idx


class Keyword(object):
    REGEXP = re.compile(r"^(\s*)#\+([^:]+):(\s+(.*)|$)")

    def __init__(self, key, value=""):
        self.key = key
        self.value = value

    def get(self, key):
        pass

    @classmethod
    def match(cls, document, lines):
        match = cls.REGEXP.match(lines[0])
        if not match:
            return None, 0
        n = cls(match[2], match[4])
        if n.key in ["CAPTION", "ATTR_HTML"]:
            pass
        else:
            document.set(n.key, n.value)
        return n, 1


class Comment(object):
    REGEXP = re.compile(r"^(\s*)#(.*)")

    def __init__(self, content):
        self.content = content

    @classmethod
    def match(cls, document, lines):
        beg, end = 0, len(lines)
        while beg < end:
            if not cls.REGEXP.match(lines[beg]):
                break
        if beg == 0:
            return None, 0
        return cls(), 0

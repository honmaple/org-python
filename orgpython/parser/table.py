#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re


def split_fields():
    pass


class TableColumn(object):
    def __init__(self, align, is_header=False, children=[]):
        self.align = align
        self.children = children
        self.is_header = is_header


class TableRow(object):
    SEP_REGEXP = re.compile(r"^(\s*)(\|[+-|]*)\s*$")
    ROW_REGEXP = re.compile(r"^(\s*)(\|.*)")
    ALIGN_REGEXP = re.compile(r"^<(l|c|r)>$")

    def __init__(self, separator=False, children=None):
        self.separator = separator
        self.children = children

    @classmethod
    def match(cls, document, lines):
        line = lines[0]
        match = cls.ROW_REGEXP.match(line)
        if not match:
            return None, 0
        if cls.SEP_REGEXP.match(line):
            return cls(), 1

        aligns = []
        children = []
        for text in split_fields(match[2]):
            text = text.strip()
            m = cls.ALIGN_REGEXP.match(text)
            if m:
                aligns.append(m[1])
            children.append(TableColumn())
        return cls(children=children), 1


class Table(object):
    def __init__(self, aligns, numberic=False, children=[]):
        self.aligns = aligns
        self.numberic = numberic
        self.children = children

    @classmethod
    def match(cls, document, lines):
        children = []
        idx, end = 0, len(lines)
        while idx < end:
            row, ridx = document.parse_tablerow(lines[idx:])
            if not row:
                break
            idx = idx + ridx
            children.append(row)
        if len(children) == 0:
            return None, 0
        return cls(children=children), idx

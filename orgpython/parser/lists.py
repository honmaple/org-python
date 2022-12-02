#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re


def line_level(line):
    return len(line) - len(line.lstrip())


def is_blankline(line):
    return line.strip() == ""


class List(object):
    def __init__(self, list_type, children=[]):
        self.list_type = list_type
        self.children = children

    @classmethod
    def match(cls, document, lines):
        item, idx = document.parse_listitem(lines)
        if not item:
            return None, 0

        li = cls(list_type=item.kind(), children=[item])
        end = len(lines)

        while idx < end:
            level = line_level(lines[idx])
            if level < item.level:
                break
            next_item, ln = document.parse_listitem(lines[idx:])
            if next_item and next_item.level == item.level and next_item.kind(
            ) == item.kind():
                li.children.append(item)
                idx = idx + ln
                continue
            break
        return li, idx


class ListItem(object):
    '''
    BULLET COUNTER-SET CHECK-BOX TAG CONTENTS
    '''
    REGEXP = re.compile(r"^(\s*)(([0-9]+|[a-zA-Z])[.)]|[+*-])(\s+(.*)|$)")
    CHECKBOX_REGEXP = re.compile(r"\[( |X|-)\]\s")

    ORDERLIST = "OrderList"
    UNORDERLIST = "UnorderList"
    DESCRIPTIVE = "Descriptive"

    def __init__(self, title="", checkbox="", children=[]):
        self.title = title
        self.checkbox = checkbox
        self.bullet = ""
        self.level = 0
        self.children = children

    def kind(self):
        if self.bullet in ["-*+"]:
            return self.UNORDERLIST
        return self.ORDERLIST

    @classmethod
    def match(cls, document, lines):
        match = cls.REGEXP.match(lines[0])
        if not match:
            return None, 0
        checkbox, title = "", match[4]
        m = cls.CHECKBOX_REGEXP.match(title)
        if m:
            checkbox, title = m[1], title[len("[ ] ")]
        b = cls(title, checkbox)
        spa = 0
        idx, end = 1, len(lines)
        while idx < end:
            if is_blankline(lines[idx]):
                spa = spa + 1
                if spa == 2:
                    break
                idx = idx + 1
                continue

            spa = 0
            level = line_level(lines[idx])
            if level <= b.level:
                break
            idx = idx + 1
        b.children = document.parse_all([title] + lines[1:idx])
        return b, idx

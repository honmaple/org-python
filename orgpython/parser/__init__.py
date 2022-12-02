#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .elements import (Blankline, Block, BlockResult, Drawer, Heading, Hr,
                       Pargraph, Section, PropertyDrawer)
from .lists import List, ListItem
from .objects import Emphasis, Footnote, Percent, Text, Timestamp
from .table import Table, TableRow


class Document(object):
    def __init__(self, content, keywords=dict(), properties=dict()):
        keywords.setdefault("TODO", "TODO | DONE | CANCELED")
        self.keywords = keywords
        self.properties = properties
        self.todo_keywords = keywords["TODO"].split(" | ")
        self.sections = Section()
        self.children = self.parse_all(content.split("\n"))

    def is_todo(self, keyword):
        return keyword in self.todo_keywords

    def get(self, key):
        return self.keywords.get(key)

    def set(self, key, value):
        self.keywords[key] = value

    def parse_text(self, line, index):
        return Text.match(self, line, index)

    def parse_percent(self, line, index):
        return Percent.match(self, line, index)

    def parse_timestamp(self, line, index):
        return Timestamp.match(self, line, index)

    def parse_footnote(self, line, index):
        return Footnote.match(self, line, index)

    def parse_emphasis(self, line, index):
        return Emphasis.match(self, line, index)

    def parse_object(self, line, index):
        tokens = [
            "linebreak", "emphais", "link", "percent", "footnote", "timestamp"
        ]
        for b in tokens:
            func = "parse_" + b
            if not hasattr(self, func):
                continue
            obj, idx = getattr(self, func)(line, index)
            if not obj:
                continue
            return obj, idx
        return None, 0

    def parse_objects(self, line, raw=False):
        if raw:
            return [Text(line)]
        idx, end = 0, len(line)
        objs = []
        while idx < end:
            obj, i = self.parse_object(line, idx)
            if obj:
                objs.append(obj)
                idx = idx + i
                continue
            obj, next_obj, i = self.parse_text(line, idx)
            if obj:
                objs.append(obj)
            if next_obj:
                objs.append(next_obj)
            idx = idx + i
        return objs

    def parse(self, lines):
        names = [
            "blankline", "heading", "table", "list", "drawer", "block",
            "block_result", "keyword", "hr"
        ]
        for name in names:
            func = "parse_" + name
            if not hasattr(self, func):
                continue
            node, idx = getattr(self, func)(lines)
            if not node:
                continue
            return node, idx
        return None, 0

    def parse_all(self, lines, raw=False):
        if raw and len(lines) > 0:
            return self.parse_objects("\n".join(lines), raw)

        idx, end, nodes = 0, len(lines), []
        while idx < end:
            node, i = self.parse(lines[idx:])
            if node:
                idx = idx + i
                nodes.append(node)
                continue

            node, next_node, i = self.parse_pargraph(lines[idx:])
            if node:
                nodes.append(node)
            if next_node:
                nodes.append(next_node)
            idx = idx + i
        return nodes

    def parse_hr(self, lines):
        return Hr.match(self, lines)

    def parse_section(self, heading):
        return self.sections.add(heading)

    def parse_heading(self, lines):
        return Heading.match(self, lines)

    def parse_pargraph(self, lines):
        return Pargraph.match(self, lines)

    def parse_blankline(self, lines):
        return Blankline.match(self, lines)

    def parse_block(self, lines):
        return Block.match(self, lines)

    def parse_block_result(self, lines):
        return BlockResult.match(self, lines)

    def parse_drawer(self, lines):
        return Drawer.match(self, lines)

    def parse_proerty_drawer(self, lines):
        return PropertyDrawer.match(self, lines)

    def parse_list(self, lines):
        return List.match(self, lines)

    def parse_listitem(self, lines):
        return ListItem.match(self, lines)

    def parse_table(self, lines):
        return Table.match(self, lines)

    def parse_tablerow(self, lines):
        return TableRow.match(self, lines)

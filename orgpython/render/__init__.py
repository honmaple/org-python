#!/usr/bin/env python
# -*- coding: utf-8 -*-

from orgpython.parser import Pargraph

from .html import HTML


def render(r, n, level):
    name = n.__class__.__name__.lower()
    func = "render_" + name
    if hasattr(r, func):
        return getattr(r, func)(n, level)
    if hasattr(n, "children"):
        return r._render(
            n.__class__.__name__,
            n.children,
            level,
            "\n",
        )
    return name


_ = HTML


class Debug(object):
    def __init__(self, document):
        self.document = document

    def _render(self, name, children, level, sep):
        if len(children) > 0:
            text = sep.join([render(self, child, level) for child in children])
            return f"{' ' * level * 2}{name}\n{text}"
        return " " * level * 2 + name

    def render_paragraph(self, n: Pargraph, level: int):
        return "%s%s\n%s%s" % (
            " " * level * 2,
            n.__class__.__name__,
            " " * (level + 1) * 2,
            "",
        )

    def render(self):
        return self._render("", self.document.children, 0, "\n")

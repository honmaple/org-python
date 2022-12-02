#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from orgpython.parser.document import *

from orgpython.parser.elements import (
    Section,
    Heading,
    Pargraph,
    Hr,
    Blankline,
    Block,
    BlockResult,
    Drawer,
)

from orgpython.parser.lists import (
    List,
    ListItem,
)

from orgpython.parser.table import (
    Table,
    TableRow,
    TableColumn,
)

from orgpython.parser.objects import (
    Text,
    Percent,
    Timestamp,
    Footnote,
    Emphasis,
    LineBreak,
    Link,
)

try:
    import pygments
    from pygments import lexers
    from pygments import formatters
except ImportError:
    pygments = None


def highlight(language, text):
    if pygments is None:
        return text

    try:
        lexer = lexers.get_lexer_by_name(language)
    except pygments.util.ClassNotFound:
        lexer = lexers.guess_lexer(text)
    formatter = formatters.HtmlFormatter()
    return pygments.highlight(text, lexer, formatter)


class HTML(object):
    def __init__(self, document=None, toc=False, offset=0, highlight=None):
        self.document = document
        self.toc = toc
        self.offset = offset
        self.highlight = highlight

    def _render_node(self, child, level):
        name = child.__class__.__name__.lower()
        func = "render_" + name
        if not hasattr(self, func):
            return ""
        if name in [
                "text",
                "linebreak",
                "timestamp",
                "footnote",
                "percent",
                "link",
        ]:
            return getattr(self, func)(child)
        return getattr(self, func)(child, level)

    def _render(self, children, level, sep):
        strs = [self._render_node(child, level) for child in children]
        return sep.join(strs)

    def render_text(self, n: Text):
        return n.content

    def render_linebreak(self, n: LineBreak):
        return "\n" * n.count

    def render_timestamp(self, n: Timestamp):
        return f"<code>[{n.num}]</code>"

    def render_footnote(self, n: Footnote):
        return f'<sup><a id="fnr:{n.content}" class="footref" href="#fn.{n.content}">{n.content}</a></sup>'

    def render_percent(self, n: Percent):
        return f"<code>[{n.num}]</code>"

    def render_link(self, n: Link):
        if n.is_image():
            return f"<img src=\"{n.url}\"/>"
        if n.is_video():
            return f"<video src=\"{n.url}\">{n.url}</video>"
        if not n.desc:
            return f"<a href=\"{n.url}\">{n.url}</a>".format(n.url)
        return f"<a href=\"{n.url}\">{n.desc}</a>"

    def render_emphasis(self, n: Emphasis):
        text = self._render(n.children)
        if n.marker in ["=", "~", "`"]:
            return f"<code>{text}</code>"
        m = {
            "*": "<bold>%s</bold>",
            "_": "<span style=\"text-decoration:underline\">%s</span>",
            "+": "<del>%s</del>",
            "/": "<i>%s</i>",
        }
        if n.marker in m:
            return m[n.marker] % text
        return ""

    def _render_heading(self, n: Heading, level: int):
        keyword = ""
        if n.keyword:
            keyword = f"<span class=\"todo\">{n.keyword}</span>"
        priority = ""
        if n.priority:
            priority = f"<span class=\"priority\">{n.priority}</span>"
        tags = "".join([f"<span class=\"tag\">{tag}</span>" for tag in n.tags])
        stars = n.stars + self.offset
        title = self._render(n.title, level, "")
        return f"<h{stars}>{keyword}{priority}{title}{tags}</h{stars}>"

    def render_section(self, n: Section):
        text = ""
        for child in n.children:
            hid = child.heading.id()
            heading = self._render_heading(child.heading, 0)
            text = text + f"<li><a href=\"{hid}\">{heading}</a>"
            if child.children:
                text = text + "\n"
                text = text + self.render_section(child)
            text = text + "</li>\n"
        return f"<ul>{text}</ul>"

    def render_heading(self, n: Heading, level: int):
        heading = self._render_heading(n, level)
        text = self._render(n.children, level, "\n")
        return f"{heading}{text}"

    def render_list_item(self, n: ListItem, level: int):
        text = self._render(n.children, level, "\n")
        if n.status != "":
            text = f"<code>{n.status}</code> {text}"
        return f"<li>\n{text}</li>"

    def render_list(self, n: List, level: int):
        text = self._render(n.children, level, "\n")
        if n.list_type == "order":
            return f"<ol>\n{text}\n</ol>"
        if n.list_type == "unorder":
            return f"<ul>\n{text}\n</ul>"
        if n.list_type == "d":
            return f"<dl>\n{text}\n</dl>"
        return ""

    def render_table_column(self, n: TableColumn, level: int):
        text = self._render(n.children, level, "")
        if n.is_header:
            return f"<th class=\"align-\">{text}</th>"
        return f"<td class=\"align-\">{text}</td>"

    def render_table_row(self, n: TableRow, level: int):
        if n.separator:
            return ""
        text = self._render(n.children, level, "\n")
        return f"<tr>\n{text}\n</tr>"

    def render_table(self, n: Table, level: int):
        text = self._render(n.children, level, "\n")
        return f"<table>\n{text}\n</table>"

    def render_block(self, n: Block, level: int):
        if n.block_type == "SRC":
            lang = n.parameters[0]
            text = self._render(n.children)
            if self.highlight:
                return self.highlight(lang, text)
            return f"<pre class=\"src src-{lang}\">\n{text}\n</pre>"
        if n.block_type == "EXAMPLE":
            text = self._render(n.children)
            return f"<pre class=\"src src-example\">\n{text}\n</pre>"
        if n.block_type == "CENTER":
            text = self._render(n.children)
            return f"<p style=\"text-align:center;\">{text}</p>"
        if n.block_type == "QUOTE":
            text = self._render(n.children)
            return f"<blockquote>\n{text}\n</blockquote>"
        if n.block_type == "VERSE":
            te = ""
            for child in n.children:
                if isinstance(child, LineBreak):
                    te = te + "<br />\n"
                    continue
                te = te + self._render_node(child, level)
            return f"<p>\n{te}\n</p>"
        if n.block_type == "EXPORT":
            return text

        text = self._render(n.children)
        return text

    def render_block_result(self, n: BlockResult, level: int):
        return self._render(n.children, level, "\n")

    def render_drawer(self, n: Drawer, level: int):
        return self._render(n.children, level, "\n")

    def render_blankline(self, n: Blankline, level: int):
        return ""

    def render_hr(self, n: Hr, level: int):
        return "<hr/>"

    def render_paragraph(self, n: Pargraph, level: int):
        text = self._render(n.children, level, "")
        return f"<p>\n{text}\n</p>"

    def render(self):
        text = self._render(self.document.children, 0, "\n")
        if not self.toc or self.document.get("toc") == "nil":
            return text
        return self.render_section(self.document.sections) + text

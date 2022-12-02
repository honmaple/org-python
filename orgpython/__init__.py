#!/usr/bin/env python
# -*- coding: utf-8 -*-

from orgpython.parser import Document
from orgpython.render import HTML, Debug


def to_html(content, **kwargs):
    return render_html(content, **kwargs)


def render_html(content, **kwargs):
    r = HTML(**kwargs)
    r.document = Document(content)
    return r.render()


def render_debug(content, **kwargs):
    r = Debug(**kwargs)
    r.document = Document(content)
    return r.render()

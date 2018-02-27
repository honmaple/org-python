#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ********************************************************************************
# Copyright © 2018 jianglin
# File Name: inline.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2018-02-26 11:41:22 (CST)
# Last Update: Tuesday 2018-02-27 09:53:40 (CST)
#          By:
# Description:
# ********************************************************************************
from collections import OrderedDict

from .regex import Regex

html_escape_table = {
    # "&": "&amp;",
    # '"': "&quot;",
    # "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
}


def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c, c) for c in text)


class InlineElement(object):
    label = '{text}'

    def __init__(self, text, regex):
        self.text = text
        self.regex = regex
        self.children = []

    def to_html(self):
        def _match(match):
            text = self.label.format(text=match.group(2))
            if match.group(1):
                text = match.group(1) + text
            if match.group(3):
                text = text + match.group(3)
            return text

        return self.regex.sub(_match, self.text)

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, self.text.strip())


class Fn(InlineElement):
    '''
    <sup><a id="fnr.1" class="footref" href="#fn.1">1</a></sup>
    '''
    label = '<sup><a id="fnr:{text}" class="footref" href="#fn.{text}">{text}</a></sup>'

    def to_html(self):
        def _match(match):
            return self.label.format(text=match.group('text'))

        return self.regex.sub(_match, self.text)


class Underlined(InlineElement):
    label = '<span style="text-decoration:underline">{text}</span>'


class Bold(InlineElement):
    label = '<b>{text}</b>'


class Italic(InlineElement):
    label = '<i>{text}</i>'


class Code(InlineElement):
    label = '<code>{text}</code>'


class Delete(InlineElement):
    label = '<del>{text}</del>'


class Verbatim(InlineElement):
    label = '<code>{text}</code>'


class NewLine(InlineElement):
    def to_html(self):
        return self.regex.sub('<br/>', self.text)


class Image(InlineElement):
    label = '<img src="{text}"/>'

    def to_html(self):
        def _match(match):
            return self.label.format(text=match.group('text'))

        return self.regex.sub(_match, self.text)


class Link(InlineElement):
    label = '<a href="{href}">{text}</a>'

    def to_html(self):
        def _match(match):
            if not match.group('text'):
                return Image.label.format(text=match.group('href'))
            return self.label.format(
                href=match.group('href'), text=match.group('text'))

        return self.regex.sub(_match, self.text)


class OriginLink(InlineElement):
    label = '<a href="{0}">{0}</a>'

    def to_html(self):
        def _match(match):
            return self.label.format(match.group())

        return self.regex.sub(_match, self.text)


class Text(InlineElement):
    regex = OrderedDict([
        ('comment', Regex.comment),
        ('newline', Regex.newline),
        ('italic', Regex.italic),
        ('bold', Regex.bold),
        ('underlined', Regex.underlined),
        ('code', Regex.code),
        ('delete', Regex.delete),
        ('verbatim', Regex.verbatim),
        ('fn', Regex.fn),
        ('link', Regex.link),
        ('image', Regex.image),
    ])

    def __init__(self, text, force=True):
        self.text = text
        self.force = force
        if self.force:
            self.text = html_escape(self.text)

    def parse(self, text):
        if not isinstance(text, str):
            text = text.to_html()
        if not self.force:
            return text
        for parse, regex in self.regex.items():
            if regex.search(text):
                return getattr(self, 'parse_' + parse)(text, regex)
        return text

    def parse_comment(self, text, regex):
        return text

    def parse_newline(self, text, regex):
        return self.parse(NewLine(text, regex))

    def parse_italic(self, text, regex):
        return self.parse(Italic(text, regex))

    def parse_bold(self, text, regex):
        return self.parse(Bold(text, regex))

    def parse_underlined(self, text, regex):
        return self.parse(Underlined(text, regex))

    def parse_code(self, text, regex):
        return self.parse(Code(text, regex))

    def parse_delete(self, text, regex):
        return self.parse(Delete(text, regex))

    def parse_verbatim(self, text, regex):
        return self.parse(Verbatim(text, regex))

    def parse_fn(self, text, regex):
        return self.parse(Fn(text, regex))

    def parse_link(self, text, regex):
        return self.parse(Link(text, regex))

    def parse_image(self, text, regex):
        return self.parse(Image(text, regex))

    def to_html(self):
        return self.parse(self.text)

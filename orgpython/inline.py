#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ********************************************************************************
# Copyright © 2018 jianglin
# File Name: inline.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2018-02-26 11:41:22 (CST)
# Last Update: Wednesday 2018-02-28 21:11:25 (CST)
#          By:
# Description:
# ********************************************************************************
from collections import OrderedDict

from .regex import Regex


def html_escape(text, quote=False):
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    if quote:
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&#39;')
    return text


class InlineElement(object):
    label = '{text}'

    def __init__(self, text):
        self.text = text
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

    def __repr__(self):
        return self.__str__()


class Fn(InlineElement):
    '''
    <sup><a id="fnr.1" class="footref" href="#fn.1">1</a></sup>
    '''
    label = '<sup><a id="fnr:{text}" class="footref" href="#fn.{text}">{text}</a></sup>'
    regex = Regex.fn

    def to_html(self):
        def _match(match):
            return self.label.format(text=match.group('text'))

        return self.regex.sub(_match, self.text)


class Comment(InlineElement):
    regex = Regex.comment

    def to_html(self):
        return self.text


class Underlined(InlineElement):
    label = '<span style="text-decoration:underline">{text}</span>'
    regex = Regex.underlined


class Bold(InlineElement):
    label = '<b>{text}</b>'
    regex = Regex.bold


class Italic(InlineElement):
    label = '<i>{text}</i>'
    regex = Regex.italic


class Code(InlineElement):
    label = '<code>{text}</code>'
    regex = Regex.code


class Delete(InlineElement):
    label = '<del>{text}</del>'
    regex = Regex.delete


class Verbatim(InlineElement):
    label = '<code>{text}</code>'
    regex = Regex.verbatim


class NewLine(InlineElement):
    regex = Regex.newline

    def to_html(self):
        return self.regex.sub('<br/>', self.text)


class Image(InlineElement):
    label = '<img src="{text}"/>'
    regex = Regex.image

    def to_html(self):
        def _match(match):
            return self.label.format(text=match.group('text'))

        return self.regex.sub(_match, self.text)


class Link(InlineElement):
    label = '<a href="{href}">{text}</a>'
    regex = Regex.link

    def to_html(self):
        def _match(match):
            text = match.group('text')
            href = match.group('href')
            if not text:
                return Image.label.format(text=href)
            return self.label.format(href=href, text=text)

        return self.regex.sub(_match, self.text)


class OriginLink(InlineElement):
    label = '<a href="{0}">{0}</a>'
    regex = Regex.origin_link

    def to_html(self):
        def _match(match):
            return self.label.format(match.group())

        return self.regex.sub(_match, self.text)


class Text(InlineElement):
    regex = OrderedDict([
        ('comment', Comment),
        ('newline', NewLine),
        ('italic', Italic),
        ('bold', Bold),
        ('underlined', Underlined),
        ('code', Code),
        ('delete', Delete),
        ('verbatim', Verbatim),
        ('fn', Fn),
        ('link', Link),
        ('image', Image),
    ])

    def __init__(self, text, force=True, escape=False):
        self.text = text
        self.force = force

        if escape:
            self.text = html_escape(text)

    def parse_comment(self, text):
        return text

    def parse(self, text):
        if not isinstance(text, str):
            text = text.to_html()
        if not self.force:
            return text
        for name, element in self.regex.items():
            if element.regex.search(text):
                name = "parse_" + name
                return getattr(self, name)(text) if hasattr(
                    self, name) else self.parse(element(text))
        return text

    def to_html(self):
        return self.parse(self.text)

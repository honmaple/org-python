#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ********************************************************************************
# Copyright © 2018-2019 jianglin
# File Name: inline.py
# Author: jianglin
# Email: mail@honmaple.com
# Created: 2018-02-26 11:41:22 (CST)
# Last Update: Thursday 2019-06-06 21:11:12 (CST)
#          By:
# Description:
# ********************************************************************************
# from orgpython1 import regex as R
from . import regex as R


def html_escape(text, quote=False):
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    if quote:
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&#39;')
    return text


class InlineText(object):
    def __init__(self, text, needparse=True, escape=True):
        self.text = text
        self.lines = []
        self.escape = escape
        self.needparse = needparse

        self.items = [
            'comment',
            'newline',
            'hr',
            'italic',
            'bold',
            'underlined',
            'code',
            'delete',
            'verbatim',
            'fn',
            'link',
            'image',
        ]

    def init(self):
        if self.escape: self.text = html_escape(self.text)

    def _inline(self, text, label="", regex=None):
        if not regex or not regex.search(text):
            return text

        def _match(match):
            text = label.format(match.group(2))
            if match.group(1):
                text = match.group(1) + text
            if match.group(3):
                text = text + match.group(3)
            return text

        return regex.sub(_match, text)

    def comment(self, text):
        return text

    def newline(self, text):
        if R.newline.search(text):
            return R.newline.sub('<br/>', text)
        return text

    def hr(self, text):
        if R.hr.search(text):
            return R.hr.sub('<hr>', text)
        return text

    def italic(self, text):
        return self._inline(text, '<i>{0}</i>', R.italic)

    def bold(self, text):
        return self._inline(text, '<b>{0}</b>', R.bold)

    def underlined(self, text):
        return self._inline(
            text, '<span style="text-decoration:underline">{0}</span>',
            R.underlined)

    def code(self, text):
        return self._inline(text, '<code>{0}</code>', R.code)

    def delete(self, text):
        return self._inline(text, '<del>{0}</del>', R.delete)

    def verbatim(self, text):
        return self._inline(text, '<code>{0}</code>', R.delete)

    def fn(self, text):
        if not R.fn.search(text):
            return text

        def _match(match):
            return '<sup><a id="fnr:{0}" class="footref" href="#fn.{0}">{0}</a></sup>'.format(
                match.group(1))

        return R.fn.sub(_match, text)

    def link(self, text):
        if not R.link.search(text):
            return text

        def _match(match):
            href = match.group(1)
            text = match.group(2)
            if not text:
                return '<img src="{0}"/>'.format(href)
            return '<a href="{0}">{1}</a>'.format(href, text)

        return R.link.sub(_match, text)

    def image(self, text):
        if not R.image.search(text):
            return text

        def _match(match):
            return '<img src="{0}"/>'.label.format(match.group(1))

        return R.image.sub(_match, text)

    def to_html(self):
        if not self.needparse:
            return self.text
        text = self.text
        for name in self.items:
            text = getattr(self, name)(text)
        return text

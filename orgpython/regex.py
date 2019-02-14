#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ********************************************************************************
# Copyright © 2019 jianglin
# File Name: regex.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2018-02-26 11:42:14 (CST)
# Last Update: Thursday 2019-02-14 12:08:15 (CST)
#          By:
# Description:
# ********************************************************************************
import re


class Regex(object):
    _inline_regex = r'((?:^|\s|[\u4e00-\u9fa5])(?![/\\])){0}([^\s]*?|[^\s]+.*?[^\s]+)(?<![/\\]|\s){0}(\B|[\u4e00-\u9fa5])'
    blankline = re.compile(r'^$')
    newline = re.compile(r'\\$')
    heading = re.compile(r'^(?P<level>\*+)\s+(?P<title>.+)$')
    comment = re.compile(r'^(\s*)#(.*)$')
    bold = re.compile(_inline_regex.format('\*'))
    italic = re.compile(_inline_regex.format('\*\*'))
    underlined = re.compile(_inline_regex.format('_'))
    code = re.compile(_inline_regex.format('='))
    delete = re.compile(_inline_regex.format('\+'))
    verbatim = re.compile(_inline_regex.format('~'))

    # image = re.compile(r'\[\[(?P<text>.+?)[.](jpg|png|gif)\]\]')
    # link = re.compile(r'\[\[(?P<href>https?://.+?)\](?:\[(?P<text>.+?)\])?\]')

    image = re.compile(r'\[\[(?P<text>.+?)\]\]')
    link = re.compile(r'\[\[(?P<href>.+?)\](?:\[(?P<text>.+?)\])?\]')
    origin_link = re.compile(
        r'(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?'
    )
    fn = re.compile(r'\[fn:(?P<text>.+?)\]')
    hr = re.compile(r'^\s*\-{5,}\s*')

    begin_example = re.compile(r'\s*#\+(BEGIN_EXAMPLE|begin_example)$')
    end_example = re.compile(r'\s*#\+(END_EXAMPLE|end_example)$')

    begin_verse = re.compile(r'\s*#\+(BEGIN_VERSE|begin_verse)$')
    end_verse = re.compile(r'\s*#\+(END_VERSE|end_verse)$')

    begin_center = re.compile(r'\s*#\+(BEGIN_CENTER|begin_center)$')
    end_center = re.compile(r'\s*#\+(END_CENTER|end_center)$')

    begin_quote = re.compile(r'\s*#\+(BEGIN_QUOTE|begin_quote)$')
    end_quote = re.compile(r'\s*#\+(END_QUOTE|end_quote)$')

    begin_src = re.compile(r'\s*#\+(BEGIN_SRC|begin_src)\s+(?P<lang>.+)$')
    end_src = re.compile(r'\s*#\+(END_SRC|end_src)$')

    begin_export = re.compile(r'\s*#\+(BEGIN_EXPORT|begin_export)\s+(?P<lang>.+)$')
    end_export = re.compile(r'\s*#\+(END_EXPORT|end_export)$')

    any_depth = re.compile(r'(?P<depth>\s*)(?P<title>.+)$')
    order_list = re.compile(r'(?P<depth>\s*)\d+(\.|\))\s+(?P<title>.+)$')
    unorder_list = re.compile(r'(?P<depth>\s*)(-|\+)\s+(?P<title>.+)$')
    checkbox = re.compile(r'\[(?P<check>.+)\]\s+(?P<title>.+)$')

    table = re.compile(r'\s*\|(?P<cells>(.+\|)+)s*$')
    table_sep = re.compile(r'^(\s*)\|((?:\+|-)*?)\|?$')
    table_setting = re.compile(r'\s*#\+ATTR_HTML:\s*:class\s*(?P<cls>.+)$')

    attr = re.compile(r'^(\s*)#\+(.*): (.*)$')

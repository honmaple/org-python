#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ********************************************************************************
# Copyright © 2018-2019 jianglin
# File Name: regex.py
# Author: jianglin
# Email: mail@honmaple.com
# Created: 2018-02-26 11:42:14 (CST)
# Last Update: Thursday 2019-06-06 21:11:43 (CST)
#          By:
# Description:
# ********************************************************************************
import re

_inline_regex = r'((?:^|\s|[\u4e00-\u9fa5])(?![/\\])){0}([^\s]*?|[^\s]+.*?[^\s]+)(?<![/\\]|\s){0}(\B|[\u4e00-\u9fa5])'
bold = re.compile(_inline_regex.format('\*'))
italic = re.compile(_inline_regex.format('\*\*'))
underlined = re.compile(_inline_regex.format('_'))
code = re.compile(_inline_regex.format('[\=|`]'))
delete = re.compile(_inline_regex.format('\+'))
verbatim = re.compile(_inline_regex.format('~'))

heading = re.compile(r'^(\*+)\s+(.+)$')
comment = re.compile(r'^(\s*)#(.*)$')
blankline = re.compile(r'^$')
newline = re.compile(r'\\$')

image = re.compile(r'\[\[(.+?)\]\]')
link = re.compile(r'\[\[(.+?)\](?:\[(.+?)\])?\]')
origin_link = re.compile(
    r'(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?'
)
fn = re.compile(r'\[fn:(.+?)\]')
hr = re.compile(r'^\s*\-{5,}\s*')

begin_example = re.compile(r'\s*#\+(BEGIN_EXAMPLE|begin_example)$')
end_example = re.compile(r'\s*#\+(END_EXAMPLE|end_example)$')

begin_verse = re.compile(r'\s*#\+(BEGIN_VERSE|begin_verse)$')
end_verse = re.compile(r'\s*#\+(END_VERSE|end_verse)$')

begin_center = re.compile(r'\s*#\+(BEGIN_CENTER|begin_center)$')
end_center = re.compile(r'\s*#\+(END_CENTER|end_center)$')

begin_quote = re.compile(r'\s*#\+(BEGIN_QUOTE|begin_quote)$')
end_quote = re.compile(r'\s*#\+(END_QUOTE|end_quote)$')

begin_src = re.compile(r'\s*#\+(BEGIN_SRC|begin_src)\s+(.+)$')
end_src = re.compile(r'\s*#\+(END_SRC|end_src)$')

begin_export = re.compile(r'\s*#\+(BEGIN_EXPORT|begin_export)\s+(.+)$')
end_export = re.compile(r'\s*#\+(END_EXPORT|end_export)$')

depth = re.compile(r'(\s*)(.+)$')
orderlist = re.compile(r'(\s*)\d+(\.|\))\s+(.+)$')
unorderlist = re.compile(r'(\s*)(-|\+)\s+(.+)$')
checkbox = re.compile(r'\[(.+)\]\s+(.+)$')

table = re.compile(r'\s*\|(.+?)\|*$')
tablesep = re.compile(r'^(\s*)\|((?:\+|-)*?)\|?$')

attr = re.compile(r'^(\s*)#\+(.*): (.*)$')

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ********************************************************************************
# Copyright © 2017-2020 jianglin
# File Name: src.py
# Author: jianglin
# Email: mail@honmaple.com
# Created: 2018-02-26 12:41:22 (CST)
# Last Update: Sunday 2020-08-16 19:45:32 (CST)
#          By:
# Description:
# ********************************************************************************
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

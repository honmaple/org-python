#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ********************************************************************************
# Copyright © 2019 jianglin
# File Name: __init__.py
# Author: jianglin
# Email: mail@honmaple.com
# Created: 2019-05-29 18:06:22 (CST)
# Last Update: Thursday 2019-06-06 17:14:32 (CST)
#          By:
# Description:
# ********************************************************************************
from .block import Block, Toc


class Org(Block):
    def __init__(self, text, offset=0, toc=True, escape=True):
        super(Org, self).__init__(text)
        self.escape = escape
        self.offset = offset
        self.toc = Toc() if toc else None

    def to_html(self, init=True):
        text = super(Org, self).to_html(init)
        if self.toc:
            text = self.toc.to_html() + text
        return text


def org_to_html(text, offset=0, toc=True, escape=True):
    return Org(text, offset, toc, escape).to_html()

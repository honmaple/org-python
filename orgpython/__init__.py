#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ********************************************************************************
# Copyright © 2017-2020 jianglin
# File Name: __init__.py
# Author: jianglin
# Email: mail@honmaple.com
# Created: 2019-05-29 18:06:22 (CST)
# Last Update: Sunday 2020-08-16 19:45:09 (CST)
#          By:
# Description:
# ********************************************************************************
from .document import Document


def to_text(content, **kwargs):
    return Document(content, **kwargs).to_text()


def to_html(content, **kwargs):
    return Document(content, **kwargs).to_html()


def to_markdown(content, **kwargs):
    return Document(content, **kwargs).to_markdown()

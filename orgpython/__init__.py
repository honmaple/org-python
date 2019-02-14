#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ********************************************************************************
# Copyright © 2019 jianglin
# File Name: __init__.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2018-02-26 11:41:17 (CST)
# Last Update: Thursday 2019-02-14 12:08:14 (CST)
#          By:
# Description:
# ********************************************************************************
from .element import Org


def org_to_html(text, offset=0, toc=True, escape=True):
    return Org(text, offset, toc, escape).to_html()

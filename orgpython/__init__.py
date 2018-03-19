#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ********************************************************************************
# Copyright © 2018 jianglin
# File Name: __init__.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2018-02-26 11:41:17 (CST)
# Last Update: Monday 2018-03-19 14:48:43 (CST)
#          By:
# Description:
# ********************************************************************************
from .element import Org


def org_to_html(text, offset=0, toc=True, escape=True):
    return Org(text, offset, toc, escape).to_html()

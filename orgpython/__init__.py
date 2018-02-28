#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ********************************************************************************
# Copyright © 2018 jianglin
# File Name: __init__.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2018-02-26 11:41:17 (CST)
# Last Update: Wednesday 2018-02-28 15:01:25 (CST)
#          By:
# Description:
# ********************************************************************************
from .element import Org


def org_to_html(text, offset=0, toc=True, escape=False):
    return Org(text, offset, toc, escape).to_html()

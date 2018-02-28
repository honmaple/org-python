#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: test.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-03-16 16:28:32 (CST)
# Last Update: Wednesday 2018-02-28 17:02:36 (CST)
#          By:
# Description:
# **************************************************************************
import unittest
# from org1 import org_to_html
from orgpython import org_to_html
from orgpython import Org
from orgpython.element import Heading


class TestOrg(unittest.TestCase):
    def test_heading(self):
        text = ["* heading1", "** heading2", "*** heading3", "* heading4",
                "heading5"]
        text = '\n'.join(text)
        org = Org(text)
        org.to_html()
        count = [i for i in org.children if isinstance(i, Heading)]
        self.assertEqual(len(count), 4)

    def test_text(self):
        text = '''
        *bold* bold* *bold\* \*bold\* \*bold*
        **italic** italic** **italic\** \**italic\** \**italic**
        =code= code= =code\= \=code\= \=code=
        ~code~ code~ ~code\~ \~code\~ \~cod~
        '''
        html = org_to_html(text)
        self.assertEqual(html.count('<b>'), 2)
        self.assertEqual(html.count('<i>'), 2)
        self.assertEqual(html.count('<code>'), 4)


if __name__ == '__main__':
    unittest.main()

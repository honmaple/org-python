#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: test.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-03-16 16:28:32 (CST)
# Last Update: Friday 2019-05-31 16:54:19 (CST)
#          By:
# Description:
# **************************************************************************
import unittest
# from org1 import org_to_html
from orgpython import org_to_html
from orgpython import Org
from orgpython.block import Heading

TEXT = '''* Heading1
** Heading2
*** Heading3.1
    *bold* bold* *bold\* \*bold\* \*bold*
    **italic** italic** **italic\** \**italic\** \**italic**
    =code= code= =code\= \=code\= \=code=
    ~code~ code~ ~code\~ \~code\~ \~cod~
*** Heading3.2
    [[link][url]]
'''


class TestOrg(unittest.TestCase):
    def setUp(self):
        self.org = Org(TEXT)
        self.org.init()

    def test_heading(self):
        self.assertEqual(len(self.org.children), 1)
        heading = self.org.children[0]
        self.assertEqual(heading.title, "Heading1")
        self.assertEqual(heading.level, 1)

        self.assertEqual(len(heading.children), 1)
        heading2 = heading.children[0]
        self.assertEqual(heading2.title, "Heading2")
        self.assertEqual(heading2.level, 2)

        self.assertEqual(len(heading2.children), 2)

    def test_inlinetext(self):
        pass


if __name__ == '__main__':
    unittest.main()

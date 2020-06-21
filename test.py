#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: test.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-03-16 16:28:32 (CST)
# Last Update: Thursday 2020-02-06 14:32:51 (CST)
#          By:
# Description:
# **************************************************************************
import unittest
from orgpython import Block

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
    def test_heading(self):
        text = "* TODO heading  :TAG1:TAG2:"

        b = Block(text)
        b.init()
        heading = b.children[0]
        self.assertEqual(heading.title, "heading")
        self.assertEqual(heading.stars, 1)
        self.assertEqual(heading.tags, ["TAG1", "TAG2"])
        self.assertEqual(heading.keyword, "TODO")

        text = "* [#B] heading  :TAG1:TAG2:"
        b = Block(text)
        b.init()
        heading = b.children[0]

        self.assertEqual(heading.title, "heading")
        self.assertEqual(heading.stars, 1)
        self.assertEqual(heading.tags, ["TAG1", "TAG2"])
        self.assertEqual(heading.keyword, None)
        self.assertEqual(heading.priority, "[#B]")

    def test_src(self):
        pass


if __name__ == '__main__':
    unittest.main()

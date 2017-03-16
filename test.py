#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: test.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-03-16 16:28:32 (CST)
# Last Update:星期四 2017-3-16 16:44:6 (CST)
#          By:
# Description:
# **************************************************************************
import unittest
from org import orgmode


class TestOrg(unittest.TestCase):
    def test_heading(self):
        html = orgmode('* hello').to_html()
        self.assertEqual(html, '<h1>hello</h1>')

    def test_bold(self):
        text = '''
        *bold* bold*
        bold* bold*
        *bold* *bold*
        '''
        html = orgmode(text).to_html()
        self.assertEqual(html,
                         '<b>bold</b> bold*bold* bold*<b>bold</b> <b>bold</b>')

    def test_italic(self):
        text = '''
        **italic** italic*
        italic* italic*
        **italic** **italic**
        '''
        html = orgmode(text).to_html()
        self.assertEqual(
            html,
            '<i>italic</i> italic*italic* italic*<i>italic</i> <i>italic</i>')


if __name__ == '__main__':
    unittest.main()

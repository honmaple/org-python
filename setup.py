#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: setup.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-07-14 22:07:06 (CST)
# Last Update:星期五 2017-7-21 9:24:12 (CST)
#          By:
# Description:
# **************************************************************************
from setuptools import setup


setup(
    name='org-python',
    version='0.1.2',
    url='https://github.com/honmaple/org-python',
    license='BSD',
    author='honmaple',
    author_email='xiyang0807@gmail.com',
    description='convert orgmode to html based on python.',
    long_description='Please visit https://github.com/honmaple/org-python',
    py_modules=['orgpython'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

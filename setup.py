#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: setup.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-07-14 22:07:06 (CST)
# Last Update: Monday 2018-03-19 14:51:13 (CST)
#          By:
# Description:
# **************************************************************************
from setuptools import setup
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='org-python',
    version='0.2.0',
    url='https://github.com/honmaple/org-python',
    license='BSD',
    author='honmaple',
    author_email='xiyang0807@gmail.com',
    description='convert orgmode to html based on python.',
    long_description=read('README.rst'),
    packages=['orgpython'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[],
    classifiers=[
        'Environment :: Web Environment', 'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent', 'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ])

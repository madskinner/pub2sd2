# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 04:09:26 2017

@author: marks
"""
import re

FIND_LEADING_DIGITS = re.compile(r'^\d+')
FIND_LEADING_ALPHANUM = re.compile(r'^\w+')
FIND_TRAILING_DIGITS = re.compile(r'\d+$')
TRIM_LEADING_DIGITS = re.compile(r'^\d+(.+?)')
TRIM_LEADING_ALPHANUM = re.compile(r'^\w+(.+?)')
TRIM_TRAILING_DIGITS = re.compile(r'(.+?)\d+$')
DOUBLE_SPACE_TO_SINGLE = re.compile(r'(.*?)\s\s(.*?)')

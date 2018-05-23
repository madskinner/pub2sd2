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
DOUBLE_SPACE_TO_SINGLE = re.compile(r'\s\s+')
TAB = re.compile(r'\t')
RETURN = re.compile(r'\r')
NEWLINE = re.compile(r'\n')
RETAB = re.compile(r'&#9;')
RERETURN = re.compile(r'&#13')
RENEWLINE = re.compile(r'&#10;')
HEX_CHAR = re.compile(r'0[xX][0-9a-fA-F]{4,4}')

def _nothing(title):
    return title

def _leading_digits(title):
    return TRIM_LEADING_DIGITS.sub(r'\1', title)

def _trailing_digits(title):
    return TRIM_TRAILING_DIGITS.sub(r'\1', title)

def _leading_aphanum(title):
    prefix = FIND_LEADING_ALPHANUM.findall(title)[0] \
                            if FIND_LEADING_ALPHANUM.findall(title) else ''
    if prefix:
        prefix = prefix.split('_')[0]
        title = title[len(prefix):]
    return title

STRIPPERS = {
            #en-US
            "Nothing":_nothing, \
            "Leading digits":_leading_digits, \
            "Trailing digits":_trailing_digits, \
            "Leading alphanumerics":_leading_aphanum, \
            #fr-FR
            "Rien":_nothing, \
            "Chiffres initiauxs":_leading_digits, \
            "Alphanumériques précédents":_trailing_digits, \
            "Derniers chiffres":_leading_aphanum, \
            #pt-PT
            "Nada":_nothing, \
            "Dígitos iniciais":_leading_digits, \
            "Alfanuméricos iniciais":_trailing_digits, \
            "Dígitos finais":_leading_aphanum, \
            }

def escape_tab_return_feed(text):
    result = TAB.sub(r'&#9;', text)
    result = RETURN.sub(r'&#13;', result)
    result = NEWLINE.sub(r'&#10;', result)
    return result

def unescape_tab_return_feed(text):
    result = RETAB.sub(r'\t', text)
    result = RERETURN.sub(r'\r', result)
    result = RENEWLINE.sub(r'\n', result)
    return result

# -*- coding: utf-8 -*-
"""
Created on Sun May 13 16:23:28 2018

@author: marks
"""
import fnmatch
import os
import platform

import shutil

import codecs
#from .myconst.audio import AUDIO

BASIC_LATIN = [chr(c) for c in range(0x20, 0x0080)]
LATIN1_SUPPLEMENT = [chr(c) for c in range(0x0080, 0x0100)]
LATIN_EXTENDED_A = [chr(c) for c in range(0x0100, 0x0180)]
LATIN_EXTENDED_B = [chr(c) for c in range(0x0180, 0x0250)]
SPACINGMODIFIER_LETTERS = [chr(c) for c in range(0x02B0, 0x0300)]
LATINEXTENDED_ADDITIONAL = [chr(c) for c in range(0x1E00, 0x1F00)]
LATINEXTENDED_C = [chr(c) for c in range(0x2C60, 0x2C80)]
LATINEXTENDED_D = [chr(c) for c in range(0xA720, 0xA800)]
LATINEXTENDED_E = [chr(c) for c in range(0xAB30, 0xAB70)]
IPA_EXTENSIONS = [chr(c) for c in range(0x0250, 0x02B0)]
PHONETIC_EXTENSIONS = [chr(c) for c in range(0x1D00, 0x1D80)]
PHONETIC_EXTENSIONS_SUPPLEMENT = [chr(c) for c in range(0x1D80, 0x1DC0)]
SUPERSCRIPTS_AND_SUBSCRIPTS = [chr(c) for c in range(0x1D80, 0x1DC0)]
LETTERLIKE_SYMBOLS = [chr(c) for c in range(0x2070, 0x20A0)]
NUMBERFORMS = [chr(c) for c in range(0x2150, 0x2190)]
ILLEGALCHARS = [chr(i) for i in range(1, 0x20)] + \
                            [chr(0x7F), '"', '*', '/', ':', '<', '>', \
                                                              '?', '\\', '|']


def main():
    """take an mp3 file and rename it with every combination of characters
    updating the title at same time"""
    outdir = "C:\\Users\\marks\\Desktop\\TestDir\\"
    filein = "C:\\Conversion\\SDCard\\Kulumi\\NT\\00\\The_Story_of_Jesus...mp3"

    titles = [c for c in [b for b in BASIC_LATIN if b not in ILLEGALCHARS] if c.strip()]
    thisdir = os.path.normpath(outdir + 'BASIC_LATIN')
    if not os.path.isdir(thisdir):
        os.makedirs(thisdir, mode=0o777, exist_ok=True)
    for atitle in titles:
        fileout = thisdir + '\\' + hex(ord(atitle)) + '_' + atitle + '.mp3'
        try:
            shutil.copy(filein, fileout)
        except Exception as e:
            print("type error: " + str(e))
    print("BASIC_LATINS {} tried".format(len(titles)))
        
    titles = [c for c in LATIN1_SUPPLEMENT if c.strip()]
    thisdir = os.path.normpath(outdir + 'LATIN1_SUPPLEMENT')
    if not os.path.isdir(thisdir):
        os.makedirs(thisdir, mode=0o777, exist_ok=True)
    for atitle in titles:
        fileout = thisdir + '\\' + hex(ord(atitle)) + '_' + atitle + '.mp3'
        try:
            shutil.copy(filein, fileout)
        except Exception as e:
            print("type error: " + str(e))
    print("LATIN1_SUPPLEMENT {} tried".format(len(titles)))
        
    titles = [c for c in LATIN_EXTENDED_A if c.strip()]
    thisdir = os.path.normpath(outdir + 'LATIN_EXTENDED_A')
    if not os.path.isdir(thisdir):
        os.makedirs(thisdir, mode=0o777, exist_ok=True)
    for atitle in titles:
        fileout = thisdir + '\\' + hex(ord(atitle)) + '_' + atitle + '.mp3'
        try:
            shutil.copy(filein, fileout)
        except Exception as e:
            print("type error: " + str(e))
    print("LATIN_EXTENDED_A {} tried".format(len(titles)))
        
    titles = [c for c in LATIN_EXTENDED_B if c.strip()]
    thisdir = os.path.normpath(outdir + 'LATIN_EXTENDED_B')
    if not os.path.isdir(thisdir):
        os.makedirs(thisdir, mode=0o777, exist_ok=True)
    for atitle in titles:
        fileout = thisdir + '\\' + hex(ord(atitle)) + '_' + atitle + '.mp3'
        try:
            shutil.copy(filein, fileout)
        except Exception as e:
            print("type error: " + str(e))
    print("LATIN_EXTENDED_B {} tried".format(len(titles)))
        
    titles = [c for c in SPACINGMODIFIER_LETTERS if c.strip()]
    thisdir = os.path.normpath(outdir + 'SPACINGMODIFIER_LETTERS')
    if not os.path.isdir(thisdir):
        os.makedirs(thisdir, mode=0o777, exist_ok=True)
    for atitle in titles:
        fileout = thisdir + '\\' + hex(ord(atitle)) + '_' + atitle + '.mp3'
        try:
            shutil.copy(filein, fileout)
        except Exception as e:
            print("type error: " + str(e))
    print("SPACINGMODIFIER_LETTERS {} tried".format(len(titles)))
        
    titles = [c for c in LATINEXTENDED_ADDITIONAL if c.strip()]
    thisdir = os.path.normpath(outdir + 'LATINEXTENDED_ADDITIONAL')
    if not os.path.isdir(thisdir):
        os.makedirs(thisdir, mode=0o777, exist_ok=True)
    for atitle in titles:
        fileout = thisdir + '\\' + hex(ord(atitle)) + '_' + atitle + '.mp3'
        try:
            shutil.copy(filein, fileout)
        except Exception as e:
            print("type error: " + str(e))
    print("LATINEXTENDED_ADDITIONAL {} tried".format(len(titles)))
        
    titles = [c for c in LATINEXTENDED_C if c.strip()]
    thisdir = os.path.normpath(outdir + 'LATINEXTENDED_C')
    if not os.path.isdir(thisdir):
        os.makedirs(thisdir, mode=0o777, exist_ok=True)
    for atitle in titles:
        fileout = thisdir + '\\' + hex(ord(atitle)) + '_' + atitle + '.mp3'
        try:
            shutil.copy(filein, fileout)
        except Exception as e:
            print("type error: " + str(e))
    print("LATINEXTENDED_C {} tried".format(len(titles)))
        
    titles = [c for c in LATINEXTENDED_D if c.strip()]
    thisdir = os.path.normpath(outdir + 'LATINEXTENDED_D')
    if not os.path.isdir(thisdir):
        os.makedirs(thisdir, mode=0o777, exist_ok=True)
    for atitle in titles:
        fileout = thisdir + '\\' + hex(ord(atitle)) + '_' + atitle + '.mp3'
        try:
            shutil.copy(filein, fileout)
        except Exception as e:
            print("type error: " + str(e))
    print("LATINEXTENDED_D {} tried".format(len(titles)))
        
    titles = [c for c in LATINEXTENDED_E if c.strip()]
    thisdir = os.path.normpath(outdir + 'LATINEXTENDED_E')
    if not os.path.isdir(thisdir):
        os.makedirs(thisdir, mode=0o777, exist_ok=True)
    for atitle in titles:
        fileout = thisdir + '\\' + hex(ord(atitle)) + '_' + atitle + '.mp3'
        try:
            shutil.copy(filein, fileout)
        except Exception as e:
            print("type error: " + str(e))
    print("LATINEXTENDED_E {} tried".format(len(titles)))
        
    titles = [c for c in IPA_EXTENSIONS if c.strip()]
    thisdir = os.path.normpath(outdir + 'IPA_EXTENSIONS')
    if not os.path.isdir(thisdir):
        os.makedirs(thisdir, mode=0o777, exist_ok=True)
    for atitle in titles:
        fileout = thisdir + '\\' + hex(ord(atitle)) + '_' + atitle + '.mp3'
        try:
            shutil.copy(filein, fileout)
        except Exception as e:
            print("type error: " + str(e))
    print("IPA_EXTENSIONS {} tried".format(len(titles)))
        
    titles = [c for c in PHONETIC_EXTENSIONS if c.strip()]
    thisdir = os.path.normpath(outdir + 'PHONETIC_EXTENSIONS')
    if not os.path.isdir(thisdir):
        os.makedirs(thisdir, mode=0o777, exist_ok=True)
    for atitle in titles:
        fileout = thisdir + '\\' + hex(ord(atitle)) + '_' + atitle + '.mp3'
        try:
            shutil.copy(filein, fileout)
        except Exception as e:
            print("type error: " + str(e))
    print("PHONETIC_EXTENSIONS {} tried".format(len(titles)))
        
    titles = [c for c in PHONETIC_EXTENSIONS_SUPPLEMENT if c.strip()]
    thisdir = os.path.normpath(outdir + 'PHONETIC_EXTENSIONS_SUPPLEMENT')
    if not os.path.isdir(thisdir):
        os.makedirs(thisdir, mode=0o777, exist_ok=True)
    for atitle in titles:
        fileout = thisdir + '\\' + atitle + '.mp3'
        try:
            shutil.copy(filein, fileout)
        except Exception as e:
            print("type error: " + str(e))
    print("PHONETIC_EXTENSIONS_SUPPLEMENT {} tried".format(len(titles)))
        
    titles = [c for c in SUPERSCRIPTS_AND_SUBSCRIPTS if c.strip()]
    thisdir = os.path.normpath(outdir + 'SUPERSCRIPTS_AND_SUBSCRIPTS')
    if not os.path.isdir(thisdir):
        os.makedirs(thisdir, mode=0o777, exist_ok=True)
    for atitle in titles:
        fileout = thisdir + '\\' + hex(ord(atitle)) + '_' + atitle + '.mp3'
        try:
            shutil.copy(filein, fileout)
        except Exception as e:
            print("type error: " + str(e))
    print("SUPERSCRIPTS_AND_SUBSCRIPTS {} tried".format(len(titles)))
        
    titles = [c for c in LETTERLIKE_SYMBOLS if c.strip()]
    thisdir = os.path.normpath(outdir + 'LETTERLIKE_SYMBOLS')
    if not os.path.isdir(thisdir):
        os.makedirs(thisdir, mode=0o777, exist_ok=True)
    for atitle in titles:
        fileout = thisdir + '\\' + hex(ord(atitle)) + '_' + atitle + '.mp3'
        try:
            shutil.copy(filein, fileout)
        except Exception as e:
            print("type error: " + str(e))
    print("LETTERLIKE_SYMBOLS {} tried".format(len(titles)))
        
    titles = [c for c in NUMBERFORMS if c.strip()]
    thisdir = os.path.normpath(outdir + 'NUMBERFORMS')
    if not os.path.isdir(thisdir):
        os.makedirs(thisdir, mode=0o777, exist_ok=True)
    for atitle in titles:
        fileout = thisdir + '\\' + hex(ord(atitle)) + '_' + atitle + '.mp3'
        try:
            shutil.copy(filein, fileout)
        except Exception as e:
            print("type error: " + str(e))
    print("NUMBERFORMS {} tried".format(len(titles)))
    pass

if __name__ == '__main__':
    main()

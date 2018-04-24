# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 04:37:05 2017

@author: marks
"""
#import sys
import fnmatch
import os
import platform
import webbrowser
import queue
import threading

import codecs
import shutil
import glob
import hashlib
import pickle
from urllib.parse import urlparse
import json
import re
from tkinter import font, Tk, filedialog, messagebox, StringVar, \
                    IntVar, NO, Text, FALSE, Menu
from tkinter.ttk import Button, Checkbutton, Entry, Frame, Label, LabelFrame, \
                        Radiobutton, Scrollbar, Combobox, Notebook, \
                        Progressbar, Treeview, Style

import ast
import psutil
from lxml import etree
from unidecode import unidecode
from mutagen.mp3 import MP3

##All are used in preparing_file_scaning_for_tags by exec(a string)...
from mutagen.id3 import ID3, error, APIC#, \
#                        TXXX, WXXX, ETCO, MLLT, SYTC, USLT, SYLT, COMM, \
#                        RVA2, EQU2, RVAD, RVRB, APIC, PCNT, PCST, POPM, \
#                        GEOB, RBUF, AENC, LINK, POSS, UFID, USER, OWNE, \
#                        COMR, ENCR, GRID, PRIV, SIGN, SEEK, ASPI, TIPL, \
#                        TMCL, IPLS, MCDI, TBPM, TLEN, TORY, TSIZ, TYER, \
#                        TPOS, TRCK, MVIN, MVNM, TALB, TCOM, TCON, TCOP, \
#                        TCMP, TDAT, TDEN, TDES, TKWD, TCAT, TDLY, TDOR, \
#                        TDRC, TDRL, TDTG, TENC, TEXT, TFLT, TGID, TIME, \
#                        TIT1, TIT2, TIT3, TKEY, TLAN, TMED, TMOO, TOAL, \
#                        TOFN, TOLY, TOPE, TOWN, TPE1, TPE2, TPE3, TPE4, \
#                        TPRO, TPUB, TRSN, TRSO, TSO2, TSOA, TSOC, TSOP, \
#                        TSOT, TSRC, TSSE, TSST, WCOM, WCOP, WOAF, WOAR, \
#                        WOAS, WORS, WPAY, WPUB

from .myconst.audio import AUDIO
from .myconst.regexs import FIND_LEADING_DIGITS, FIND_LEADING_ALPHANUM, \
                            FIND_TRAILING_DIGITS, TRIM_LEADING_DIGITS, \
                            TRIM_TRAILING_DIGITS
from .myconst.localizedText import INTERFACE_LANGS, SET_TAGS, LOCALIZED_TEXT, \
                                    TRIM_TAG, DEFAULT_VALUES
from .myconst.readTag import IDIOT_TAGS, READ_TAG_INFO, HASH_TAG_ON

from .myconst.therest import THIS_VERSION, THE_IDIOT_P, THE_P, LATIN1, \
                            PICTURE_TYPE, TF_TAGS#, PF,
from .tooltip import CreateToolTip
from .threads import MyThread
from .backend import Backend

def get_script_directory():
    """return path to current script"""
    return os.path.dirname(__file__)

SCRIPT_DIR = get_script_directory()
qcommand = queue.Queue()
qreport = queue.Queue()


class GuiCore(Tk):
    """Handle the graphical interface for Pub2SDwizard and most of the logic"""
    def __init__(self, parent):
        Tk.__init__(self, parent)
        self.parent = parent
        self._initialize()

    def _initialize(self):
        """initialize the GuiCore"""
        self.backend = Backend()
        self.backend.run(qcomand, qreport)


        self.tree = Treeview(self, selectmode="extended", height=8)
        self.tree.grid(column=0, row=0, \
                       columnspan=12, rowspan=20, sticky='news', padx=5)
        ysb = Scrollbar(self, orient='vertical', command=self.tree.yview)
        xsb = Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        ysb.grid(row=0, column=11, rowspan=20, padx=5, sticky='nse')
        xsb.grid(row=20, column=0, columnspan=12, padx=5, sticky='ews')



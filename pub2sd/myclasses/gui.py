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

def get_script_directory():
    """return path to current script"""
    return os.path.dirname(__file__)

SCRIPT_DIR = get_script_directory()


class GuiCore(Tk):
    """Handle the graphical interface for Pub2SDwizard and most of the logic"""
    def __init__(self, parent):
        Tk.__init__(self, parent)
        self.parent = parent
        self._initialize()

    def _initialize(self):
        """initialize the GuiCore"""
        self._initialize_variables()

        lang = 'en-US'
        self._initialize_main_window(lang)

        if platform.system() not in  ['Windows', 'Linux']:
            # so on f0, the Project tab…
            messagebox.showwarning(\
                              'Warning', "Help I've been kidnaped by {}!!!".\
                                                   format(platform.system()))
            self.Pub2SD = os.path.expanduser('~') + '/Pub2SD'
        if platform.system() == 'Linux':
            self.Pub2SD = os.path.expanduser('~') + '/Pub2SD'
        elif platform.system() == 'Windows':
            self.Pub2SD = '/'.join(os.path.expanduser('~').split("\\")[0:3]) \
                                  + '/Pub2SD'
        if not os.path.isdir(self.Pub2SD):
            os.makedirs(self.Pub2SD, 0o777) #make the dir

        self._initialize_f0(lang) # so on f1, recommended mp3tags
        self._initialize_f1(lang) # so on f2, special characters
        self._initialize_f2(lang) # so on f3 tab Edit Hierarchy
        self._initialize_f3(lang) #on f4 - featurephone features?
        self._initialize_f4(lang) # on f5 - publish to...
        self._initialize_f5(lang)

        if platform.system() == 'Linux': #create on f6
            self._initialize_f6(lang) #will be for locking/unlocking SD cards
        pud2sd_styles = Style()
        pud2sd_styles.configure('lowlight.TButton', \
                                font=('Sans', 8, 'bold'),)
        pud2sd_styles.configure('highlght.TButton', \
                                font=('Sans', 11, 'bold'), \
                                background='white', foreground='#007F00')
        pud2sd_styles.configure('wleft.TRadiobutton', \
                                anchor='w', justify='left')

    def _initialize_project_variables(self):
        """The project variables that will be saved on clicking 'save project'.
        The sfn variable hold the settings for their associated tab (fn) of
        the notebook widget on the main window. The child 'tree'holds a copy
        of all the file locations and any modifications to their metadata"""
        self.list_projects = []
        self.project_lines = []
        self.indent = 0
        self.Treed = False
        self.root = etree.Element('root')
        #add child 'settings', all user configurable bits under here
        self.settings = etree.SubElement(self.root, "settings")
        self.old_mode = dict()
        self.spreferred = etree.SubElement(self.settings, "preferred")
        self.smode = etree.SubElement(self.settings, "mode")
        self.stemp = etree.SubElement(self.settings, "template")
        self.sf0 = etree.SubElement(self.settings, "f0")
        self.sf1 = etree.SubElement(self.settings, "f1")
        self.sf2 = etree.SubElement(self.settings, "f2")
        self.sf4 = etree.SubElement(self.settings, "f4")
        self.trout = etree.SubElement(self.root, "tree")
        self.project_id = ''

    def _initialize_variables(self):
        """initialize variables for GuiCore"""
        self.font = font.Font()

        self.files = {}
        self.maxcolumnwidths = [0, 0, 0, ]

        self._initialize_project_variables()

        self.taglist = []
        self.displayTags = set()
        self.recommendedTags = ['TIT2', 'TALB', 'TPE1', 'TPE2', 'TCOP', \
                                'APIC', 'TDRC', 'TRCK', 'TPOS', 'COMM', \
                                'TCON', 'TCOM']
        self.selected_tags = list()
        self.listoftags = list()

        self.columns = []
        self.displayColumns = []

        self.nos_tracks = 0
        self.template = dict()
        self.pref = list()
        self.pref_char = list()
        self.hashed_graphics = dict()
        self.illegalChars = [chr(i) for i in range(1, 0x20)]
        self.illegalChars.extend([chr(0x7F), '"', '*', '/', ':', '<', '>', \
                                                              '?', '\\', '|'])

        self.output_to = []
        self.play_list_targets = []

        #define all StringVar(), BooleanVar(), etc… needed to hold info
        self.selected_lang = StringVar()
        self.int_var = IntVar()
        self.current_project = StringVar()
        self.current_template = StringVar()
        self.outputTo = StringVar()
        self.selected_drive = StringVar()
        self.currentEntry = StringVar()
        self.playLists = StringVar()
        self.set_tag = StringVar()
        self.set_trim = StringVar()
        self.next_track = 0
        self.is_copy_playlists_to_top = IntVar()
        self.isCoolMusic = IntVar()
        self.EnterList = StringVar()
        self.additionalTags = StringVar()
        self.folderList = StringVar()
        self.pictureType = StringVar()
        self.etrDesc = StringVar()
        self.tnames = StringVar()
        self.mode = IntVar()
        self.preferred = IntVar()
        self.PrefChar = StringVar()
        self.InitialDigit = StringVar()
        self.cbv = [StringVar(), StringVar(), StringVar(), StringVar(), \
                    StringVar(), StringVar(), StringVar(), StringVar()]
        self.M3UorM3U8 = IntVar()

    def _initialize_main_window_menu(self, lang='en-US'):
        """initialize the menubar on the main window"""

        self.option_add('*tearOff', FALSE)
        self.menubar = Menu(self)
        self.config(menu=self.menubar)
        self.filemenu = Menu(self.menubar)
        self.menubar.add_cascade(label=LOCALIZED_TEXT[lang]['File'], \
                                 menu=self.filemenu)
        self.filemenu.add_command(label=\
                            LOCALIZED_TEXT[lang]['Load project settings'], \
                                          command=self._on_click_f0_next)
        self.filemenu.add_command(label=LOCALIZED_TEXT[lang]['Save'], \
                                  command=self._on_save_project)
        self.filemenu.add_command(label=\
                            LOCALIZED_TEXT[lang]['Delete project settings'], \
                                          command=self._on_del_project)
        self.filemenu.add_separator()
        self.filemenu.add_command(label=LOCALIZED_TEXT[lang]['Exit'], \
                                  command=self.quit)

        self.helpmenu = Menu(self.menubar)
        self.menubar.add_cascade(label=LOCALIZED_TEXT[lang]['Help'], \
                                 menu=self.helpmenu)
        self.helpmenu.add_command(label=LOCALIZED_TEXT[lang]['Read Me'], \
                                  command=self._on_read_me)
        self.helpmenu.add_command(label=LOCALIZED_TEXT[lang]['About...'], \
                                  command=on_copyright)
#                                  command=self._on_copyright)

    def _initialize_main_window_notebook(self, lang):
        """initializes notebook widget on main window"""
        #self.n = Notebook(self, width=1400)
        #notebook
        self.n = Notebook(self, width=1015)
        self.n.grid(column=0, columnspan=7, row=1, padx=5, pady=5, sticky='ew')
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.n.grid_rowconfigure(0, weight=1)
        self.n.grid_columnconfigure(0, weight=1)
        # chose project name -
        #  defaults to last or pull downlist of existing ones?
        #  enter new, can delete selected project, move to next
        self.f0 = Frame(self.n)
        self.f1 = Frame(self.n)   # recommended tags show/hide
        self.f2 = Frame(self.n)   # special characters
        # Import and/or Edit file Hierachy,
        #  Edit MP3 tags for one file or for all files within a collection
        self.f3 = Frame(self.n)
        self.f3.grid(column=0, row=0, sticky='news')
        self.f3.grid_rowconfigure(0, weight=1)
        self.f3.grid_columnconfigure(0, weight=1)
        # set additional options for featurephone specific locations for
        #  playlists, process files to temp dir and create playlists
        self.f4 = Frame(self.n)
        # output project to SD card copying play lists to any, may have
        #  additional options for featurephone specific locations for playlists
        self.f5 = Frame(self.n)
        self.f6 = Frame(self.n)   # Lock SD card

        self.n.add(self.f0, text=LOCALIZED_TEXT[lang]['Project name'])
        self.n.add(self.f1, \
                   text=LOCALIZED_TEXT[lang]['Commonly used MP3 tags'])
        self.n.add(self.f2, text=LOCALIZED_TEXT[lang]['Special characters'])
        self.n.add(self.f3, \
                   text=LOCALIZED_TEXT[lang]['Edit Hierachy and MP3 tags'])
        self.n.add(self.f4, text=LOCALIZED_TEXT[lang]['Feature-phone options'])
        self.n.add(self.f5, text=LOCALIZED_TEXT[lang]['Output to…'])
        self.n.add(self.f6, text=LOCALIZED_TEXT[lang]['Lock SD card'])

        self.n.hide(1)
        self.n.hide(2)
        self.n.hide(3)
        self.n.hide(4)
        self.n.hide(5)
        self.n.hide(6)


    def _initialize_main_window(self, lang='en-US'):
        """ initialize the main window"""

        self._initialize_main_window_menu(lang)
        self.f_1 = Frame(self)
        self.f_1.grid(column=0, row=0, sticky='news')
        self.f_1.grid_rowconfigure(0, weight=0)
        self.f_1.grid_columnconfigure(0, weight=0)
       # in top of window
        self.btnSaveProject = Button(self.f_1, \
                                     text=LOCALIZED_TEXT[lang]["Save"], \
                                                command=self._on_save_project)
        self.btnSaveProject.grid(column=0, row=0, padx=5, pady=5, sticky='e')
        self.btnSaveProject['state'] = 'disabled'
        self.btnSaveProject_ttp = CreateToolTip(self.btnSaveProject, \
                                        LOCALIZED_TEXT[lang]['Save_ttp'])
        self.lblProject = Label(self.f_1, text=\
                                    LOCALIZED_TEXT[lang]['Current Project>'], \
                                                  width=50)
        self.lblProject.grid(column=1, row=0, columnspan=2, padx=5, pady=5, \
                             sticky='ew')
        self.lblProject['justify'] = 'left'

        self.lblGuiLanguage = Label(self.f_1, \
                            text=LOCALIZED_TEXT[lang]['Interface language>'])
        self.lblGuiLanguage.grid(column=4, row=0, padx=5, pady=5, sticky='e')
        self.lblGuiLanguage['justify'] = 'right'
        # Create and fill the dropdown ComboBox.
        self.ddnGuiLanguage = Combobox(self.f_1, \
                                       textvariable=self.selected_lang)
        self.ddnGuiLanguage.grid(column=5, columnspan=1, row=0, \
                                 padx=5, pady=5, sticky='w')
        self.ddnGuiLanguage['text'] = 'Interface language:'
        self.ddnGuiLanguage['justify'] = 'left'
        self.ddnGuiLanguage.bind('<<ComboboxSelected>>', self._change_lang)
        self.ddnGuiLanguage['values'] = [INTERFACE_LANGS['langs'][k] \
                                for k in sorted(INTERFACE_LANGS['langs'])]
        self.ddnGuiLanguage.set(INTERFACE_LANGS['langs']['0'])

        self.lblMode = Label(self.f_1, text=LOCALIZED_TEXT[lang]['Mode>'])
        self.lblMode.grid(column=6, row=0, padx=5, pady=5, sticky='e')

        #assumes tab based interface
        #main frame holds gui interface lange pull down, lists current project,
        #and save settings button
        self._initialize_main_window_notebook(lang)

        self.progbar = Progressbar(self, maximum=100, variable=self.int_var)
        self.progbar.grid(column=0, row=6, columnspan=8, padx=5, pady=5, \
                          sticky='news')
        self.status = Label(self, text=LOCALIZED_TEXT[lang]['empty string'], \
                            anchor='w', justify='left')
        self.status.grid(column=0, row=7, columnspan=8, padx=5, pady=5, \
                         sticky='news')

    def _initialize_f0(self, lang='en-US'):
        """initialize Project Name tab"""

        self.f0_ttp = Label(self.f0, text=LOCALIZED_TEXT[lang]['f0_ttp'], \
                            anchor='w', justify='left', wraplength=600)
        self.f0_ttp.grid(column=0, row=0, columnspan=3, padx=5, pady=5, \
                                                                   sticky='ew')

        self.lblCurProject = Label(self.f0, \
                               text=LOCALIZED_TEXT[lang]['Current Project>'], \
                                                   anchor='w', justify='right')
        self.lblCurProject.grid(column=0, row=1, padx=5, pady=5, sticky='e')

        self.ddnCurProject = Combobox(self.f0, \
                                      textvariable=self.current_project)
        self.ddnCurProject.grid(column=1, row=1, padx=5, pady=5, sticky='news')
        self.ddnCurProject['text'] = 'Current Project:'
        self.ddnCurProject['justify'] = 'left'

        self.btnDelProject = Button(self.f0, \
                               text=LOCALIZED_TEXT[lang]['Delete Project'], \
                                                  command=self._on_del_project)
        self.btnDelProject.grid(column=2, row=1, padx=5, pady=5, sticky='news')
        self.btnDelProject_ttp = CreateToolTip(self.btnDelProject, \
                                    LOCALIZED_TEXT[lang]['Delete Project_ttp'])

        self.lblIdiot = Label(self.f0, \
                              text=LOCALIZED_TEXT[lang]['IdiotMode'], \
                                    anchor='w', justify='left', wraplength=600)
        self.lblIdiot.grid(column=0, row=3, columnspan=3, padx=5, pady=5, \
                           sticky='ew')

        self.rdbIdiot = Radiobutton(self.f0, \
                                    text=LOCALIZED_TEXT[lang]["Simple"], \
                                    variable=self.mode, value=0, \
                                    style="wleft.TRadiobutton")
        self.rdbIdiot.grid(column=1, row=4, padx=5, pady=5, sticky='news')
        self.rdbAdvanced = Radiobutton(self.f0, \
                                       text=LOCALIZED_TEXT[lang]["Advanced"], \
                                        variable=self.mode, value=1, \
                                        style="wleft.TRadiobutton")
        self.rdbAdvanced.grid(column=1, row=5, padx=5, pady=5, sticky='news')
        self.mode.set(0)

        self.boxOptional = LabelFrame(self.f0, \
                               text=LOCALIZED_TEXT[lang]["Optional"], \
                                                 labelanchor='nw', \
                                                 borderwidth=1)
        self.boxOptional.grid(column=0, row=6, columnspan=3, padx=5, pady=5, \
                              sticky='news')
        self.lblCurTemplate_ttp = Label(self.boxOptional, \
                                text=LOCALIZED_TEXT[lang]['CurTemplate_ttp'], \
                                    anchor='w', justify='left', wraplength=600)
        self.lblCurTemplate_ttp.grid(column=0, row=2, columnspan=3, \
                                     padx=5, pady=5, sticky='ew')
        self.lblCurTemplate = Label(self.boxOptional, \
                                text=LOCALIZED_TEXT[lang]['UseTemplate>'], \
                                                anchor='w', justify='right')
        self.lblCurTemplate.grid(column=0, row=3, padx=5, pady=5, sticky='e')

        # list templates in Pub2SD and load to ddnCurTemplate
        self.ddnCurTemplate = Combobox(self.boxOptional, \
                                       textvariable=self.current_template)
        self.ddnCurTemplate.grid(column=1, row=3, padx=5, pady=5, \
                                 sticky='news')
        self.ddnCurTemplate['text'] = 'Current template:'
        self.ddnCurTemplate['justify'] = 'left'

        self.list_templates = [f[:-5] for f in os.listdir(self.Pub2SD) \
                                      if f.endswith('.json')]
        self.list_templates.insert(0, '')

        self.ddnCurTemplate['values'] = self.list_templates
        self.ddnCurTemplate.current(0)

        self.lblInitialDigit = Label(self.boxOptional, \
                                text=LOCALIZED_TEXT[lang]['InitialDigit'], \
                                    anchor='w', justify='left', wraplength=600)
        self.lblInitialDigit.grid(column=0, row=4, columnspan=3, \
                                  padx=5, pady=5, sticky='ew')
        self.etrInitialDigit = Entry(self.boxOptional, \
                                     textvariable=self.InitialDigit)
        self.etrInitialDigit.grid(column=1, row=5, columnspan=1, \
                                  padx=5, pady=5, sticky='news')

        # list projects in Pub2SD and load to ddnCurProject
        self.list_projects = [f[:-4] for f in os.listdir(self.Pub2SD) \
                                     if f.endswith('.prj')]

        self.ddnCurProject['values'] = sorted(self.list_projects)
#        if len(self.list_projects) > 0:
        if self.list_projects:
            self.ddnCurProject.set(sorted(self.list_projects)[0])

        self.btnF0Next = Button(self.f0, text=LOCALIZED_TEXT[lang]["Next"], \
                                             command=self._on_click_f0_next, \
                                             style='highlight.TButton')
        self.btnF0Next.grid(column=2, row=7, padx=5, pady=5, sticky='news')
        self.btnF0Next_ttp = CreateToolTip(self.btnF0Next, \
                                           LOCALIZED_TEXT[lang]['F0Next_ttp'])

    def _initialize_f1(self, lang='en-US'):
        """initialize Choose MP3 Tags tab"""

        self.labelf1 = Label(self.f1, text=LOCALIZED_TEXT[lang]['labelf1'], \
                             anchor='w', justify='left', wraplength=600)
        self.labelf1.grid(column=0, row=0, columnspan=5, padx=5, pady=5, \
                          sticky='w')

        self.tagtree = Treeview(self.f1, selectmode="extended", show='tree', \
                                height=20)
        self.tagtree.grid(column=0, row=1, \
                       columnspan=3, rowspan=20, sticky='news', padx=5)
        ysb = Scrollbar(self.f1, orient='vertical', command=self.tagtree.yview)
        #xsb = Scrollbar(self.f1, orient='horizontal', \
        #                                          command=self._tagtree.xview)
        self.tagtree.configure(yscroll=ysb.set) #, xscroll=xsb.set)
        ysb.grid(row=1, column=2, rowspan=20, padx=5, sticky='nse')
        #xsb.grid(row=11, column=0, columnspan=3, padx=5, sticky='ews')

        #fill tagtree
        self.listoftags = [item for item in self.recommendedTags]
        if self.mode.get() == 0:
            #Idiot mode
            for t in sorted(IDIOT_TAGS.keys()):
                if t not in self.listoftags:
                    self.listoftags.extend([t])
        else:
            #advanced mode
            for t in sorted(SET_TAGS[lang].keys()):
                if t not in self.listoftags:
                    self.listoftags.extend([t])

        for t in self.listoftags:
#            tagtreechild = self.tagtree.insert('', index='end', iid=t, \
            self.tagtree.insert('', index='end', iid=t, open=True, \
                    values=[0], text='({}) {}'.format(t, SET_TAGS[lang][t]))
        if t in self.recommendedTags:
            self.tagtree.selection_add(t)
        self.tagtree.see('')
        self.update()

        self.btnDefaultTags = Button(self.f1, \
                               text=LOCALIZED_TEXT[lang]["Set default tags"], \
                                               command=self._set_default_tags)
        self.btnDefaultTags.grid(column=3, row=1, padx=5, pady=5, \
                                 sticky='news')

        self.btnCreateTemplate = Button(self.f1, \
                                text=LOCALIZED_TEXT[lang]["CreateTemplate"], \
                                            command=self._on_create_template)
        self.btnCreateTemplate.grid(column=3, row=2, padx=5, pady=5, \
                                    sticky='news')

        self.btnF1Next = Button(self.f1, text=LOCALIZED_TEXT[lang]["Next"], \
                                command=self._on_click_f1_next, \
                                style='highlight.TButton')
        self.btnF1Next.grid(column=3, row=20, padx=5, pady=5, sticky='news')

    def _initialize_f2(self, lang='en-US'):
        """ initialize the Special Characters tab"""

        self.labelf2 = Label(self.f2, text=LOCALIZED_TEXT[lang]['labelf2'], \
                             anchor='w', justify='left', wraplength=600)
        self.labelf2.grid(column=0, row=0, columnspan=5, padx=5, pady=5, \
                          sticky='w')

        self.lblPreferred = Label(self.f2, \
                                  text=LOCALIZED_TEXT[lang]['lblPreferred'], \
                                anchor='w', justify='left', wraplength=600)
        self.lblPreferred.grid(column=0, row=1, columnspan=3, padx=5, pady=5, \
                               sticky='ew')
        self.rdbDefault = Radiobutton(self.f2, \
                                      text=LOCALIZED_TEXT[lang]["Default"], \
                                      variable=self.preferred, value=0, \
                                      style='wleft.TRadiobutton')
        self.rdbDefault.grid(column=1, row=2, padx=5, pady=5, sticky='news')
        self.rdbPreferred = Radiobutton(self.f2, \
                                    text=LOCALIZED_TEXT[lang]["Preferred"], \
                                    variable=self.preferred, value=1, \
                                    style='wleft.TRadiobutton')
        self.rdbPreferred.grid(column=1, row=3, padx=5, pady=5, sticky='news')
        self.lblLatin1 = Label(self.f2, \
                               text=LOCALIZED_TEXT[lang]["AddLatin1Example"], \
                                anchor='w', justify='left', wraplength=200)
        self.lblLatin1.grid(column=3, row=3, padx=5, pady=5, sticky='news')

        self.preferred.set(0)

        self.ddnPrefChar = Combobox(self.f2, textvariable=self.PrefChar)
        self.ddnPrefChar.grid(column=4, row=3, padx=5, pady=5, sticky='news')
        self.ddnPrefChar.bind("<<ComboboxSelected>>", self._on_loadPrefChar)
        self.ddnPrefChar['text'] = 'Current template:'
        self.ddnPrefChar['justify'] = 'left'

        self.list_PrefChar = ['Latin1',]
        self.list_PrefChar.extend([f[:-4] \
                                            for f in os.listdir(self.Pub2SD) \
                                            if f.endswith('.csv')])

        #self.list_PrefChar.insert(0, 'Latin1')
        #self.list_PrefChar.insert(1, '')

        self.ddnPrefChar['values'] = self.list_PrefChar

        self.btnSavePref = Button(self.f2, \
                                  text=LOCALIZED_TEXT[lang]["SavePref"], \
                                  command=lambda: \
                            self._on_SavePref('', '', \
                                self.txtPrefChar.get(0.0, 9999.9999).strip()))
        self.btnSavePref.grid(column=4, row=4, padx=5, pady=5, sticky='news')

        self.txtPrefChar = Text(self.f2, height=10, width=60)
        self.txtPrefChar.grid(column=0, row=4, \
                              columnspan=3, rowspan=6, padx=5, pady=5, \
                              sticky='news')
        ysb = Scrollbar(self.f2, orient='vertical', \
                              command=self.txtPrefChar.yview)
        self.txtPrefChar.configure(yscroll=ysb.set, font=("sans", 12), \
                                                       undo=True, wrap='word')
        ysb.grid(row=4, column=3, rowspan=6, sticky='nws')

        self.btnF2Next = Button(self.f2, text=LOCALIZED_TEXT[lang]["Next"], \
                                              command=self._on_click_f2_next, \
                                              style='highlight.TButton')
        self.btnF2Next.grid(column=3, row=20, columnspan=2, padx=5, pady=5, \
                                                                 sticky='news')

    def _initialize_f3(self, lang='en-US'):
        """initialize the Edit... tab"""

        self.tree = Treeview(self.f3, selectmode="extended", height=8)
        self.tree.grid(column=0, row=0, \
                       columnspan=12, rowspan=20, sticky='news', padx=5)
        ysb = Scrollbar(self.f3, orient='vertical', command=self.tree.yview)
        xsb = Scrollbar(self.f3, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        ysb.grid(row=0, column=11, rowspan=20, padx=5, sticky='nse')
        xsb.grid(row=20, column=0, columnspan=12, padx=5, sticky='ews')

        self.m = Notebook(self.f3, width=1000)
        self.m.grid(column=0, row=21, \
                    columnspan=12, padx=5, pady=5, sticky='news')

        self.m0 = Frame(self.n)   # Import hierarchy
        self.m1 = Frame(self.n)   # Edit hierarchy
        self.m2 = Frame(self.n)   # Edit MP3 tags


        self.m.add(self.m0, text=LOCALIZED_TEXT[lang]['Import hierarchy'])
        self.m.add(self.m1, text=LOCALIZED_TEXT[lang]['Edit hierarchy'])
        self.m.add(self.m2, text=LOCALIZED_TEXT[lang]['Edit MP3 tags'])


        #self.m.hide(1)
        #self.m.hide(2)
        self._initialize_f3m0(lang) # on m0
        self._initialize_f3m1(lang) # on m1
        self._initialize_f3m2(lang)  # on m2

    def _initialize_f3m0(self, lang='en-US'):
        """initialize the 'Import heirachy' sub-tab of the Edit... tab"""

        self.boxOuter = Frame(self.m0, borderwidth=1)
        self.boxOuter.grid(column=0, row=0, \
                           columnspan=3, padx=5, pady=5, sticky='news')

        self.btnImportContents = Button(self.boxOuter, \
                    text=LOCALIZED_TEXT[lang]["Add the Contents of Folder"], \
                    state='normal', command=self._on_add_contents, \
                    style='lowlight.TButton')

        self.btnImportContents.grid(column=0, row=0, \
                                    rowspan=1, padx=5, pady=5, sticky='news')
        self.btnImportContents_ttp = CreateToolTip(self.btnImportContents, \
                                       LOCALIZED_TEXT[lang]['AddContents_ttp'])

        self.btnImportHierarchy = Button(self.boxOuter, \
                   text=LOCALIZED_TEXT[lang]["Add Folder and it's Contents"], \
                                      command=self._on_add_folder)
        self.btnImportHierarchy.grid(column=0, row=1, \
                                     rowspan=1, padx=5, pady=5, sticky='news')
        self.btnImportHierarchy_ttp = CreateToolTip(self.btnImportHierarchy, \
                                        LOCALIZED_TEXT[lang]['AddFolder_ttp'])

        self.box0 = LabelFrame(self.boxOuter, \
                               text=LOCALIZED_TEXT[lang]["and/or"], \
                                                 labelanchor='w', \
                                                 borderwidth=1)
        self.box0.grid(column=1, row=0, \
                       rowspan=2, padx=5, pady=5, sticky='news')

        self.btnAddCollection = Button(self.box0, \
                                text=LOCALIZED_TEXT[lang]["Add Collection"], \
                                                command=self._on_add_collection)
        self.btnAddCollection.grid(column=0, row=0, \
                                   columnspan=2, padx=5, pady=5, sticky='news')
        self.btnAddCollection_ttp = CreateToolTip(self.btnAddCollection, \
                                    LOCALIZED_TEXT[lang]['AddCollection_ttp'])
        self.btnAddFiles = Button(self.box0, \
                                  text=LOCALIZED_TEXT[lang]["Add Files"], \
                                                    command=self._on_add_item)
        self.btnAddFiles.grid(column=0, row=1, \
                              columnspan=2, padx=5, pady=5, sticky='news')
        self.btnAddFiles_ttp = CreateToolTip(self.btnAddFiles, \
                                        LOCALIZED_TEXT[lang]['AddFiles_ttp'])

        self.box1 = LabelFrame(self.boxOuter, \
                        text=LOCALIZED_TEXT[lang]['Adjust order of files'], \
                                              labelanchor='w', borderwidth=1)
        self.box1.grid(column=2, row=0, \
                       rowspan=2, padx=5, pady=5, sticky='news')

        self.btnMoveUpM0 = Button(self.box1, text="\u02c4\u02c4\u02c4", \
                                  command=self._on_move_up)
        self.btnMoveUpM0.grid(column=0, row=0, \
                              columnspan=2, padx=5, pady=5, sticky='news')
        self.btnMoveUpM_ttp = CreateToolTip(self.btnMoveUpM0, \
                                            LOCALIZED_TEXT[lang]['MoveUp_ttp'])
        self.btnMoveDownM0 = Button(self.box1, text="\u02C5\u02C5\u02C5", \
                                    command=self._on_move_down)
        self.btnMoveDownM0.grid(column=0, row=1, \
                                columnspan=2, padx=5, pady=5, sticky='news')
        self.btnMoveDownM0_ttp = CreateToolTip(self.btnMoveDownM0, \
                                        LOCALIZED_TEXT[lang]['MoveDown_ttp'])

        self.box2 = LabelFrame(self.m0, \
                               text=LOCALIZED_TEXT[lang]['As needed'], \
                                                 labelanchor='n', \
                                                 borderwidth=1)
        self.box2.grid(column=3, row=0, padx=5, pady=5, sticky='news')

        self.ddnTrimFromTitle = Combobox(self.box2, textvariable=self.set_trim)
        self.ddnTrimFromTitle.grid(column=0, row=0, \
                                   columnspan=2, padx=5, pady=5, sticky='news')

        self.btnTrimTitle = Button(self.box2, \
                                   text=LOCALIZED_TEXT[lang]["Trim Title"], \
                                    command=self._on_strip_leading_numbers, \
                                    style='lowlight.TButton')
        self.btnTrimTitle.grid(column=2, row=0, padx=5, pady=5, sticky='news')
        self.lblTrimTitle = Label(self.box2, \
                                  text=LOCALIZED_TEXT[lang]['TrimTitle_ttp'], \
                                    anchor='w', justify='left', wraplength=200)
        self.lblTrimTitle.grid(column=0, row=2, \
                               columnspan=3, padx=5, pady=5, sticky='news')

        self.lblM0 = Label(self.boxOuter, \
                            text=LOCALIZED_TEXT[lang]['M0_ttp'], \
                                    anchor='w', justify='left', wraplength=600)
        self.lblM0.grid(column=0, row=8, \
                        columnspan=3, padx=5, pady=5, sticky='news')


        set_taga = [TRIM_TAG[lang]['Nothing'], \
                    TRIM_TAG[lang]['Leading digits'], \
                    TRIM_TAG[lang]['Leading alphanumerics'], \
                    TRIM_TAG[lang]['Trailing digits']]
        #?remove readonly to allow arbitary trim
        self.ddnTrimFromTitle['values'] = set_taga
        self.ddnTrimFromTitle.set(set_taga[0])
        self.ddnTrimFromTitle['text'] = 'Trim from Title:'
        self.ddnTrimFromTitle['justify'] = 'left'
        self.ddnTrimFromTitle_ttp = CreateToolTip(self.ddnTrimFromTitle, \
                                        LOCALIZED_TEXT[lang]['dropdown5_ttp'])

        #Next button moves to m1
        self.btnF3M0Next = Button(self.m0, text=LOCALIZED_TEXT[lang]["Next"], \
                                  command=self._on_click_f3m0_next, \
                                  style='highlight.TButton')
        self.btnF3M0Next.grid(column=4, row=0, rowspan=2, padx=5, pady=5, \
                              sticky='news')

    def _initialize_f3m1(self, lang='en-US'):
        """initialize the 'Edit heirachy' sub-tab of the Edit... tab"""

        self.btnDeleteItem = Button(self.m1, \
                                    text=LOCALIZED_TEXT[lang]["Delete Item"], \
                                                      command=self._on_delete)
        self.btnDeleteItem.grid(column=0, row=0, padx=5, pady=5, sticky='news')
        self.btnDeleteItem_ttp = CreateToolTip(self.btnDeleteItem, \
                                         LOCALIZED_TEXT[lang]['Delete_ttp'])

        self.box1M1 = LabelFrame(self.m1, \
                                 text=LOCALIZED_TEXT[lang]['Change indent'], \
                                            labelanchor='n', borderwidth=1)
        self.box1M1.grid(column=1, row=0, \
                         columnspan=2, padx=5, pady=5, sticky='news')

        self.btnPromote = Button(self.box1M1, text="<==", \
                                 command=self._on_promote)
        self.btnPromote.grid(column=0, row=0, padx=5, pady=5, sticky='news')
        self.btnPromote_ttp = CreateToolTip(self.btnPromote, \
                                        LOCALIZED_TEXT[lang]['Promote_ttp'])
        self.btnDemote = Button(self.box1M1, text="==>", \
                                                       command=self._on_demote)
        self.btnDemote.grid(column=1, row=0, padx=5, pady=5, sticky='news')
        self.btnDemote_ttp = CreateToolTip(self.btnDemote, \
                                           LOCALIZED_TEXT[lang]['Demote_ttp'])

        self.box2M1 = LabelFrame(self.m1, \
                                 text=LOCALIZED_TEXT[lang]['Change order'], \
                                                labelanchor='n', borderwidth=1)
        self.box2M1.grid(column=3, row=0, \
                         columnspan=2, padx=5, pady=5, sticky='ew')

        self.btnMoveUp = Button(self.box2M1, text="\u02c4\u02c4\u02c4", \
                                command=self._on_move_up)
        self.btnMoveUp.grid(column=0, row=0, padx=5, pady=5, sticky='news')
        self.btnMoveUp_ttp = CreateToolTip(self.btnMoveUp, \
                                           LOCALIZED_TEXT[lang]['MoveUp_ttp'])
        self.btnMoveDown = Button(self.box2M1, text="\u02C5\u02C5\u02C5", \
                                  command=self._on_move_down)
        self.btnMoveDown.grid(column=1, row=0, padx=5, pady=5, sticky='news')
        self.btnMoveDown_ttp = CreateToolTip(self.btnMoveDown, \
                                        LOCALIZED_TEXT[lang]['MoveDown_ttp'])

        # next buttons moves to m2
        self.btnF3M1Next = Button(self.m1, text=LOCALIZED_TEXT[lang]["Next"], \
                                  command=self._on_click_f3m1_next, \
                                  style='highlight.TButton')
        self.btnF3M1Next.grid(column=6, row=0, \
                              rowspan=2, padx=5, pady=5, sticky='nes')

    def _initialize_f3m2(self, lang='en-US'):
        """initialize the 'Edit MP3 tags' sub-tab of the Edit... tab"""

        self.boxOuter = Frame(self.m2, borderwidth=1)
        self.boxOuter.grid(column=0, row=0, columnspan=3, padx=5, pady=5, \
                           sticky='news')

        self.boxEnter = LabelFrame(self.boxOuter, text='=', labelanchor='w', \
                                   borderwidth=1)
        self.boxEnter.grid(column=0, row=0, columnspan=3, padx=5, pady=5, \
                           sticky='news')

        self.etrTagValue = Entry(self.boxEnter, \
                                 textvariable=self.currentEntry, width=70)
        self.etrTagValue.grid(column=0, row=1, \
                              columnspan=3, padx=5, pady=5, sticky='news')
        self.etrTagValue['justify'] = 'left'
        self.etrTagValue_ttp = CreateToolTip(self.etrTagValue, \
                                        LOCALIZED_TEXT[lang]['entry1_ttp'])

        set_tagb = []
#        for tag in SET_TAGS[lang].keys():
        for tag in SET_TAGS[lang]:
            tagname = SET_TAGS[lang][tag]
            #??? need to ensure tagname is translated to fr and pt
            set_tagb.append('{}:({})'.format(tagname, tag.upper()))
            #print(set_tagb)
        self.ddnSelectTag = Combobox(self.boxEnter, state='readonly', \
                                     textvariable=self.set_tag, width=70)
        self.ddnSelectTag.bind("<<ComboboxSelected>>", self._on_get)
        self.ddnSelectTag.grid(column=0, row=0, columnspan=3, padx=5, pady=5, \
                               sticky='news')
        self.ddnSelectTag['text'] = 'Tag to set:'
        self.ddnSelectTag['justify'] = 'left'
        self.ddnSelectTag_ttp = CreateToolTip(self.ddnSelectTag, \
                                    LOCALIZED_TEXT[lang]['ddnSelectTag_ttp'])

        self.lblParameters = Label(self.boxEnter, \
                                   text='', \
                                    anchor='w', justify='left', wraplength=600)
        self.lblParameters.grid(column=0, row=2, columnspan=3, \
                                padx=5, pady=5, sticky='news')

        self.btnGet = Button(self.boxOuter, text=LOCALIZED_TEXT[lang]["Get"], \
                             command=self._on_get)
        self.btnGet_ttp = CreateToolTip(self.btnGet, \
                                        LOCALIZED_TEXT[lang]['Get_ttp'])
        self.btnGet.grid(column=0, row=1, padx=5, pady=5, sticky='news')

        self.btnSet = Button(self.boxOuter, text=LOCALIZED_TEXT[lang]["Set"], \
                             command=self._on_set)
        self.btnSet_ttp = CreateToolTip(self.btnSet, \
                                        LOCALIZED_TEXT[lang]['Set_ttp'])
        self.btnSet.grid(column=1, row=1, padx=5, pady=5, sticky='news')

        self.btnGetDefault = Button(self.boxOuter, \
                                text=LOCALIZED_TEXT[lang]["Get default"], \
                                                  command=self._on_get_default)
        self.btnGetDefault.grid(column=2, row=1, padx=5, pady=5, sticky='news')

        self.lblM2 = Label(self.boxOuter, \
                           text=LOCALIZED_TEXT[lang]['M2_ttp1'] \
                            if self.mode.get() == 0 else \
                            LOCALIZED_TEXT[lang]['M2_ttp'], \
                           anchor='w', justify='left', wraplength=590)
        self.lblM2.grid(column=0, row=2, columnspan=3, padx=5, pady=5, \
                        sticky='news')
        self.boxArt = LabelFrame(self.m2, text='', labelanchor='n', \
                                 borderwidth=1)
        self.boxArt.grid(column=4, row=0, columnspan=2, padx=5, pady=5, \
                         sticky='news')

        self.btnSelectArtwork = Button(self.boxArt, \
                                text=LOCALIZED_TEXT[lang]["Select Artwork"], \
                                                command=self._on_select_artwork)
        self.btnSelectArtwork.grid(column=0, row=0, padx=5, pady=5, \
                                   sticky='news')

        self.ddnPictureType = Combobox(self.boxArt, \
                                       textvariable=self.pictureType)
        self.ddnPictureType.grid(column=0, row=1, padx=5, pady=5, \
                                 sticky='news')
        self.ddnPictureType['text'] = 'Picture Type:'
        self.ddnPictureType['justify'] = 'left'
        self.ddnPictureType['values'] = sorted(PICTURE_TYPE.keys())

        self.ddnPictureType.set('COVER_FRONT')
        self.etrDescription = Entry(self.boxArt, textvariable=self.etrDesc)
        self.etrDescription.grid(column=0, row=2, padx=5, pady=5, \
                                 sticky='news')

        self.lblArt = Label(self.boxArt, \
                            text=LOCALIZED_TEXT[lang]["Art_ttp"], \
                            anchor='w', justify='left', wraplength=275)
        self.lblArt.grid(column=0, row=3, padx=5, pady=5, sticky='ew')


        #next button
        self.btnF3M2Next = Button(self.m2, text=LOCALIZED_TEXT[lang]["Next"], \
                                  command=self._on_click_f3m2_next, \
                                  style='highlight.TButton')
        self.btnF3M2Next_ttp = CreateToolTip(self.btnF3M2Next, \
                                    LOCALIZED_TEXT[lang]['btnF3M2Next_ttp'])
        self.btnF3M2Next.grid(column=9, row=0, rowspan=2, padx=5, pady=5, \
                              sticky='news')

    def _initialize_f4(self, lang='en-US'):
        """initialize the 'Feature-phone options' tab"""

        self.lblPlayLists = Label(self.f4, \
                    text=LOCALIZED_TEXT[lang]["PlayListsIntro"], \
                                    anchor='w', justify='left', wraplength=600)
        self.lblPlayLists.grid(column=0, row=0, columnspan=2, padx=5, pady=5, \
                               sticky='news')

        self.lblEnterList = Label(self.f4, \
                                  text=LOCALIZED_TEXT[lang]["EnterList"], \
                                    anchor='w', justify='left', wraplength=600)
        self.lblEnterList.grid(column=0, row=1, columnspan=2, padx=5, pady=5, \
                               sticky='news')
        self.etrList = Entry(self.f4, textvariable=self.EnterList)
        self.etrList.grid(column=0, row=2, columnspan=2, padx=5, pady=5, \
                          sticky='news')
        self.chkCopyPlayListsToTop = Checkbutton(self.f4, \
                            text=LOCALIZED_TEXT[lang]["CopyPlayListsToTop"], \
                                        variable=self.is_copy_playlists_to_top)
        self.chkCopyPlayListsToTop.grid(column=0, row=3, padx=5, pady=5, \
                                        sticky='w')

        self.boxM3U = LabelFrame(self.f4, \
                            text=LOCALIZED_TEXT[lang][\
                            'Create playlists using Legacy/UTF-8 encoding'], \
                                 labelanchor='n', borderwidth=1)
        self.boxM3U.grid(column=1, row=3, padx=5, pady=5, sticky='news')
        self.rdbM3U = Radiobutton(self.boxM3U, text="M3U", \
                                  variable=self.M3UorM3U8, value=1)
        self.rdbM3U.grid(column=0, row=0, padx=5, pady=5, sticky='news')
        self.rdbM3U8 = Radiobutton(self.boxM3U, text="M3U8", \
                                   variable=self.M3UorM3U8, value=2)
        self.rdbM3U8.grid(column=1, row=0, padx=5, pady=5, sticky='news')
        self.rdbBoth = Radiobutton(self.boxM3U, \
                                   text=LOCALIZED_TEXT[lang]["Both"], \
                                    variable=self.M3UorM3U8, value=3)
        self.rdbBoth.grid(column=2, row=0, padx=5, pady=5, sticky='news')
        self.M3UorM3U8.set(2)
        #next button - this create project folder under  ~/Pub2SD/Temp
        #  and process and place all files within
        self.btnF4Next = Button(self.f4, text=LOCALIZED_TEXT[lang]["Next"], \
                                command=self._on_click_f4_next, \
                                style='highlight.TButton')
        self.btnF4Next_ttp = CreateToolTip(self.btnF4Next, \
                                         LOCALIZED_TEXT[lang]['btnF4Next_ttp'])
        self.btnF4Next.grid(column=2, row=4, padx=5, pady=5, sticky='news')

    def _initialize_f5(self, lang='en-US'):
        """initialize the 'Output to...' tab"""

        #label explaining what doing…, say what size needed to hold project,
        # choose pub to SD/USB or to hard disk under ~/Pub2SD/project
        self.lblOutputIntro = Label(self.f5, \
                                    text=LOCALIZED_TEXT[lang]["OutputIntro"], \
                                    anchor='w', justify='left', wraplength=600)
        self.lblOutputIntro.grid(column=0, row=0, \
                                 columnspan=3, padx=5, pady=5, sticky='news')
        self.lblOutputSizeText = Label(self.f5, \
                                 text=LOCALIZED_TEXT[lang]["OutputSizeText"], \
                                    anchor='w', justify='left')
        self.lblOutputSizeText['justify'] = 'right'
        self.lblOutputSizeText.grid(column=0, row=1, padx=5, pady=5, \
                                    sticky='e')
        self.lblOutputSize = Label(self.f5, text='?Gb', anchor='w', \
                                   justify='left')
        self.lblOutputSize.grid(column=1, row=1, padx=5, pady=5, sticky='w')
        self.lblOutputSize['justify'] = 'left'

        self.boxlf5list = LabelFrame(self.f5, \
                                    text=LOCALIZED_TEXT[lang]['Available'], \
                                    labelanchor='n', borderwidth=1)
        self.boxlf5list.grid(column=0, row=2, columnspan=2, padx=5, pady=5, \
                             sticky='news')

        self.cb = []
        for i in range(0, 8):
            self.cb.append(Checkbutton(self.boxlf5list, text='0', \
                                       onvalue='t', offvalue='f', \
                                       variable=self.cbv[i]))
            self.cb[-1].grid(column=0, row=i, padx=5, pady=1, sticky='w')
            self.cbv[i].set('f')

        self.box1f5 = LabelFrame(self.f5, text=LOCALIZED_TEXT[lang]['Or'], \
                                 labelanchor='s', \
                                 borderwidth=1)
        self.box1f5.grid(column=0, row=3, \
                         columnspan=3, padx=5, pady=5, sticky='news')

        self.btnBuildOutputTo = Button(self.box1f5, \
                            text=LOCALIZED_TEXT[lang]['Output to>'], \
                            command=self._on_build_output_to, \
                            style='highlight.TButton')
        self.btnBuildOutputTo.grid(column=0, row=0, padx=5, pady=5, \
                                   sticky='news')

        self.lblOutputTo = Label(self.box1f5, text='', anchor='w', \
                                 justify='left')
        self.lblOutputTo.grid(column=1, row=0, padx=5, pady=5, sticky='news')

        self._on_refresh_drives()
        self.btnRefreshDrives = Button(self.f5, \
                                       text=LOCALIZED_TEXT[lang]["Refresh"], \
                                            command=self._on_refresh_drives)
        self.btnRefreshDrives.grid(column=2, row=2, padx=5, pady=5, \
                                   sticky='news')
        self.btnRefreshDrives_ttp = CreateToolTip(self.btnRefreshDrives, \
                                        LOCALIZED_TEXT[lang]['Refresh_ttp'])
        self.btnPub2SD = Button(self.box1f5, \
                            text=LOCALIZED_TEXT[lang]["Publish to SD/USB"], \
                            command=self._on_publish_to_SD, \
                            style='highlight.TButton')
        self.btnPub2SD.grid(column=0, row=1, \
                            columnspan=3, padx=5, pady=5, sticky='news')
        project = self.ddnCurProject.get()
#        if len(project) > 0:
        if project:
            self.btnPub2HD = Button(self.f5, \
                text=LOCALIZED_TEXT[lang]["Publish to '~\\Pub2SD\\{}_SD'"].\
                                   format(project), \
                                  command=self._on_publish_to_HD)
        else:
            self.btnPub2HD = Button(self.f5, \
                text=LOCALIZED_TEXT[lang]["Publish to '~\\Pub2SD\\{}_SD'"].\
                                   format("<project>"), \
                                  command=self._on_publish_to_HD, \
                                  style='highlight.TButton')
        self.btnPub2HD.grid(column=0, row=4, \
                            columnspan=2, padx=5, pady=5, sticky='news')


    def _initialize_f6(self, lang):
        """The lock unlock SD card tab, to be implemented?"""
        pass

    def _on_loadPrefChar(self, dummy, _prefchar=None, _lst='', _filein=''):
        """load a set of preferred character pairs from LATIN1 constant
                                                 or a utf8 coded  .csv file"""

        lst = _lst if len(_lst) > 0 else self.ddnPrefChar.get()
        prefchar = _prefchar if _prefchar is not None else self.txtPrefChar
        if lst == 'Latin1':
#            if len(self.txtPrefChar.get(0.0, 9999.9999).rstrip()) > 0:
            if prefchar.get(0.0, 9999.9999).rstrip():
                prefchar.insert(9999.9999, ', ' + LATIN1)
            else:
                prefchar.insert(9999.9999, LATIN1)
        elif lst == '': #del
            prefchar.delete(0.0, 9999.9999)
        else: #load txt file
            if len(_filein) == 0:
                filein = os.path.normpath(self.Pub2SD + '/'+ lst + '.csv')
            else:
                filein = _filein
            fin = codecs.open(filein, mode='r', encoding='utf-8')
            text = fin.read()
#            if len(self.txtPrefChar.get(0.0, 9999.9999).strip()) > 0:
            if prefchar.get(0.0, 9999.9999).strip():
                text = ', ' + text
            prefchar.insert(9999.9999, text)
            fin.close()
#            if self.txtPrefChar.get(0.0, 9999.9999).rstrip():
#                self.txtPrefChar.insert(9999.9999, ', ' + LATIN1)
#            else:
#                self.txtPrefChar.insert(9999.9999, LATIN1)
#        elif lst == '': #del
#            self.txtPrefChar.delete(0.0, 9999.9999)
#        else: #load txt file
#            if len(_filein) == 0:
#                filein = os.path.normpath(self.Pub2SD + '/'+ lst + '.csv')
#            else:
#                filein = _filein
#            fin = codecs.open(filein, mode='r', encoding='utf-8')
#            text = fin.read()
##            if len(self.txtPrefChar.get(0.0, 9999.9999).strip()) > 0:
#            if self.txtPrefChar.get(0.0, 9999.9999).strip():
#                text = ', ' + text
#            self.txtPrefChar.insert(9999.9999, text)
#            fin.close()

    def _on_SavePref(self, _lang='en-US', _fileout='', _text=""):
        """save your list of preferred character pairs to a utf-8 coded 
        .csv file. If _fileout is supplied the filedialog
        will not be called. If _text is supplied self.txtPrefChar will not 
        be accessed"""

        lang = self.ddnGuiLanguage.get() if len(_lang) == 0 else _lang

        fileout = filedialog.asksaveasfilename(\
                        filetypes=[('Preferred characters file', '.csv'), ], \
                                    initialdir=self.Pub2SD, \
                                    initialfile='', \
                                    title=LOCALIZED_TEXT[lang]['SavePref'], \
                                    defaultextension='.csv') \
                  if len(_fileout) == 0 else _fileout
        if len(fileout) != 0: 
            text = self.txtPrefChar.get(0.0, 9999.9999).strip() \
                        if len(_text) == 0 else _text
            text = ' '.join(text.split('\n'))
            text = ' '.join(text.split('\r'))
            text = ' '.join(text.split('\f'))
            if ',' in text:
                pairs = [p.strip for p in text.split(',')]
            else:
                pairs = [text,]
            fout = codecs.open(fileout, mode='w', encoding='utf-8')
            fout.write(', '.join(pairs))
            fout.close()

    def _set_default_tags(self):
        """restores the list of selected tags to the default setting"""
        self.tagtree.selection_set('TIT2')
        for item in self.recommendedTags:
            self.tagtree.selection_add(item)

    def _on_create_template(self, _lang='', _template=None, _fileout=''):
        """saves the currently selected combination of tags
                                               to a utf-8 encoded .json file"""
        
        lang = _lang if _lang else self.ddnGuiLanguage.get()
            
        a_template = _template if _template is not None \
                               else {key: '' \
                                     for key in self.tagtree.selection()}
            
#        self.template = {key: '' for key in self.tagtree.selection()}
        fileout = _fileout if _fileout \
                           else filedialog.asksaveasfilename(\
                                filetypes=[('Template file', '.json'), ], \
                                           initialdir=self.Pub2SD, \
                                           initialfile='', \
                                title=LOCALIZED_TEXT[lang]['CreateTemplate'], \
                                           defaultextension='.json')
#        if len(fileout) > 0: #output template
        if fileout: #output template
            output = codecs.open(fileout, mode='w', encoding='utf-8')

            j = json.dumps(self.template, indent=4, sort_keys=True)
            output.write(j)
            output.close()
        return a_template

    def _on_load_template(self):
        """loads an existing template file (utf-8, .json) which specifies
                        which tags are to be displayed and outputto SD cards"""

        lang = self.ddnGuiLanguage.get()
        thisone = os.path.normpath(self.Pub2SD + '/'+ \
                                   self.ddnCurTemplate.get() + '.json')
        if os.path.isfile(thisone):
            filein = codecs.open(thisone, mode='r', encoding='utf-8')
            lines = filein.readlines()
            self.template = json.loads(''.join(lines))
            self.stemp.text = self.ddnCurTemplate.get()
            attributes = self.stemp.attrib
            for k in self.template.keys():
                attributes[k] = self.template[k]
            filein.close()
#        elif len(self.ddnCurTemplate.get()) == 0:
        elif not self.ddnCurTemplate.get():
            pass
        else:
            messagebox.showerror(\
                    LOCALIZED_TEXT[lang]['Template file not found!'], \
                    LOCALIZED_TEXT[lang]["Can't find {} template, prior \
                    settings unchanged."].format(self.ddnCurTemplate.get()))

    def _on_read_me(self):
        """calls the appropriate 'help' file from the menubar"""

        lang = self.ddnGuiLanguage.get()
        app_dir = get_script_directory()
        # open an HTML file on my own (Windows) computer
        if lang == 'en-US':
            url = os.path.normpath("file://" + app_dir + "/Read_Me.html")
        elif lang == 'fr-FR':
            url = os.path.normpath("file://" + app_dir + "/Lire_Moi.html")
        elif lang == 'pt-PT':
            #need portugese version, default to eng
            url = os.path.normpath("file://" + app_dir + "/Read_Me.html")
        else:
            messagebox.showwarning(\
            'Warning', "Error in on_read_me: " +\
            "{} is unrecognised lang, defaulting to 'en-US.'".format(lang))
            url = os.path.normpath("file://" + app_dir + "/Read_Me.html")
        webbrowser.open(url)


    def _on_build_output_to(self):
        """builds the output to list from selected drives
                     and verifies that sufficent space is available on each"""

        lang = self.ddnGuiLanguage.get()

        self.output_to = []
        self.lblOutputTo['text'] = ''
        needed = folder_size(os.path.normpath(self.Pub2SD + '/Temp/' \
                                        + self.project)) / (1024.0 * 1024.0)

        for i in range(0, 8):
            if (self.cb[i]['state'] == 'normal') \
                                                and (self.cbv[i].get() == 't'):
                if needed < self.tlist[i][1]:
                    self.output_to.append(self.tlist[i][0].split(',')[0])
                else:
                    messagebox.showerror(\
                     LOCALIZED_TEXT[lang]['Insufficent space on {}'].\
                        format(self.tlist[i][0].split(',')[0]), \
                     LOCALIZED_TEXT[lang]["Needs {}Mb, has {}Mb free space."].\
                        format(needed, self.tlist[i][1] / (1024.0 * 1024.0)))
                    self.output_to = []
                    return
        if platform.system() == 'Windows':
            self.lblOutputTo['text'] = \
                             ', '.join(', '.join(self.output_to).split(', , '))
        elif platform.system() == 'Linux':
            self.lblOutputTo['text'] = ', '.join(', '.join([t.split('/')[-1] \
                            for t in self.output_to]).split(', , '))
        else:
            pass
        self.update()

    def _on_refresh_drives(self):
        '''Linux not seeing usb/SD drives'''

        lang = self.ddnGuiLanguage.get()
        giga_bytes = LOCALIZED_TEXT[lang]['Gb']
        mega_bytes = LOCALIZED_TEXT[lang]['Mb']
        self.tlist = [['', 0], ['', 0], ['', 0], ['', 0], \
                      ['', 0], ['', 0], ['', 0], ['', 0]]
        i = 0
        if platform.system() == 'Linux':
            for part in psutil.disk_partitions():
                if ('vfat' in part.fstype or 'fuseblk' in part.fstype) \
                          and 'rw' in part.opts \
                              and 'sda' not in part.device[5:8] and i < 8:
                    usage = psutil.disk_usage(part.mountpoint)
                    total = usage.total/(1024.0 * 1024.0)
                    total = '{0:.2f}{1}'.format(total/1024, giga_bytes) \
                             if total > 1024 else '{:.2f}{}'.format(total, mega_bytes)
                    used = usage.used/(1024.0 * 1024.0)
                    used = '{0:.2f}{1}'.format(used/1024, giga_bytes) \
                            if used > 1024 else '{:.2f}{}'.format(used, mega_bytes)
                    free = usage.free/(1024.0 * 1024.0)
                    free = '{0:.2f}{1}'.format(free/1024, giga_bytes) \
                            if free > 1024 else '{:.2f}{}'.format(free, mega_bytes)
                    percent = '{0:0.1%}'.format(usage.percent/100)
                    self.tlist[i] = ['{}, {}, {}, {}, {}'.\
                        format(part.mountpoint, total, used, free, percent), \
                              usage.free]
                    i += 1
        elif platform.system() == 'Windows':
            for part in psutil.disk_partitions():
                if 'removable' in part.opts and 'rw' in part.opts and i < 8:
                    usage = psutil.disk_usage(part.mountpoint)
                    total = usage.total/(1024.0 * 1024.0)
                    total = '{0:.2f}{1}'.format(total/1024, giga_bytes) \
                             if total > 1024 else '{:.2f}{}'.format(total, mega_bytes)
                    used = usage.used/(1024.0 * 1024.0)
                    used = '{0:.2f}{1}'.format(used/1024, giga_bytes) \
                            if used > 1024 else '{:.2f}{}'.format(used, mega_bytes)
                    free = usage.free/(1024.0 * 1024.0)
                    free = '{0:.2f}{1}'.format(free/1024, giga_bytes) \
                            if free > 1024 else '{:.2f}{}'.format(free, mega_bytes)
                    percent = '{0:0.1%}'.format(usage.percent/100)
                    self.tlist[i] = ['{}, {}, {}, {}, {}'.\
                        format(part.mountpoint, total, used, free, percent), \
                                usage.free]
                    i += 1
        else:
            messagebox.showerror('Unrecognised OS', \
                  "Help I've been kidnapped by {}.".format(platform.system()))

        for i in range(0, 8):
#            if len(self.tlist[i][0]) > 0:
            if self.tlist[i][0]:
                if platform.system() == 'Windows':
                    self.cb[i]['text'] = self.tlist[i][0]
                elif platform.system() == 'Linux':
                    self.cb[i]['text'] = self.tlist[i][0].split('/')[-1]
                self.cb[i]['state'] = 'normal'
            else:
                self.cb[i]['text'] = ''
                self.cb[i]['state'] = 'disabled'
                self.cbv[i].set('f')

    def _pdup_state(self, astate):
        """sets the states of the Promote, Demote, MoveUp and moveDown buttons
                                              on the 'Edit heirachy' sub-tab"""
        self.btnPromote['state'] = astate
        self.btnDemote['state'] = astate
        self.btnMoveUp['state'] = astate
        self.btnMoveDown['state'] = astate

    def _get_template_and_mode_for_load_project(self, lang):
        """attach temlate if specified and calculateidiot_case"""
#        if len(self.ddnCurTemplate.get()) > 0:
        if self.ddnCurTemplate.get():
            if self.stemp.text != self.ddnCurTemplate.get():
                self._on_load_template() #attach new template
        else:
            self.current_project.set(self.stemp.text)
#        new_mode = self.mode.get()
        self.lblMode['text'] = '{}{}'.format(LOCALIZED_TEXT[lang]['Mode>'], \
                    LOCALIZED_TEXT[lang]['Simple'] \
                                  if self.mode.get() == 0 \
                                  else LOCALIZED_TEXT[lang]['Advanced'])
        map(self.tagtree.delete, self.tagtree.get_children())
        #idiot_case
        #old_mode['idiot'] == 'True', new_mode=0  ==> 0, no change
        #old_mode['idiot'] == 'False', new_mode=0 ==> 1, downgrade
        #old_mode['idiot'] == 'True', new_mode=1 ==> 2, upgrade
        #old_mode['idiot'] == 'False', new_mode=1 ==> 3, no change
        if 'idiot' in self.old_mode:
            idiot_case = int(not self.old_mode['idiot'] == 'True') \
                                                + 2 * int(self.mode.get() == 1)
        else:
            idiot_case = 0
            
        return idiot_case

    def _load_project(self, thefile):
        """loads an existing project (.prj) file,adapting it's contents
                                      to the current Simple/Advanced choice"""

        lang = self.ddnGuiLanguage.get()
        linesin = list()
        filein = codecs.open(thefile, mode='r', encoding='utf-8')
        for aline in filein.readlines():
#            if len(aline.strip()) > 0:
            if aline.strip():
                linesin.extend([aline.strip()])
        filein.close()
        lines = ''.join(linesin)
        self.root = etree.fromstring(lines)
        self.settings = self.root.find("settings")
        self.smode = self.settings.find("mode")
        self.stemp = self.settings.find("template")
        self.sf1 = self.settings.find("f1")
        self.sf2 = self.settings.find("f2")
        self.sf4 = self.settings.find("f4")
        self.trout = self.root.find("tree")
        self.old_mode = dict(self.smode.attrib)
        self.template = dict(self.stemp.attrib)
        #print('load project self.old_mode=>{}<'.format(self.old_mode))
        idiot_case = self._get_template_and_mode_for_load_project(lang)
        if idiot_case == 1:
            # downgrade
            self.mode.set(0)
            if not messagebox.askokcancel(\
                        LOCALIZED_TEXT[lang]['Confirm Downgrade?'], \
                        LOCALIZED_TEXT[lang][\
                        "This will downgrade this project from 'Advanced' " \
                        + "to 'Simple'. Some data may be lost."]):
                return
        elif idiot_case == 2:
            # upgrade:
            if not messagebox.askokcancel( \
                        LOCALIZED_TEXT[lang]['Confirm Upgrade?'], \
                        LOCALIZED_TEXT[lang][\
                        "This will upgrade this project from 'Simple' to "\
                        + "'Advanced'."]):
                return
            self.mode.set(1)
        else:
            #self.mode.set(0)
            pass

        if self.mode.get() == 0:
            self.listoftags.extend([t for t in sorted(IDIOT_TAGS.keys()) \
                                    if t not in self.listoftags])
            self._pdup_state('disabled')
        else:
            #self.mode.get() == 1
            self.listoftags.extend(\
                            [t for t in sorted(SET_TAGS[lang].keys()) \
                                    if t not in self.listoftags])
            self._pdup_state('normal')

        self.preferred.set(int(self.smode.attrib['preferred'] == 'True'))
        self.txtPrefChar.delete(0.0, 9999.9999)
        if self.sf2.text != None:
            self.txtPrefChar.insert(9999.9999, self.sf2.text)

        #load tags into tree
        [self.tagtree.insert('', index='end', iid=item, \
                        open=True, values=[0], \
                        text='({}) {}'.format(item, SET_TAGS[lang][item])) \
                                    for item in self.listoftags \
                                    if item not in self.tagtree.get_children()]

        self.tagtree.selection_set('TIT2')
        #now select tags
        attributes = self.sf1.attrib
        [self.tagtree.selection_add(item) for item in attributes.keys() \
                                                    if item in self.listoftags]
        #now add any additional tags in template
        [self.tagtree.selection_add(item) for item in self.template]
        #f4 feature phone folders
        self.EnterList.set(self.sf4.get('folderList'))
        if 'is_copy_playlists_to_top' in self.sf4.attrib:
            self.is_copy_playlists_to_top.set(\
                                int(self.sf4.attrib['is_copy_playlists_to_top']))
        if 'M3UorM3U8' in self.sf4.attrib:
            self.M3UorM3U8.set(int(self.sf4.attrib['M3UorM3U8']))

        # unpickle hashed graphic
        picklein = thefile[:-4] + '.pkl'
        self.hashed_graphics = pickle.load(open(picklein, 'rb')) \
                                          if os.path.isfile(picklein) \
                                          else dict()


    def _on_click_f0_next(self):
        """loads the setting on the 'Project Name' tab
                                  and proceeds to the 'Choose MP3 tags' tab"""

        lang = self.ddnGuiLanguage.get()

        conf_file = self.ddnCurProject.get()
        self._on_load_template()

#        if len(conf_file) == 0:
        if not conf_file:
            messagebox.showinfo("'{}' {}.".format(\
                                LOCALIZED_TEXT[lang]['Current Project>'], \
                                LOCALIZED_TEXT[lang]['is empty']), \
                                "{}".format(LOCALIZED_TEXT[lang][\
                                     'Please enter a name for your project.']))
            return

        self.lblProject['text'] = LOCALIZED_TEXT[lang]['Current Project>'] + \
                                                                ' ' + conf_file
        self.lblMode['text'] = '{}{}'.format(LOCALIZED_TEXT[lang]['Mode>'], \
                                         LOCALIZED_TEXT[lang]['Simple'] \
                                         if self.mode.get() == 0 \
                                         else LOCALIZED_TEXT[lang]['Advanced'])
        conf_file += '.prj' if not conf_file.endswith('.prj') else ''
        thefile = os.path.normpath(self.Pub2SD + '/' + conf_file)
        self.listoftags = [item for item in self.recommendedTags]
        if os.path.isfile(thefile):
            self._load_project(thefile)

        else:
            #new project
            if self.mode.get() == 0:
                #Idiot mode
                self.listoftags.extend([t for t in sorted(IDIOT_TAGS.keys()) \
                                        if t not in self.listoftags])
                self._pdup_state('disabled')
            else:
                self.listoftags.extend([t for t in sorted(SET_TAGS[lang].keys()) \
                                        if t not in self.listoftags])
                self._pdup_state('normal')
            self.tagtree.selection_set('TIT2')
            short = list(set(\
                      self.recommendedTags).intersection(self.template.keys()))
            rest = list(set(\
                        self.template.keys()).difference(self.recommendedTags))
#            if len(self.template) > 0:
            if self.template:
                [self.tagtree.selection_add(item) for item in short]
                [self.tagtree.selection_add(item) for item in rest]
            else:
                self._set_default_tags()
                [self.tagtree.selection_add(item) \
                                            for item in self.recommendedTags]
        self.tagtree.see('')
        self.update()


#        if len(self.ddnCurProject.get()) > 0:
        if self.ddnCurProject.get():
            self.n.add(self.f1)#show recommended tags
            self.n.select(1)
            self.btnSaveProject['state'] = 'normal'
        else:
            messagebox.showerror('Error in on_click_f0()', \
                                          "Error can't find project.")
        self.update()

    def _upgrade_data(self, the_values, item, child):
        """smarten data up from simple(idiot) mode to advanced with encoding
           and full structure for each tag of the specified item.
                 e.g. on a text frame, 'a string' becomes [3, ['astring', ]]"""

        #for each frame in last value in the_values, smarten it up
        this_frame = the_values[-1]
        #hang on was idiot so single frames par tout
        #look up tag default value,
        if the_values[0] not in ['collection', 'project']:
            #is file so process
            if item in DEFAULT_VALUES['ide3v24']:
                #insert text as appropriate
                if item == 'APIC':
                    if the_values[-1][0:2] == 'b"' \
                                             or the_values[-1][0:2] == "b'":
                        #is place holder
                        #grab APIC_, first frame!
                        this_frame = \
                                            child.attrib['APIC_'].split('|')[0]
                        param = ast.literal_eval(this_frame)
                        #is bytes
                        #_encoding = 3
                        #_mime = param[1]
                        #_type = int(param[2])
                        #_desc = ''
                        _data = "b'{}Kb'".format(\
                                    len(self.hashed_graphics[param[4]]/1024) \
                                       if param[4] in self.hashed_graphics \
                                                else 0)
                        #      _encoding,_mime,_type,_desc,_data
                        the_values[-1] = "[3,{},{},{},{}]".\
                                              format(param[1], int(param[2]), \
                                              '', _data)
                    else: #is string
                        #_encoding = 3
                        _mime = 'image/png' \
                                         if the_values[-1][-4:] == '.png' \
                                                      else 'image/jpg'
                        #_type = 3
                        #_desc = ''
                        #add check file exists else break!!!!!
                        the_values[-1] = "[3,{},3,'',{}]".\
                                              format(_mime, this_frame)
                elif item == 'TBPM':
                    packit = '["' + this_frame + '"]'
                    this_frame = DEFAULT_VALUES['ide3v24'][item].\
                                                    replace('["0"]', packit)
                else:
                    packit = '["' + this_frame + '"]'
                    this_frame = DEFAULT_VALUES['ide3v24'][item].\
                                                    replace('[""]', packit)
                the_values[-1] = this_frame
            elif item == 'APIC_':
                #and return to last value in the_values
                the_values[-1] = this_frame
        return the_values


    def _copy_old_columns_to_new_where_exist(self, child, idiot_case, \
                                                                old_columns):
        """copy data from columns in old project to the new project
           where the old column is still selected in the new project,
                                               for the specified file (item)"""
        the_values = list()
        for item in self.columns:
#            if len(old_columns) > 0:
            if old_columns:
                if item in old_columns and item in child.attrib.keys():
                    if not (item == 'adummy' or item == 'APIC_') \
                           or (the_values[0] not in ['collection', 'project']):
                        the_values.extend([child.attrib[item]])
                    else:
                        the_values.extend([child.attrib[item]])
                else:
                    #not in old, so new defaults to '-'
                    the_values.extend(['-'])
            else:
                    #no dif so in attribs
                if item in child.attrib:
                    if not (item == 'adummy' or item == 'APIC_') \
                           or (the_values[0] not in ['collection', 'project']):
                        the_values.extend([child.attrib[item]])
            if idiot_case in ['upgrade data',]:
                the_values = self._upgrade_data(the_values, item, child)
            elif idiot_case in ['downgrade data',]:
                the_values = downgrade_data(the_values, item)
        return the_values

    def _load_file_to_tree(self, child, treeparent, \
                                      idiot_case, old_columns):
        """loads old project data into new project where possible"""
        # need to copy old columns to new where exist else default to '-'
        the_values = self._copy_old_columns_to_new_where_exist(child, \
                                                              idiot_case, \
                                                              old_columns)
        self._stick_it_in_the_tree(child, treeparent, the_values)

    def _stick_it_in_the_tree(self, child, treeparent, the_values):
        """loads file data into the Treeview widget on the 'Edit...' tab"""
        #print("type(child.text) =>{}<".format(type(child.text)))
#        if type(child.text) != 'NoneType' or len(child.text) == 0:
        if type(child.text) != 'NoneType' or not child.text:
        #if not isinstance(child.text, None) or len(child.text) == 0:
            treechild = self.tree.insert(treeparent, index='end', \
                                                values=the_values, \
                                                open=True, \
                                                text='')
        else:
            treechild = self.tree.insert(treeparent, index='end', \
                                                values=the_values, \
                                                open=True, \
                                                text=child.text)
        return treechild

    def _load_collection_to_tree(self, etreeparent, treeparent, \
                                            idiot_case, old_columns):
        """loads a parent collection (and all dependants) from old project
           into new project and displays the in the Treeview widget on the
           'Edit...' tab"""
        #load the parent collection
        # need to copy old columns to new where exist else default to '-'
        the_values = self._copy_old_columns_to_new_where_exist(etreeparent, \
                                                              idiot_case, \
                                                              old_columns)
        treechild = self._stick_it_in_the_tree(etreeparent, treeparent, \
                                                                  the_values)
        #then deal with children!
        for child in etreeparent:
            if child.attrib['Type'] in ['collection',]:
                #recursing down collection trees
                self._load_collection_to_tree(child, treechild, \
                                            idiot_case, old_columns)
            else:
                #is file so process
                self._load_file_to_tree(child, treechild, \
                                      idiot_case, old_columns)

    def _load_children_to_tree(self, project_node, tree_project, \
                              idiot_case, old_columns=[]):
        """for each child of project_node etree load to tree"""
        for child in project_node:
            if child.attrib['Type'] == 'collection':
                self._load_collection_to_tree(child, tree_project, \
                                                    idiot_case, old_columns)
            else:
                self._load_file_to_tree(child, tree_project, \
                                                      idiot_case, old_columns)

    def _etree2tree(self, etreeparent, treeparent, old_columns=[]):
        """The project was loaded from the xml prj file into an lxml etree root
        'etreeparent'. Whose first child is the top level collection named
        after the project. This collection holds all other collections and
        files. Each child of this collection (and any subsequent collections)
        may be either a collection or a file. Their location and any metadata
        are held as attributes of the child. for each child the information
        must be transfered to treeparent (the root of the ttk.treeview used
        to display them.
        prj file lists old columns, Gui defines new columns for display,
        each column represents one mp3 tag of metadata.
        A collection has only a Type='collection' and Title (TIT2)- taken
        from folder name if loaded as a folder else blank until manually
        assigned
        A file has name, location, title(TIT2) taken from file name if no
        embedded tag, plus ast tag, adummy column used for formatting and
        may have an _APIC tag which holds additional data for the APIC tag
        if present.
        Tags not explicitly listed will be absent from published files."""
        #the_project = etreeparent.listchildren()[0]
        #the_project has Type="project" Name="" Location=""
        #load to tree
        #four cases
        # 1: old project = idiot, current project = idiot => no change just load
        # 2: old project = idiot, current project = advanced => upgrade data
        # 3: old project = advanced, current project = idiot => downgrade data
        # 4: old project = advanced, current project = advanced => no change just load
        #print("self.old_mode[idiot]=>{}<".format(self.old_mode['idiot']))
        if 'idiot' in self.old_mode and self.old_mode['idiot'] == 'True' and self.mode.get() != 0:
            idiot_case = 'upgrade data'
        elif 'idiot' in self.old_mode and self.old_mode['idiot'] == 'False' and self.mode.get() == 0:
            idiot_case = 'downgrade data'
        else:
            idiot_case = 'no change'
        #tree should be empty but
        if self.tree.get_children():
            #just in case get rid of any children
            self.tree.delete(self.tree.get_children())
        
        #first have to insert the parent node this sameas name of project
        vout = ['project', '', '']
        tree_project = self.tree.insert('', index='end', values=vout, \
                                    open=True, text=self.ddnCurProject.get())
        if len(etreeparent) > 0:
            #is existing project
            last_project_node = etreeparent[0]
#        for project_node in etreeparent:
#            #only has one child
#            #load_project_to_tree
#            tree_project = self.tree.insert(treeparent, index='end', \
#                                                values="Type='project'", \
#                                                open=True, \
#                                                text='')
#            last_project_node = project_node
#        print(project_node)
#        self._load_children_to_tree(last_project_node, tree_project, idiot_case, \
        #etreeparent has only one child 'the project'
            self._load_children_to_tree(etreeparent[0], tree_project, \
                                        idiot_case, old_columns)
        else:
            #is new project so nothing to load
            pass

    def _list_old_columns(self, old_attrib, new_attrib, lang):
        """list the columnsselceted in the old project"""

        old_columns = list()
        if old_attrib < new_attrib or old_attrib > new_attrib:
            #create old_columns
            listoftags = list()
            listoftags.extend([t for t in (sorted(SET_TAGS[lang].keys() \
                            if self.mode.get() == 1 else IDIOT_TAGS.keys())) \
                                    if t not in listoftags])
            old_columns = ['Type', 'Name', 'Location'] #+ self.recommendedTags

            old_columns.extend([atag for atag in listoftags \
                                if atag in old_attrib])
            old_columns.extend(['adummy'])
            if 'APIC' in old_columns:
                old_columns.extend(['APIC_'])
        return old_columns

    def _set_btn_state_for_on_click_f1_next(self, lang):
        """set btn state for on_click_f1_next"""
        self.btnImportContents['state'] = "normal"
        if self.mode.get() == 0:
            #idiot
            self.ddnSelectTag['values'] = ['{}:{}'.format(k, \
                             SET_TAGS[lang][k]) \
                                for k in self.selected_tags if k != 'APIC']

            self.btnImportContents['state'] = "normal"
            self.btnAddCollection['state'] = "disabled"
            self.btnAddFiles['state'] = "disabled"
            self.btnPromote['state'] = "disabled"
            self.btnDemote['state'] = "disabled"
        else:
            #not idiot
            self.ddnSelectTag['values'] = ['{}:{}'.format(k, \
                             SET_TAGS[lang][k]) \
                                for k in self.selected_tags]
            self.btnAddCollection['state'] = "normal"
            self.btnAddFiles['state'] = "normal"
            self.btnPromote['state'] = "normal"
            self.btnDemote['state'] = "normal"

    def _on_click_f1_next(self):
        """setup all the columns selected in the Treeview widget
        on the 'Edit...' tab and proceed to the 'Special Characters' tab"""

        lang = self.ddnGuiLanguage.get()
        self.ddnPrefChar.current(0)
        self.sf1.clear()
        self.selected_tags = [i for i in self.tagtree.selection()]
        if 'TIT2' not in self.selected_tags:
            self.selected_tags.insert(0, 'TIT2')
        self.columns = ['Type', 'Name', 'Location'] #+ self.recommendedTags
        self.columns.extend(self.selected_tags)
        self.displayColumns = [item for item in self.columns]
        self.displayColumns.remove('Location')
        self.displayColumns.remove('Name')

        map(self.sf1.attrib.pop, self.sf1.attrib.keys())
        #put tag state into xml
        for i in range(0, len(self.selected_tags)):
            self.sf1.attrib[self.selected_tags[i]] = 'show'
        old_columns = self._list_old_columns(set(self.sf1.attrib.keys()), \
                                            set(self.sf1.attrib.keys()), \
                                            lang)
        # now got full list of all tags to display! So display tree columns
        # add adummy column
        if 'adummy' not in self.columns:
            self.columns.extend(['adummy'])
        if 'adummy' not in self.displayColumns:
            self.displayColumns.extend(['adummy'])

        if 'APIC' in self.columns:
            self.columns.extend(['APIC_'])

        self.tree['columns'] = self.columns
        self.tree["displaycolumns"] = self.displayColumns
        self.tree.column("#0", minwidth=0, width=100, stretch=NO)
        self.tree.heading('#0', text=LOCALIZED_TEXT[lang]['#0'])

        self.tree.column('Type', minwidth=0, width=75, anchor='center', \
                         stretch=NO)
        self.tree.heading('#1', text=LOCALIZED_TEXT[lang]['Type'])

        self.Treed = True
        for item in self.displayColumns[1:-1]:
            if self.mode.get() == 0:
                #is idiot
                self.tree.heading(item, text=SET_TAGS[lang][item])
                self.tree.column(item, minwidth=0, \
                        width=self.font.measure(SET_TAGS[lang][item]), \
                                              anchor='center', stretch=NO)
            else:
                #not an idiot so show tag codes not descriptions
                self.tree.heading(item, text=item)
                self.tree.column(item, minwidth=0, \
                        width=self.font.measure(item), stretch=NO)
        self.tree.heading('adummy', text='')
        #override width for 'adummy' column
        self.tree.column('adummy', minwidth=10, width=10, stretch=NO)

        if 'APIC_' in self.tree['columns']:
            self.tree.column('APIC_', minwidth=0, width=0, stretch=NO)

        #load project tree into treeview
#        if len(self.trout) > 0:
#        if self.trout is not None
        #print(self.trout)
        #print("self.trout.keys()=>{}<".format(self.trout.keys()))
        if self.trout is not None:
            self._etree2tree(self.trout, '', old_columns)
            list_of_children = self.tree.get_children('')
            self.project_id = list_of_children[0]
        else:
            vout = ['project', '', '']
            self.project_id = self.tree.insert('', index='end', values=vout, \
                                    open=True, text=self.ddnCurProject.get())
        self._rename_children_of(self.project_id)

        self.n.add(self.f2)
        self.n.select(2)
        self._set_btn_state_for_on_click_f1_next(lang)
        self._change_lang()

    def _on_click_f2_next(self):
        """load settings and preferred character pairs,
            checking for illeagal combinations and proceed to 'Edit...' tab"""

        lang = self.ddnGuiLanguage.get()
        self.pref = list()
        self.pref_char = list()

        #load from self.txtPrefChar
        text = self.txtPrefChar.get(0.0, 9999.9999).strip()
        text = ' '.join(text.split('\n'))
        text = ' '.join(text.split('\r'))
        text = ' '.join(text.split('\f'))
#        if len(text) > 0:
        if text:
            pairs = [c.strip() for c in text.split(',')]
            for p in pairs:
                p = p.strip()
                t = p.split('/')
#                if len(t) == 2 and len(t[0]) > 0:
                if len(t) == 2 and t[0]:
                    #is valid so...
                    t[0] = de_hex(t[0])
                    t[1] = de_hex(t[1])
                    if '\\' not in t[0] and '\\' not in t[1] \
                                    and '/' not in t[0] \
                                                    and '/' not in t[1]:
                        if any(x[0] == t[0] for x in self.pref):
                            #is a copy
                            #error message!
                            messagebox.showwarning(\
                            LOCALIZED_TEXT[lang][\
                                'Discarding duplicate mapping {}'].format(p), \
                            LOCALIZED_TEXT[lang][\
                                  'Only one mapping allowed for each string.'])
                        else:
                            t.extend([re.compile(t[0]),])
                            self.pref.extend([t,])
                            self.pref_char.extend([t[1],])
                            #print(t)
                    else:
                        #error message
                        messagebox.showwarning(\
                        LOCALIZED_TEXT[lang][\
                                      'Discarding illegal map {}'].format(p), \
                        LOCALIZED_TEXT[lang][\
                                           "'\\' characters are not allowed."])
                else:
                    #error message
                    messagebox.showwarning(\
                    LOCALIZED_TEXT[lang][\
                                      'Discarding illegal map {}'].format(p), \
                    LOCALIZED_TEXT[lang][\
                "Initial string can not be null and a sole '/' is mandatory."])
        #strip any illegal chars out of pref_chars
        self.pref_char = [c for c in self.pref_char \
                             if c not in self.illegalChars]
        self._rename_children_of(self.project_id)
        self.n.add(self.f3)
        self.n.select(3)

    def _on_click_f3m0_next(self):
        """proceed to 'Edit heirarchy' sub-tab"""
        self.m.add(self.m1)
        self.m.select(1)

    def _on_click_f3m1_next(self):
        """proceed to 'Edit MP3 tags' sub-tab"""
        self.m.add(self.m2)
        self.m.select(2)

    def _on_click_f3m2_next(self):
        """proceed to 'Feature-phone options' tab"""
        self.n.add(self.f4)
        self.n.select(4)

    def _on_click_f4_next(self):
        """Load playlist settings,
           build list of all files in project,
           copy them into a temporary working folder structure,
           applying any changes to the working copies only,
           build playlists.
           Then proceed to 'Output to...' tab."""

        lang = self.ddnGuiLanguage.get()

        #open all new files
        self.project = self.ddnCurProject.get()

        self.files = {}
        #walk down tree creating filenames
        # and opening them in pairs iid:filename
        temp_path = os.path.normpath(self.Pub2SD + '/Temp/' + self.project)
        try:
            delete_folder(temp_path)
        except:
            messagebox.showerror(\
                LOCALIZED_TEXT[lang]['Error in on_click_f4_next()'], \
                LOCALIZED_TEXT[lang]["Folder <{}> may be in use by another \
                program. Close all other programs \
                and try again.".format(temp_path)])
            return
        project_path_ = os.path.normpath(self.project)
        # trailling '\\' will be removed
        self._childrens_filenames(self.project_id, temp_path, project_path_)
        #test if any files, if not give up now!
#        if len(self.files) == 0:
        if not self.files:
            messagebox.showwarning(\
                    LOCALIZED_TEXT[lang]['No collections or files found.'], \
                    LOCALIZED_TEXT[lang][\
                                    "Please add collections and their files."])
            return
        self._on_prepare_files()
        self.n.select(4)
        self.update()
        self._on_generate_playlists()
        self.n.select(4)
        self.update()
        self.lblOutputSize['text'] = "{:0.1f} MB".format( \
            folder_size(\
    os.path.normpath(self.Pub2SD + '/Temp/' + self.project))/(1024.0 * 1024.0))
        #if top
        #if cool_music
        self.play_list_targets = set()
        if self.isCoolMusic.get() == 1:
            self.play_list_targets.add('COOL_MUSIC')
        #if list
#        if len(self.EnterList.get()) > 0:
        if self.EnterList.get():
            self.play_list_targets.update(set(self.EnterList.get().split(',')))

        self.n.add(self.f5)
        self.n.select(5)

    def _on_click_f5_next(self):
        """waiting on lock/unlock SD card software!"""
        self.n.add(self.f6)
        self.n.select(6)


    def _on_add_collection(self):
        """add a collection to treeview widget at the current focus"""
        focus = self.tree.focus()

        vout = ['collection', '-', '-']
        vout.extend(['-' for item in self.displayColumns[2:-1]])
#        focus = self.tree.insert(focus if focus else '', \
        focus = self.tree.insert(focus if focus else self.project_id, \
                                 index='end', values=vout, open=True, \
                                 text='empty collection')
#                                 text='collection')
#        focus = self.tree.insert(focus if len(focus) > 0 else '', \
#                                 index='end', values=vout, open=True, \
#                                 text='collection')
        self._rename_children_of(self.project_id)
        self.tree.see(focus)
        self.update()


    def _rename_children_of(self, parent):
        """rename all the children of parent, parents name is unchanged.
           Typicaly will always call on the top level project collection"""
        #rename all branches
        initial_digit = self.InitialDigit.get().upper()
        prefix = self.InitialDigit.get()

        children = self.tree.get_children(parent)
        ancestor_name = str(self.tree.set(parent, 'Name')) if parent else ''
#        ancestor_name = str(self.tree.set(parent, 'Name')) if len(parent) > 0 \
#                                                           else ''
#        print("parent=>{}< of {}".format(parent, children))
#        for achild in children:
#            print("child text=>{}<".format(self.tree.item(achild)['text']))
        self.tree.item(self.project_id, text=self.ddnCurProject.get())
        my_isalpha = True
#        if len(ancestor_name) > 0:
        if ancestor_name:
            if ancestor_name[-1] == '@':
                my_name = '@'
            else:
                my_name = 1
                my_isalpha = ancestor_name[-1].isdecimal()
        else:
            my_name = 1
#            if len(initial_digit) > 0:
            if initial_digit:
                my_isalpha = initial_digit[-1].isdecimal()
            else:
                my_name = 1
                my_isalpha = False
        my_num = 1

        nos_digits = (len(str(len(children)))-1) \
                     if my_name == 1 and not my_isalpha else 0
        for child in children:
            the_format = '{0:0' + '{}'.format(nos_digits) + 'd}'
            #bullet proofed in to_aplpha() so not exceed limit of single digit
            my_str = to_alpha(my_name) \
                             if my_isalpha else the_format.format(my_name)
            if self.tree.set(child, 'Type') == 'collection':
                title = self._my_unidecode(self.tree.set(child, 'TIT2'))
                #strip out any unapproved punctuation - done in my_unidecode
                self.tree.set(child, 'Name', ancestor_name + my_str)
                #print(prefix, ancestor_name, my_str, title)
                self.tree.item(child, text="{0}{1}{2}-{3}".format(prefix, \
                               ancestor_name, my_str, title))
                my_name += 1
                self._rename_children_of(child)
            else: #is file so use
                size = os.path.getsize(self.tree.set(child, 'Location')) \
                                if self.tree.set(child, 'Location') != '-' \
                                else 0
                if size == 0:
                    #fetch location, trim off path and '.mp3' extension,
                    #transliterate unicode(utf-8) to 7-bit ascii or Latin-1?
                    title = self._my_unidecode(os.path.basename(\
                                            self.tree.set(child, 'Location')))
                    #transliterate unicode(utf-8) to 7-bit ascii or Latin-1?
                    #replace spaces and punctuation  - done in my_unidecode
                    self.tree.set(child, 'Name', ancestor_name + my_str)
                    self.tree.item(child, text="{0}{1}{2}-{3}".format(prefix, \
                                   ancestor_name, my_str, title))
                else: #             idiot/not idiot
                    title = self._my_unidecode(self.tree.set(child, 'TIT2')) \
                                if self.mode.get() == 0 \
                                else self._my_unidecode(self.tree.set(child, \
                                    'TIT2')[5:-2].split(',')[0][1:-1])
                    self.tree.set(child, 'Name', \
                                  "{0}-{1:02d}".format(ancestor_name, my_num))
                    self.tree.item(child, \
                                   text="{0}{1}-{2:02d}-{3}".format(prefix, \
                                         ancestor_name, my_num, title))
                my_num += 1

#    def _splitlist(self, alist):
#        print(alist)
#        pass

    def _on_add_item(self):
        """ add an item(mp3 file) to the selected collection"""

        lang = self.ddnGuiLanguage.get()
        focus = self.tree.focus()
        if len(focus) < 1:
            messagebox.showwarning('', LOCALIZED_TEXT[lang][\
                                                   "Please select a row."])
        else:
            if self.tree.set(focus, 'Type') == 'collection':
                full_path = filedialog.askopenfilenames(\
                                    initialdir=os.path.expanduser('~'), \
                                    filetypes=[('MP3 files', '*.mp3'),], \
                                              title="Select MP3 file…")
#                filenames = self._splitlist(full_path)
                filenames = full_path
                self.progbar['maximum'] = len(filenames)
                self.progbar['value'] = 0

                ff = {}
                flist = {}
                for f in filenames:
#                    print(f)
                    filename = os.path.basename(f)[:-4]
                    lf = sort_key_for_filenames(filename)
                    ff[lf] = filename
                    flist[filename] = f

                for ll in sorted(ff):
                    filename = ff[ll]
                    f = flist[filename]
                    somevalues = self._read_idiot_mp3_tags(f) \
                                                    if self.mode.get() == 0 \
                                                    else self._read_mp3_tags(f)
                    self.tree.insert(focus, index='end', values=somevalues, \
                            open=True, text='file')
                    self.progbar.step()
                    self.update()

        self._rename_children_of(self.project_id)
        self.tree.see(focus)
        self.update()

    def _read_mp3_process_atag(self, atag, k, apic_params, filepath):
        """process the (advanced) mp3 tag"""

        theParameters = None
        if k == 'APIC':
            m = hashlib.sha256(atag.data)
            if m.hexdigest() not in self.hashed_graphics:
                self.hashed_graphics[m.hexdigest()] = atag.data
            theParameters = [int(atag.encoding), atag.mime, \
                             int(atag.type), atag.desc, \
                                m.hexdigest()]
            apic_params.extend([str(theParameters)])
            length = int(len(atag.data)/1024 + 0.5)
            theParameters[4] = "b'{}Kb'".format(length)
            #aresult.extend([str(theParameters)])
        elif k in THE_P:
#            print("{} >{}<".format(k,THE_P[k]))
#            theParameters = ast.literal_eval(THE_P[k])
            theParameters = THE_P[k](atag, True)
        else:
            messagebox.showerror(\
                'Error in read_mp3_tags()', \
                "{} is unrecognized  MP3 tag in {}".format(\
                                               atag, filepath))
        return theParameters

    def _read_mp3_tags(self, filepath):
        """read in an mp3 files tags to Treeview wiget"""

        if os.path.getsize(filepath) > 0:
            audio = ID3(filepath)
            result = ['file', '', filepath]
            apic_params = list()
            for k in self.displayColumns[1:-1]:
                list_tags = audio.getall(k)
                aresult = list()
#                if len(list_tags) > 0:
                if list_tags:
                    for atag in list_tags:
                        theParameters = \
                                self._read_mp3_process_atag(atag, k, apic_params, filepath)
                        if theParameters != None:
                            aresult.extend([str(theParameters)])
                    result.extend(['|'.join(aresult)])
                else:
                    title = os.path.basename(filepath)[:-4]
                    result.extend(['[3, ["{}"]]'.format(title.strip())]\
                                         if k == 'TIT2' else ['-',])
#                if k in self.template.keys() and len(self.template[k]) > 0 \
#                                                         and result[-1] == '-':
                if k in self.template.keys() and self.template[k] \
                                                         and result[-1] == '-':
                    result[-1] = DEFAULT_VALUES['ide3v24'][k].\
                                    replace('[""]', '["{}"]'.\
                                            format(self.template[k]))
            #now add empty string for 'adummy' column
            result.extend(['',])
            #add HIDDEN column to hold full APIC data if present!
#            if len(apic_params) > 0:
            if apic_params:
                result.extend(['|'.join(apic_params)])
            for index in range(0, len(self.displayColumns)):
                if self.displayColumns[index] in self.template.keys() and \
                               self.template[self.displayColumns[index]] != "":
                    result[index].replace('-', \
                              self.template[self.displayColumns[index]])
        else: #zero length file No Tags!
            result = ['file', '', filepath]
            if 'TIT2' in self.displayColumns[2:-1]:
                result.extend(['[3, ["{}"]]'.format(\
                                     os.path.basename(filepath)[:-4])] \
                                     if k == 'TIT2' else ['#',])
        return result

    def _read_idiot_mp3_process(self, atag, k, apic_params, filepath):
        """process the idiot mp3 tag"""

        theParameters = None
        if k in THE_IDIOT_P:
            theParameters = THE_P[k](atag, False)
        elif k == 'APIC':
            m = hashlib.sha256(atag.data)
            if m.hexdigest() not in self.hashed_graphics:
                self.hashed_graphics[m.hexdigest()] = atag.data
            apic_params.extend([str([int(atag.encoding), \
                                     atag.mime, \
                                     int(atag.type), \
                                        atag.desc, \
                                        m.hexdigest()])])
            length = int(len(atag.data)/1024 + 0.5)
            theParameters = "b'{}Kb'".format(length)
        else:
            messagebox.showerror(\
        'Error in read_idiot_mp3_tags()', \
        "{} is unrecognized MP3 tag in simple mode in {}.".\
             format(atag, filepath))
            theParameters = ''
        return theParameters

    def _read_idiot_mp3_tags(self, filepath):
        """read the mp3 tags of file in idiot mode"""

        if os.path.getsize(filepath) > 0:
            audio = ID3(filepath)
            result = ['file', '', filepath]
            apic_params = list()
            for k in self.displayColumns[1:-1]:
                list_tags = audio.getall(k)
                aresult = list()
#                if len(list_tags) > 0:
                if list_tags:
                    for atag in [list_tags[0],]:
                        theParameters = self._read_idiot_mp3_process(atag, k, \
                                                        apic_params, filepath)
                        if theParameters != None:
                            aresult.extend([str(theParameters)])

                    result.extend(['|'.join(aresult)])
                else:
                    if k == 'TIT2':
                        title = os.path.basename(filepath[:-4]) \
                                                if '/'in filepath else filepath
                        result.extend(['{}'.format(title.strip())])
                    else:
                        result.extend(['-',])
                if k in self.template.keys() \
                         and self.template[k] and result[-1] == '-':
#                         and (len(self.template[k]) > 0 and result[-1]) == '-':
                    result[-1] = self.template[k]
            #insert empty string for adummy column
            result.extend(['',])
#            if len(apic_params) > 0:
            if apic_params:
                result.extend(['|'.join(apic_params)])
        else: #zero length file No Tags!
            result = ['file', '', filepath]
            if 'TIT2' in self.displayColumns[1:-1]:
                title = os.path.basename(filepath)[:-4]
                result.extend(['{}'.format(title)])
            else:
                result.extend(['#',])
        return result

    def _count_mp3_files_below(self, adir_path):
        """counts all mp3 files below given dir including subdirs"""
#        files = glob.glob(adir_path + '/*.mp3')
        matches = []
        for root, dirnames, filenames in os.walk(adir_path):
            for filename in fnmatch.filter(filenames, '*.mp3'):
                matches.append(os.path.join(root, filename))
        return(len(matches))
#        return(len(files))

    def _on_add_folder(self):
        """add folder as collection with its dependants to Treeview widget"""
        focus = self.tree.focus()
        if focus == '':
            focus = self.project_id
        dir_path = filedialog.askdirectory(initialdir=os.path.expanduser('~'),\
                                    title="Select folder…", mustexist=True)
        if dir_path:
            self.nos_tracks = self._count_mp3_files_below(dir_path)
        else:
            self.nos_tracks = 0
        self._count_files_below(focus)
        self.progbar['maximum'] = self.nos_tracks
        self.progbar['value'] = 0
        self._add_tree(focus, dir_path, False)
        #now set column widths using self.maxcolumnwidths?
        self.tree.see(focus)
        self._rename_children_of(self.project_id)

        self.status['text'] = ''
        self.progbar['value'] = 0
        self.update()

    def _on_add_contents(self):
        """add contents of a folder with its dependants to existing collection
                                                          in Treeview widget"""

        lang = self.ddnGuiLanguage.get()

        focus = self.tree.focus()
        if focus == '':
            focus = self.project_id
        dir_path = filedialog.askdirectory(initialdir=os.path.expanduser('~'),\
                                        title="Select folder…", mustexist=True)
        if dir_path:
            self.nos_tracks = self._count_mp3_files_below(dir_path)
        else:
            self.nos_tracks = 0
        self.progbar['maximum'] = self.nos_tracks
        self.progbar['value'] = 0
#        if len(glob.glob(dir_path + '/*.mp3')) == 0:
        if not glob.glob(dir_path + '/*.mp3'):
            #dir_path holds no bare MP3 files
            self._add_tree(focus, dir_path, True)
        else:
            #dir_path holds bare mp3 files
#            if len([child \
#                    for child in self.tree.get_children(self.project_id) \
#                    if self.tree.set(focus, 'Type') is 'collection']) == 0:
            if not [child \
                    for child in self.tree.get_children(self.project_id) \
                    if self.tree.set(focus, 'Type') == 'collection']:
                #no collections listed...
                messagebox.showwarning(\
                        LOCALIZED_TEXT[lang]["Add the Contents of Folder"], \
                        LOCALIZED_TEXT[lang]["bareMP3ImportFolder"])
                self._add_tree(focus, dir_path, False)
            else:
                if focus is self.project_id:
                    #Warning message  saying 'folder holds bare MP3 files so
                    #select collection or import folder to create a new
                    #collection'
                    messagebox.showwarning(\
                        LOCALIZED_TEXT[lang]["Add the Contents of Folder"], \
                        LOCALIZED_TEXT[lang]['bareMP3selectCreateCollection'])
                else:
                    self._add_tree(focus, dir_path, True)
        #now set column widths using self.maxcolumnwidths?
        self.tree.see(focus)
        self._rename_children_of(self.project_id)
        self.status['text'] = ''
        self.progbar['value'] = 0
        self.update()


    def _add_tree(self, the_focus, adir_path, noTop=False):
        """add folder and dependants, with or without creating a new
           collection of the same name as the folder at the current focus
           in the Treeview widget"""

        lang = self.ddnGuiLanguage.get()
        self.status['text'] = LOCALIZED_TEXT[lang]['Unpacking'] + adir_path
        self.update()
        vout = ['collection', '-', '-']
        if 'TIT2' in self.displayColumns:
            vout.extend([self._my_unidecode(os.path.split(adir_path)[-1]),])
        vout.extend(['-' for item in self.displayColumns[2:-1]])

        thisdir = the_focus if noTop \
                            else self.tree.insert(the_focus, \
                                     index='end', values=vout, open=True, \
                                     text='collection')

        #now list all 'mp3' files in this directory (with their full path)

        _ff = {}
        flist = {}
        #step through a list of filepaths for all mp3 files in current dir only
        for f_ in [forward_slash_path(afile) \
                   for afile in glob.glob(adir_path + '/*.mp3')]:
            _ff[sort_key_for_filenames(os.path.basename(f_)[:-4])] = \
                                                    os.path.basename(f_)[:-4]
            flist[os.path.basename(f_)[:-4]] = f_

        for _ll in sorted(_ff):
            f_ = flist[_ff[_ll]]
            somevalues = self._read_idiot_mp3_tags(f_) \
                                        if self.mode.get() == 0 \
                                        else self._read_mp3_tags(f_)
            nos_columns = len(somevalues)
            if 'APIC' in self.tree['displaycolumns']:
                nos_columns -= 1
            if len(self.maxcolumnwidths) < nos_columns:
                self.maxcolumnwidths = [0 for v in range(0, nos_columns)]
            #calc width of displayed columns to fit their text
            self.maxcolumnwidths = [self.font.measure(somevalues[v]) \
                if self.font.measure(somevalues[v]) > self.maxcolumnwidths[v] \
                else self.maxcolumnwidths[v] \
                                for v in range(0, nos_columns)]
            #scale to fit display
            self.maxcolumnwidths = [int(4*self.maxcolumnwidths[v]/5)+2  \
                                if int(4*self.maxcolumnwidths[v]/5) > 75 \
                                else 75 \
                                for v in range(0, len(self.maxcolumnwidths))]
#            imagetk = None #???
#            if imagetk is not None:
#                self.tree.insert(thisdir, index='end', values=somevalues, \
#                                 open=True, text='file', image=imagetk)
#            else:
#                self.tree.insert(thisdir, index='end', values=somevalues, \
#                                 open=True, text='file')
            self.tree.insert(thisdir, index='end', values=somevalues, \
                                 open=True, text='file')
            self.progbar.step()
            self.update()
        # recurse through sub-dirs
        for adir in sorted([os.path.normpath(adir_path + '/' + d) \
                            for d in os.listdir(adir_path) \
                                if os.path.isdir(adir_path + '/' + d) \
                                            and len(d) > 0]):
            self._add_tree(thisdir, adir)

    def _set_width_of_this_column(self, column, _text, _anchor='w'):
        """sets display width of specified column in the Treeview widget"""
        _width = int((4 * self.font.measure(_text) / 5) + 2)
        self.tree.column(column, anchor=_anchor, minwidth=50, width=_width, \
                         stretch=False)

    def _set_column_width(self):
        """set all column widths in Treeview widget"""
        self.tree.column('#0', anchor='center', minwidth=50, width=100, \
                         stretch=False)

        self.tree.column('#1', anchor='center', minwidth=50, \
                         width=self.maxcolumnwidths[0], stretch=False)
        self.tree.column('#2', anchor='center', minwidth=60, \
                         width=self.maxcolumnwidths[1], stretch=False)
        self.tree.column('#3', anchor='w', minwidth=50, \
                         width=self.maxcolumnwidths[3], stretch=False)
        for vv in range(4, len(self.maxcolumnwidths)):
            self.tree.column('#{}'.format(vv), anchor='center', \
                             minwidth=50, width=self.maxcolumnwidths[vv], \
                                                        stretch=False)


    def _on_move_up(self):
        """move item up one position within current collection"""
        focus = self.tree.focus()
        index = self.tree.index(focus)
        parent = self.tree.parent(focus)
        if self.tree.set(parent, 'Type') in ['collection', 'project']:
            if index > 0:
                self.tree.move(focus, parent, index - 1)
        self._rename_children_of(parent)
        self.tree.see(focus)

    def _on_move_down(self):
        """move item down one position within current collection"""
        focus = self.tree.focus()
        index = self.tree.index(focus)
        parent = self.tree.parent(focus)
        if self.tree.set(parent, 'Type') in ['collection', 'project']:
            children = self.tree.get_children(parent)
            if index < (len(children)-1):
                self.tree.move(focus, parent, index + 1)
        self._rename_children_of(parent)
        self.tree.see(focus)

    def _on_delete(self):
        """delete the current item selected in Treeview widget"""
        list_of_items = self.tree.selection()
#        if len(list_of_items) > 0:
        if list_of_items:
            for focus in list_of_items:
                if self.tree.set(focus, 'Type') != 'project':
                    self.tree.delete(focus)

    def _list_children_of(self, parent, etparent):
        """list children of parent"""
        children = self.tree.get_children(parent)
        for child in children:
            echild = etree.SubElement(etparent, child)
            the_values = self.tree.item(child)['values']
            columns = [c for c in self.tree['columns']]
            for i in range(0, len(the_values)):
                echild.attrib[columns[i]] = str(the_values[i])
            self._list_children_of(child, echild)

    def _on_del_project(self):
        """Delete current project"""
        project = self.ddnCurProject.get()
#        if len(project) > 0:
        if project:
            if '.prj' not in project:
                project += '.prj'
            os.remove(self.Pub2SD + '/'+ project)
            self.list_projects = [f.rstrip('.prj') \
                                  for f in os.listdir(self.Pub2SD) \
                                                     if f.endswith('.prj')]
            self.ddnCurProject['values'] = self.list_projects
#            if len(self.list_projects) > 0:
            if self.list_projects:
                self.ddnCurProject.set(self.list_projects[0])
            else:
                self.ddnCurProject.set('')

    def _on_save_project(self):
        """save current project"""

        lang = self.ddnGuiLanguage.get()

        project = self.ddnCurProject.get()

        fileout = filedialog.asksaveasfilename(\
                                    filetypes=[('Project file', '.prj'), ], \
                                          initialdir=self.Pub2SD, \
                                          initialfile=project, \
                                          title=LOCALIZED_TEXT[lang]['Save'], \
                                          defaultextension='.prj')
        new_project = fileout.split('/')[-1]
        new_project = new_project[:-4]
        if new_project != project:
            self.lblProject['text'] = \
                           LOCALIZED_TEXT[lang]['Current Project>'] + \
                           ' ' + new_project
        #create new project tree, throwing away any existing tree
        self.root = etree.Element('root')
        #add child 'settings', all user configurable bits under here
        self.settings = etree.SubElement(self.root, "settings")
        self.smode = etree.SubElement(self.settings, "mode")
        self.stemp = etree.SubElement(self.settings, "template")
        self.sf0 = etree.SubElement(self.settings, "f0")
        self.sf1 = etree.SubElement(self.settings, "f1")
        self.sf2 = etree.SubElement(self.settings, "f2")
        self.sf4 = etree.SubElement(self.settings, "f4")
        self.trout = etree.SubElement(self.root, "tree")
        #                               idiot                  not idiot
        self.smode.attrib['idiot'] = 'True' \
                         if self.mode.get() == 0 else 'False'
        #print("self.smode.attrib['idiot']=>{}<".format(self.smode.attrib['idiot']))
        self.old_mode['idiot'] = self.smode.attrib['idiot']
        self.smode.attrib['preferred'] = 'False' \
                         if self.preferred.get() == 0 else 'True'

        for atag in self.selected_tags:
            self.sf1.attrib[atag] = 'show'
        self.sf2.text = self.txtPrefChar.get(0.0, 9999.9999)

        self.stemp.text = self.ddnCurTemplate.get() \
                                if self.ddnCurTemplate.get() else ''
#                                if len(self.ddnCurTemplate.get()) > 0 else ''

        self.sf4.set('folderList', self.etrList.get())
        self.sf4.attrib['is_copy_playlists_to_top'] = \
                       str(self.is_copy_playlists_to_top.get())
        self.sf4.attrib['M3UorM3U8'] = str(self.M3UorM3U8.get())

        if os.path.exists(fileout):
            os.remove(fileout)

#        if len(fileout) > 0:
        if fileout:
            output = codecs.open(fileout, mode='w', encoding='utf-8')
            self._list_children_of('', self.trout)
            output.write(etree.tostring(self.root, encoding='unicode', \
                                         pretty_print=True))
            output.close()
            pickleout = fileout[:-4] + '.pkl'
            pout = open(pickleout, 'wb')
            pickle.dump(self.hashed_graphics, pout, pickle.HIGHEST_PROTOCOL)
            # list projects in Pub2SD and update list in self.ddnCurProject
            self.list_projects = [f.rstrip('.prj') \
                                  for f in os.listdir(self.Pub2SD) \
                                                     if f.endswith('.prj')]
            self.ddnCurProject['values'] = self.list_projects
            self.ddnCurProject.set(new_project)
        else:
            pass

    def _list_different_frames(self, currentFrames, text, tag):
        """list different frames, for tags which support this
                                                      (e.g. COMM, APIC,...)"""

        lang = self.ddnGuiLanguage.get()
        is_different_to_all = list()
        textParams = ast.literal_eval(text)
        #test all frames have same length as text, flag error and return false
        for aFrame in currentFrames:
#            if len(aFrame) > 0:
            if aFrame:
                frameParams = ast.literal_eval(aFrame)
                if len(frameParams) != len(textParams):
                    messagebox.showwarning('', \
                                    LOCALIZED_TEXT[lang]['MissMatchedFrames'])
                    return [False]
                is_diff = [True if HASH_TAG_ON[tag][x] \
                           and frameParams[x] is not textParams[x] \
                                else False for x in range(0, len(textParams))]
                is_different_to_all.extend([(True in is_diff)])
        return is_different_to_all

    def _is_different_hash(self, currentFrames, text, tag):
        """true if 'text' not in 'currentFrames' and tag is hashable"""

        return False \
            if False in self._list_different_frames(currentFrames, text, tag) \
            else True

    def _set_tag_(self, parent):
        """set tag specified in column with value in text, for current
           item or it's dependants"""
        column = self.ddnSelectTag.get().split(':')[0]
        text = self.etrTagValue.get()
        if self.tree.set(parent, 'Type') in ['collection', 'project']:
            children = self.tree.get_children(parent)
            for child in children:
                self._set_tag_(child)
        else: #is file so…
            if self.mode.get() == 0: #is idiot
                self.tree.set(parent, column, text)
            else: #not idiot
                if is_hashable(column):
                    currentTag = self.tree.set(parent, column)
                    currentFrames = str(currentTag).split('|')
                    textFrames = text.split('|')
                    if len(textFrames) > 1: #multiple frames
                        if textFrames is not currentFrames: #so replace them
                            self.tree.set(parent, column, text)
                    else:
                        #text is single frame
                        if self._is_different_hash(currentFrames, text, column):
                            #so append
                            currentFrames.extend([text])
                        else: #replace a frame
                            currentFrames[\
                                    self._list_different_frames(currentFrames, \
                                            text, column).index(False)] = text
                        self.tree.set(parent, column, '|'.join(currentFrames))
                else:
                    self.tree.set(parent, column, text)
            self.tree.see(parent)

    def _set_sort_(self, parent):
        """set one of the sort order tags
                                      'TSOA', 'TSOC', 'TSOP', 'TSOT', 'TSO2'"""
        column = self.ddnSelectTag.get().split(':')[0]
        if self.tree.set(parent, 'Type') in ['collection', 'project']:
            children = self.tree.get_children(parent)
            for child in children:
                self._set_sort_(child)
        else:
            #is file so…
            name = self.tree.set(parent, '#2')
            if self.isHide.get() == 1:
                name = '"' + name + '"'
            else:
                name = DEFAULT_VALUES['ide3v24'][column][0:5] + name + \
                                        DEFAULT_VALUES['ide3v24'][column][5:]
            self.tree.set(parent, column, name)
            self.tree.see(parent)

    def _set_tracks(self, parent, tp0='', tp1='', trest=list()):
        """set tracks"""
        children = self.tree.get_children(parent)
        for child in children:
            if self.tree.set(child, 'Type') in ['collection', 'project']:
                self._set_tracks(child, tp0, tp1, trest)
            else:
#                if len(tp1) > 0:
                if tp1:
                    newtrack = ['{}/{}'.format(self.next_track, tp1),]
                    for nt in trest:
                        newtrack.extend(['{}'.format(nt)])
                    if self.mode.get() == 0:
                        self.tree.set(child, 'TRCK', \
                                      '{}'.format(','.join(newtrack)))
                    else:
                        self.tree.set(child, 'TRCK', \
                                      '[3,["{}"]]'.format(','.join(newtrack)))
                else:
                    newtrack = ['{}'.format(self.next_track),]
                    for nt in trest:
                        newtrack.extend([nt])
                    if self.mode.get() == 0:
                        self.tree.set(child, 'TRCK', \
                                      '{}'.format(','.join(newtrack)))
                    else:
                        self.tree.set(child, 'TRCK', \
                                      '[3,["{}"]]'.format(','.join(newtrack)))
                self.tree.see(child)
                self.next_track += 1

    def _on_get(self, _column=''):
        """get the current tag value of selected row and column
                                         and display in enter tag value box"""

        lang = self.ddnGuiLanguage.get()
        if self.tree.focus() == '':
            messagebox.showinfo('', \
                                LOCALIZED_TEXT[lang]['Please select a row.'])
        elif len(self.ddnSelectTag.get()) < 4:
            messagebox.showinfo('', \
                                LOCALIZED_TEXT[lang]['Please select a tag.'])
        else:
            self.etrTagValue.delete(0, len(self.etrTagValue.get()))
            column = self.ddnSelectTag.get().split(':')[0].upper()
            got_it = self.tree.set(self.tree.focus(), column)
            if self.mode.get() == 0: #idiot
                self.etrTagValue.insert(0, got_it)
            else: #not idiot
                self.etrTagValue.insert(0, got_it \
                                        if got_it != '-' \
                                        else DEFAULT_VALUES['ide3v24'][column])
            if self.mode.get() != 0: #not idiot
                self.lblParameters['text'] = READ_TAG_INFO[column]
        self._rename_children_of(self.project_id)
        self.update()

    def _on_get_default(self, _column=''):
        '''get default value of tag'''

        lang = self.ddnGuiLanguage.get()
        if self.tree.focus() == '':
            messagebox.showinfo('', \
                                LOCALIZED_TEXT[lang]['Please select a row.'])
        elif len(self.ddnSelectTag.get()) < 4:
            messagebox.showinfo('', \
                                LOCALIZED_TEXT[lang]['Please select a tag.'])
        else:
            self.etrTagValue.delete(0, len(self.etrTagValue.get()))
            column = self.ddnSelectTag.get().split(':')[0].upper()
            self.etrTagValue.insert(0, DEFAULT_VALUES['ide3v24'][column])
            self.lblParameters['text'] = READ_TAG_INFO[column]
        self._rename_children_of(self.project_id)
        self.update()


    def _count_files_below(self, focus):
        '''count nos of files below this point'''
        if self.tree.set(focus, 'Type') in ['collection', 'project']:
            children = self.tree.get_children(focus)
            for child in children:
                self._count_files_below(child)
        else:
            #is file so...
            self.nos_tracks += 1

    def _is_track_of_tracks(self, tp, tempstr, focus, text, lang):
        """track specified as 1/10 format so set for this file or all
           dependants of a collection. Where 0/0 count dependants and
           set as n/count."""

        if tp[0].isdecimal and tp[1].isdecimal: #is track / of tracks
            self.next_track = int(tp[0])
            if not self.focus \
                        or self.tree.set(focus, 'Type') \
                        in ['collection', 'project']:
                if self.next_track == 0:
                    self.next_track = 1
                    if tp[1] == '0':
                        self.nos_tracks = 0
                        self._count_files_below(focus)
                        tp[1] = str(self.nos_tracks)
                self._set_tracks(focus, tp[0], tp[1], '' \
                                if self.mode.get() == 0 \
                                else tempstr[1:])
            else: #is file so…
#                if len(tp[1]) > 0:
                if tp[1]:
                    newtrack = ['"{}/{}"'.\
                                format(self.next_track, tp[1]),]
                    for nt in tempstr[1:]:
                        newtrack.extend([nt])
                    self.tree.set(focus, 'TRCK', '[3,[{}]]'.\
                                  format(','.join(newtrack)))
                else:
                    newtrack = ['"{}"'.format(self.next_track),]
                    for nt in tempstr[1:]:
                        newtrack.extend([nt])
                    self.tree.set(focus, 'TRCK', '[3,[{}]]'.\
                                  format(','.join(newtrack)))
                self.next_track += 1
                self.tree.see(focus)
        else: #invalid track or set of
            messagebox.showwarning('', \
                    LOCALIZED_TEXT[lang]['Set'] + ' TRCK, >{}< {}'\
                    .format(text, LOCALIZED_TEXT[lang][\
            "'track in/set_of' doesn't contain a valid integers."]))

    def _on_set_is_url(self, text, focus, column, lang):
        """set one of the WCOM, WCOP, WOAF, WOAR,
                                        WOAS, WORS, WPAY, WPUB internet tags"""

        tempstr = unidecode(text if self.mode.get() == 0 \
                                 else text[1:-1].split(',')[0][1:-1])
        res = urlparse(tempstr)
        if res[0] in ['http', 'https', 'ftp', 'ftps', 'finger', 'news', \
                      'NNTP', 'local'] \
                      and '.' in res[1] and res[2]:
#                      and '.' in res[1] and len(res[2]) > 0:
            if self.tree.set(focus, 'Type') in ['collection', 'project']:
                self._set_tag_(focus)
            else: #is file, so...
                self.tree.set(focus, column, '["{}"]'.format(tempstr))
        else:
            messagebox.showwarning(\
                            LOCALIZED_TEXT[lang]['Set'] + ' ' + column, \
                            LOCALIZED_TEXT[lang]["URL is invalid."])

    def _on_set_trck(self, tempstr, focus, lang, text, column):
        """is TRCK tag so set track no"""
        tp = tempstr[0].split('/')
        if len(tp) > 1:
            self._is_track_of_tracks(tp, tempstr, focus, text, lang)#, column)
        elif tempstr[0].isdecimal: #is track
            self.next_track = 1 if int(tempstr[0]) == 0 \
                                else int(tempstr[0])
            if self.tree.set(focus, 'Type') in ['collection', 'project']:
                self._set_tracks(focus, tempstr[0], '', tempstr[1:])
            elif self.isHide.get() == 1:
                tempstr[0] = '"{}"'.format(self.next_track)
                self.tree.set(focus, column, ','.join(tempstr))
        else: #invalid track
            messagebox.showwarning('', \
              LOCALIZED_TEXT[lang]['Set'] + ' TRCK, >{}< {}'.format(text, \
                LOCALIZED_TEXT[lang]["doesn't contain a valid integer."]))

    def _on_set(self):
        '''set value of tag'''

        lang = self.ddnGuiLanguage.get()
        column = self.ddnSelectTag.get().split(':')[0]
        text = self.etrTagValue.get()
        #test if right nos parameters for this tag
        #- compare length with HAS_TAG_ON
        list_of_items = self.tree.selection()
#        focus = list_of_items[0] if len(list_of_items) > 0 else self.project_id
        focus = list_of_items[0] if list_of_items else self.project_id
        if self.mode.get() != 0:
            for test in text.split('|'):
                if len(HASH_TAG_ON[column]) != len(ast.literal_eval(test)):
                    messagebox.showerror("Invalid number of parameters", \
                                    "In row {}, {} tag=>{}<, {} required.".\
                                    format(self.tree.set(focus, 'Name'),\
                                    column, test, len(HASH_TAG_ON[column])))
                    return
        if column == 'TRCK':
            self._on_set_trck(\
            [t[1:-1] for t in text[4:-2].split(',')] if self.mode.get() != 0 \
                                                     else [text,], \
                                                    focus, lang, text, column)
        elif column in ['WCOM', 'WCOP', 'WOAF', 'WOAR', 'WOAS', 'WORS', \
                                                            'WPAY', 'WPUB']:
            self._on_set_is_url(text, focus, column, lang)
        elif column in ['TSOA', 'TSOC', 'TSOP', 'TSOT', 'TSO2']:
            if self.tree.set(focus, 'Type') in ['collection', 'project']:
                self._set_sort_(focus)
            else: #is file so...
                self._set_tag_(focus)
        elif column == 'TIT2' \
                    and (self.tree.set(focus, 'Type') == 'collection' \
                    or os.path.getsize(self.tree.set(focus, 'Location')) == 0):
            #if 'Advanced' mode need to filter out the [3,[""]] stuff from text!
            if self.mode.get() == 0:
                #idiot mode
                self.tree.set(focus, column, text)
#                print('renaming to {}'.format(text))
            else:
                #advanced mode
                #[3,[""]]
                _start = text.find('[', text.find('[') + 1) + 2
                _end = text.find(']') - 1
                self.tree.set(focus, column, text[_start:_end])
#                print('renaming to {}'.format(text[_start:_end]))
#            self._rename_children_of(self.project_id)
                            
        else:
            self._set_tag_(focus)
        self.tree.focus(focus)
        self.tree.see(focus)

        self._rename_children_of(self.project_id)
        self.status['text'] = ''
        self.progbar['value'] = 0
        self.update()

    def _on_promote(self):
        """promote item one level in the heirachy"""
        focus = self.tree.focus()
        father = self.tree.parent(focus)
#        if len(father) > 0 and father != self.project_id:
        if father and father != self.project_id:
            #not root so promote
            grandfather = self.tree.parent(father)
            index = self.tree.index(father)
            self.tree.detach(focus)
            self.tree.move(focus, grandfather, index)
        self._rename_children_of(self.project_id)
        self.tree.see(focus)

    def _on_demote(self):
        """demote item one level in the heirachy"""
        list_of_items = self.tree.selection()
#        if len(list_of_items) > 0 and self.project_id not in list_of_items:
        if list_of_items and self.project_id not in list_of_items:
            focus = list_of_items[0]
            index = self.tree.index(focus)
            father = self.tree.parent(focus)
            children = self.tree.get_children(father)
            below = children.index(list_of_items[-1])
            #in list below+1 to endof children find first collection
            #  and move list_of_items there else
            #  if no collection create new and move there
            test_these = children[below+1:]
            son = None
            for item in test_these:
                if self.tree.set(item, 'Type') == 'collection':
                    son = item
                    break
            if son is None:
                vout = ['collection', '-', '-']
                vout.extend(['-' for item in self.displayColumns[2:-1]])

                son = self.tree.insert('', index='end', \
                        values=['collection', '-', '-', '-', '-', '-', '-', \
                                '-', '-', '-', '-', '-', '-', '-'], \
                                open=True, text='collection')
            for focus in list_of_items:
                self.tree.detach(focus)
                self.tree.move(focus, son, 'end')
                self.tree.see(focus)
#            if len(father) > 0:
            if father:
                #is not root so make father of son
                self.tree.detach(son)
                self.tree.move(son, father, index)
        self._rename_children_of(self.project_id)

    def _stripping(self, title, to_strip):
        """applys to_strip to title"""

        lang = self.ddnGuiLanguage.get()

        if to_strip == TRIM_TAG[lang]["Nothing"]:
            pass
        elif to_strip == TRIM_TAG[lang]["Leading digits"]:
            title = TRIM_LEADING_DIGITS.sub(r'\1', title)
        elif to_strip == TRIM_TAG[lang]["Trailing digits"]:
            title = TRIM_TRAILING_DIGITS.sub(r'\1', title)
        elif to_strip == TRIM_TAG[lang]["Leading alphanumerics"]:
            prefix = FIND_LEADING_ALPHANUM.findall(title)[0] \
                            if FIND_LEADING_ALPHANUM.findall(title) else ''
#                            if len(FIND_LEADING_ALPHANUM.findall(title)) > 0 \
#                            else ''
#            if len(prefix) > 0:
            if prefix:
                prefix = prefix.split('_')[0]
                title = title[len(prefix):]
        elif title.find(to_strip) == 0:
            title = title[len(to_strip):]

        return get_rid_of_multiple_spaces(title.strip('-_ ‒–—―'))

    def _strip_children_of(self, parent):
        """applys to_strip to children of parent recursively"""

        children = self.tree.get_children(parent)
        to_strip = self.ddnTrimFromTitle.get()
        for child in children:
            #lchars = ''

            if self.tree.set(child, 'Type') == 'file':
                #first force the TIT2 list into standard format
                if self.mode.get() == 0: #idiot
                    self.tree.set(child, 'TIT2', \
                        self._stripping(str(self.tree.set(child, 'TIT2')).strip(), \
                                                                     to_strip))
                else:
                    # encoding not hidden so pull it in directly
                    title = ast.literal_eval(self.tree.set(child, 'TIT2'))
                    titles = title[1]
                    #now for each title in the list...
                    for i in range(0, len(titles)):
                        titles[i] = \
                         self._stripping(titles[i].strip('"').strip(), to_strip)
                    title[1] = titles
                    self.tree.set(child, 'TIT2', str(title))
            else:
                #is collection
                self.tree.set(child, 'TIT2', \
                        self._stripping(self.tree.set(child, 'TIT2').strip(), \
                                                                   to_strip))
                self._strip_children_of(child)
        #self.update()

    def _on_strip_leading_numbers(self):
        """applys to_strip to file or a collections dependants"""

        focus = self.tree.selection()
        if focus == '':
            focus = self.project_id
        to_strip = self.ddnTrimFromTitle.get()
        strtype = self.tree.set(focus, 'Type')
        if len(focus) is 0 or strtype in ['collection', 'project']:
            self._strip_children_of(focus)
        else: #is file so...
            self.tree.set(focus, 'TIT2', \
                         self._stripping(self.tree.set(focus, 'TIT2').strip(), \
                                         to_strip))
        self._rename_children_of(self.project_id)

    def _attach_artwork_to(self, target, _picture_type, _desc, artwork):
        """attaches the artwork to item in focus or to its dependants
                                                             if collection"""
        if self.mode.get() == 0:
            #is idiot so...
            text = artwork
        else:
            #is NOT idiot so...
            text = '[3,"{}",{},"{}","{}"]'.format(\
                'image/png' \
                if artwork[-4:] == '.png' else 'image/jpg', \
                str(_picture_type), _desc, artwork)
        if self.tree.set(target, 'Type') == 'file':
            currentTag = self.tree.set(target, 'APIC')
            if currentTag == '-' or self.mode.get() == 0:
                self.tree.set(target, 'APIC', text)
            else:
                currentFrames = currentTag.split('|')
                if self._is_different_hash(currentFrames, text, 'APIC'):
                    #so append
                    currentFrames.extend([text])
                else:
                    #replace a frame
                    currentFrames[self._list_different_frames(currentFrames, \
                                            text, 'APIC').index(False)] = text
                self.tree.set(target, 'APIC', '|'.join(currentFrames))
        else:
            #is collection, list children of focus and attach artwork to each
            children = self.tree.get_children(target)
            for child in children:
                self._attach_artwork_to(child, _picture_type, _desc, artwork)


    def _on_select_artwork(self):
        '''select the cover art'''

        lang = self.ddnGuiLanguage.get()
        list_of_items = self.tree.selection()
        _picture_type = PICTURE_TYPE[self.ddnPictureType.get()]
        _desc = self.etrDescription.get()
#        if len(list_of_items) > 0:
        if list_of_items:
            fart = filedialog.askopenfilename(\
                        initialdir=os.path.expanduser('~'), \
                          filetypes=[('PNG files', '*.png'), \
                                     ('JPG files', '*.jpg')], \
                          title="Select PNG or JPG file…")
            #now replace windows backslashes with forward slashes
            fart = forward_slash_path(fart)
#            if len(fart) > 0:
            if fart:
                for focus in list_of_items:
                    if self.mode.get() == 0:
                        self._attach_artwork_to(focus, PICTURE_TYPE['COVER_FRONT'], '', fart)
                    else:
                        self._attach_artwork_to(focus, _picture_type, _desc, fart)
                    self.tree.see(focus)
            else:
                #no file selected so blank apic if idiot
                if self.mode.get() == 0:
                    for focus in list_of_items:
                        self.tree.set(list_of_items[0], 'APIC', '-')
        else:
            messagebox.showwarning(LOCALIZED_TEXT[lang]['Select Artwork'], \
                          LOCALIZED_TEXT[lang]["no items selected"])
        self._rename_children_of(self.project_id)
        self.update()

    def _preparing_file_scaning_for_tags_idiot_mode(self, atag, child):
        """preparing file scaning for tags idiot mode"""
        #idiot so just one front cover
        if atag[0:2] in ["b'", 'b"']:
            #is bytes
            apic_params = self.tree.set(child, 'APIC_').split('|')
            para = ast.literal_eval(apic_params[0])
            _encoding = 3
            _mime = para[1]
            _type = para[2]
            _desc = ''
            if para[4] in self.hashed_graphics:
                _data = self.hashed_graphics[para[4]]
            else:
                #error message? Can't find graphic
                #in hashed_graphics so return?
                messagebox.showerror(\
                    "Can't find graphic in hashed_graphics", \
                    "lost saved graphic for {}.".\
                    format(self.tree.item(child)['text']))
        else:
            #is string
            _encoding = 3
            _mime = 'image/png' \
                    if atag[-4:] == '.png' \
                    else 'image/jpg'
            _type = 3
            _desc = ''
            #add check file exists else break!!!!!
            _data = open(os.path.normpath(atag), \
                                     'rb').read()
        return [_encoding, _mime, _type, _desc, _data]

    def _preparing_file_scaning_for_tags_advanced_mode(self, \
                                atag, lang, child, picture_type_1_2, thetags):
        """preparing file scaning for tags advanced mode"""
        #not idiot
        param = ast.literal_eval(atag)
        _encoding = int(param[0])
        _mime = param[1]
        _type = int(param[2])
        if picture_type_1_2:
            if _type in [1, 2]:
                messagebox.showwarning('', \
                        LOCALIZED_TEXT[lang]['MultpleFileIcons'].\
                        format(self.files[child][0]))
#                break
            else:
                picture_type_1_2 = True
        _desc = param[3]
        #if placeholder "b'...'" use saved data else load file
        tindex = thetags.index(atag)
        if param[4][0:2] in ['b"', "b'"]:
            apic_params = self.tree.set(child, 'APIC_').split('|')
            para = ast.literal_eval(\
                            apic_params[tindex])
            if para[4] in self.hashed_graphics:
                _data = \
                self.hashed_graphics[para[4]]
            else:
#                break
                pass
        else:
            _data = open(\
        os.path.normpath(param[4]), 'rb').read()
        return [_encoding, _mime, _type, _desc, _data]

    def _p_f_s_f_t_process_apic(self, child, audio, thetags, lang):
        """add the APIC tag and data to the audio file"""
        picture_type_1_2 = False
        for atag in thetags:
            if atag != '-' and atag != '#':
                # is not empty so add it!
                if self.mode.get() == 0:
                    _encoding, _mime, _type, _desc, _data = \
                        self._preparing_file_scaning_for_tags_idiot_mode(\
                                                    atag, child)
                else:
                    _encoding, _mime, _type, _desc, _data = \
                       self._preparing_file_scaning_for_tags_advanced_mode(\
                            atag, lang, child, picture_type_1_2, thetags)
                audio.add(APIC(_encoding, _mime, _type, \
                               _desc, _data))

    def _preparing_file_scaning_for_tags(self, child, k, audio, thetags, lang):
        """process tag for on_prepare_files"""

        if k == "APIC":
            self._p_f_s_f_t_process_apic(child, audio, thetags, lang)
        else:
            list_owners = list()
            #list_owners is used by exec(PF['ENCR']) and exec(PF['GRID']),
            #these tags may have multiple entries with different owners
            #specified
            for atag in thetags:
                if atag != '-':
                    # is not empty so add it!
#                    if self.mode.get() != 0:
#                        param = ast.literal_eval(atag)
#                        print(k, 3, param[1])
                    # if parameters include byte data do I need
                    # to have explicit command for each? probably!
                    # Hmm, can break into groups like read_mp3_tag
                    #so...
                    if k in AUDIO:
                        atuple = (audio, atag, (self.mode.get() != 0), \
                                  list_owners, lang, self.files[child][0])
                        AUDIO[k](atuple)
#                    if k in TF_TAGS:
#                        exec('audio.add({}(3,"{}"))'.format(k, atag) \
#                                        if self.mode.get() == 0 \
#                                            else 'audio.add({}({}))'.\
#                                                format(k, str(param)[1:-1]))
#                    elif k in ['WCOM', 'WCOP', 'WOAF', 'WOAR', 'WOAS', \
#                               'WORS', 'WPAY', 'WPUB']: #url frame
#                        exec('audio.add({}("{}"))'.format(k, atag) \
#                                        if self.mode.get() == 0 \
#                                                else 'audio.add({}({}))'.\
#                                                        format(k, str(param)))
#                    elif k in PF:
#                        exec(PF[k])
                    else:
                        messagebox.showerror(\
                                             'Error in on_prepare_files()', \
                                             '>{}< is unrecognized tag'.\
                                             format(k))


    def _on_prepare_files(self):
        '''prepare files in temp folder'''

        lang = self.ddnGuiLanguage.get()
        self.project = self.ddnCurProject.get()

        self.progbar['maximum'] = len(self.files)
        self.progbar['value'] = 0
        #copy all file to Temp workarea
        self.status['text'] = LOCALIZED_TEXT[lang]['Copying all source ' +\
                                            'files to a working directory...']
        self.update()
        for child in sorted(self.files.keys()):
            self.status['text'] = self.files[child][1]
            self.update()
            #   copy            from                  to
            shutil.copyfile(self.files[child][1], self.files[child][0])
            if int(os.path.getsize(self.files[child][1])) > 0:
                #load mp3 tags
                audio = ID3(self.files[child][0])#, ID3=ID3)
                #read tags into tree - read when file first selected

                try:
                    audio.delete()
                    audio.save()
                except:
                    messagebox.showerror(LOCALIZED_TEXT[lang]['No ID3 tag'], \
        "{} <{}>, {}".format(LOCALIZED_TEXT[lang]['No ID3 tags found in'], \
                        self.files[child][0], \
                        LOCALIZED_TEXT[lang]["so it's not a valid MP3 file."]))
                    return
                audio.update_to_v23()
                for k in self.displayColumns[2:-1]:
                    #typically of form '[3,[""]]'
                    thetags = self.tree.set(child, k).split('|')
                    self._preparing_file_scaning_for_tags(child, k, audio, thetags, lang)
                #now save back to file
                audio.save(self.files[child][0], v1=0, v2_version=3)
                #now discover length
                audio_len = MP3(self.files[child][0])
                self.files[child][4] = int(audio_len.info.length +0.5)
            self.progbar.step()
            self.update()
        self.progbar['value'] = 0
        self.status['text'] = ''
        self.update()

        #move on to playlists
        self.n.add(self.f2)
        #self.n.hide(self.f1)
        self.n.select(2)

    def _on_publish_to_SD(self):
        """publish files and playlists to SDs"""

        lang = self.ddnGuiLanguage.get()
        threads = []
        self.progbar['maximum'] = len(self.files)*4*len(self.output_to)
        self.progbar['value'] = 0

        i = 1
        currentThreadsActive = threading.activeCount()
        self.progbar['value'] = 0
        self.progbar.start()
        for atarget in self.output_to:
#            if len(atarget) > 0:
            if atarget:
                if os.path.exists(atarget):
                    target = atarget
                    threads.append(MyThread(target, \
                                            self.ddnGuiLanguage.get(), \
                                            self.Pub2SD, self.project, \
                                            self.play_list_targets, \
                                            self.is_copy_playlists_to_top.get(), \
                                                                self.files))
                    i += 1
                    threads[-1].start()
                    self.status['text'] = \
                               LOCALIZED_TEXT[lang]['{} Threads active'].\
                           format(threading.activeCount()-currentThreadsActive)
                    self.update()
                else:
                    messagebox.showerror(\
                                        LOCALIZED_TEXT[lang]["Invalid path"], \
                                        LOCALIZED_TEXT[lang]["Can't find {}"].\
                                                      format(atarget))

        while threading.activeCount() > currentThreadsActive:
            self.status['text'] = LOCALIZED_TEXT[lang]['{} Threads active'].\
                       format(threading.activeCount()-currentThreadsActive)
            self.update()
        self.progbar.stop()
        [athread.join() for athread in threads]

        self.progbar['value'] = 0
        self.status['text'] = \
                   LOCALIZED_TEXT[lang]["Output to SD('s) completed."]
        self.update()

    def _on_publish_to_HD(self):
        """publish files and playlists to your HD"""

        lang = self.ddnGuiLanguage.get()
        target = os.path.normpath(self.Pub2SD + '/' + \
                                  self.ddnCurProject.get() + '_SD')
        self.progbar['maximum'] = len(self.files)*4
        self.progbar['value'] = 0
        self.status['text'] = \
                   LOCALIZED_TEXT[lang]["Output to HD in progress..."]
        self.update()
        self._on_publish_files(target)
        self.status['text'] = LOCALIZED_TEXT[lang]["Output to HD completed."]
        self.update()

    def _on_publish_files(self, target):
        """copy files to final destination,
        opening all files,
        copying all files
        then closing all files.
        To ensure same creation date and last modified date for all files.
        So that they will only sort in the order specified."""

        #finally copy all file to final destination):
        lang = self.ddnGuiLanguage.get()
        self.status['text'] = \
                   LOCALIZED_TEXT[lang]['Removing any old project files...']
        self.update()
        if target[1:] != ':\\' and \
                 os.path.exists(os.path.normpath(target + '/' + self.project)):
            # remove if exists
            shutil.rmtree(os.path.normpath(target + '/' + self.project))

        tp = os.path.normpath(target + '/' + self.project)
        os.makedirs(tp, mode=0o777, exist_ok=True)
        target += '/'
        target = forward_slash_path(target)
        #decide if space avaialable on target - abort if not with error message
        self.status['text'] = \
                   LOCALIZED_TEXT[lang]['Calculating needed space...']
        self.update()
        _, _, free = shutil.disk_usage(os.path.normpath(target))
        needed = folder_size(\
                    os.path.normpath(self.Pub2SD + '/Temp/'+self. project)) / \
                             (1024.0 * 1024.0)
        free = free / (1024.0 * 1024.0)
        if needed > free:
            messagebox.showerror(\
                LOCALIZED_TEXT[lang]["Insufficent space on target!"], \
                LOCALIZED_TEXT[lang]["Needed {}Mb, but only {}Mb available"].\
                              format(needed, free))
            return
        #os.makedirs(tp, mode=0o777, exist_ok=True)
        self.status['text'] = \
                   LOCALIZED_TEXT[lang]['Making project directories...']
        self.update()
        #now open all files at once to make create dates the same
        fileId = {}
        listpaths = []
        for child in self.files:
            final_path = os.path.normpath(target + \
                                '/'.join(self.files[child][3].split('/')[:-1]))
            if final_path not in listpaths:
                os.makedirs(final_path, mode=0o777, exist_ok=True)
                listpaths.extend([final_path])
            #self.status['text'] = final_path
            self.progbar.step()
            self.update()
        self.status['text'] = LOCALIZED_TEXT[lang]['Opening target files...']
        self.update()
        for child in self.files:
            fileId[child] = open(target + self.files[child][3], mode='wb')
            self.progbar.step()
            self.update()
        self.status['text'] = \
                   LOCALIZED_TEXT[lang]['Copying to target files...']
        self.update()
        for child in self.files:
            filein = open(self.files[child][0], mode='rb')
            fileId[child].write(filein.read())
            filein.close()
            self.progbar.step()
            self.update()
        self.status['text'] = LOCALIZED_TEXT[lang]['Closing target files...']
        self.update()
        for child in self.files:
            fileId[child].close()
            self.progbar.step()
            self.update()
        self._on_copy_playlists(target)

    def _on_copy_playlists(self, target):
        """copy playlists to target, at locatons specified in
                                                         play_list_targets"""
        source = os.path.normpath(self.Pub2SD + '/Temp/'+ self.project + '/')
        playlists = [p for p in os.listdir(source) \
                     if p.endswith('.M3U8') or p.endswith('M3U')]
        #main playlists
        for pp in playlists:
            shutil.copyfile(os.path.normpath(source + '/' + pp), \
                            os.path.normpath(target + self.project + '/' + pp))
            self.progbar.step()
            self.update()
        #now top level?
        if self.is_copy_playlists_to_top.get() == 1:
            for pp in playlists:
                encode = 'utf-8' if pp.endswith('.M3U8') else 'cp1252'
                fin = codecs.open(os.path.normpath(source + '/'+ pp),\
                                          mode='r', encoding=encode)
                fout = codecs.open(os.path.normpath(target + pp), mode='w', \
                                   encoding=encode)

                fout.write(fin.read().replace('../', './'))
                fin.close()
                fout.close()
                self.progbar.step()
                self.update()
        #now in list
        for tt in self.play_list_targets:
#            if len(tt) > 0:
            if tt:
                os.makedirs(target + tt, mode=0o777, exist_ok=True)
                for pp in playlists:
                    shutil.copyfile(os.path.normpath(source + '/' + pp), \
                                    os.path.normpath(target + tt + '/' + pp))
                    self.progbar.step()
                    self.update()

    def _make_filename(self, child):
        """make mp3 title = filename after appropriate normalization"""
        title = str(self.tree.set(child, 'TIT2'))
        title = self._my_unidecode(title) \
                        if self.mode.get() == 0 \
                        else self._my_unidecode(title[5:-2].split(',')[0][1:-1])
        return ''.join([c if self._approved_char(c) else '_' for c in title])

    def _childrens_filenames(self, parent, temp_path, project_path_):
        '''form childrens file names'''
        children = self.tree.get_children(parent)
        for child in children:
            new_dir = self.tree.item(child)['text']

            if self.tree.set(child, 'Type') == 'collection':
                thispath = os.path.normpath(temp_path + '/' + new_dir)
                final_path = os.path.normpath(project_path_ + '/' + new_dir)
                os.makedirs(thispath, mode=0o777, exist_ok=True)
                self._childrens_filenames(child, thispath, final_path)
            else: #is file
                title = self.tree.item(child)['text'].strip()
                thispath = temp_path + '/' + title + '.mp3'
                thatpath = project_path_ + '/' + title + '.mp3'
                if 'APIC' in self.displayColumns:
                    #                   temp path,
                    #                   source path,
                    #                   Apic,
                    #                   target, ?,
                    #                   title
                    self.files[child] = [thispath, \
                                          self.tree.set(child, 'Location'), \
                                          self.tree.set(child, 'APIC'), \
                                          thatpath, '', \
                                          self.tree.set(child, 'TIT2')]
                else:
                    self.files[child] = [thispath, \
                                          self.tree.set(child, 'Location'), \
                                          '', self._my_unidecode(thatpath), \
                                          '', self.tree.set(child, 'TIT2')]
                self.status['text'] = thispath
                #now step update progessbar
                self.progbar.step()
                self.update()

    def _count_nodes(self, parent):
        '''count nodes'''
        for child in self.tree.get_children(parent):
            self.nodes += 1
            if self.tree.set(child, 'Type') == 'collection':
                self._count_nodes(child)

    def _on_generate_playlists(self):
        '''generate the playlists'''

        # this is where all labels changed modify for new prog
        # - just kept as example
        lang = self.ddnGuiLanguage.get()
        self.nodes = 0
        self._count_nodes('')
        self.progbar['maximum'] = self.nodes
        self.progbar['value'] = 0
        self.status['text'] = LOCALIZED_TEXT[lang]['Creating playlists...']
        self.progbar['value'] = 0
        self.update()
        #list_children split list into file_children and coll_children
        # for each coll child
        project_path_ = '../{}/'.format(self.project)
        project_file_list = list()
        self._create_play_list(self.project_id, project_path_, \
                                                          project_file_list)
        self.status['text'] = ''
        self.progbar['value'] = 0
        self.update()

    def _create_play_list(self, pid, ploc, glist):
        """create play list
                 pid = collection node in tree
                ploc = path to collection
               glist = ancestors list/index to plists
               plistid index to plists which holds all play lists in
                              form [[name, [list/set of targetfilepaths]],]"""
        this_list = list() #list for this pid
        self.progbar.step()

        for child in self.tree.get_children(pid):
            if self.tree.set(child, 'Type') in ['collection', 'project']:
                cloc = ploc + self.tree.item(child)['text'] + '/'
                self._create_play_list(child, cloc, this_list)
            else:
                #is file so...
                this_list.append([os.path.normpath(self.files[child][3]), \
                                                self.tree.set(child, 'TIT2'), \
                                                self.tree.set(child, 'TALB'), \
                                                str(self.files[child][4])])
        #found all of my children so copy this list upto glist
        glist.extend(this_list)
        #now make playlist for this collection
        playlist = ['#EXTM3U',]
        #write out to self.Pub2SD +/Temp/+ self.project/ collection name
        if self.M3UorM3U8.get() == 2:
            #is utf-8
            for item in this_list:#   secs,alb,title,location
                playlist.append('#EXTINF:{},{}-{}\r\n../{}'.\
                                format(item[3], item[2], item[1], \
                                       forward_slash_path(item[0])))
            filepath = os.path.normpath('{}/Temp/{}/{}.M3U8'.\
                                        format(self.Pub2SD, self.project, \
                                               self.tree.item(pid)['text']))
            fileout = codecs.open(filepath, mode='w', encoding='utf-8')
            fileout.write('\r\n'.join(playlist))
            fileout.close()
        elif self.M3UorM3U8.get() == 1:
            #is legacy
            for item in this_list:
                playlist.append('#EXTINF:{},{}-{}\r\n../{}'.\
                                format(item[3], self._my_unidecode(item[2]), \
                                       self._my_unidecode(item[1]), \
                                                forward_slash_path(item[0])))
            filepath = os.path.normpath('{}/Temp/{}/{}.M3U'.\
                                        format(self.Pub2SD, self.project, \
                                               self.tree.item(pid)['text']))
            fileout = codecs.open(filepath, mode='w', encoding='cp1252')
            fileout.write('\r\n'.join(playlist))
            fileout.close()
        else:
            #is both
            utf8list = ['#EXTM3U',]
            playlist = ['#EXTM3U',]
            for item in this_list:#   secs,alb,title,location
                utf8list.append('#EXTINF:{},{}-{}\r\n../{}'.\
                                format(item[3], item[2], item[1], \
                                       forward_slash_path(item[0])))
                playlist.append('#EXTINF:{},{}-{}\r\n../{}'.\
                                format(item[3], self._my_unidecode(item[2]), \
                                       self._my_unidecode(item[1]), \
                                                forward_slash_path(item[0])))
            #utf-8
            fileputf = os.path.normpath('{}/Temp/{}/{}.M3U8'.\
                                        format(self.Pub2SD, self.project, \
                                               self.tree.item(pid)['text']))
            fileutf = codecs.open(fileputf, mode='w', encoding='utf-8')
            fileutf.write('\r\n'.join(utf8list))
            fileutf.close()
            #legacy
            filepath = os.path.normpath('{}/Temp/{}/{}.M3U'.\
                                        format(self.Pub2SD, self.project, \
                                               self.tree.item(pid)['text']))
            fileout = codecs.open(filepath, mode='w', encoding='cp1252')
            fileout.write('\r\n'.join(playlist))
            fileout.close()

    def _change_lang_1(self, lang):
        '''change lang of labels to interfacelang'''

        self.menubar.entryconfig(0, label=LOCALIZED_TEXT[lang]['File'])
        self.menubar.entryconfig(1, label=LOCALIZED_TEXT[lang]['Help'])

        self.filemenu.entryconfig(0, \
                        label=LOCALIZED_TEXT[lang]['Load project settings'])
        self.filemenu.entryconfig(1, label=LOCALIZED_TEXT[lang]['Save'])
        self.filemenu.entryconfig(2, \
                        label=LOCALIZED_TEXT[lang]['Delete project settings'])
        self.filemenu.entryconfig(4, label=LOCALIZED_TEXT[lang]['Exit'])

        self.helpmenu.entryconfig(0, label=LOCALIZED_TEXT[lang]['Read Me'])
        self.helpmenu.entryconfig(1, label=LOCALIZED_TEXT[lang]['About...'])

        self.lblGuiLanguage['text'] = \
                           LOCALIZED_TEXT[lang]['Interface language>']
        self.lblProject['text'] = LOCALIZED_TEXT[lang]['Current Project>'] + \
                                               ' ' + self.ddnCurProject.get()
        self.lblMode['text'] = '{}{}'.format(LOCALIZED_TEXT[lang]['Mode>'], \
                    LOCALIZED_TEXT[lang]['Simple' if self.mode.get() == 0 \
                                                  else 'Advanced'])

        self.lblCurTemplate_ttp['text'] = \
                               LOCALIZED_TEXT[lang]['CurTemplate_ttp']
        self.lblCurTemplate['text'] = LOCALIZED_TEXT[lang]['UseTemplate>']
        self.btnCreateTemplate['text'] = LOCALIZED_TEXT[lang]["CreateTemplate"]

        self.btnSavePref['text'] = LOCALIZED_TEXT[lang]["SavePref"]

        self.boxOptional['text'] = LOCALIZED_TEXT[lang]["Optional"]
        self.lblInitialDigit['text'] = LOCALIZED_TEXT[lang]['InitialDigit']

        self.lblIdiot['text'] = LOCALIZED_TEXT[lang]['IdiotMode']
        self.rdbIdiot['text'] = LOCALIZED_TEXT[lang]['Simple']
        self.rdbAdvanced['text'] = LOCALIZED_TEXT[lang]['Advanced']
        self.f0_ttp['text'] = LOCALIZED_TEXT[lang]['f0_ttp']

        self.lblLatin1['text'] = LOCALIZED_TEXT[lang]["AddLatin1Example"]
        self.btnF2Next['text'] = LOCALIZED_TEXT[lang]["Next"]

        self.lblM0['text'] = LOCALIZED_TEXT[lang]['M0_ttp']
        self.lblM2['text'] = \
                  LOCALIZED_TEXT[lang]['M2_ttp1' if self.mode.get() == 1 \
                                                 else 'M2_ttp']
        self.lblArt['text'] = LOCALIZED_TEXT[lang]["Art_ttp"]
        self.lblCurProject['text'] = LOCALIZED_TEXT[lang]['Current Project>']
        self.btnBuildOutputTo['text'] = LOCALIZED_TEXT[lang]['Output to>']
        self.lblTrimTitle['text'] = LOCALIZED_TEXT[lang]['TrimTitle_ttp']
        self.box0['text'] = LOCALIZED_TEXT[lang]["and/or"]
        self.box1['text'] = LOCALIZED_TEXT[lang]['Adjust order of files']
        self.box2['text'] = LOCALIZED_TEXT[lang]['As needed']
        self.box1M1['text'] = LOCALIZED_TEXT[lang]['Change indent']
        self.box2M1['text'] = LOCALIZED_TEXT[lang]['Change order']
        self.labelf1['text'] = LOCALIZED_TEXT[lang]['labelf1']

    def _change_lang_2(self, lang):
        '''change lang of labels to interfacelang'''

        self.lblPlayLists['text'] = LOCALIZED_TEXT[lang]["PlayListsIntro"]
        self.chkCopyPlayListsToTop['text'] = \
                                  LOCALIZED_TEXT[lang]["CopyPlayListsToTop"]
        self.boxM3U['text'] = \
           LOCALIZED_TEXT[lang]['Create playlists using Legacy/UTF-8 encoding']
        self.rdbBoth['text'] = LOCALIZED_TEXT[lang]["Both"]

        self.lblEnterList['text'] = LOCALIZED_TEXT[lang]["EnterList"]
        self.lblOutputIntro['text'] = LOCALIZED_TEXT[lang]["OutputIntro"]
        self.lblOutputSizeText['text'] = LOCALIZED_TEXT[lang]["OutputSizeText"]
        self.btnDelProject['text'] = LOCALIZED_TEXT[lang]['Delete Project']
        self.btnDelProject_ttp.text = \
                                LOCALIZED_TEXT[lang]['Delete Project_ttp']
        self.btnRefreshDrives['text'] = LOCALIZED_TEXT[lang]['Refresh']
        self.btnRefreshDrives_ttp.text = LOCALIZED_TEXT[lang]['Refresh_ttp']
        self.btnF0Next['text'] = LOCALIZED_TEXT[lang]['Next']
        self.btnF0Next_ttp.text = LOCALIZED_TEXT[lang]['F0Next_ttp']
        self.btnDefaultTags['text'] = LOCALIZED_TEXT[lang]["Set default tags"]
        self.btnF1Next['text'] = LOCALIZED_TEXT[lang]['Next']

        self.labelf2['text'] = LOCALIZED_TEXT[lang]['labelf2']
        self.lblPreferred['text'] = LOCALIZED_TEXT[lang]['lblPreferred']
        self.rdbDefault['text'] = LOCALIZED_TEXT[lang]['Default']
        self.rdbPreferred['text'] = LOCALIZED_TEXT[lang]['Preferred']

        self.btnF3M0Next['text'] = LOCALIZED_TEXT[lang]['Next']
        self.btnF3M1Next['text'] = LOCALIZED_TEXT[lang]['Next']
        self.btnF3M2Next['text'] = LOCALIZED_TEXT[lang]['Next']
        self.btnF3M2Next_ttp.text = LOCALIZED_TEXT[lang]['btnF3M2Next_ttp']
        self.btnF4Next['text'] = LOCALIZED_TEXT[lang]['Prepare Files']
        self.btnF4Next_ttp.text = LOCALIZED_TEXT[lang]['F0Next_ttp']

        self.btnAddCollection['text'] = LOCALIZED_TEXT[lang]['Add Collection']
        self.btnAddCollection_ttp.text = \
                                    LOCALIZED_TEXT[lang]['AddCollection_ttp']
        self.btnAddFiles['text'] = LOCALIZED_TEXT[lang]['Add Files']
        self.btnAddFiles_ttp.text = LOCALIZED_TEXT[lang]['AddFiles_ttp']
        self.btnPromote_ttp.text = LOCALIZED_TEXT[lang]['Promote_ttp']
        self.btnDemote_ttp.text = LOCALIZED_TEXT[lang]['Demote_ttp']
        self.btnMoveUp_ttp.text = LOCALIZED_TEXT[lang]['MoveUp_ttp']
        self.btnMoveDown_ttp.text = LOCALIZED_TEXT[lang]['MoveDown_ttp']
        self.btnDeleteItem['text'] = LOCALIZED_TEXT[lang]['Delete Item']
        self.btnDeleteItem_ttp.text = LOCALIZED_TEXT[lang]['Delete_ttp']
        self.btnSaveProject['text'] = LOCALIZED_TEXT[lang]['Save']
        self.btnSaveProject_ttp.text = LOCALIZED_TEXT[lang]['Save_ttp']
        self.btnSelectArtwork['text'] = LOCALIZED_TEXT[lang]['Select Artwork']
        self.btnImportHierarchy['text'] = \
                        LOCALIZED_TEXT[lang]["Add Folder and it's Contents"]
        self.btnImportHierarchy_ttp.text = \
                                        LOCALIZED_TEXT[lang]['AddFolder_ttp']
        self.btnImportContents['text'] = \
                             LOCALIZED_TEXT[lang]["Add the Contents of Folder"]
        self.btnImportContents_ttp.text = \
                                        LOCALIZED_TEXT[lang]['AddContents_ttp']
        self.etrTagValue_ttp.text = LOCALIZED_TEXT[lang]['entry1_ttp']
        self.ddnSelectTag_ttp.text = LOCALIZED_TEXT[lang]['ddnSelectTag_ttp']
        self.btnGet['text'] = LOCALIZED_TEXT[lang]["Get"]
        self.btnSet['text'] = LOCALIZED_TEXT[lang]['Set']
        self.btnSet_ttp.text = LOCALIZED_TEXT[lang]['Set_ttp']
        self.btnGetDefault['text'] = LOCALIZED_TEXT[lang]['Get default']

    def _change_lang_3(self, lang):
        '''change lang of labels to interfacelang'''

        self.btnTrimTitle['text'] = LOCALIZED_TEXT[lang]['Trim Title']
        self.btnPub2SD['text'] = LOCALIZED_TEXT[lang]["Publish to SD/USB"]
        project = self.ddnCurProject.get()
        self.btnPub2HD['text'] = \
            LOCALIZED_TEXT[lang]["Publish to '~\\Pub2SD\\{}_SD'"].\
                          format(project if project else "<project>")
#                          format(project if len(project) > 0 else "<project>")
        self.n.tab(self.f0, text=LOCALIZED_TEXT[lang]['Project name'])
        self.n.tab(self.f1, \
                   text=LOCALIZED_TEXT[lang]['Commonly used MP3 tags'])
        self.n.tab(self.f2, text=LOCALIZED_TEXT[lang]['Special characters'])
        self.n.tab(self.f3, \
                   text=LOCALIZED_TEXT[lang]['Edit Hierachy and MP3 tags'])
        self.n.tab(self.f4, text=LOCALIZED_TEXT[lang]['Feature-phone options'])
        self.n.tab(self.f5, text=LOCALIZED_TEXT[lang]['Output to…'])
        self.n.tab(self.f6, text=LOCALIZED_TEXT[lang]['Lock SD card'])
        self.m.tab(self.m0, text=LOCALIZED_TEXT[lang]['Import hierarchy'])
        self.m.tab(self.m1, text=LOCALIZED_TEXT[lang]['Edit hierarchy'])
        self.m.tab(self.m2, text=LOCALIZED_TEXT[lang]['Edit MP3 tags'])
        self.boxlf5list['text'] = LOCALIZED_TEXT[lang]['Available']
        self.box1f5['text'] = LOCALIZED_TEXT[lang]['Or']

        if self.Treed:
            self.tree.heading('#0', text=LOCALIZED_TEXT[lang]['#0'])
            self.tree.heading('#1', text=LOCALIZED_TEXT[lang]['Type'])
            for item in self.displayColumns[1:-1]:
                sometext = item if self.mode.get() != 0 \
                                else SET_TAGS[lang][item]
                self.tree.heading(item, text=sometext)

        set_taga = [TRIM_TAG[lang]['Nothing'], \
                    TRIM_TAG[lang]['Leading digits'], \
                            TRIM_TAG[lang]['Leading alphanumerics'], \
                                    TRIM_TAG[lang]['Trailing digits']]

        self.ddnTrimFromTitle['values'] = set_taga
        self.ddnTrimFromTitle.set(set_taga[0])
        self.ddnTrimFromTitle_ttp.text = LOCALIZED_TEXT[lang]['dropdown5_ttp']

    def _change_lang(self, dummy=''):
        '''change lang of labels to interfacelang'''

        lang = self.ddnGuiLanguage.get()

        self._change_lang_1(lang)
        self._change_lang_2(lang)
        self._change_lang_3(lang)

        self.update()

    def _approved_char(self, achar):
        """is approved character"""
        return True if achar.isalnum() or achar in self.pref_char else False

    def _my_unidecode(self, text):
        """normalize strings to avoid unicode character which won't display
           correctly or whose use in filenames may crash filesystem"""
        l = list()
        #print(self.pref)
        if self.preferred.get() != 1:
            self.pref = list()
        #fix eng/Eng 'bug' in unidecode
#        if ['ŋ', 'ng', re.compile('ŋ')] not in self.pref:
        if 'ŋ' not in [v[0] for v in self.pref]:
            self.pref.append(['ŋ', 'ng', re.compile('ŋ')])
#        if ['Ŋ', 'Ng', re.compile('Ŋ')] not in self.pref:
        if 'Ŋ' not in [v[0] for v in self.pref]:
            self.pref.append(['Ŋ', 'Ng', re.compile('Ŋ')])
 #        if self.preferred.get() == 1:
#            #scan list of preffered character/string pairs
#            for kv in self.pref:# in range(0,len(text)):
#                #build list of all hits in text
#                l.extend([[m.start(), len(kv[0]), kv[1]] \
#                           for m in kv[2].finditer(text)])
        #scan list of preffered character/string pairs
        for kv in self.pref:# in range(0,len(text)):
            #build list of all hits in text
            l.extend([[m.start(), len(kv[0]), kv[1]] \
                       for m in kv[2].finditer(text)])
#        if len(l) > 0:
        if l:
            #now sort list of hits into sequence order
            l = sorted(l, key=lambda student: student[0])
            result = ''
            s = 0
            for ll in l:
                #from end of last match to start of new match + new match aggress
                result += ''.join([c if c.isalnum() or \
                                        c in self.pref_char else '_' \
                                    for c in unidecode(text[s:ll[0]])]) + ll[2]
                #start of match + len of match
                s = ll[0] + ll[1]
            if s < len(text):
                #from end of last match to end of string aggress
                result += ''.join([c if c.isalnum() or \
                                        c in self.pref_char else '_' \
                                        for c in unidecode(text[s:])])
            return result
        else:
            return ''.join([c if c.isalnum() or c in self.pref_char else '_' \
                            for c in unidecode(text)])

def sort_key_for_filenames(filename):
    """build the sort key for imported file names, attempting to guess
       which order is implied by various numbering schemes
       (e.g. chapter numbers without leading zeros, etc...)"""
    #print(filename)
    if filename[0].isdigit():
        #starts with digit
        digits = FIND_LEADING_DIGITS.findall(filename)[0]
        postfix = FIND_TRAILING_DIGITS.findall(filename)[0] \
                        if FIND_TRAILING_DIGITS.findall(filename) else ''
#                             if len(FIND_TRAILING_DIGITS.findall(filename)) \
#                                  else ''
        name = filename[len(digits):len(postfix)] \
                        if postfix else filename[len(digits):]
#                            if len(postfix) > 0 else filename[len(digits):]
        #print('\t>{}<,>{}<,>{}<'.format(digits, name, postfix))
#            if len(postfix) == 0:
        if not postfix:
            lf = "{:05d}{}".format(int(digits), name)
        else:
            lf = "{:05d}{}{:05d}".format(int(digits), name, int(postfix))
    elif filename[0].isalpha():
        word = FIND_LEADING_ALPHANUM.findall(filename)[0] \
                    if FIND_LEADING_ALPHANUM.findall(filename) else ''
#                        if len(FIND_LEADING_ALPHANUM.findall(filename)) > 0 \
#                        else ''
        word = word.split('_')[0]
        #grab trailing digits in word[0]
        digits = FIND_TRAILING_DIGITS.findall(word)[0] \
                        if FIND_TRAILING_DIGITS.findall(word) else ''
#                            if len(FIND_TRAILING_DIGITS.findall(word)) > 0 \
#                            else ''
#            prefix = word[:-len(digits)] if len(digits) > 0 else word
        prefix = word[:-len(digits)] if digits else word
        postfix = FIND_TRAILING_DIGITS.findall(filename)[0] \
                    if FIND_TRAILING_DIGITS.findall(filename) else ''
#                        if len(FIND_TRAILING_DIGITS.findall(filename)) > 0 \
#                        else ''
#            name = filename[len(word):-len(postfix)] if len(postfix) > 0 \
        name = filename[len(word):-len(postfix)] if postfix \
                                               else filename[len(word):]
#            if len(digits) > 0:
        if digits:
            lf = "{}{:05d}{}{:05d}".format(prefix, int(digits), name, \
                                                          int(postfix)) \
                      if postfix \
                        else "{}{:05d}{}".format(prefix, int(digits), name)
#                          if len(postfix) > 0 \
#                            else "{}{:05d}{}".format(prefix, int(digits), name)
        else:
            lf = "{}{}{:05d}".format(prefix, name, int(postfix)) \
                  if postfix else "{}{}".format(prefix, name)
#                      if len(postfix) > 0 else "{}{}".format(prefix, name)
    else:
        #only get here if filename starts with non alphanum '_' etc...
        lf = filename
    return lf

def downgrade_data(the_values, item):
    """reduce all idiot tags to core data,
    (e.g. on a text frame, [3, ['astring', ]] becomes 'a string')
                                             chucking all advanced tabs"""
    if the_values[0] not in ['collection', 'project']:
        #is file so process
        this_frame = the_values[-1].split('|')[0]
        if this_frame != '-':
            if item in IDIOT_TAGS or item == 'APIC_':
                if item == 'APIC_':
                    param = this_frame[1:-1].split(', ')
                    param[0] = int(param[0])
                    param[1] = param[1][1:-1]
                    param[2] = int(param[2][param[2].\
                                               find(':')+1:-1].strip()) \
                                        if '<PictureType.' in param[2] \
                                        else int(param[2].strip())
                    param[3] = param[3][1:-1]
                    param[4] = ast.literal_eval(param[4])
                else:
                    param = ast.literal_eval(this_frame)
                if item == 'APIC':
                    this_frame = param[-1]
                elif item in TF_TAGS or item == 'COMM':
                    this_frame = param[-1][0]
                elif item in ['WCOM', 'WCOP', 'WOAF', 'WOAR', 'WOAS', \
                              'WORS', 'WPAY', 'WPUB', 'WXXX']:
                    this_frame = param[-1]
        the_values[-1] = this_frame
    return the_values

def on_copyright():
    """displays the copyright info when called from menubar"""
    messagebox.showinfo(\
                            "Pub2SDwizard v{}".format(THIS_VERSION), \
                            "©2016-2017 SIL International\n" + \
                            "License: MIT license\n" + \
                            "Web: https://www.silsenelgal.org\n" + \
                            "Email: Academic_Computing_SEB@sil.org\n\n" + \
                            "Powered by: mutagen\n" + \
                            "(https://mutagen.readthedocs.io/)")

def is_hashable(tag):
    '''return true if tag hashable'''

    return True if True in HASH_TAG_ON[tag] else False

def get_rid_of_multiple_spaces(tin):
    '''replace multiple spaces with single space and strip leading and
    trailing spaces'''
    tout = tin.split(' ')
    while '' in tout:
        tout.remove('')
    return ' '.join(tout)

def de_hex(tin):
    '''turn hex string to int and return string'''
    t = tin
    tout = ''
    i = 0
    while i < len(tin):
        if (len(tin) - i) > 5 and is_hex(tin[i: i + 6]):
            tout += chr(int(t[i:i + 6], 16))
            i += 6
        else:
            tout += tin[i]
            i += 1
    return tout

def is_hex(s):
    '''return true if string is hex value'''
    try:
        int(s, 16)
        return True
    except ValueError:
        return False

def to_alpha(anumber):
    """Convert a positive number n to its digit representation in base 26."""
    output = ''
    if anumber == 0:
        pass
    else:
        while anumber > 0:
            anumber = anumber - 1
            output += chr(anumber % 26 + ord('A'))
            anumber = anumber // 26
    return output[::-1]

def empty_the_dir(top):
    '''remove files and folders from the bottom of the tree upwards'''
    for root, dirs, files, rootfd in os.fwalk(top, topdown=False):
        [os.remove(name, dir_fd=rootfd) for name in files]
        [os.rmdir(name, dir_fd=rootfd) for name in dirs]

def delete_folder(path):
    '''if folder exists remove it'''
    if os.path.exists(path):
        # remove if exists
        shutil.rmtree(path)

def folder_size(top):
    '''return size used by folder in bytes'''
    this_folder_size = 0
    for (path, dirs, files) in os.walk(top):
        for file in files:
            filename = os.path.join(path, file)
            this_folder_size += os.path.getsize(filename)
    return this_folder_size

def forward_slash_path(apath):
    '''replace all backslashes with forward slash'''
    return '/'.join(apath.split('\\'))

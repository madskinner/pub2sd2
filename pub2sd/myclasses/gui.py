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
#from urllib.parse import urlparse
import json
import re
from tkinter import font, Tk, filedialog, messagebox, StringVar, \
                    IntVar, NO, Text, FALSE, Menu, PhotoImage
from tkinter.ttk import Button, Checkbutton, Entry, Frame, Label, LabelFrame, \
                        Radiobutton, Scrollbar, Combobox, Notebook, \
                        Progressbar, Treeview, Style

from pathlib import Path

import ast
#import queue
import psutil
from PIL import Image, ImageTk
from lxml import etree
from unidecode import unidecode
from mutagen.mp3 import MP3


from .closeableQueue import CloseableQueue as CQ
from .closeableQueue import CloseablePriorityQueue as CPQ

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

#class PQueue(queue.PriorityQueue):
class PQueue(CPQ):
    '''A custom queue subclass that provides a :meth:`clear` method.'''

    def clear(self):
        ''' Clears all items from the queue.'''

        with self.mutex:
            unfinished = self.unfinished_tasks - len(self.queue)
            if unfinished <= 0:
                if unfinished < 0:
                    raise ValueError('task_done() called too many times')
                self.all_tasks_done.notify_all()
            self.unfinished_tasks = unfinished
            self.queue.clear()
            self.not_full.notify_all()

qcommand = queue.Queue()
qreport = queue.Queue()
#qcommand = CQ()
#qreport = CQ()
#aqr = [PQueue(), PQueue(), PQueue(), PQueue(), \
#       PQueue(), PQueue(), PQueue(), PQueue()]
#aqr = [queue.Queue(), queue.Queue(), queue.Queue(), queue.Queue(), \
#       queue.Queue(), queue.Queue(), queue.Queue(), queue.Queue()]
aqr = [CQ(), CQ(), CQ(), CQ(), \
       CQ(), CQ(), CQ(), CQ()]

class GuiCore(Tk):
    """Handle the graphical interface for Pub2SDwizard and the gui logic"""
    def __init__(self, parent, scriptdir):
        Tk.__init__(self, parent)
        self.parent = parent
        self.script_dir = scriptdir
        self._initialize()
        self._report_queue = {
            'CLEARTAGTREE':self._CLEARTAGTREE, \
            'CLEARTREE':self._CLEARTREE, \
            'SEEFOCUS':self._SEEFOCUS, \
            'INSERTTAGTREETAGS':self._INSERTTAGTREETAGS, \
            'SETTAGTREE':self._SETTAGTREE, \
            'SELECTIONTAGTREE':self._SELECTIONTAGTREE, \
            'ENTERLIST':self._ENTERLIST, \
            'IS_COPY_PLAYLISTS_TO_TOP':self._IS_COPY_PLAYLISTS_TO_TOP, \
            'M3UorM3U8':self._M3UorM3U8, \
            'ADD_FILE':self._ADD_FILE, \
            'ADD_ITEMS':self._ADD_ITEMS, \
            'RENAME_CHILDREN':self._RENAME_CHILDREN, \
            'STATUS':self._STATUS, \
            'STATUS{}':self._STATUSBB, \
            'MESSAGEBOXASKOKCANCEL':self._MESSAGEBOXASKOKCANCEL, \
            'MESSAGEBOXERROR':self._MESSAGEBOXERROR, \
            'MESSAGEBOXWARNTRACK':self._MESSAGEBOXWARNTRACK, \
            'MESSAGEBOXSHOWWARNING2':self._MESSAGEBOXSHOWWARNING2, \
            'MESSAGEBOXWARNTRACK2':self._MESSAGEBOXWARNTRACK2, \
            'MESSAGEBOXSHOWWARNINGMULTPLEFILEICONS':\
                        self._MESSAGEBOXSHOWWARNINGMULTPLEFILEICONS, \
            'MESSAGEBOXSHOWERRORIN':self._MESSAGEBOXSHOWERRORIN, \
            'MESSAGEBOXSHOWERRORERRORINON_PREPARE_FILES':\
                        self._MESSAGEBOXSHOWERRORERRORINON_PREPARE_FILES, \
            'MESSAGEBOXSHOWERRORINSUFFICENT':\
                        self._MESSAGEBOXSHOWERRORINSUFFICENT, \
            'MESSAGEBOXSHOWHASHERROR':self._MESSAGEBOXSHOWHASHERROR, \
            'MESSAGEBOXSHOWERRORLOSTGRAPHIC':\
                        self._MESSAGEBOXSHOWERRORLOSTGRAPHIC, \
            'MESSAGEBOXSHOWERRORTHREADS':self._MESSAGEBOXSHOWERRORTHREADS, \
            'PROGSTEP':self._PROGSTEP, \
            'PROGSTOP':self._PROGSTOP, \
            'PROGMAX':self._PROGMAX, \
            'PROGVALUE':self._PROGVALUE, \
            'COMPLETE':self._COMPLETE, \
            'LOCKGUI':self._LOCKGUI, \
            'UNLOCKGUI':self._UNLOCKGUI, \
            'FOLDERSIZE':self._FOLDERSIZE, \
            'TXTPREFCHARDEL':self._TXTPREFCHARDEL, \
            'TXTPREFCHARINSERT':self._TXTPREFCHARINSERT, \
            'CONTINUE_F0_NEXT':self._CONTINUE_F0_NEXT, \
            'HASHEDGRAPHICS':self._HASHEDGRAPHICS, \
            'FILES_PREPARED':self._FILES_PREPARED, \
            'DELETEDTEMP':self._DELETEDTEMP, \
            'IM_OUT_OF_HERE':self._IM_OUT_OF_HERE, \
            'PREFERRED':self._PREFERRED, \
            'PRINT':self._PRINT, \
            }
        self._usb_report_queue = {\
            'PROGSTEP':self._PROGSTEP, \
            'PRINT':self._USBPRINT, \
            'PRINTdiag':self._PRINT, \
            'STATUS':self._USBSTATUS, \
            }

    def _initialize(self):
        """initialize the GuiCore"""
        self.backendthread = Backend(qcommand, qreport, aqr, \
                                     SCRIPT_DIR, lang='en-US')
        self.backendthread.start()
#        self.script_dir = 'frontend'
#        print(self.script_dir)

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

        pud2sd_styles = Style()
        pud2sd_styles.configure('lowlight.TButton', \
                                font=('Sans', 8, 'bold'),)
        if platform.system() == 'Windows':
            pud2sd_styles.configure('highlight.TButton', \
                                font=('Sans', 11, 'bold'), \
                                background='blue', foreground='green')
        elif platform.system() == 'Linux':
            pud2sd_styles.configure('highlight.TButton', \
                                font=('Sans', 11, 'bold'), \
                                background='white', foreground='green')
        pud2sd_styles.configure('wleft.TRadiobutton', \
                                anchor='w', justify='left')

        self._initialize_f0(lang) # so on f1, recommended mp3tags
        self._initialize_f1(lang) # so on f2, special characters
        self._initialize_f2(lang) # so on f3 tab Edit Hierarchy
        self._initialize_f3(lang) #on f4 - featurephone features?
        self._initialize_f4(lang) # on f5 - publish to...
        self._initialize_f5(lang)

#        if platform.system() == 'Linux':
#            #create on f6,will be for locking/unlocking SD cards
#            self._initialize_f6(lang)
        self._process_report_queue()

    def _process_report_queue(self):
#        lang = self.ddnGuiLanguage.get()
        while not qreport.empty():
            lang = self.ddnGuiLanguage.get()
            areport = qreport.get()
            if areport[0] in self._report_queue.keys():
#                print(areport, lang)
                self._report_queue[areport[0]](areport[1], lang)
            else:
                print('Unknown report >{}<'.format(areport))
            qreport.task_done()
        #now scan queues from pub to SD threads
        for i in range(0, 8):
            if not aqr[i].empty():
                aqreport = aqr[i].get()
#                self._usb_report_queue
                if aqreport[0] in self._usb_report_queue.keys():
#                    self._report_queue[areport[0]](areport[1], i)
                    #simple fifo queue
                    #i says which status slot to update, ignored for PROGSTEP
#                    print("aqreport=>{}<".format(aqreport))
                    self._usb_report_queue[aqreport[0]](aqreport[1], i)
                else:
                    pass
                aqr[i].task_done()
        self.lblProject.after(100, self._process_report_queue)

    def _CLEARTAGTREE(self, _, __):
        map(self.tagtree.delete, self.tagtree.get_children())

    def _CLEARTREE(self, _, __):
        self.tree.delete(*self.tree.get_children())

    def _SEEFOCUS(self, areport, _):
        self.tree.see(areport)
        self.tree.focus(areport)
        self.tree.selection_set(areport)

    def _INSERTTAGTREETAGS(self, areport, lang):
        for item in areport:
            if item not in self.tagtree.get_children():
                self.tagtree.insert('', index='end', iid=item, \
                        open=True, values=[0], \
                        text="({}) {}".format(\
                              item, SET_TAGS[lang][item]))
    def _SETTAGTREE(self, areport, _):
        self.tagtree.selection_set(areport)

    def _SELECTIONTAGTREE(self, areport, _):
        self.tagtree.selection_add(areport)

    def _ENTERLIST(self, areport, _):
        self.EnterList.set(areport)

    def _IS_COPY_PLAYLISTS_TO_TOP(self, areport, _):
        self.is_copy_playlists_to_top.set(areport)

    def _M3UorM3U8(self, areport, _):
        self.M3UorM3U8.set(areport)

    def _ADD_FILE(self, areport, _):
        self.tree.insert(areport[1], index='end', iid=areport[2], \
                         values=areport[3], open=True, text='file')
    def _ADD_ITEMS(self, areport, _):
        #items handled in the order thet were added to the list
        for item in areport:
            newItem = self.tree.insert(item[1][0], index='end', \
                                iid=item[0], values=item[1][1], \
                                open=True, text=item[1][2])
            self.progbar.step()
        self._enable_tabs()
        self.update_idletasks()

    def _RENAME_CHILDREN(self, areport, _):
        #so now rename them
        for iid in areport.keys():
            vout = areport[iid][0]
            for c, v in vout:
                self.tree.set(iid, c, v)
            self.tree.item(iid, text=areport[iid][1])
            self.progbar.step()
        self._enable_tabs()
        self.update_idletasks()

    def _PRINT(self, areport, _):
        print(areport)

    def _USBPRINT(self, areport, i):
        print("from thread {} => {}".format(i, areport))

    def _LISTPROJECTS(self, areport, _):
        self.list_projects = [f.rstrip('.prj') \
                              for f in os.listdir(self.Pub2SD) \
                                             if f.endswith('.prj')]
        self.ddnCurProject['values'] = self.list_projects
        self.ddnCurProject.set(areport[1])

    def _STATUS(self, areport, lang):
        if areport:
            self.status['text'] = LOCALIZED_TEXT[lang][areport]
        else:
            self.status['text'] = ''

    def _USBSTATUS(self, areport, i):
        lang = self.ddnGuiLanguage.get()
        if areport in LOCALIZED_TEXT[lang].keys():
            self.usb_status[i] = LOCALIZED_TEXT[lang][areport]
        else:
            self.usb_status[i] = areport
        self.status['text'] = ';'.join(\
                   [t for t in self.usb_status if t])

    def _STATUSBB(self, areport, _):
#        print("in _STATUSBB, areport=>{}<".format(areport))
        lang = self.ddnGuiLanguage.get()
        if len(areport) > 1:
            if lang not in LOCALIZED_TEXT.keys():
                print("in _STATUSBB, lang=>{}<, areport=>{}<".format(lang, areport))
            if areport[0] not in  LOCALIZED_TEXT[lang].keys():
                print("in _STATUSBB, areport=>{}<".format(areport))
            self.status['text'] = LOCALIZED_TEXT[lang][areport[0]].format(areport[1])
        else:
            self._STATUS(areport, lang)
#        self.status['text'] = LOCALIZED_TEXT[lang]['STATUS{}'].\
#                                            format(areport) \
#                                            if areport else ''

    def _MESSAGEBOXASKOKCANCEL(self, areport, lang):
        qcommand.put(('OKCANCEL', messagebox.askokcancel(\
                            LOCALIZED_TEXT[lang][areport[0]], \
                            LOCALIZED_TEXT[lang][areport[1]])))

    def _MESSAGEBOXERROR(self, areport, lang):
        messagebox.showerror(areport[1][0], \
                            "{} <{}>, {}".format(\
                            LOCALIZED_TEXT[lang][areport[1]], \
                            areport[2], \
                            LOCALIZED_TEXT[lang][areport[3]]))

    def _MESSAGEBOXWARNTRACK(self, areport, lang):
        messagebox.showwarning(areport[0], \
            LOCALIZED_TEXT[lang]['Set'] + ' TRCK, >{}< {}'.format(\
                              areport[2], \
                              LOCALIZED_TEXT[lang][\
           "'track in/set_of' doesn't contain a valid integers."]))

    def _MESSAGEBOXSHOWWARNING2(self, areport, lang):
        messagebox.showwarning(areport[0], \
                        LOCALIZED_TEXT[lang][areport[1][1]])

    def _MESSAGEBOXWARNTRACK2(self, areport, lang):
        messagebox.showwarning(LOCALIZED_TEXT[lang][areport[0]] + \
                               ' {}'.format(areport[1]), \
                        LOCALIZED_TEXT[lang][areport[2]])

    def _MESSAGEBOXSHOWWARNINGMULTPLEFILEICONS(self, areport, lang):
        messagebox.showwarning('', \
                        LOCALIZED_TEXT[lang][areport[0]].format(areport[1]))

    def _MESSAGEBOXSHOWERRORIN(self, areport, _):
        messagebox.showerror(areport[0], areport[1])

    def _MESSAGEBOXSHOWERRORERRORINON_PREPARE_FILES(self, areport, _):
        messagebox.showerror(areport[0], areport[1])

    def _MESSAGEBOXSHOWERRORINSUFFICENT(self, areport, lang):
        messagebox.showerror(\
                            LOCALIZED_TEXT[lang][areport[0]], \
                            LOCALIZED_TEXT[lang][areport[1]].\
                            format(areport[2], areport[3]))

    def _MESSAGEBOXSHOWHASHERROR(self, areport, _):
        self.complete = messagebox.showerror("Invalid number of parameters", \
                        "In row {}, {} tag=>{}<, {} required.".\
                        format(areport[0],\
                        areport[1], \
                        areport[2], \
                        areport[3]))
        qcommand.put(('OKCANCEL', self.complete))

    def _MESSAGEBOXSHOWERRORLOSTGRAPHIC(self, areport, _):
        messagebox.showerror('', areport)

    def _MESSAGEBOXSHOWERRORTHREADS(self, areport, lang):
        messagebox.showerror(LOCALIZED_TEXT[lang][areport[0]], \
                             LOCALIZED_TEXT[lang][areport[1]].\
                             format(areport[2]))

    def _PROGSTEP(self, areport, _):
        self.progbar.step(areport)

    def _USBPROGSTEP(self, areport, _):
        #ignores which thread it's from and just does step
        self.progbar.step(areport)

    def _PROGSTOP(self, areport, _):
        self.progbar.stop()

    def _PROGMAX(self, areport, _):
        self.progbar['maximum'] = areport
        self.progbar['value'] = 0
        self.update_idletasks()

    def _PROGVALUE(self, areport, _):
        self.progbar['value'] = areport
        self.update_idletasks()

    def _COMPLETE(self, areport, _):
#        self.complete = areport[1]
        self.complete = areport

    def _LOCKGUI(self, areport, _):
        self._disable_tabs()

    def _UNLOCKGUI(self, areport, _):
        self._enable_tabs()
        self.update_idletasks()

    def _FOLDERSIZE(self, areport, _):
        self.lblOutputSize['text'] = \
                                    "{:0.1f} MB".format(areport)

    def _TXTPREFCHARDEL(self, areport, _):
        self.txtPrefChar.delete(areport[0], areport[1])

    def _TXTPREFCHARINSERT(self, areport, _):
        self.txtPrefChar.insert(areport[0], areport[1])

    def _CONTINUE_F0_NEXT(self, areport, lang):
        if areport:
            self._on_click_f0_next_continued(lang)
        else:
            print("can't continue")
        self.update_idletasks()

    def _HASHEDGRAPHICS(self, areport, _):
        self.hashed_graphics = areport

    def _FILES_PREPARED(self, areport, _):
        self._on_prepare_files_continued()

    def _DELETEDTEMP(self, areport, _):
        qcommand.put(('DIE_DIE_DIE', ''))

    def _IM_OUT_OF_HERE(self, areport, _):
        for pq in aqr:
#            pq.clear()
            pq.close()
        self.destroy()

    def _PREFERRED(self, areport, _):
        self.preferred.set(areport)

    def _initialize_project_variables(self):
        """The project variables that will be saved on clicking 'save project'.
        The sfn variable hold the settings for their associated tab (fn) of
        the notebook widget on the main window. The child 'tree'holds a copy
        of all the file locations and any modifications to their metadata"""
        self.project_id = ''
        self.complete = 0

    def _initialize_variables(self):
        """initialize variables for GuiCore"""
        self.font = font.Font()

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
        self.list_images = list()
        if platform.system() == 'Windows':
            self.next_image = PhotoImage(file='mainc.png')
        elif platform.system() == 'Linux':
            self.next_image = PhotoImage(file='/usr/share/pub2sdwizard/mainc.png')
        else:
            messagebox.showwarning('Warning', "Gui:Help I've been kidnaped by {}!!!".\
                                   format(platform.system()))
        self.illegalChars = [chr(i) for i in range(1, 0x20)] + \
                            [chr(0x7F), '"', '*', '/', ':', '<', '>', \
                                                              '?', '\\', '|']
        self.output_to = set()
        self.play_list_targets = set()
        self.needed = 0 #in Mb
        self.temp_dir_deleted = False
        self.usb_status = ['', '', '', '', '', '', '', '']
        self.Treed = False
        self.next_track = 0

        self._initialize_Vars()

    def _initialize_Vars(self):
        """define all StringVar(), BooleanVar(), etc… needed to hold info"""
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
        self.is_copy_playlists_to_top = IntVar()
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
                                  command=self._quit)

        self.helpmenu = Menu(self.menubar)
        self.menubar.add_cascade(label=LOCALIZED_TEXT[lang]['Help'], \
                                 menu=self.helpmenu)
        self.helpmenu.add_command(label=LOCALIZED_TEXT[lang]['Read Me'], \
                                  command=self._on_read_me)
        self.helpmenu.add_command(label=LOCALIZED_TEXT[lang]['About...'], \
                                  command=on_copyright)

    def _quit(self):
        qcommand.put(('DELETETEMP', None))

    def _initialize_main_window_notebook(self, lang):
        """initializes notebook widget on main window"""
        #notebook
        if platform.system() == 'Windows':
            self.n = Notebook(self, width=1015)
        elif platform.system() == 'Linux':
            self.n = Notebook(self, width=1070)
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

        self.btnHTMLProject = Button(self.f_1, \
                                     text=LOCALIZED_TEXT[lang]["HTML"], \
                                                command=self._on_html_project)
        self.btnHTMLProject.grid(column=2, row=0, columnspan=2, \
                                 padx=5, pady=5, sticky='news')
        self.btnHTMLProject['state'] = 'disabled'
        self.btnHTMLProject_ttp = CreateToolTip(self.btnHTMLProject, \
                                        LOCALIZED_TEXT[lang]['HTML_ttp'])

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

        self.progbar = Progressbar(self, maximum=100, variable=self.int_var, \
                                   mode="determinate")
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
        self.tagtree.configure(yscroll=ysb.set)
        ysb.grid(row=1, column=2, rowspan=20, padx=5, sticky='nse')

        #fill tagtree
        self.listoftags = list(self.recommendedTags)
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
            self.tagtree.insert('', index='end', iid=t, open=True, \
                    values=[0], text='({}) {}'.format(t, SET_TAGS[lang][t]))
        if t in self.recommendedTags:
            self.tagtree.selection_add(t)
        self.tagtree.see('')
        self.update_idletasks()

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
        self.rdbDisable = Radiobutton(self.f2, \
                                    text=LOCALIZED_TEXT[lang]["Disable Normalization"], \
                                    variable=self.preferred, value=2, \
                                    style='wleft.TRadiobutton')
        self.rdbDisable.grid(column=1, row=4, padx=5, pady=5, sticky='news')
        self.lblLatin1 = Label(self.f2, \
                               text=LOCALIZED_TEXT[lang]["AddLatin1Example"], \
                                anchor='w', justify='left', wraplength=200)
        self.lblLatin1.grid(column=3, row=4, padx=5, pady=5, sticky='news')

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


        self.ddnPrefChar['values'] = self.list_PrefChar

        self.btnSavePref = Button(self.f2, \
                                  text=LOCALIZED_TEXT[lang]["SavePref"], \
                                  command=lambda: \
                            self._on_SavePref('', '', \
                                self.txtPrefChar.get(0.0, 9999.9999).strip()))
        self.btnSavePref.grid(column=4, row=4, padx=5, pady=5, sticky='news')

        self.txtPrefChar = Text(self.f2, height=10, width=60)
        self.txtPrefChar.grid(column=0, row=5, \
                              columnspan=3, rowspan=6, padx=5, pady=5, \
                              sticky='news')
        ysb = Scrollbar(self.f2, orient='vertical', \
                              command=self.txtPrefChar.yview)
        self.txtPrefChar.configure(yscroll=ysb.set, font=("sans", 12), \
                                                       undo=True, wrap='word')
        ysb.grid(row=5, column=3, rowspan=6, sticky='nws')

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
                    style='highlight.TButton')

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
        self.btnMergeFiles = Button(self.m1, \
                                    text=LOCALIZED_TEXT[lang]["Merge files"], \
                                                      command=self._on_merge)
        self.btnMergeFiles.grid(column=0, row=1, padx=5, pady=5, sticky='news')
        self.btnMergeFilesm_ttp = CreateToolTip(self.btnDeleteItem, \
                                         LOCALIZED_TEXT[lang]['Merge_ttp'])

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


        set_tagb = []
        for tag in SET_TAGS[lang]:
            #??? need to ensure tagname is translated to fr and pt
            set_tagb.append('{}:({})'.format(SET_TAGS[lang][tag], tag.upper()))
        self.ddnSelectTag = Combobox(self.boxEnter, state='readonly', \
                                     textvariable=self.set_tag, width=70)
        self.ddnSelectTag.bind("<<ComboboxSelected>>", self._on_get)
        self.ddnSelectTag.grid(column=0, row=0, columnspan=3, padx=5, pady=5, \
                               sticky='news')
        self.ddnSelectTag['text'] = 'Tag to set:'
        self.ddnSelectTag['justify'] = 'left'
        self.ddnSelectTag_ttp = CreateToolTip(self.ddnSelectTag, \
                                    LOCALIZED_TEXT[lang]['ddnSelectTag_ttp'])
        self.etrTagValue = Entry(self.boxEnter, \
                                 textvariable=self.currentEntry, width=70)
        self.etrTagValue.grid(column=0, row=1, \
                              columnspan=3, padx=5, pady=5, sticky='news')
        self.etrTagValue['justify'] = 'left'
        self.etrTagValue_ttp = CreateToolTip(self.etrTagValue, \
                                        LOCALIZED_TEXT[lang]['entry1_ttp'])

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

        self.btnAppend = Button(self.boxOuter, text=LOCALIZED_TEXT[lang]["Append"], \
                             command=self._on_append)
        self.btnAppend_ttp = CreateToolTip(self.btnSet, \
                                        LOCALIZED_TEXT[lang]['Append_ttp'])
        self.btnAppend.grid(column=1, row=2, padx=5, pady=5, sticky='news')
        self.btnAppend['state'] = 'disabled'

        self.btnGetDefault = Button(self.boxOuter, \
                                text=LOCALIZED_TEXT[lang]["Get default"], \
                                                  command=self._on_get_default)
        self.btnGetDefault.grid(column=2, row=1, padx=5, pady=5, sticky='news')

        self.lblM2 = Label(self.boxOuter, \
                           text=LOCALIZED_TEXT[lang]['M2_ttp1'] \
                            if self.mode.get() == 0 else \
                            LOCALIZED_TEXT[lang]['M2_ttp'], \
                           anchor='w', justify='left', wraplength=590)
        self.lblM2.grid(column=0, row=3, columnspan=3, padx=5, pady=5, \
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
        self.imgCover = Label(self.f4, text='placeholder', anchor='w')
        self.imgCover.configure(image=self.next_image)
        self.imgCover.grid(column=1, row=4, padx=5, pady=5, sticky='news')

        self.btnF4Next = Button(self.f4, text=LOCALIZED_TEXT[lang]["Next"], \
                                command=self._on_click_f4_next, \
                                style='highlight.TButton')
        self.btnF4Next_ttp = CreateToolTip(self.btnF4Next, \
                                         LOCALIZED_TEXT[lang]['btnF4Next_ttp'])
        self.btnF4Next.grid(column=2, row=5, padx=5, pady=5, sticky='news')

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

        self.btnExit = Button(self.f5, \
                text=LOCALIZED_TEXT[lang]["Delete temporary files and exit."], \
                                  command=self._quit, \
                                  style='highlight.TButton')
        self.btnExit.grid(column=3, row=5, \
                            columnspan=2, padx=5, pady=5, sticky='news')


#    def _initialize_f6(self, lang):
#        """The lock unlock SD card tab, to be implemented?"""
#        pass

    def _on_html_project(self):
        """Export the whole project tree to an HTML file and open it with
                                                      your default browser."""
        qcommand.put(('EXPORTHTML', None))

    def _on_loadPrefChar(self, dummy, _prefchar=None, _lst='', _filein=''):
        """load a set of preferred character pairs from LATIN1 constant
                                                 or a utf8 coded  .csv file"""

        lst = _lst if _lst else self.ddnPrefChar.get()
        prefchar = _prefchar if _prefchar is not None else self.txtPrefChar
        if lst == 'Latin1':
            if prefchar.get(0.0, 9999.9999).rstrip():
                prefchar.insert(9999.9999, ', ' + LATIN1)
            else:
                prefchar.insert(9999.9999, LATIN1)
        elif lst == '': #del
            prefchar.delete(0.0, 9999.9999)
        else: #load txt file
            if not _filein:
                filein = os.path.normpath(self.Pub2SD + '/'+ lst + '.csv')
            else:
                filein = _filein
            fin = codecs.open(filein, mode='r', encoding='utf-8')
            text = fin.read()
            if prefchar.get(0.0, 9999.9999).strip():
                text = ', ' + text
            prefchar.insert(9999.9999, text)
            fin.close()

    def _set_tabs(self, astate="normal"):
        #mo
        self.btnImportContents["state"] = astate
        self.btnImportHierarchy["state"] = astate
        self.btnMoveUpM0["state"] = astate
        self.btnMoveDownM0["state"] = astate
        self.btnTrimTitle["state"] = astate
        self.btnF3M0Next["state"] = astate
        #m1
        self.btnDeleteItem["state"] = astate
        self.btnF3M1Next["state"] = astate
        #m2
        self.btnGet["state"] = astate
        self.btnSet["state"] = astate
        self.btnGetDefault["state"] = astate
        self.btnSelectArtwork["state"] = astate
        self.btnF3M2Next["state"] = astate

        if self.mode.get() != 0:
            #Advanced mode
            #m0
            self.btnAddCollection["state"] = astate
            self.btnAddFiles["state"] = astate
            #m1
            self.btnPromote["state"] = astate
            self.btnDemote["state"] = astate
            self.btnMoveUp["state"] = astate
            self.btnMoveDown["state"] = astate
            #m2
        self.btnImportContents.focus_set()

        self.update_idletasks()

    def _enable_tabs(self):
        self._set_tabs("normal")

    def _disable_tabs(self):
        self._set_tabs("disable")

    def _on_SavePref(self, _lang='en-US', _fileout='', _text=""):
        """save your list of preferred character pairs to a utf-8 coded
        .csv file. If _fileout is supplied the filedialog
        will not be called. If _text is supplied self.txtPrefChar will not
        be accessed"""

        lang = self.ddnGuiLanguage.get() if not _lang else _lang

        fileout = filedialog.asksaveasfilename(\
                        filetypes=[('Preferred characters file', '.csv'), ], \
                                    initialdir=self.Pub2SD, \
                                    initialfile='', \
                                    title=LOCALIZED_TEXT[lang]['SavePref'], \
                                    defaultextension='.csv') \
                  if not _fileout else _fileout
        if fileout:
            text = self.txtPrefChar.get(0.0, 9999.9999).strip() \
                        if not _text else _text
            text = ' '.join(text.split('\n'))
            text = ' '.join(text.split('\r'))
            text = ' '.join(text.split('\f'))
            if ',' in text:
                pairs = [p.strip() for p in text.split(',')]
                astr = ', '.join(pairs)
            elif text:
                astr = text
            else:
                astr = ' '
            fout = codecs.open(fileout, mode='w', encoding='utf-8')
            fout.write(astr)
            fout.close()

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
        new_project = Path(fileout).stem
        if new_project != project:
            self.lblProject['text'] = \
                           LOCALIZED_TEXT[lang]['Current Project>'] + \
                           ' ' + new_project
        #create new project tree, throwing away any existing tree
        #fileout is full path as string
        qcommand.put(('ONSAVEPROJECT', fileout))

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
                               else {key:'show' \
                                     for key in self.tagtree.selection()}

        fileout = _fileout if _fileout \
                           else filedialog.asksaveasfilename(\
                                filetypes=[('Template file', '.json'), ], \
                                           initialdir=self.Pub2SD, \
                                           initialfile='', \
                                title=LOCALIZED_TEXT[lang]['CreateTemplate'], \
                                           defaultextension='.json')
        if fileout: #output template
            output = codecs.open(fileout, mode='w', encoding='utf-8')

            j = json.dumps(a_template, indent=4, sort_keys=True)
            output.write(j)
            output.close()
        return a_template

    def _on_read_me(self):
        """calls the appropriate 'help' file from the menubar"""

        lang = self.ddnGuiLanguage.get()
        app_dir = get_script_directory()
        # open an HTML file on my own computer
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

        self.output_to = list()
        self.lblOutputTo['text'] = ''

        the_range_limit = len(self.tlist) if len(self.tlist) < 8 else 8
        for i in range(0, the_range_limit):
            self.update_idletasks()
            i_get = self.cbv[i].get()
            if i_get == 't':
                if self.needed < self.tlist[i][1]:
                    the_drive = self.tlist[i][0].split(',')
                    self.output_to.append(the_drive[0].strip())
                else:
                    messagebox.showerror(\
                     LOCALIZED_TEXT[lang]['Insufficent space on {}'].\
                        format(self.tlist[i][0].split(',')[0]), \
                     LOCALIZED_TEXT[lang]["Needs {}Mb, has {}Mb free space."].\
                        format(self.needed, self.tlist[i][1] / (1024.0 * 1024.0)))
                    self.output_to = []
                    return
            else:
                print("arrgh fails, self.cbv[i].get()={}".format(i_get))
        qcommand.put(('OUTPUT_TO', self.output_to))
        if platform.system() == 'Windows':
            self.lblOutputTo['text'] = \
                             ', '.join(', '.join(self.output_to).split(', , '))
        elif platform.system() == 'Linux':
            self.lblOutputTo['text'] = ', '.join(', '.join([t.split('/')[-1] \
                            for t in self.output_to]).split(', , '))
        else:
            pass
        self.update_idletasks()

    def _on_refresh_drives(self):
        '''Linux not seeing usb/SD drives'''

        lang = self.ddnGuiLanguage.get()
        giga_bytes = LOCALIZED_TEXT[lang]['Gb']
        mega_bytes = LOCALIZED_TEXT[lang]['Mb']
        self.tlist = [['', 0], ['', 0], ['', 0], ['', 0], \
                      ['', 0], ['', 0], ['', 0], ['', 0]]
        self.tlist = list()
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
                    self.tlist.append(['{}, {}, {}, {}, {}'.\
                        format(part.mountpoint, total, used, free, percent), \
                              usage.free])
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
                    self.tlist.append(['{}, {}, {}, {}, {}'.\
                        format(part.mountpoint, total, used, free, percent), \
                                usage.free])
                    i += 1
        else:
            messagebox.showerror('Unrecognised OS', \
                  "Help I've been kidnapped by {}.".format(platform.system()))

        for i in range(0, 8):
            self.cb[i]['text'] = ''
            self.cb[i]['state'] = 'disabled'
            self.cbv[i].set('f')
            if i < len(self.tlist) and self.tlist[i][0]:
                if platform.system() == 'Windows':
                    self.cb[i]['text'] = self.tlist[i][0]
                elif platform.system() == 'Linux':
                    self.cb[i]['text'] = self.tlist[i][0].split('/')[-1]
                self.cb[i]['state'] = 'normal'

    def _pdup_state(self, astate):
        """sets the states of the Promote, Demote, MoveUp and moveDown buttons
                                              on the 'Edit heirachy' sub-tab"""
        self.btnPromote['state'] = astate
        self.btnDemote['state'] = astate
        self.btnMoveUp['state'] = astate
        self.btnMoveDown['state'] = astate

    def _on_click_f0_next(self):
        """loads the setting on the 'Project Name' tab and proceeds to the
        'Choose MP3 tags' tab"""
        qcommand.put(('SCRIPT_DIR', self.script_dir))
        lang = self.ddnGuiLanguage.get()

        qcommand.put(('INITIALDIGIT', self.InitialDigit.get()))

        qcommand.put(('MODE', self.mode.get()))
        conf_file = self.ddnCurProject.get()
        if not conf_file:
            messagebox.showinfo("'{}' {}.".format(\
                                LOCALIZED_TEXT[lang]['Current Project>'], \
                                LOCALIZED_TEXT[lang]['is empty']), \
                                "{}".format(LOCALIZED_TEXT[lang][\
                                     'Please enter a name for your project.']))
            return
        qcommand.put(('CONF_FILE', conf_file))


    def _on_click_f0_next_continued(self, lang):
        """conf file loaded or project created so continue"""
        #now load template if any
        if self.ddnCurTemplate.get():
            thisone = Path(self.Pub2SD, (self.ddnCurTemplate.get() + '.json'))
            if thisone.exists() and thisone.is_file():
                qcommand.put(('LOAD_TEMPLATE', str(thisone)))
        elif not self.ddnCurTemplate.get():
            pass
        else:
            messagebox.showerror(\
                    LOCALIZED_TEXT[lang]['Template file not found!'], \
                    LOCALIZED_TEXT[lang]["Can't find {} template, prior " + \
                    "settings unchanged."].format(self.ddnCurTemplate.get()))

        conf_file = self.ddnCurProject.get()
        self.lblProject['text'] = LOCALIZED_TEXT[lang]['Current Project>'] + \
                                                                ' ' + conf_file
        self.lblMode['text'] = '{}{}'.format(LOCALIZED_TEXT[lang]['Mode>'], \
                                         LOCALIZED_TEXT[lang]['Simple'] \
                                         if self.mode.get() == 0 \
                                         else LOCALIZED_TEXT[lang]['Advanced'])


        if conf_file:
            self.n.add(self.f1)#show recommended tags
            self.n.select(1)
            self.btnSaveProject['state'] = 'normal'
        else:
            messagebox.showerror('Error in on_click_f0()', \
                                          "Error can't find project.")
        self.update_idletasks()

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
        self.selected_tags = list(self.tagtree.selection())
        if 'TIT2' not in self.selected_tags:
            self.selected_tags.insert(0, 'TIT2')
        qcommand.put(('SELECTED_TAGS', self.selected_tags))
        self.columns = ['Type', 'Name', 'Location'] #+ self.recommendedTags
        self.columns.extend(self.selected_tags)
        self.displayColumns = list(self.columns)
        self.displayColumns.remove('Location')

        qcommand.put(('DISPLAYCOLUMNS', (self.displayColumns, self.columns)))
        self.Treed = True

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

        #handled by backend
        qcommand.put(('LOADTREEFROMTROUT', None))

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
        if text:
            pairs = [c.strip() for c in text.split(',')]
            for p in pairs:
                p = p.strip()
                t = p.split('/')
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
        qcommand.put(('SELFPREF', (self.pref, self.pref_char, self.preferred.get(), self.template)))
        self.Treed = True
        self.n.add(self.f3)
        self.n.select(3)
        self.btnHTMLProject['state'] = 'normal'
        self.tree.focus('I00001')
        self.tree.selection_set('I00001')
        self.update_idletasks()


    def _on_click_f3m0_next(self):
        """proceed to 'Edit heirarchy' sub-tab"""
        self.status['text'] = ''
        self.progbar['value'] = 0
        self.update_idletasks()
        self.m.add(self.m1)
        self.m.select(1)

    def _on_strip_leading_numbers(self):
        qcommand.put(('STRIPTITLE', \
                      (self.ddnTrimFromTitle.get(), self.tree.focus())))

    def _on_click_f3m1_next(self):
        """proceed to 'Edit MP3 tags' sub-tab"""
        self.status['text'] = ''
        self.progbar['value'] = 0
        self.update_idletasks()
        self.m.add(self.m2)
        self.m.select(2)

    def _on_click_f3m2_next(self):
        """proceed to 'Feature-phone options' tab"""
        #create self.files here?
        qcommand.put(('HASHEDGRAPHICS', self.hashed_graphics))

        self.status['text'] = ''
        self.progbar['value'] = 0
        self.update_idletasks()
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

        #walk down tree creating filenames
        # and opening them in pairs iid:filename
        temp_path = os.path.normpath(self.Pub2SD + '/Temp/' + self.project)
        if os.path.isdir(temp_path):
            self.status['text'] = LOCALIZED_TEXT[lang]['Deleting old temporary folder.']
            self.update_idletasks()
            try:
                delete_folder(temp_path)
            except:
                messagebox.showerror(\
                    LOCALIZED_TEXT[lang]['Error in on_click_f4_next()'], \
                    LOCALIZED_TEXT[lang]["Folder <{}> may be in use by another \
                    program. Close all other programs \
                    and try again."].format(temp_path))
                return
        project_path_ = os.path.normpath(self.project)
        # trailling '\\' will be removed
        qcommand.put(('CHILDRENS_FILENAMES', (self.project_id, \
                                               temp_path, project_path_)))
        self.play_list_targets = set()
        if self.EnterList.get():
            self.play_list_targets.update(set(self.EnterList.get().split(',')))
        qcommand.put(('SETCOPYPLAYLISTS', (self.play_list_targets, \
                                           self.is_copy_playlists_to_top.get())))
        qcommand.put(('M3UorM3U8', self.M3UorM3U8.get()))

        self._on_prepare_files()
        self.update_idletasks()
        qcommand.put(('FOLDERSIZE', temp_path))

    def _on_click_f5_next(self):
        """waiting on lock/unlock SD card software!"""
        self.n.add(self.f6)
        self.n.select(6)


    def _on_add_collection(self):
        """add a collection to treeview widget at the current focus"""
        focus = self.tree.focus()

        self._disable_tabs()
        qcommand.put(('ADD_COLLECTION', focus))

        self.update_idletasks()

    def _on_add_item(self):
        """ add an item(mp3 file) to the selected collection"""

        lang = self.ddnGuiLanguage.get()
        focus = self.tree.focus()
        if focus or self.tree.set(focus, 'Type') != 'collection':
            messagebox.showwarning('', LOCALIZED_TEXT[lang][\
                                                "Please select a collection."])
        else:
            full_path = filedialog.askopenfilenames(\
                                initialdir=os.path.expanduser('~'), \
                                filetypes=[('MP3 files', '*.mp3'),], \
                                          title="Select MP3 file…")
            filenames = full_path
            self.progbar['maximum'] = len(filenames)
            self.progbar['value'] = 0
            self._disable_tabs()
            qcommand.put(('ADD_FILES', filenames))
        self.update_idletasks()

    def _on_add_folder(self):
        """add folder as collection with its dependants to Treeview widget"""
        lang = self.ddnGuiLanguage.get()
        focus = self.tree.focus()
        if focus == '':
            focus = self.project_id
        dir_path = filedialog.askdirectory(initialdir=os.path.expanduser('~'),\
                                    title="Select folder…", mustexist=True)
        if dir_path:
            self._disable_tabs()
            self.progbar['value'] = 0
            self.status['text'] = LOCALIZED_TEXT[lang]["Unpacking"] + dir_path
            qcommand.put(('ADD_FOLDER', (focus, dir_path)))
        self.update_idletasks()

    def _on_add_contents(self):
        """add contents of a folder with its dependants to existing collection
                                                          in Treeview widget"""

        lang = self.ddnGuiLanguage.get()

        focus = self.tree.focus()
        if focus == '':
            focus = self.project_id
        dir_path = filedialog.askdirectory(initialdir=os.path.expanduser('~'),\
                                        title="Select folder…", mustexist=True)
        #if mp3 files in top level of dir path arrrgh
        if dir_path:
            if focus in ['', 'I00001'] and \
                            [f for f in os.listdir(dir_path) \
                             if f[-4:] in ['.mp3', '.MP3']]:
                messagebox.showerror(\
                LOCALIZED_TEXT[lang]["Project can't hold '.mp3' files directly."], \
                LOCALIZED_TEXT[lang]["Add a collection first or use 'Add Folder...'."])
            else:
                self._disable_tabs()
                self.status['text'] = LOCALIZED_TEXT[lang]["Unpacking"] + dir_path
                qcommand.put(('ADD_CONTENTS', (focus, dir_path)))
        self.update_idletasks()



    def _on_move_up(self):
        """move item up one position within current collection"""
        qcommand.put(('MOVEUP', self.tree.focus()))

    def _on_move_down(self):
        """move item down one position within current collection"""
        qcommand.put(('MOVEDOWN', self.tree.focus()))

    def _on_promote(self):
        """promote item one level in the heirachy"""
        qcommand.put(('PROMOTE', self.tree.focus()))

    def _on_demote(self):
        """demote item one level in the heirachy"""
        qcommand.put(('DEMOTE', self.tree.focus()))

    def _on_merge(self):
        qcommand.put(('MERGE', self.tree.focus()))

    def _on_delete(self):
        """delete the current item selected in Treeview widget"""
        qcommand.put(('DELETE', self.tree.focus()))

    def _on_del_project(self):
        """Delete current project"""
        project = self.ddnCurProject.get()
        if project:
            if '.prj' not in project:
                project += '.prj'
            os.remove(self.Pub2SD + '/'+ project)
            self.list_projects = [f.rstrip('.prj') \
                                  for f in os.listdir(self.Pub2SD) \
                                                     if f.endswith('.prj')]
            self.ddnCurProject['values'] = self.list_projects
            if self.list_projects:
                self.ddnCurProject.set(self.list_projects[0])
            else:
                self.ddnCurProject.set('')


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
            if self.mode.get() and is_hashable(column):
                self.btnAppend['state'] = 'normal'
            else:
                self.btnAppend['state'] = 'disabled'

        self.update_idletasks()

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

    def _on_append(self):
        #                          focus,      column, text, location
        focus = self.tree.focus()
        if self.mode and is_hashable(self.ddnSelectTag.get().split(':')[0].upper()):
        #splitting 'get' on ':' and discarding all but the first str
            the_frames = self.etrTagValue.get().split('|')
            qcommand.put(('ON_APPEND', (focus, \
                                self.ddnSelectTag.get().split(':')[0].upper(), \
                                the_frames[0])))
            self.status['text'] = ''
            self.progbar['value'] = 0
            self.update_idletasks()

    def _on_set(self):
        '''set value of tag'''
        #                          focus,      column, text, location
        focus = self.tree.focus()
        #splitting 'get' on ':' and discarding all but the first str
        qcommand.put(('ON_SET', (focus, \
                            self.ddnSelectTag.get().split(':')[0].upper(), \
                            self.etrTagValue.get())))
        self.status['text'] = ''
        self.progbar['value'] = 0
        self.update_idletasks()


    def _on_select_artwork(self):
        '''select the cover art'''

        lang = self.ddnGuiLanguage.get()
        list_of_items = self.tree.selection()
        _picture_type = PICTURE_TYPE[self.ddnPictureType.get()]
        _desc = self.etrDescription.get()
        if list_of_items:
            fart = filedialog.askopenfilename(\
                        initialdir=os.path.expanduser('~'), \
                          filetypes=[('PNG files', '*.png'), \
                                     ('JPG files', '*.jpg')], \
                          title="Select PNG or JPG file…")
            #now replace windows backslashes with forward slashes
            fart = forward_slash_path(fart)
            if fart:
                for focus in list_of_items:
                    if self.mode.get() == 0:
                        qcommand.put(('ATTACH_ARTWORK_TO', \
                            (focus, PICTURE_TYPE['COVER_FRONT'], '', fart)))
                    else:
                        qcommand.put(('ATTACH_ARTWORK_TO', \
                                      (focus, _picture_type, _desc, fart)))
            else:
                #no file selected so blank apic if idiot
                if self.mode.get() == 0:
                    for focus in list_of_items:
                        qcommand.put(('ATTACH_ARTWORK_TO', \
                                      (focus, '', '', '')))
        else:
            messagebox.showwarning(LOCALIZED_TEXT[lang]['Select Artwork'], \
                          LOCALIZED_TEXT[lang]["no items selected"])
        self.update_idletasks()

    def _on_prepare_files(self):
        '''prepare files in temp folder'''

        lang = self.ddnGuiLanguage.get()
        self.project = self.ddnCurProject.get()

        #copy all file to Temp workarea
        self.status['text'] = LOCALIZED_TEXT[lang]['Copying all source ' +\
                                            'files to a working directory...']
        self._disable_tabs()
        self.update_idletasks()
#        print('PREPARE_FILES')
        qcommand.put(('PREPARE_FILES', None))

    def _on_prepare_files_continued(self):
        '''prepared files in temp folder, so now move to publish to...'''

        self.n.add(self.f5)
        self.n.select(5)

    def _on_publish_to_SD(self):
        """publish files and playlists to SDs"""
        self.usb_status = ['', '', '', '', '', '', '', '']
        qcommand.put(('PUBLISH_TO_SD', self.output_to))
        self.update_idletasks()

    def _on_publish_to_SD_continued(self):
        """feedback completed"""
        lang = self.ddnGuiLanguage.get()
        self._enable_tabs()
        self.progbar['value'] = 0
        self.update_idletasks()
        self.status['text'] = \
                   LOCALIZED_TEXT[lang]["Output to SD('s) completed."]
        self.update_idletasks()

    def _on_publish_to_HD(self):
        """publish files and playlists to your HD"""

        lang = self.ddnGuiLanguage.get()
        target = os.path.normpath(self.Pub2SD + '/' + \
                                  self.ddnCurProject.get() + '_SD')

        self.update_idletasks()
        qcommand.put(('PUBLISHFILES', target))
        self.status['text'] = LOCALIZED_TEXT[lang]["Output to HD completed."]
        self.update_idletasks()

    def _count_nodes(self, parent):
        '''count nodes'''
        for child in self.tree.get_children(parent):
            self.nodes += 1
            if self.tree.set(child, 'Type') == 'collection':
                self._count_nodes(child)


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
        self.rdbDisable['text'] = LOCALIZED_TEXT[lang]['Disable Normalization']

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

    def _change_lang_3(self, lang):
        '''change lang of labels to interfacelang'''

        self.btnGet['text'] = LOCALIZED_TEXT[lang]["Get"]
        self.btnSet['text'] = LOCALIZED_TEXT[lang]['Set']
        self.btnSet_ttp.text = LOCALIZED_TEXT[lang]['Set_ttp']
        self.btnAppend['text'] = LOCALIZED_TEXT[lang]['Append']
        self.btnAppend_ttp.text = LOCALIZED_TEXT[lang]['Append_ttp']
        self.btnGetDefault['text'] = LOCALIZED_TEXT[lang]['Get default']
        self.btnTrimTitle['text'] = LOCALIZED_TEXT[lang]['Trim Title']
        self.btnPub2SD['text'] = LOCALIZED_TEXT[lang]["Publish to SD/USB"]
        self.btnExit['text'] = LOCALIZED_TEXT[lang][\
                                        "Delete temporary files and exit."]
        project = self.ddnCurProject.get()
        self.btnPub2HD['text'] = \
            LOCALIZED_TEXT[lang]["Publish to '~\\Pub2SD\\{}_SD'"].\
                          format(project if project else "<project>")
        self.btnHTMLProject['text'] = LOCALIZED_TEXT[lang]["HTML"]
        self.btnHTMLProject_ttp.text = LOCALIZED_TEXT[lang]['HTML_ttp']
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

        self.update_idletasks()

def count_mp3_files_below(adir_path):
    """counts all mp3 files below given dir including subdirs"""
    matches = []
    for root, dirnames, filenames in os.walk(adir_path):
        for filename in fnmatch.filter(filenames, '*.mp3'):
            matches.append(os.path.join(root, filename))
    return len(matches)

def forward_slash_path(apath):
    '''replace all backslashes with forward slash'''
    return '/'.join(apath.split('\\'))

def on_copyright():
    """displays the copyright info when called from menubar"""
    messagebox.showinfo(\
                            "Pub2SDwizard v{}".format(THIS_VERSION), \
                            "©2016-2019 SIL International\n" + \
                            "License: MIT license\n" + \
                            "Web: https://www.silsenelgal.org\n" + \
                            "Email: Academic_Computing_SEB@sil.org\n\n" + \
                            "Powered by: mutagen\n" + \
                            "(https://mutagen.readthedocs.io/)")

def de_hex(tin):
    """turn hex string to int and return string"""
    tout = ''
    i = 0
    while i < len(tin) - 5:
        if tin[i:i+1] == 'Ox':
            tout += chr(int(tin[i:i+6], 16))
            i += 6
        else:
            tout += tin[i]
            i += 1
    tout += tin[i:]
    return tout

def delete_folder(path):
    '''if folder exists remove it'''
    if os.path.exists(path):
        # remove if exists
        shutil.rmtree(path)

def is_hashable(tag):
    '''return true if tag hashable'''
    return True in HASH_TAG_ON[tag]

# -*- coding: utf-8 -*-
"""
Created on Mon Apr  9 13:09:42 2018

@author: marks
"""
#import queue
import fnmatch
import threading
import os
import platform
import glob
import hashlib
import webbrowser
import codecs
import re
import ast
import shutil
import pickle
import json
import time
import zipfile

from urllib.parse import urlparse
from tkinter import messagebox
from pathlib import Path

from unidecode import unidecode
from pydub import AudioSegment
#import wand
#from twisted.internet import task, reactor

from lxml import etree

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


from  .myconst.regexs import FIND_LEADING_DIGITS, FIND_LEADING_ALPHANUM, \
                            FIND_TRAILING_DIGITS, TRIM_LEADING_DIGITS, \
                            TRIM_TRAILING_DIGITS, STRIPPERS, TAB, RETURN, \
                            NEWLINE, RETAB, RERETURN, RENEWLINE, \
                            DOUBLE_SPACE_TO_SINGLE, \
                            escape_tab_return_feed, unescape_tab_return_feed
from .myconst.readTag import IDIOT_TAGS, READ_TAG_INFO, HASH_TAG_ON

from .myconst.therest import THIS_VERSION, THE_IDIOT_P, THE_P, LATIN1, \
                            PICTURE_TYPE, TF_TAGS, URL_TAGS, SORT_TAGS#, PF,
from .myconst.localizedText import SET_TAGS, TRIM_TAG, DEFAULT_VALUES
from .myconst.webstuff import STARTHEADER, MAINTITLE, MYCSSAJAMI, MYCSSLATIN, \
                                SUMMARYCSSAJAMI, SUMMARYCSSLATIN, \
                                CLOSEHEADER, OPENNAVBAR, SUMMARYNAVBAR, \
                                ANAVLINK, FILECSSLATIN


from .myconst.audio import AUDIO
from .threads import MyThread



class Backend(threading.Thread):
    """handle processing files"""

    def __init__(self, qc, qr, aqr, scriptdir): #, tl):
        threading.Thread.__init__(self)
        self.threadID = 1
        self.name = 'backend'
        self.qc = qc
        self.qr = qr
        self.aqr = aqr
#        self.threadlock = tl
        self.exitFlag = 0
        self.mode = 0
        self.displayColumns = list()
        self.pref = list()
        self.pref_char = list()
        self.preferred = 0
        self.template = dict()
        self.hashed_graphics = dict()
        self.root = etree.Element('root')
        self.iids = list()
        self.recommendedTags = ['TIT2', 'TALB', 'TPE1', 'TPE2', 'TCOP', \
                                'APIC', 'TDRC', 'TRCK', 'TPOS', 'COMM', \
                                'TCON', 'TCOM']
        self.list_of_tags = set()
        self.next_iid = 1
        self.displayColumns = list()
        self.columns = list()
        self.to_be_renamed = dict()
        self.initial_digit = ''
        self.prefix = ''
        self.html_out = ''
        self.script_dir = scriptdir

        #bodge to get past WinPython....
        self.Pub2SD = Path(Path.home(), 'Pub2SD')
#        self.Pub2SD = os.path.normpath(os.path.expanduser('~') + '/Pub2SD')
#        if platform.system() == 'Windows':
#            temp = self.Pub2SD.split('\\')
#            self.Pub2SD = '\\'.join(temp[:3]) + '\\Pub2SD'

        self.selected_tags = list()
        self.project = ''
        self.next_track = 0
        self.nos_tracks = 0
        self.ishide = 0
        self.files = dict()
        self.M3UorM3U8 = 2
        self.output_to = list()
        self._command_queue = {'EXIT':self._EXIT, \
                     'SCRIPT_DIR':self._SCRIPT_DIR, \
                     'MODE':self._MODE, \
                     'INITIALDIGIT':self._INITIALDIGIT, \
                     'CONF_FILE':self._CONF_FILE, \
                     'LOAD_TEMPLATE':self._LOAD_TEMPLATE, \
                     'LOADTREEFROMTROUT':self._LOADTREEFROMTROUT, \
                     'MERGE':self._MERGE, \
                     'SELFPREF':self._SELFPREF, \
                     'DISPLAYCOLUMNS':self._DISPLAYCOLUMNS, \
                     'SELECTED_TAGS':self._SELECTED_TAGS, \
                     'STRIPTITLE':self._STRIPTITLE, \
                     'HASHEDGRAPHICS':self._HASHEDGRAPHICS, \
                     'ADD_FOLDER':self._ADD_FOLDER, \
                     'ADD_CONTENTS':self._ADD_CONTENTS, \
                     'ADD_COLLECTION':self._ADD_COLLECTION, \
                     'ADD_FILE':self._ADD_FILE, \
                     'CHILDRENS_FILENAMES':self._CHILDRENS_FILENAMES, \
                     'FOLDERSIZE':self._FOLDERSIZE, \
                     'PUBLISHFILES':self._PUBLISHFILES, \
                     'PREPARE_FILES':self._PREPARE_FILES, \
                     'ONSAVEPROJECT':self._ONSAVEPROJECT, \
                     'DELETE':self._DELETE, \
                     'MOVEUP':self._MOVEUP, \
                     'MOVEDOWN':self._MOVEDOWN, \
                     'PROMOTE':self._PROMOTE, \
                     'DEMOTE':self._DEMOTE, \
                     'ON_SET':self._ON_SET, \
                     'ON_APPEND':self._ON_APPEND, \
                     'ATTACH_ARTWORK_TO':self._ATTACH_ARTWORK_TO, \
                     'SETCOPYPLAYLISTS':self._SETCOPYPLAYLISTS, \
                     'M3UorM3U8':self._M3UorM3U8, \
                     'OUTPUT_TO':self._OUTPUT_TO, \
                     'PUBLISH_TO_SD':self._PUBLISH_TO_SD, \
                     'EXPORTHTML':self._EXPORTHTML, \
                     'DELETETEMP':self._DELETETEMP, \
                     'DIE_DIE_DIE':self._DIE_DIE_DIE, \
                     }


    def run(self):
        starttime = time.time()
        while not self.exitFlag:
            acommand = self.qc.get()
            if acommand[0]:
                if acommand[0] in self._command_queue.keys():
                    self._command_queue[acommand[0]](acommand[1])
                else:
                    self.qr.put(('PRINT', 'backend lost, acommand was {}'.\
                                 format(acommand)))
                self.qc.task_done()
            else:
                pass
            time.sleep(0.066 - ((time.time() - starttime) % 0.066))

#    def _scan_command_queue(self):
#        acommand = self.qc.get()
#        if 'EXIT' in acommand:
#            self.exitFlag = 1
#            self.qc.task_done()
#            # self.exitFlag can be set by error condition in backend
#        elif 'SCRIPT_DIR' in acommand:
#            self.script_dir = acommand[1]
##            self.qr.put(('PRINT',"received script_dir >{}<".format(self.script_dir)))
#            self.qc.task_done()
#        elif 'MODE' in acommand:
#            self.mode = acommand[1]
#            self.qc.task_done()
#        elif 'INITIALDIGIT' in acommand:
#            self.initial_digit = acommand[1].upper()
#            self.prefix = acommand[1]
#            self.qc.task_done()
#        elif 'CONF_FILE' in acommand:
##            self.qr.put(('PRINT', 'received CONF_FILE =>{}<'.format(acommand[1])))
#            self.qc.task_done()
#            self.project = acommand[1]
#            self._load_conf_file(acommand[1])
#        elif 'LOAD_TEMPLATE' in acommand:
##                self.template = acommand[1]
#            self._load_template(acommand[1])
#            self.qc.task_done()
#        elif 'LOADTREEFROMTROUT' in acommand:
#            self._on_reload_tree()
#            self.qc.task_done()
#        elif 'MERGE' in acommand:
#            self._on_merge_files(acommand[1])
#            self.qc.task_done()
#        elif 'SELFPREF' in acommand:
#            self.pref = acommand[1][0]
#            self.pref_char = acommand[1][1]
#            self.preferred = acommand[1][2]
#            self.template = acommand[1][3]
#            self.qc.task_done()
#        elif 'DISPLAYCOLUMNS' in acommand:
#            self.displayColumns, self.columns = acommand[1]
#            self.qc.task_done()
#        elif 'SELECTED_TAGS' in acommand:
#            map(self.sf1.attrib.pop, self.sf1.attrib.keys())
#            #put tag state into xml
#            self.selected_tags = acommand[1]
#            for i in range(0, len(self.selected_tags)):
#                self.sf1.attrib[self.selected_tags[i]] = 'show'
#            self.qc.task_done()
#        elif 'STRIPTITLE' in acommand:
##            to_strip, focus = acommand[1]
#            self._on_strip(acommand[1][0], acommand[1][1])
#            self.to_be_renamed = dict()
#            self._rename_children_of(acommand[1][1])
#            self.qr.put(('RENAME_CHILDREN', self.to_be_renamed))
#            self.qc.task_done()
#        elif 'HASHEDGRAPHICS' in acommand:
##                self.qr.put(('PRINT', 'running self._extract_hashed_graphics()'))
#            self.hashed_graphics = acommand[1]
##                self._extract_hashed_graphics()
#            self.qc.task_done()
#        elif 'ADD_FOLDER' in acommand:
#            self.qr.put(('LOCKGUI', None))
#            self.to_be_inserted = list()
##            the_focus, adir_path = acommand[1]
#            self.qr.put(('PROGMAX', count_mp3_files_below(acommand[1][1]) * 2))
#            self._add_tree(acommand[1][0], acommand[1][1], False)
#            self._on_reload_tree()
#            self._rename_children_of('I00001')
#            self.qr.put(('RENAME_CHILDREN', self.to_be_renamed))
#            self.qr.put(('STATUS', "Unpacking complete."))
#            self.qr.put(('PROGVALUE', 0))
#            self.qr.put(('UNLOCKGUI', None))
#            self.qc.task_done()
#        elif 'ADD_CONTENTS' in acommand:
#            the_focus, adir_path = acommand[1]
#            #if the_focus is I00001 then any .mp3 files in current folder
#            # would be directly below project. Need to have at least one
#            # collection in way
#            self.qr.put(('LOCKGUI', None))
#            self.qr.put(('PROGMAX', count_mp3_files_below(adir_path) * 2))
#            self.to_be_inserted = list()
#            self._add_tree(the_focus, adir_path, True)
##                self.qr.put(('PRINT', "about to reload_tree"))
#            self._on_reload_tree()
##                self.qr.put(('PRINT', "reloaded tree"))
#            self._rename_children_of('I00001')
#            self.qr.put(('RENAME_CHILDREN', self.to_be_renamed))
#            self.qr.put(('STATUS', "Unpacking complete."))
#            self.qr.put(('PROGVALUE', 0))
#            self.qr.put(('UNLOCKGUI', None))
#            self.qc.task_done()
#        elif 'ADD_COLLECTION' in acommand:
##            focus = acommand[1]
#            self.qr.put(('LOCKGUI', None))
#            self._add_collection(acommand[1])
#            self._on_reload_tree()
#            self.qr.put(('STATUS', "Unpacking complete."))
#            self.qr.put(('PROGVALUE', 0))
#            self.qr.put(('UNLOCKGUI', None))
#            self.qc.task_done()
#        elif 'ADD_FILE' in acommand:
##            focus, filenames = acommand[1]
#            self.qr.put(('LOCKGUI', None))
#            self.qr.put(('PROGMAX', len(acommand[1][1]) * 2))
#            self.to_be_inserted = list()
#            self._add_files(acommand[1][0], acommand[1][1])
#            self._on_reload_tree()
#            self.qr.put(('UNLOCKGUI', None))
#            self.qc.task_done()
#        elif 'CHILDRENS_FILENAMES' in acommand:
#            self.project_id, temp_path, project_path_ = acommand[1]
#            #self.project_id should be set to 'I00001', but for safety
#            self._childrens_filenames(self.trout.find(".//I00001"), \
#                                      temp_path, project_path_)
#        elif 'FOLDERSIZE' in acommand:
##            size_in_Mb = folder_size(\
##                str(Path(self.Pub2SD, 'Temp', self.project)))/(1024.0 * 1024.0)
#            self.qr.put(('FOLDERSIZE', \
#                         folder_size(str(Path(self.Pub2SD, \
#                                    'Temp', self.project)))/(1024.0 * 1024.0)))
#        elif 'PUBLISHFILES' in acommand:
#            self._on_publish_files(acommand[1])
#        elif 'PREPARE_FILES' in acommand:
#            self.qr.put(('LOCKGUI', None))
#            self._on_prepare_files()
#            self.qr.put(('UNLOCKGUI', None))
#        elif 'ONSAVEPROJECT' in acommand:
#            self._on_save_project(acommand[1])
#        elif 'DELETE' in acommand:
#            self._on_delete(acommand[1])
#        elif 'MOVEUP' in acommand:
#            self._on_move_up(acommand[1])
#        elif 'MOVEDOWN' in acommand:
#            self._on_move_down(acommand[1])
#        elif 'PROMOTE' in acommand:
#            self._on_promote(acommand[1])
#        elif 'DEMOTE' in acommand:
#            self._on_demote(acommand[1])
#            self._on_reload_tree()
#        elif 'ON_SET' in acommand:
#            self._on_set(acommand[1])
#        elif 'ON_APPEND' in acommand:
#            self._on_append(acommand[1])
#            self._on_reload_tree()
#        elif 'ATTACH_ARTWORK_TO' in acommand:
#            focus, _picture_type, _desc, artwork = acommand[1]
#            #hash it here, pass hash_tag and length
##            partwork = Path(artwork)
#            if artwork \
#                    and Path(artwork).exists() \
#                    and Path(artwork).suffix in ['.png', 'jpg',]:
##                    and os.path.exists(artwork) \
##                    and artwork[-4:] in ['.png', 'jpg',]:
##                    fart = codecs.open(artwork, mode='rb').read()
##                fart = Path(artwork).read_bytes()
#                hash_tag, length = self._hash_it(Path(artwork).read_bytes())
#                mime = 'image/' + artwork[-3:]
#                self._attach_artwork_to(focus, _picture_type, _desc, \
#                                        hash_tag, length, mime)
#                self._on_reload_tree()
#            else:
#                #clear tag
#                self._attach_artwork_to(focus, '', '', '', '', '')
#        elif 'SETCOPYPLAYLISTS' in acommand:
#            self.play_list_targets, self.is_copy_playlists_to_top = acommand[1]
#        elif 'M3UorM3U8' in acommand:
#            self.M3UorM3U8 = acommand[1]
#        elif 'OUTPUT_TO' in acommand:
#            self.output_to = acommand[1]
#        elif 'PUBLISH_TO_SD' in acommand:
#            self._on_publish_to_SD()
#        elif 'EXPORTHTML' in acommand:
#            self._export_to_html()
#        elif 'DELETETEMP' in acommand:
#            self.qr.put(('STATUS', \
#                    "Deleting temporary files, this may take a few minutes."))
#            self._delete_temp_folder()
#            self.qr.put(('DELETEDTEMP', None))
##            break
#        elif 'DIE_DIE_DIE' in acommand:
#            self.exitFlag = True
#            self.qr.put(('IM_OUT_OF_HERE', "I'm out of here!!!"))
##            for pq in self.aqr:
##                pq.clear()
##                    pq.close()
##                self.qc.close()
##                self.qr.close()
##
##            break
#
#        else:
#            self.qr.put(('PRINT', 'backend lost, acommand was {}'.\
#                         format(acommand)))
#            self.qc.task_done()

#    def _scan_command_queue(self):
#        acommand = self.qc.get()

    def _EXIT(self, dummy):
        self.exitFlag = 1

    def _SCRIPT_DIR(self, acommand):
        self.script_dir = acommand

    def _MODE(self, acommand):
        self.mode = acommand

    def _INITIALDIGIT(self, acommand):
        self.initial_digit = acommand.upper()
        self.prefix = acommand

    def _CONF_FILE(self, acommand):
        self.project = acommand
        self._load_conf_file(acommand)

    def _LOAD_TEMPLATE(self, acommand):
        self._load_template(acommand)

    def _LOADTREEFROMTROUT(self, _):
        self._on_reload_tree()

    def _MERGE(self, acommand):
        self._on_merge_files(acommand)

    def _SELFPREF(self, acommand):
        self.pref = acommand[0]
        self.pref_char = acommand[1]
        self.preferred = acommand[2]
        self.template = acommand[3]

    def _DISPLAYCOLUMNS(self, acommand):
        self.displayColumns, self.columns = acommand

    def _SELECTED_TAGS(self, acommand):
        map(self.sf1.attrib.pop, self.sf1.attrib.keys())
        #put tag state into xml
        self.selected_tags = acommand
        for i in range(0, len(self.selected_tags)):
            self.sf1.attrib[self.selected_tags[i]] = 'show'

    def _STRIPTITLE(self, acommand):
#            to_strip, focus = acommand[1]
        self._on_strip(acommand[0], acommand[1])
        self.to_be_renamed = dict()
        self._rename_children_of(acommand[1])
        self.qr.put(('RENAME_CHILDREN', self.to_be_renamed))

    def _HASHEDGRAPHICS(self, acommand):
        self.hashed_graphics = acommand

    def _ADD_FOLDER(self, acommand):
        self.qr.put(('LOCKGUI', None))
        self.to_be_inserted = list()
#            the_focus, adir_path = acommand[1]
        self.qr.put(('PROGMAX', count_mp3_files_below(acommand[1]) * 2))
        self._add_tree(acommand[0], acommand[1], False)
        self._on_reload_tree()
        self._rename_children_of('I00001')
        self.qr.put(('RENAME_CHILDREN', self.to_be_renamed))
        self.qr.put(('STATUS', "Unpacking complete."))
        self.qr.put(('PROGVALUE', 0))
        self.qr.put(('UNLOCKGUI', None))

    def _ADD_CONTENTS(self, acommand):
        the_focus, adir_path = acommand
        #if the_focus is I00001 then any .mp3 files in current folder
        # would be directly below project. Need to have at least one
        # collection in way
        self.qr.put(('LOCKGUI', None))
        self.qr.put(('PROGMAX', count_mp3_files_below(adir_path) * 2))
        self.to_be_inserted = list()
        self._add_tree(the_focus, adir_path, True)
        self._on_reload_tree()
        self._rename_children_of('I00001')
        self.qr.put(('RENAME_CHILDREN', self.to_be_renamed))
        self.qr.put(('STATUS', "Unpacking complete."))
        self.qr.put(('PROGVALUE', 0))
        self.qr.put(('UNLOCKGUI', None))

    def _ADD_COLLECTION(self, acommand):
        self.qr.put(('LOCKGUI', None))
        self._add_collection(acommand)
        self._on_reload_tree()
        self.qr.put(('STATUS', "Unpacking complete."))
        self.qr.put(('PROGVALUE', 0))
        self.qr.put(('UNLOCKGUI', None))

    def _ADD_FILE(self, acommand):
#            focus, filenames = acommand[1]
        self.qr.put(('LOCKGUI', None))
        self.qr.put(('PROGMAX', len(acommand[1]) * 2))
        self.to_be_inserted = list()
        self._add_files(acommand[0], acommand[1])
        self._on_reload_tree()
        self.qr.put(('UNLOCKGUI', None))

    def _CHILDRENS_FILENAMES(self, acommand):
        self.project_id, temp_path, project_path_ = acommand
        #self.project_id should be set to 'I00001', but for safety
        self._childrens_filenames(self.trout.find(".//I00001"), \
                                  temp_path, project_path_)
    def _FOLDERSIZE(self, _):
#            size_in_Mb = folder_size(\
#                str(Path(self.Pub2SD, 'Temp', self.project)))/(1024.0 * 1024.0)
        self.qr.put(('FOLDERSIZE', \
                     folder_size(str(Path(self.Pub2SD, \
                                'Temp', self.project)))/(1024.0 * 1024.0)))

    def _PUBLISHFILES(self, acommand):
        self._on_publish_files(acommand)

    def _PREPARE_FILES(self, _):
        self.qr.put(('LOCKGUI', None))
        self._on_prepare_files()
        self.qr.put(('UNLOCKGUI', None))

    def _ONSAVEPROJECT(self, acommand):
        self._on_save_project(acommand)

    def _DELETE(self, acommand):
        self._on_delete(acommand)

    def _MOVEUP(self, acommand):
        self._on_move_up(acommand)

    def _MOVEDOWN(self, acommand):
        self._on_move_down(acommand)

    def _PROMOTE(self, acommand):
        self._on_promote(acommand)

    def _DEMOTE(self, acommand):
        self._on_demote(acommand)
        self._on_reload_tree()

    def _ON_SET(self, acommand):
        self._on_set(acommand)

    def _ON_APPEND(self, acommand):
        self._on_append(acommand)
        self._on_reload_tree()

    def _ATTACH_ARTWORK_TO(self, acommand):
        focus, _picture_type, _desc, artwork = acommand
        #hash it here, pass hash_tag and length
#            partwork = Path(artwork)
        if artwork \
                and Path(artwork).exists() \
                and Path(artwork).suffix in ['.png', 'jpg',]:
#                    and os.path.exists(artwork) \
#                    and artwork[-4:] in ['.png', 'jpg',]:
#                    fart = codecs.open(artwork, mode='rb').read()
#                fart = Path(artwork).read_bytes()
            hash_tag, length = self._hash_it(Path(artwork).read_bytes())
            mime = 'image/' + artwork[-3:]
            self._attach_artwork_to(focus, _picture_type, _desc, \
                                    hash_tag, length, mime)
            self._on_reload_tree()
        else:
            #clear tag
            self._attach_artwork_to(focus, '', '', '', '', '')

    def _SETCOPYPLAYLISTS(self, acommand):
        self.play_list_targets, self.is_copy_playlists_to_top = acommand

    def _M3UorM3U8(self, acommand):
        self.M3UorM3U8 = acommand

    def _OUTPUT_TO(self, acommand):
        self.output_to = acommand

    def _PUBLISH_TO_SD(self, _):
        self._on_publish_to_SD()

    def _EXPORTHTML(self, _):
        self._export_to_html()

    def _DELETETEMP(self, _):
        self.qr.put(('STATUS', \
                "Deleting temporary files, this may take a few minutes."))
        self._delete_temp_folder()
        self.qr.put(('DELETEDTEMP', None))

    def _DIE_DIE_DIE(self, _):
        self.exitFlag = True
        self.qr.put(('IM_OUT_OF_HERE', "I'm out of here!!!"))



    def _delete_temp_folder(self):
        """delete the temporary folder"""
        temp = Path(self.Pub2SD, 'Temp')
        if temp.exists():
            shutil.rmtree(str(temp))
        self.qr.put(('STATUS', "Deleting old temporary folder."))

    def _load_conf_file(self, aconf_file):
        """loads the old project file into etree tree"""
#        self.qr.put(('PRINT', "In _load_conf_file"))
        result = ''
#        the_file = Path(self.Pub2SD, (aconf_file + '.prj'))
        if aconf_file and Path(self.Pub2SD, (aconf_file + '.prj')).is_file():
            result = self._load_project(\
                                str(Path(self.Pub2SD, (aconf_file + '.prj'))))
        else:
#            self.qr.put(("PRINT","Trying to create project"))
            result = self._create_project()
#            self.qr.put(("PRINT","Created project = {}".format(result)))
#        print("succeeded creating/loading project = {}".format(result))
        self.qr.put(('CONTINUE_F0_NEXT', result))

    def _load_template(self, template_path):
        """adds tags in template to tag tree displayed in f1,
           template_path is Path object"""
        tp = Path(template_path)
#        print(str(tp),tp, tp.exists())
        if tp.exists():
#            filein = codecs.open(template_path.resolve(), mode='r', encoding='utf-8')
            filein = codecs.open(str(tp), mode='r', encoding='utf-8')
#            filein = template_path.open(mode='r', encoding='utf-8')

#            fp = tp.open(mode='r', encoding='utf-8')
#            lotslines = tp.read_text(encoding='utf-8')
#            lines = lotslines.splitlines()
            lines = filein.readlines()

#            fp.close()
            filein.close()
            #load template to backend
            self.template = json.loads(''.join(lines))
            for atag in self.template.keys():
                self.qr.put(('SELECTIONTAGTREE', atag))
                self.sf1.attrib[atag] = 'show'
        else:
            #diagnostic only
            pass


    def _wait_for_responce(self):
        while True:
            if not self.qc.empty():
                aresponce = self.qc.get()
                if 'OKCANCEL' in aresponce:
                    return  aresponce[1]
                self.qc.task_done()

    def _get_idiot_case_mode_for_load_project(self):
        """calculate idiot_case"""
        #idiot_case
        #old_mode['idiot'] == 'True', new_mode=0  ==> 0, no change
        #old_mode['idiot'] == 'False', new_mode=0 ==> 1, downgrade
        #old_mode['idiot'] == 'True', new_mode=1 ==> 2, upgrade
        #old_mode['idiot'] == 'False', new_mode=1 ==> 3, no change
        if 'idiot' in self.old_mode:
            idiot_case = int(not self.old_mode['idiot'] == 'True') \
                                                + 2 * int(self.mode == 1)
        else:
            idiot_case = 0

        return idiot_case

    def _fix_old_proj_iid(self, parent):
        for child in list(parent):
            child.tag = 'I{:05X}'.format(int(child.tag[1:], 16))
            self._fix_old_proj_iid(child)

    def _load_project(self, thefile):
        """loads an existing project (.prj) file, adapting it's contents
                                      to the current Simple/Advanced choice"""
#        pthefile = Path(thefile)
        if not (Path(thefile).exists() and Path(thefile).is_file()): #no file specified so fail!
            return False

#        linesin = list()
#        filein = codecs.open(thefile, mode='r', encoding='utf-8')
#        for aline in filein.readlines():
#            if aline.strip():
#                linesin.extend([aline.strip()])
#        filein.close()
#        linesin = Path(thefile).read_text(encoding='utf-8').split()
        lines = ' '.join(Path(thefile).read_text(encoding='utf-8').split())
        self.root = etree.fromstring(lines)
        self.settings = self.root.find("settings")
        etree.strip_attributes(self.settings, ['template',])
        self.smode = self.settings.find("mode")
        #can't save project until after template already applied
        #so template setting is not needed
        self.sf1 = self.settings.find("f1")
        self.sf2 = self.settings.find("f2")
        self.sf4 = self.settings.find("f4")
        self.trout = self.root.find("tree")
        self._fix_old_proj_iid(self.trout)

        self.old_mode = dict(self.smode.attrib)
        if 'version' not in self.smode.attrib:
            self.qr.put(('MESSAGEBOXASKOKCANCEL', (\
                        'Project created in old format!', \
                        "This will attempt to update the project file " + \
                        "format to the current standard, every field " + \
                        "must be verified. It may be faster to " + \
                        "recreate the project from scratch. " +
                        "Do you wish to continue?")))
            if not self._wait_for_responce():
                return False
            self.smode.attrib['version'] = THIS_VERSION

            if 'idiot' in self.old_mode and self.old_mode['idiot'] == 'True':
                self._upgrade_child_of(self.trout)
        else:
            #data doesn't need upgrading
            pass
        if 'preferred' in self.smode.attrib:
            if self.smode.attrib['preferred'] == 'True':
                self.smode.attrib['preferred'] = '1'
#                self.preferred = 1
            elif self.smode.attrib['preferred'] == 'False':
                self.smode.attrib['preferred'] = '0'
#                self.preferred = 0
            self.preferred = int(self.smode.attrib['preferred'])
        else:
            self.preferred = 0
        #now pass self.preferred back to gui!
        self.qr.put(('PREFERRED', self.preferred))

        #now check the mode radio buttons
        idiot_case = self._get_idiot_case_mode_for_load_project()
        if idiot_case == 1: # downgrade
            self.mode = 0
            self.qr.put(('MESSAGEBOXASKOKCANCEL', ('Confirm Downgrade?', \
                        "This will downgrade this project from 'Advanced' " \
                        + "to 'Simple'. Some data may be lost.")))
            #if not OK give up
            if not self._wait_for_responce():
                return ''
            #do downgrade!
            #remove all non idiot tags
            difference = set(SET_TAGS['en-US'].keys()).\
                                            difference(set(IDIOT_TAGS.keys))
            etree.strip_attributes(self.trout, difference)
            etree.strip_attributes(self.sf1, difference)
#            pass
        elif idiot_case == 2: # upgrade:
            self.qr.put(('MESSAGEBOXASKOKCANCEL', ('Confirm Upgrade?', \
                        "This will upgrade this project from 'Simple' to " \
                        + "'Advanced'.")))
            #if not OK give up
            if not self._wait_for_responce():
                return ''
            self.mode = 1
        else:
            pass
        self.template = dict(self.sf1.attrib)

        if self.mode == 0:
            self.smode.attrib['Idiot'] = 'True'
            self.list_of_tags = list(set(IDIOT_TAGS.keys()))
            #so list_of_tags is a set of all idiot tags
            all_tags = self.recommendedTags + list(set(self.recommendedTags)\
                                        .difference(set(IDIOT_TAGS.keys())))
            #so all_tags now holds a LIST of recommended tags
            # followed by any idiot tags left out
        else:
            self.smode.attrib['Idiot'] = 'False'
            #so list_of_tags holds all advanced tags
            self.list_of_tags = list(set(SET_TAGS['en-US'].keys()))
            all_tags = self.recommendedTags + \
               list(set(self.recommendedTags).\
                                    difference(set(SET_TAGS['en-US'].keys())))
            #all_tags now holds a LIST of recommended tags
            # followed by any advanced tags left out
        self.preferred = int(self.smode.attrib['preferred'] == 'True')
        self.qr.put(('TXTPREFCHARDEL', (0.0, 9999.9999)))
        if self.sf2.text is not None:
            self.qr.put(('TXTPREFCHARINSERT', (9999.9999, self.sf2.text)))

        #clear tagtree
        self.qr.put(('CLEARTAGTREE', None))
        self.qr.put(('INSERTTAGTREETAGS', all_tags))
        self.qr.put(('SETTAGTREE', 'TIT2'))
        #now select tags
        for item in self.sf1.attrib.keys():
            self.qr.put(('SELECTIONTAGTREE', item))
        #f4 feature phone folders
        self.qr.put(('ENTERLIST', self.sf4.get('folderList')))
        if 'is_copy_playlists_to_top' in self.sf4.attrib:
            self.qr.put(('IS_COPY_PLAYLISTS_TO_TOP', \
                0 if self.sf4.attrib['is_copy_playlists_to_top'] == 'False' \
                else 1))
        if 'M3UorM3U8' in self.sf4.attrib:
            self.qr.put(('M3UorM3U8', int(self.sf4.attrib['M3UorM3U8'])))

        # unpickle hashed graphic
        if thefile[:-4]:
            picklein = thefile[:-4] + '.pkl'
            self.hashed_graphics = pickle.load(open(picklein, 'rb')) \
                                              if Path(picklein).is_file \
                                              else dict()
        return 'True'

    def _downgrade_child_of(self, parent, difference=None):
        for child in parent.getchildren():
            for tag in difference:
                child.attrib.pop(tag, None)
            self._downgrade_child_of(child)


    def _downgrade_data(self, item, child):
        """reduce all idiot tags to core data,
            (e.g. on a text frame, [3, ['astring', ]] becomes 'a string')
            chucking all advanced tabs
            N.B. this is for display purposes only!"""
        #by default data is unchanged unless is a file
        the_value = child.attrib[item]
        if item in ['Type', 'Name', 'Location',]:
            return child.attrib[item]
        if child.attrib['Type'] in ['file',]:
            #is file so process
            #idiot mode so split into frames on '|' and
            # pick last frame read for this tag
            this_frame = child.attrib[item].split('|')[-1]
            if this_frame not in ['-', '']:
                #not an 'empty' frame
                this_frame = escape_tab_return_feed(this_frame)
                if item in IDIOT_TAGS:
                    param = ast.literal_eval(str(this_frame))
                    if item == 'APIC':
                        result = param[-1]
                    elif item in TF_TAGS or item == 'COMM':
                        result = unescape_tab_return_feed(param[-1][0])
                    elif item in ['WCOM', 'WCOP', 'WOAF', 'WOAR', 'WOAS', \
                                  'WORS', 'WPAY', 'WPUB', 'WXXX']:
                        result = unescape_tab_return_feed(param[-1])
                    else:
                        result = this_frame
                    return result
                elif item in ['APIC_',]:
                    #never dowgrade this data
                    return this_frame
                else:
                    #not idiot tag so discard 'advanced' data
                    return ''
            else:# is 'empty' frame
                return this_frame
        return the_value

    def _upgrade_child_of(self, parent):
        for child in parent.getchildren():
            if child.attrib['Type'] not in ['project', 'collection']:
                for tag in child.attrib.keys():
                    self.list_of_tags.add(tag)
                    child.attrib[tag] = self._upgrade_data(tag, child)
            self._upgrade_child_of(child)

    def _upgrade_data(self, item, child):
        """smarten data up from simple(idiot) mode to advanced with encoding
           and full structure for each tag of the specified item.
                 e.g. on a text frame, 'a string' becomes [3, ['astring', ]]"""

        #for each frame in last value in the_values, smarten it up
        #hang on was idiot so single frames par tout
        #look up tag default value,
        a_frame = child.attrib[item]
        if child.attrib['Type'] not in ['collection', 'project']:
            #is file so process
            if item in DEFAULT_VALUES['ide3v24']:
                #insert text as appropriate
                if item == 'APIC':
                    if a_frame[-1][0:2] == 'b"' \
                                             or a_frame[-1][0:2] == "b'":
                        #is place holder
                        #grab APIC_, first frame!
                        this_frame = child.attrib['APIC_']
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
                        this_frame = '[3,"{}",{},"{}",{}]'.\
                                              format(param[1], int(param[2]), \
                                              '', _data)
                    else: #is string
                        #_encoding = 3
                        _mime = 'image/png' \
                                         if a_frame[-1][-4:] == '.png' \
                                                      else 'image/jpg'
                        #_type = 3
                        #_desc = ''
                        #add check file exists else break!!!!!
                        this_frame = '[3,"{}",3,"","{}"]'.\
                                              format(_mime, a_frame)
                elif item == 'TBPM':
                    packit = '["' + a_frame + '"]'
                    this_frame = DEFAULT_VALUES['ide3v24'][item].\
                                                    replace('["0"]', packit)
                else:
                    packit = '["' + a_frame + '"]'
                    this_frame = DEFAULT_VALUES['ide3v24'][item].\
                                                    replace('[""]', packit)
            elif item == 'APIC_':
                #and return to last value in the_values
                if a_frame:
                    outframe = list()
                    for aframe in a_frame.split('|'):
                        param = ast.literal_eval(aframe)
                        outframe.append('[3,"{}",3,"","{}"]'.\
                                                  format(param[1], param[4]))
                    this_frame = '|'.join(outframe)
                else:
                    this_frame = ""
            else:
                this_frame = a_frame
        else:
            this_frame = a_frame
        return this_frame

    def _upgrade_text(self, item, text):
        """smarten data up from simple(idiot) mode to advanced with encoding
           and full structure for each tag of the specified item.
                 e.g. on a text frame, 'a string' becomes [3, ['astring', ]]
            item is tag, text holds current 'frame'."""

        #for each frame in last value in the_values, smarten it up
        #hang on was idiot so single frames par tout
        #look up tag default value,
        if item in DEFAULT_VALUES['ide3v24']:
            #insert text as appropriate
            a_frame = DEFAULT_VALUES['ide3v24'][item]
            a_frame = a_frame.replace('[""]', '["{}"]'.format(text))
            return a_frame
        else:
            return text

    def _create_project(self):
        """create new project"""
#        print("in _create_project")
        #create new project tree, throwing away any existing tree
        self.root = etree.Element('root')
        #add child 'settings', all user configurable bits under here
        self.settings = etree.SubElement(self.root, "settings")
        self.smode = etree.SubElement(self.settings, "mode")
        self.sf0 = etree.SubElement(self.settings, "f0")
        self.sf1 = etree.SubElement(self.settings, "f1")
        self.sf2 = etree.SubElement(self.settings, "f2")
        self.sf4 = etree.SubElement(self.settings, "f4")
        self.trout = etree.SubElement(self.root, "tree")

        first_node = etree.SubElement(self.trout, "I00001")
        first_node.attrib['Type'] = 'project'
        first_node.attrib['Name'] = ''
        first_node.attrib['Location'] = ''
        first_node.text = self.project
        self.next_iid = 2

        self.template = dict()
        #                               idiot                  not idiot
        self.smode.attrib['idiot'] = 'True' \
                         if self.mode == 0 else 'False'
        self.smode.attrib['preferred'] = 'False' \
                         if self.preferred == 0 else 'True'
        self.smode.attrib['version'] = THIS_VERSION
        self.old_mode = dict(self.smode.attrib)

        if self.mode == 0:
            self.list_of_tags = self.list_of_tags.union(set(IDIOT_TAGS.keys()))
        else:
            self.list_of_tags = self.list_of_tags.union(\
                                                set(SET_TAGS['en-US'].keys()))
        self.qr.put(('INSERTTAGTREETAGS', self.list_of_tags))

        for atag in self.recommendedTags:
            self.sf1.attrib[atag] = 'show'
        self.qr.put(('SELECTIONTAGTREE', self.recommendedTags))

        self.sf2.text = ''

        self.sf4.attrib['folderList'] = ''
        self.sf4.attrib['is_copy_playlists_to_top'] = 'False'
        self.sf4.attrib['M3UorM3U8'] = '2'
#        print("created project, returning 'True'")
        return 'True'

    def _load_tree_from(self, _trout):
        if not _trout:
            tree = self.trout
            parent = ''
        else:
            tree = self.trout.find(".//" + _trout)
            parent = tree.tag
#        self.qr.put(('PRINT', etree.tostring(tree, pretty_print=True)))
#        if len(tree):

#        self.qr.put(('PRINT', 'load >{}< children of >{}<'.\
#                     format(len(tree.getchildren()), parent)))
#        self.qr.put(('PRINT', 'list children >{}<'.format(list(tree.getchildren()), parent)))
#        self.qr.put(('PRINT', 'list children >{}<'.\
#                     format([c.tag for c in tree.getchildren()], parent)))
#        if len(tree.getchildren()) and tree.getchildren()[0].tag != parent:
        if tree.getchildren() and tree.getchildren()[0].tag != parent:
            for child in tree.getchildren():
#                self.qr.put(('PRINT', 'for child>{}< of >{}<'.format(child.tag, parent)))
                vout = list()
                for k in self.columns:
                    if k not in ['adummy', 'APIC_'] and k in child.attrib:
                        if self.mode: #is advanced
                            vout.append(child.attrib[k])
                        else: #is idiot
                            data = self._downgrade_data(k, child)
                            vout.append(data)
                    else:
                        vout.append('-')
                self.to_be_inserted.append([child.tag, \
                            [parent, vout, child.text if child.text else '']])
                if child.attrib['Type'] in ['project', 'collection']:
                    self._load_tree_from(child.tag)


    def _on_save_project(self, thisproject):
        """save current project, thisproject is full path in str"""
        aproject = Path(thisproject)
        if aproject.exists():
#            os.remove(aproject)
            aproject.unlink()

        if aproject:
            output = aproject.open(mode='w', encoding='utf-8')
            output.write(etree.tostring(self.root, encoding='unicode', \
                                         pretty_print=True))
            output.close()
            pickleout = Path(thisproject[:-4] + '.pkl')
            pout = pickleout.open('wb')
            pickle.dump(self.hashed_graphics, pout, pickle.HIGHEST_PROTOCOL)
            # list projects in Pub2SD and update list in self.ddnCurProject
            pout.close()
            self.qr.put(('LISTPROJECTS', aproject.stem))
#            self.qr.put(('LISTPROJECTS', os.path.basename(aproject[:-4])))
        else:
            pass


    def _add_collection(self, focus):
        node = self.trout.find(".//" + focus)
        iid = "I{:05X}".format(self.next_iid)
        self.next_iid += 1
        sub = etree.SubElement(node, iid)
        sub.text = 'collection'
        sub.attrib['Type'] = 'collection'
        sub.attrib['Name'] = ''
        sub.attrib['TIT2'] = ''

    def _add_files(self, focus, filenames):
        node = self.trout.find(".//" + focus)
        for afile in filenames:
            self.qr.put(('STATUS{}', ('Unpacking {}', afile)))
            self._add_a_file(afile, node)
            self.qr.put(('PROGSTEP', 1))

    def _add_a_file(self, afile, e_parent, values=''):
        """loads a file into e_parent within self.trout"""
        #always hold data in advanced form, only choose to diplay as idiot
        if values:
            somevalues = values
        else:
            somevalues = self._read_mp3_tags(afile)
        iid = "I{:05X}".format(self.next_iid)
        self.next_iid += 1
#        self.qr.put(('PRINT', 'inserting iid ={} and next iid {}'.format(iid, self.next_iid)))
        self.to_be_inserted.append([iid, [e_parent.tag, somevalues, 'file']])
        e_child = etree.SubElement(e_parent, iid)
        e_child.text = 'file'
        for c, v in zip(self.columns, somevalues):
            e_child.attrib[c] = v

    def _add_tree(self, the_focus, adir_path, noTop=False):
        """add folder and dependants, with or without creating a new
           collection of the same name as the folder at the current focus
           in the Treeview widget"""

        if noTop:
            thisdir = the_focus
            e_parent = self.trout.find(".//" + the_focus)
#            self.qr.put(('PRINT', 'noTop =True, e_parent = {}'.\
#                         format(e_parent.tag)))
        else:
            vout = ['collection', '-', '-']
            if 'TIT2' in self.displayColumns:
#                vout.extend([self._my_unidecode(os.path.split(adir_path)[-1]),])
                vout.extend([self._my_unidecode(Path(adir_path).name),])
            vout.extend(['-' for item in self.displayColumns[2:-1]])
#            self.qr.put(('PRINT', 'next iid ={}'.format(self.next_iid)))
            iid = "I{:05X}".format(self.next_iid)
            self.next_iid += 1
            self.to_be_inserted.append([iid, [the_focus, vout, 'collection']])
#            self.qr.put(('PRINT', 'to be inserted ={}'.\
#                         format(self.to_be_inserted[-1])))
            thisdir = iid
#            e_focus = self.trout.find(".//" + the_focus)
            e_parent = etree.SubElement(self.trout.find(".//" + the_focus), iid)
            e_parent.text = 'collection'
#            self.qr.put(('PRINT', 'e_focus {}, e_parent {}, text {}'.\
#                         format(e_focus.tag, e_parent.tag, e_parent.text)))
#            self.qr.put(('PRINT', self.columns))
#            self.qr.put(('PRINT', vout))
            for c, v in zip(self.columns, vout):
                e_parent.attrib[c] = v
#            self.qr.put(('PRINT', 'got past c,v, added {}'.\
#                                    format(e_parent.tag)))

        _ff = dict()
        flist = dict()
        #step through a list of filepaths for all mp3 files in current dir only
        for f_ in [forward_slash_path(afile) \
                   for afile in glob.glob(adir_path + '/*.mp3')]:
            _pf = Path(f_)
            _ff[sort_key_for_filenames(_pf.stem)] = \
                                                    _pf.stem
            flist[_pf.stem] = f_
#        self.qr.put(('PRINT', 'got past f_'))

        for _ll in sorted(_ff):
            self._add_a_file(flist[_ff[_ll]], e_parent)
            self.qr.put(('PROGSTEP', 1))
#            self.qr.put(('PRINT', 'got past add a file'))

        # recurse through sub-dirs
        for adir in sorted([os.path.normpath(adir_path + '/' + d) \
                            for d in os.listdir(adir_path) \
                                if os.path.isdir(adir_path + '/' + d) \
                                            and len(d) > 0]):
#            self.qr.put(('PRINT', 'Unpacking{}'.format(adir)))
            self.qr.put(('STATUS{}', ('Unpacking{}', adir)))
            self._add_tree(thisdir, adir)
#            self.qr.put(('PRINT', ' added {}'.format(adir)))

    def _rename_children_of(self, parent):
        """rename all the children of parent, parents name is unchanged.
           Typicaly will always call on the top level project collection"""
        #rename all branches
        e_parent = self.trout.find(".//" + parent)
        if e_parent is None:
            return
        parent_attribs = e_parent.attrib
#        children = list(e_parent)
        children = e_parent.getchildren()
#        ancestor_name = parent_attribs['Name']
        my_isalpha = True
        if parent_attribs['Name']:
            if parent_attribs['Name'][-1] == '@':
                my_name = '@'
            else:
                my_name = 1
                my_isalpha = parent_attribs['Name'][-1].isdecimal()
        else:
            my_name = 1
            if self.initial_digit:
                my_isalpha = self.initial_digit[-1].isdecimal()
            else:
#                my_name = 1
                my_isalpha = False
        my_num = 1

        if my_name == 1:
            nos_chars = len(to_alpha(len(children)))
            nos_digits = (len(str(len(children)))-1)
        else:
            nos_chars = 0
            nos_digits = 0

        the_format = '{0:0' + '{}'.format(nos_digits) + 'd}'
        alpha_format = '{0:A>' + '{}'.format(nos_chars) + 's}'

        for child in children:
            self.qr.put(('PROGSTEP', 1))
            #bullet proofed in to_aplpha() so not exceed limit of single digit
            my_str = alpha_format.format(to_alpha(my_name - 1)) \
                             if my_isalpha else the_format.format(my_name)
            vout = list()
            if child.attrib['Type'] == 'collection':
                title = self._my_unidecode(child.attrib['TIT2'])
                #strip out any unapproved punctuation - done in my_unidecode
                child.attrib['Name'] = parent_attribs['Name'] + my_str
                child.text = "{0}{1}{2}-{3}".format(self.prefix, \
                                               parent_attribs['Name'], \
                                               my_str, title)
#                vout = [['Name', child.attrib['Name']], ['TIT2', title]]
                self.to_be_renamed[child.tag] = [\
                        [['Name', child.attrib['Name']], ['TIT2', title]], \
                        child.text]
                my_name += 1
                self._rename_children_of(child.tag)
            else: #is file so use
                size = os.path.getsize(child.attrib['Location']) \
                                if child.attrib['Location'] != '-' \
                                else 0
                if size == 0:
                    #fetch location, trim off path and '.mp3' extension,
                    #transliterate unicode(utf-8) to 7-bit ascii or Latin-1?
#                    title = self._my_unidecode(os.path.basename(\
#                                            child.attrib['Location'][:-4]))
                    title = self._my_unidecode(\
                                        Path(child.attrib['Location'].stem))
                    #transliterate unicode(utf-8) to 7-bit ascii or Latin-1?
                    #replace spaces and punctuation  - done in my_unidecode
                    child.attrib['Name'] = parent_attribs['Name'] + my_str
                    child.text = "{0}{1}{2}-{3}".format(self.prefix, \
                                   parent_attribs['Name'], my_str, title)
                    vout = [['Name', child.attrib['Name']], ['TIT2', title]]
                else: #idiot/not idiot always downgrade TIT2 to form title
#                    tit2 = self._downgrade_data('TIT2', child)
#                    title = self._my_unidecode(tit2)
                    child.attrib['Name'] = "{0}-{1:02d}".format(\
                                parent_attribs['Name'], my_num)
                    child.text = "{0}{1}-{2:02d}-{3}".format(self.prefix, \
                                        parent_attribs['Name'], my_num, \
                                         self._my_unidecode(\
                                        self._downgrade_data('TIT2', child)))
                    if self.mode: #advanced
                        vout = [['Name', child.attrib['Name']],\
                                               ['TIT2', child.attrib['TIT2']]]
                    else: #simple
                        vout = [['Name', child.attrib['Name']], ['TIT2', \
                                self._downgrade_data('TIT2', child)]]
                self.to_be_renamed[child.tag] = [vout, child.text]
                my_num += 1
            self.qr.put(('PROGSTEP', 1))


    def _my_unidecode(self, text):
        """normalize strings to avoid unicode character which won't display
           correctly or whose use in filenames may crash filesystem"""
        l = list()
#        self._fix_eng_bug_in_unidecode()
        if self.preferred == 0:
            self.pref = list()
            #aggresively normalize
        elif self.preferred == 1:
            #use preferred list to normalize
            pass
        elif self.preferred == 2:
            #normalization disabled
            return text
        else:
            self.qr.put(('PRINT', \
                         "Error, unrecognised value for " + \
                         "self.preferred=>{}< should be [0, 1, 2]".
                         format(self.preferred)))
            return text
        self._fix_eng_bug_in_unidecode()
        #got this far so either aggressive with 'empty' list or used preferred
        #scan list of preferred character/string pairs
        for kv in self.pref:# in range(0,len(text)):
            #build list of all hits in text
            l.extend([[m.start(), len(kv[0]), kv[1]] \
                       for m in kv[2].finditer(text)])
        if l:
            #now sort list of hits into sequence order
            l = sorted(l, key=lambda student: student[0])
            result = ''
            s = 0
            for ll in l:
                #from end of last match to
                #start of new match + new match aggress
                result += ''.join([c if c.isalnum() or \
                                        c in self.pref_char \
                                        else '_' \
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
            result = ''.join([c if c.isalnum() or c in self.pref_char else '_' \
                            for c in unidecode(text)])
        return result

    def _fix_eng_bug_in_unidecode(self):
        if 'ŋ' not in [v[0] for v in self.pref]:
            self.pref.append(['ŋ', 'ng', re.compile('ŋ')])
        if 'Ŋ' not in [v[0] for v in self.pref]:
            self.pref.append(['Ŋ', 'Ng', re.compile('Ŋ')])
        if "'" not in [v[0] for v in self.pref]:
            self.pref.append(["'", '-', re.compile("'")])
        if "-" not in [v[0] for v in self.pref]:
            self.pref.append(["-", '-', re.compile("-")])

    def _hash_it(self, artworkdata):
        """put artworkdata (is bytes) into hashedgraphics
        and return hashtag and length str"""
        #so open artwork read in as bytes
        m = hashlib.sha256(artworkdata)
        length = "b'{}Kb'".format(int(len(artworkdata)/1024 + 0.5))
        #so if the hash not a key in hashed_graphics, add it
        if m.hexdigest() not in self.hashed_graphics:
            self.hashed_graphics[m.hexdigest()] = artworkdata
        return m.hexdigest(), length

    def _read_mp3_process_atag(self, atag, k, apic_params, filepath):
        """process the (advanced) mp3 tag"""
        #force utf8 encoding, which is the form all text is held in internally
        atag.encoding = 3

        theParameters = None
        if k == 'APIC':
            hash_tag, length = self._hash_it(atag.data)
            theParameters = [int(atag.encoding), atag.mime, \
                             int(atag.type), atag.desc, \
                               hash_tag]
            #There may be multiple APIC tags in a file
            # displayed in APIC as multiple frames in sequence order
            #the hash tag for each frame will be held as part of a frame
            #in APIC_ in the corresponding order
            apic_params.extend([str(theParameters)])
            theParameters[4] = length
        elif k in THE_P:
            theParameters = THE_P[k](atag, True)
        else:
            self.qr.put(('MESSAGEBOXSHOWERRORIN', \
                         ('Error in read_mp3_process atag()', \
                "{} is unrecognized  MP3 tag in {}".format(atag, filepath))))
        return theParameters

    def _read_mp3_tags(self, filepath):
        """read in an mp3 files tags to Treeview wiget"""
        if os.path.getsize(filepath) > 0:
            audio = ID3(filepath)
            result = ['file', '', filepath]
            apic_params = list()
            for k in self.displayColumns[2:-1]:
                #list all instances of that tag
                list_tags = audio.getall(k)
                aresult = list()
                if k in ['COMM',]:
                    langs = ['XXX', 'eng', 'fra', 'por']
                    comms = dict()
                    xresult = list()
                if list_tags: #not an empty list!
                    for atag in list_tags:
                        #now for each tag instance...
                        theParameters = \
                                self._read_mp3_process_atag(atag, k, \
                                                        apic_params, filepath)
                        #accumulate COMM tags in comms all others in aresult
                        if k in ['COMM',] and theParameters:
                            if theParameters[1] in comms.keys():
                                comms[theParameters[1]][theParameters[1] + \
                                      theParameters[2]] = theParameters
                            else:
                                comms[theParameters[1]] = dict()
                                comms[theParameters[1]][theParameters[1] + \
                                      theParameters[2]] = theParameters
                        elif theParameters:
                            aresult.extend([str(theParameters)])
                    #now if idiot mode choose one frame and force lang='XXX'
                    #   choice if more than one pick first XXX,
                    #                       if no XXX pick first eng,
                    #                       if no eng pick first fra,
                    #                       if no fra pick first
                    # else if advanced mode list langs
                    if k in ['COMM',]:
                        for l in langs:
                            if not xresult and l in comms.keys():
                                keylist = sorted(comms[l].keys())
                                xresult = comms[l][keylist[0]]
                                xresult[0] = 3
                                xresult[1] = 'XXX'
                                for y in keylist:
                                    this = [3, \
                                            'XXX', \
                                            comms[l][y][2], \
                                            comms[l][y][3]]
                                    aresult.append(this)
                            elif l in comms.keys():
                                keylist = sorted(comms[l].keys())
                                for y in keylist:
                                    this = [3, \
                                            comms[l][y][1], \
                                            comms[l][y][2], \
                                            comms[l][y][3]]
                                    aresult.append(this)
                        for l in sorted(set(comms.keys()).\
                                        difference(set(langs))):
                            keylist = sorted(comms[l].keys())
                            if not xresult:
                                xresult = comms[l][keylist[0]]
                                xresult[0] = 3
                                xresult[1] = 'XXX'
                                for y in keylist:
                                    this = [3, \
                                            'XXX', \
                                            comms[l][y][2], \
                                            comms[l][y][3]]
                                    aresult.append(this)
                            else:
                                for y in keylist:
                                    this = [3, \
                                            comms[l][y][1], \
                                            comms[l][y][2], \
                                            comms[l][y][3]]
                                    aresult.append(this)
                        if not self.mode:
                            aresult = [xresult,]
                    result.append('|'.join([str(s) for s in aresult]))
                else:
                    title = Path(filepath).stem
                    result.append('[3, ["{}"]]'.format(title.strip())\
                                         if k == 'TIT2' else '-')
                if k in self.template.keys() and self.template[k] \
                                                         and result[-1] == '-':
                    result[-1] = DEFAULT_VALUES['ide3v24'][k].\
                                    replace('[""]', '["{}"]'.\
                                            format(self.template[k]))
            #now add empty string for 'adummy' column
            result.extend(['',])
            #add HIDDEN column to hold full APIC data if present!
            if apic_params:
                result.extend(['|'.join(apic_params)])
            for index in range(0, len(self.displayColumns)):
                if self.displayColumns[index] in self.template.keys() and \
                               self.template[self.displayColumns[index]] != "":
                    result[index].replace('-', \
                              self.template[self.displayColumns[index]])
        else: #zero length file No Tags!
            result = ['file', '', filepath]
            if 'TIT2' in self.displayColumns[1:-1]:
                result.extend(['[3, ["{}"]]'.format(Path(filepath).stem)])
        return result

    def _childrens_filenames(self, e_parent, temp_path, project_path_):
        '''form childrens file names'''
        tp = Path(temp_path)
        pp = Path(project_path_)
        children = e_parent.getchildren()
        for e_child in children:
            new_dir = e_child.text
            attributes = e_child.attrib

            if attributes['Type'] == 'collection':
#                thispath = os.path.normpath(temp_path + '/' + new_dir)
#                final_path = os.path.normpath(project_path_ + '/' + new_dir)
                thispath = str(tp / new_dir)
                final_path = str(pp / new_dir)
                os.makedirs(thispath, mode=0o777, exist_ok=True)
                self._childrens_filenames(e_child, thispath, final_path)
            else: #is file
                title = e_child.text.strip()
                thispath = str(tp / (title + '.mp3'))
                thatpath = str(pp / (self._my_unidecode(title) + '.mp3'))
                if ('APIC' in self.displayColumns) and \
                                            ('APIC' in attributes.keys()):
                    #                   [temp path,
                    #                   source path,
                    #                   Apic,
                    #                   target, ?,
                    #                   title,
                    #                   prefix]
                    self.files[e_child.tag] = [thispath, \
                                          attributes['Location'], \
                                          attributes['APIC'], \
                                          thatpath, '', \
                                          attributes['TIT2'], \
                                          attributes['Name']]
                else:
                    self.files[e_child.tag] = [thispath, \
                                  attributes['Location'], \
                                  '', \
                                  thatpath, \
                                  '', \
                                  attributes['TIT2'] \
                                  if 'TIT2' in attributes.keys() \
                                  else Path(attributes['Location']).stem, \
                                  attributes['Name']]

    def _on_prepare_files(self):
        '''prepare files in temp folder'''
#        print('prepare files in temp folder')
        self._extract_hashed_graphics()
#        print('extracted graphics')
        self.qr.put(('PROGMAX', len(self.files)))
        for child in [self.trout.find(".//" + c) \
                      for c in sorted(self.files.keys())]:
            self.qr.put(('STATUS{}', ('Preparing =>{}', \
                         self.files[child.tag][1])))
            #   copy            from source location           to temp location
            shutil.copyfile(self.files[child.tag][1], self.files[child.tag][0])
            if int(os.path.getsize(self.files[child.tag][1])) > 0:
                #load mp3 tags
                audio = ID3(self.files[child.tag][0])#, ID3=ID3)
                #read tags into tree - read when file first selected

                try:
                    audio.delete()
                    audio.save()
                except:
                    self.qr.put(('MESSAGEBOXERROR', ('No ID3 tag', \
                                                    self.files[child.tag][0], \
                                            "so it's not a valid MP3 file.")))
                    self.qr.put(('STATUS', 'Preparation of files aborted.'))
                    return
                audio.update_to_v23()
                for k in self.displayColumns[2:-1]:
                    #typically of form '[3,[""]]'
                    thetags = child.attrib[k].split('|')
                    self._preparing_file_scaning_for_tags(child, k, audio, \
                                                                      thetags)
                #now save back to file
                audio.save(self.files[child.tag][0], v1=0, v2_version=3)
                #now discover length
                audio_len = MP3(self.files[child.tag][0])
                self.files[child.tag][4] = int(audio_len.info.length +0.5)
            else:
                #is a zero length file! So...
                pass
            self.qr.put(('PROGSTEP', 1))
        self.qr.put(('STATUS', 'Files prepared.'))
        self._on_generate_playlists()
        self.qr.put(('FILES_PREPARED', None))
        self.qr.put(('UNLOCKGUI', None))

    def _preparing_file_scaning_for_tags_idiot_mode(self, atag, child):
        """preparing file scaning for tags idiot mode"""
        #idiot so just one front cover
        if atag[0:2] in ["b'", 'b"']:
            #is bytes
            apic_params = child.attrib['APIC_'].split('|')
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
                self.qr.put(('MESSAGEBOXSHOWERRORLOSTGRAPHIC', (\
                            "Can't find graphic in hashed_graphics", \
                            "lost saved graphic for {}.".\
                            format(child.text))))
                _data = None
        else:
            #is string
            _encoding = 3
            _mime = 'image/png' \
                    if atag[-4:] == '.png' \
                    else 'image/jpg'
            _type = 3
            _desc = ''
            #add check file exists else break!!!!!
#            _data = open(os.path.normpath(atag), \
#                                     'rb').read()
            if Path(atag).exists():
                _data = Path(atag).read_bytes()
            else:
                return
        return [_encoding, _mime, _type, _desc, _data]

    def _preparing_file_scaning_for_tags_advanced_mode(self, \
                                atag, child, picture_type_1_2, thetags):
        """preparing file scaning for tags advanced mode"""
        #not idiot
        param = ast.literal_eval(atag)
        _encoding = int(param[0])
        _mime = param[1]
        _type = int(param[2])
        if picture_type_1_2:
            if _type in [1, 2]:
                self.qr.put(('MESSAGEBOXSHOWWARNINGMULTPLEFILEICONS', \
                             ('MultpleFileIcons', self.files[child.tag][0])))
            else:
                picture_type_1_2 = True
        _desc = param[3]
        #if placeholder "b'...'" use saved data else load file
        tindex = thetags.index(atag)
        if param[4][0:2] in ['b"', "b'"]:
            apic_params = child.attrib['APIC_'].split('|')

            para = ast.literal_eval(\
                            apic_params[tindex])
            if para[4] in self.hashed_graphics:
                _data = \
                self.hashed_graphics[para[4]]
            else:
                #error message? Can't find graphic
                #in hashed_graphics so return?
                self.qr.put(('MESSAGEBOXSHOWERRORLOSTGRAPHIC', (\
                            "Can't find graphic in hashed_graphics", \
                            "lost saved graphic for {}.".\
                            format(child.text))))
                _data = None
        elif param[4] in ['-',]:
            _data = None
        else:
            if Path(param[4]).exists():
                _data = Path(param[4]).read_bytes()
            else:
                _data = None
                self.qr.put(('MESSAGEBOXERROR', (\
                            "Can't find artwork.", \
                            "Can't find image for", child.text, \
                            "file may have been moved or no longer exists.")))

        return [_encoding, _mime, _type, _desc, _data]



    def _p_f_s_f_t_process_apic(self, child, audio, thetags):
        """add the APIC tag and data to the audio file"""
        picture_type_1_2 = False
        for atag in thetags:
            if atag != '-' and atag != '#':
                # is not empty so add it!
                _encoding, _mime, _type, _desc, _data = \
                       self._preparing_file_scaning_for_tags_advanced_mode(\
                            atag, child, picture_type_1_2, thetags)
                if _data:
                    audio.add(APIC(_encoding, _mime, _type, \
                               _desc, _data))

    def _preparing_file_scaning_for_tags(self, child, k, audio, thetags):
        """process tag for on_prepare_files"""

        if k == "APIC":
            self._p_f_s_f_t_process_apic(child, audio, thetags)
        else:
            list_owners = list()
            #list_owners is used by exec(PF['ENCR']) and exec(PF['GRID']),
            #these tags may have multiple entries with different owners
            #specified
            for atag in thetags:
                if atag != '-':
                    # is not empty so add it!
                    lang = None
                    if k in AUDIO:
                        #insert test if tit2, if so insert prefix to atag
                        if k == 'TIT2':
                            #atag is [3,['text']]
                            index = atag.find('[', 1)
                            if index > -1:
#                                index += 1
                                index += 2
                                atag = '{}{}-{}'.format(atag[:index], \
                                                    self.files[child.tag][6], \
                                                    atag[index:])

                        atuple = (audio, atag, (self.mode != 0), \
                                  list_owners, self.files[child.tag][0])
                        AUDIO[k](atuple)
                    else:
                        self.qr.put((\
                                "MESSAGEBOXSHOWERRORERRORINON_PREPARE_FILES", \
                                ('Error in on_prepare_files()', \
                                             '>{}< is unrecognized tag'.\
                                             format(k))))

    def _on_publish_files(self, target):
        """copy files to final destination,
        opening all files,
        copying all files
        then closing all files.
        To ensure same creation date and last modified date for all files.
        So that they will only sort in the order specified."""

        #finally copy all file to final destination):
        self.qr.put(('STATUS', 'Removing any old project files...'))
        if target[1:] != ':\\' and \
                 Path(target, self.project).exists():
            # remove if exists
#            shutil.rmtree(os.path.normpath(target + '/' + self.project))
            shutil.rmtree(Path(target, self.project))

        tp = Path(target, self.project)
        os.makedirs(str(tp), mode=0o777, exist_ok=True)
        target += '/'
        target = forward_slash_path(target)
        #decide if space avaialable on target - abort if not with error message
        self.qr.put(('STATUS', 'Calculating needed space...'))
        _, _, free = shutil.disk_usage(Path(target))
        needed = folder_size(\
                    Path(self.Pub2SD, 'Temp', self.project))\
                             / (1024.0 * 1024.0)
        free = free / (1024.0 * 1024.0)
        if needed > free:
            self.qr.put(('MESSAGEBOXSHOWERRORINSUFFICENT', \
                         ("Insufficent space on target!", \
                        "Needed {}Mb, but only {}Mb available", needed, free)))
            return
        self.qr.put(('STATUS', 'Making project directories...'))
        fileId = {}
        listpaths = []
        for child in sorted(self.files.keys()):
#            final_path = os.path.dirname(\
#                            os.path.normpath(target + self.files[child][3]))
            final_path = str(Path(target, self.files[child][3]).parent)
            if final_path not in listpaths:
                os.makedirs(final_path, mode=0o777, exist_ok=True)
                listpaths.extend([final_path])
            self.qr.put(('PROGSTEP', 1))
        #now open all files at once to make create dates the same
        self.qr.put(('STATUS', 'Opening target files...'))
        for child in self.files:
            fileId[child] = Path(target + self.files[child][3]).open(mode='wb')
            self.qr.put(('PROGSTEP', 1))
        self.qr.put(('STATUS', 'Copying to target files...'))
        for child in sorted(self.files.keys()):
#            filein = open(os.path.normpath(self.files[child][0]), mode='rb')
            fileId[child].write(Path(self.files[child][0]).read_bytes())
#            filein.close()
            self.qr.put(('PROGSTEP', 1))
        #close all files at once to make modified dates the same
        self.qr.put(('STATUS', 'Closing target files...'))
        for child in sorted(self.files.keys()):
            fileId[child].close()
            self.qr.put(('PROGSTEP', 1))
        self._on_copy_playlists(target)

        self.qr.put(('PROGVALUE', 0))
        self.qr.put(('STATUS', "Publishing completed."))


    def _on_copy_playlists(self, target):
        """copy playlists to target, at locatons specified in
                                                         play_list_targets"""
        ptarget = Path(target)
        self.qr.put(('STATUS', 'Copying playlists...'))
#        source = os.path.normpath(self.Pub2SD + '/Temp/'+ self.project + '/')
#        images = os.path.normpath(self.Pub2SD + '/Temp/'+ self.project + '/images/')
        #self.project most not have leading / if str!!!!
        source = Path(self.Pub2SD, 'Temp', self.project)
        images = Path(self.Pub2SD, 'Temp', self.project, 'images')
        playlists = [p for p in os.listdir(str(source)) \
                     if p.endswith('.M3U8') or p.endswith('M3U')]
        htmllists = [h for h in os.listdir(str(source)) \
                     if h.endswith('.html') or h.endswith('htm')]
        imglists = [i for i in os.listdir(images) \
                     if i.endswith('.png') or i.endswith('jpg')]
        self.qr.put(('PROGMAX', len(playlists) * \
                     (1 + self.is_copy_playlists_to_top + \
                          len(self.play_list_targets))))
        #main playlists
        for pp in playlists:
            ppp = Path(pp)
            shutil.copyfile(str(source / ppp), \
                            str(ptarget / Path(self.project) / ppp))
            self.qr.put(('PROGSTEP', 1))
        #main htmllists
        for hh in htmllists:
            hhh = Path(hh)
            shutil.copyfile(str(source / hhh), \
                            str(ptarget / Path(self.project) / hhh))
            self.qr.put(('PROGSTEP', 1))
        #main imglists
        for ii in imglists:
            iii = Path(ii)
            if not (ptarget / Path(self.project) / Path('images')).exists():
                os.mkdir(str(ptarget / Path(self.project) / Path('images')))
            shutil.copyfile(str(images / iii), \
                    str(ptarget / Path(self.project) / Path('images') / iii))
            self.qr.put(('PROGSTEP', 1))
        #copy css and js, actually just unpack from zip
        zipdir = Path(self.script_dir, "cssjs.zip")
        with zipfile.ZipFile(zipdir, "r") as zip_ref:
            zip_ref.extractall(ptarget / self.project)

        #now top level?
        if self.is_copy_playlists_to_top:
            self.qr.put(('STATUS', 'Copying playlists to top folder...'))
            for pp in playlists:
                encode = 'utf-8' if pp.endswith('.M3U8') else 'cp1252'
#                fin = codecs.open(os.path.normpath(source + '/'+ pp),\
#                                          mode='r', encoding=encode)
#                fout = codecs.open(os.path.normpath(target + pp), mode='w', \
#                                   encoding=encode)
#                fin = (source / pp).open(mode='r', encoding=encode)
#                fout = (ptarget / pp).open(mode='w', encoding=encode)
#
#                fout.write(fin.read().replace('../', './'))
#                fin.close()
#                fout.close()

                (ptarget / pp).write_text(\
                    (source / pp).read_text(encoding=encode).\
                        replace('../', './'),\
                            encoding=encode)
                self.qr.put(('PROGSTEP', 1))
            #now copy index.html to top as project.html
            (target / (self.project + '.html')).write_text(\
                (source / 'index.html').read_text(encoding=encode).\
                    replace('../', './'), encoding=encode)
            self.qr.put(('PROGSTEP', 1))
        #now in list
        for tt in self.play_list_targets:
            if tt:
                self.qr.put(('STATUS', 'Copying playlists to target folders...'))
                os.makedirs(ptarget / tt, mode=0o777, exist_ok=True)
                for pp in playlists:
                    shutil.copyfile(source / pp, \
                                    ptarget / tt / pp)
                    self.qr.put(('PROGSTEP', 1))

    def _make_filename(self, child):
        """make mp3 title = filename after appropriate normalization"""
        e_child = self.trout.find(".//" + child)
        attributes = e_child.attrib
        title = attributes['TIT2']
        title = self._my_unidecode(title) \
                        if self.mode == 0 \
                        else self._my_unidecode(title[5:-2].split(',')[0][1:-1])
        return ''.join([c if self._approved_char(c) else '_' for c in title])

    def _on_strip(self, to_strip, focus):
        parent = self.trout.find(".//" + focus)
        if to_strip in STRIPPERS:
#            if len(parent):
            if parent:
                for child in parent.getchildren():
                    if child.attrib['Type'] in ['collection', 'project']:
                        title = child.attrib['TIT2']
                        #replace all multiple spaces with single space and trim
                        #spurious chars fore and aft
                        atitle = STRIPPERS[to_strip](title).strip('- _‒–—﹘')
                        child.attrib['TIT2'] = atitle
                    else: #is file so dumb it down
                        title = self._downgrade_data('TIT2', child)
                        #replace all multiple spaces with single space and trim
                        #spurious chars fore and aft
                        atitle = STRIPPERS[to_strip](title).strip('- _‒–—﹘')
                        child.attrib['TIT2'] = '[3,["{}"],]'.format(atitle)
                    self._on_strip(to_strip, child.tag)
        else:
            self.qr.put(('PRINT', "unrecognised stripper >{}<".\
                                                         format(to_strip)))

    def _on_delete(self, focus):
        self.qr.put(('LOCKGUI', None))
        e_child = self.trout.find(".//" + focus)
        if etree.iselement(e_child):
            e_parent = e_child.getparent()
            e_parent.remove(e_child)
        self._on_reload_tree()
        self.qr.put(('UNLOCKGUI', None))

    def _on_move_up(self, focus):
        """get parent, find focus in list, move up one"""
        self.qr.put(('LOCKGUI', None))
        e_child = self.trout.find(".//" + focus)
        if etree.iselement(e_child):
            e_parent = e_child.getparent()
            child_index = e_parent.index(e_child)
            if child_index > 0:
                child_index -= 1
                e_parent.remove(e_child)
                e_parent.insert(child_index, e_child)
        self._on_reload_tree()
        self.qr.put(('SEEFOCUS', focus))
        self.qr.put(('UNLOCKGUI', None))

    def _on_move_down(self, focus):
        """get parent, find focus in list, move up one"""
        self.qr.put(('LOCKGUI', None))
        e_child = self.trout.find(".//" + focus)
        if etree.iselement(e_child):
            e_parent = e_child.getparent()
            child_index = e_parent.index(e_child)
            if child_index < len(list(e_parent[:-1])):
                child_index += 1
                e_parent.remove(e_child)
                e_parent.insert(child_index, e_child)
        self._on_reload_tree()
        self.qr.put(('SEEFOCUS', focus))
        self.qr.put(('UNLOCKGUI', None))

    def _on_demote(self, focus):
        """demote one level in the hierachy, \
        requires that there be a collection under parent but below child"""
        self.qr.put(('LOCKGUI', None))
        e_child = self.trout.find(".//" + focus)
        found = False
        if etree.iselement(e_child):
            if e_child.attrib['Type'] is 'project':
                self.qr.put(('MESSAGEBOXSHOWERRORIN', \
                             ("Can't demote", "Can't demote project.")))
            else:
                e_parent = e_child.getparent()
                if etree.iselement(e_parent):
                    child_index = e_parent.index(e_child)
                    if child_index < len(list(e_parent[:-1])):
                        children = e_parent.getchildren()
                        for a_child in children[child_index + 1:]:
                            if a_child.attrib['Type'] is 'collection':
                                a_child.append(e_child)
                                found = True
                                break
                    if not found:
                        #cant find collection below child
                        self.qr.put(('MESSAGEBOXSHOWERRORIN', \
                                 ("Can't demote", \
                                  "Can't find collection below child.")))
                else:
                    #cant find parent
                    self.qr.put(('MESSAGEBOXSHOWERRORIN', \
                             ("Can't demote", "Can't find parent.")))
        else:
            self.qr.put(('MESSAGEBOXSHOWERRORIN', \
                         ("Can't demote", "Can't find child.")))
        self._on_reload_tree()
        self.qr.put(('SEEFOCUS', focus))
        self.qr.put(('UNLOCKGUI', None))

    def _on_promote(self, focus):
        """promote item one level in the heirachy"""
        self.qr.put(('LOCKGUI', None))
        e_child = self.trout.find(".//" + focus)
        if etree.iselement(e_child):
            e_parent = e_child.getparent()
            if etree.iselement(e_parent):
                e_grandparent = e_parent.getparent()
                if etree.iselement(e_grandparent):
                    if self._is_promotable(e_grandparent.attrib['Type'],  \
                                           e_parent.attrib['Type'], \
                                           e_child.attrib['Type']):
                        e_grandparent.append(e_child)
                        self._on_reload_tree()
                    else:
                        #error message
                        self.qr.put(('MESSAGEBOXSHOWERRORIN', \
                                     ("Can't promote", \
                                  "Can't place file directly under project.")))
                else:
                    self.qr.put(('MESSAGEBOXSHOWERRORIN', \
                                 ("Can't promote", "Can't find grandparent.")))
            else:
                self.qr.put(('MESSAGEBOXSHOWERRORIN', \
                             ("Can't promote", "Can't find parent.")))
        else:
            self.qr.put(('MESSAGEBOXSHOWERRORIN', \
                         ("Can't promote", "Can't find child.")))

        self.qr.put(('SEEFOCUS', focus))
        self.qr.put(('UNLOCKGUI', None))

    def _is_promotable(self, gp, p, c):
        if (gp in ['project', 'collection']) and \
                    (p in ['collection',]) and \
                    (c in ['collection',]):
            result = True
        elif (gp in ['collection',]) and \
                    (p in ['collection']) and \
                    (c in ['collection', 'file']):
            result = True
        else:
            result = False
        return result

    def _on_merge_files(self, focus):
        """Merge the mp3 files contained in the selected collection, \
        into a single file with 1 second pauses between each file. \
        Then insert the new file at the same level as the collection."""
        #get parent of focus
        self.qr.put(('LOCKGUI', None))
        e_child = self.trout.find(".//" + focus)
        #if e_child is not collection/project give up
        if e_child.attrib['Type'] not in ['project', 'collection']:
            self.qr.put(('MESSAGEBOXSHOWWARNING2', \
                             ("Not a collection", \
                                  "Please select a collection not a file.")))
        else:
            #list mp3 files which are immediate children of focus
            children = [c for c in e_child if c.attrib['Type'] is 'file']
            if len(children) > 1:
                # in milliseconds                second_of_silence =
                second_of_silence = AudioSegment.silent(duration=1000)
                sound = AudioSegment.from_mp3(children[0].attrib['Location'])
                for c in children[1:]:
                    sound += second_of_silence + \
                                AudioSegment.from_mp3(c.attrib['Location'])
                # now save new file in temp workspace?
                #create temp workspace
                #walk up tree creating list of ancestors, stop at project
                ancestors = list()
                this_child = e_child
                while this_child.attrib['Type'] is not 'project':
                    e_parent = this_child.getparent()
                    ancestors.insert(0, e_parent.tag)
                    this_child = e_parent
#                workspace = os.path.normpath('{}/Temp'.format(self.Pub2SD))
                workspace = Path(self.Pub2SD / 'Temp')
                for ancestor in ancestors:
                    workspace = workspace / ancestor.tag
                    os.makedirs(workspace, mode=0o777, exist_ok=True)
#                filename = '{}/{}.mp3'.format(workspace,e_child.tag)
                filename = str(workspace / (e_child.tag + 'mp3'))
                sound.export(filename, 'mp3')
                e_parent = e_child.getparent()
                somevalues = self._read_mp3_tags(e_child.attrib['Location'])
#                self._add_a_file(afile, e_parent, somevalues)
                self._add_a_file(filename, e_parent, somevalues)
            else:
                self.qr.put(('MESSAGEBOXSHOWWARNING2', \
                    (e_child.text, \
                   "There are no immediate descendants which are mp3 files.")))

        if etree.iselement(e_child):
            e_parent = e_child.getparent()

            child_index = e_parent.index(e_child)
            if child_index > 0:
                child_index -= 1
                e_parent.remove(e_child)
                e_parent.insert(child_index, e_child)
        self._on_reload_tree()
        self.qr.put(('SEEFOCUS', focus))
        self.qr.put(('UNLOCKGUI', None))
        #list children of focus which are mp3 files

    def _on_load_tree_from_trout(self):
        self.qr.put(('HASHEDGRAPHICS', self.hashed_graphics))
        self._rename_children_of(list(self.trout)[0].tag)
        self.to_be_inserted = list()
        self._load_tree_from('')
        self.qr.put(('ADD_ITEMS', self.to_be_inserted))

    def _on_reload_tree(self):
        self.qr.put(('CLEARTREE', None))
        self._on_load_tree_from_trout()

    def _on_append(self, atuple):
        focus, column, text = atuple
        focus_item = self.trout.find(".//" + focus)
        #action only possible in advanced mode with tags that are hashable
        #if is collection/project apply to all below
        if focus_item.attrib['Type'] in ['collection', 'project']:
            #is collection... so
            children = focus_item.getchildren()
            for child in children:
                self._on_append((child.tag, column, text))
        else:
            #is file so…
            if focus_item.attrib[column]:
                focus_item.attrib[column] = \
                                '|'.join([focus_item.attrib[column], text])
            else:
                focus_item.attrib[column] = text


    def _on_set(self, atuple):
        """set value of tag"""
        focus, column, text = atuple
        focus_item = self.trout.find(".//" + focus)
        name = focus_item.attrib['Name']
        location = focus_item.attrib['Location']
        if self.mode:
            for test in text.split('|'):
                if len(HASH_TAG_ON[column]) != \
                        len(ast.literal_eval(escape_tab_return_feed(test))):
                    self.qr.put(('MESSAGEBOXSHOWHASHERROR', (name,\
                                    column, test, len(HASH_TAG_ON[column]))))
                    return
        if column == 'TRCK':
            #if advanced mode strip '[3,"' and '"]" and split any list on ','
            self._on_set_trck(\
            [t[1:-1] for t in text[4:-2].split(',')] if self.mode != 0 \
                                                     else [text,], \
                                                    focus_item, text, column)
        elif column in URL_TAGS:
            self._on_set_is_url(text, focus_item, column)
        elif column in SORT_TAGS:
            if focus_item.attrib['Type'] in ['collection', 'project']:
                self._set_sort_(focus_item)
            else: #is file so...
                self._set_tag_(focus_item)
        elif column == 'TIT2' \
                    and (focus_item.attrib['Type'] is 'collection' \
                    or os.path.getsize(location) == 0):
            if self.mode == 0:
                #idiot mode
                #so need to fill in advanced stuff
                focus_item.attrib[column] = '[3,["' + text + '"]]'
            else:
                #advanced mode
                #[3,[""]]
                #is advanced so what you see is what you get
                focus_item.attrib[column] = text
        else:
            self._set_tag_(focus_item, column, text)
        self._on_reload_tree()
        self.qr.put(('SEEFOCUS', focus_item.tag))

    def _on_set_trck(self, tempstr, focus_item, text, column):
        """is TRCK tag so set track no"""
        #test for 'track/of tracks' on first str only
        #only first str will be updated!
        tp = tempstr[0].split('/')
        if len(tp) > 1:
            self._is_track_of_tracks(tp, tempstr, focus_item, text)#, column)
        elif tempstr[0].isdecimal: #is track
            self.next_track = 1 if int(tempstr[0]) == 0 \
                                else int(tempstr[0])
            if focus_item.attrib['Type'] in ['collection', 'project']:
                self._set_tracks(focus_item, tempstr[0], '', tempstr[1:])
            elif self.isHide.get() == 1:
                tempstr[0] = '"{}"'.format(self.next_track)
                focus_item.attrib[column] = '[3,[' +','.join(tempstr) + ']'
        else: #invalid track
            self.qr.put(('MESSAGEBOXWARNTRACK', ('', 'Set', \
                                            ' TRCK, >{}< {}'.format(text, \
                                        "doesn't contain a valid integer."))))

    def _is_track_of_tracks(self, tp, tempstr, focus_item, text):
        """track specified as 1/10 format so set for this file or all
           dependants of a collection. Where 0/0 count dependants and
           set as n/count."""

        if tp[0].isdecimal and tp[1].isdecimal: #is track / of tracks
            self.next_track = int(tp[0])
            if not etree.iselement(focus_item) \
                        or focus_item.attrib['Type'] \
                            in ['collection', 'project']:
                if self.next_track == 0:
                    self.next_track = 1
                    if tp[1] == '0':
                        self.nos_tracks = 0
                        self._count_files_below(focus_item)
                        tp[1] = str(self.nos_tracks)
                self._set_tracks(focus_item, tp[0], tp[1], '' \
                                if self.mode == 0 \
                                else tempstr[1:])
            else: #is file so…
                if tp[1]:
                    newtrack = ['"{}/{}"'.\
                                format(self.next_track, tp[1]),]
                    for nt in tempstr[1:]:
                        newtrack.extend([nt])
                    focus_item.attrib['TRCK'] = '[3,[{}]]'.\
                                                    format(','.join(newtrack))
                else:
                    newtrack = ['"{}"'.format(self.next_track),]
                    for nt in tempstr[1:]:
                        newtrack.extend([nt])
                    focus_item.attrib['TRCK'] = '[3,[{}]]'.\
                                                    format(','.join(newtrack))
                self.next_track += 1
        else: #invalid track or set of
            self.qr.put(('MESSAGEBOXWARNTRACK', ('', 'Set', ' TRCK, >{}< {}', \
                text, "'track in/set_of' doesn't contain a valid integers.")))

    def _count_files_below(self, focus_item):
        '''count nos of files below this point'''
        if focus_item.attrib['Type'] in ['collection', 'project']:
            children = focus_item.getchildren()
            for child in children:
                self._count_files_below(child)
        else:
            #is file so...
            self.nos_tracks += 1

    def _set_tracks(self, e_parent, tp0='', tp1='', trest=list()):
        """set tracks"""
        children = e_parent.getchildren()
        for child in children:
            if child.attrib['Type'] in ['collection', 'project']:
                self._set_tracks(child, tp0, tp1, trest)
            else:
                if tp1:
                    newtrack = ['{}/{}'.format(self.next_track, tp1),]
                    for nt in trest:
                        newtrack.extend(['{}'.format(nt)])
                    if self.mode == 0:
                        child.attrib['TRCK'] = \
                                      '{}'.format(','.join(newtrack))
                    else:
                        child.attrib['TRCK'] = \
                                      '[3,["{}"]]'.format(','.join(newtrack))
                else:
                    newtrack = ['{}'.format(self.next_track),]
                    for nt in trest:
                        newtrack.extend([nt])
                    if self.mode == 0:
                        child.attrib['TRCK'] = \
                                      '{}'.format(','.join(newtrack))
                    else:
                        child.attrib['TRCK'] = \
                                      '[3,["{}"]]'.format(','.join(newtrack))
                self.next_track += 1

    def _on_set_is_url(self, text, focus_item, column):
        """set one of the WCOM, WCOP, WOAF, WOAR,
                                        WOAS, WORS, WPAY, WPUB internet tags"""
        #string is held in utf8 encoding but forced to ascii7 subset
        #to get text first strip the the outer []
        # then split on ,
        # and strip quote marks
        #Should only be one url!
        tempstr = unidecode(text if self.mode.get() == 0 \
                                 else text[1:-1].split(',')[0][1:-1])
        res = list(urlparse(tempstr))
        if res[0] in ['http', 'https', 'ftp', 'ftps', 'finger', 'news', \
                      'NNTP', 'local'] \
                      and '.' in res[1] and res[2]:
            if focus_item.attrib['Type'] in ['collection', 'project']:
                self._set_tag_(focus_item)
            else: #is file, so...
                focus_item.attrib[column] = '["{}"]'.format(tempstr)
        else:
            self.qr.put(('MESSAGEBOXWARNTRACK2', ('Set', column, \
                                                  "URL is invalid.")))

    def _set_sort_(self, e_parent):
        """set one of the sort order tags
                                      'TSOA', 'TSOC', 'TSOP', 'TSOT', 'TSO2'"""
        column = self.ddnSelectTag.get().split(':')[0]
        if e_parent.attrib['Type'] in ['collection', 'project']:
#            children = parent.getchildren()
            children = e_parent.getchildren()
            for child in children:
                self._set_sort_(child)
        else:
            #is file so…
#            name = parent.attrib['Name']
            name = e_parent.attrib['Name']
            if self.isHide == 1:
                name = '"' + name + '"'
            else:
                name = DEFAULT_VALUES['ide3v24'][column][0:5] + name + \
                                        DEFAULT_VALUES['ide3v24'][column][5:]
#            parent.attrib[column] = name
            e_parent.attrib[column] = name

    def _set_tag_(self, parent, column=None, text=None):
        """set tag specified in column with value in text, for current
           item or it's dependants"""
        if parent.attrib['Type'] in ['collection', 'project']:
            children = parent.getchildren()
            for child in children:
                self._set_tag_(child)
        else: #is file so…
            if not self.mode: # == 0 is idiot
                #so have to upgrade data!
                if column not in ['APIC',]:
                    parent.attrib[column] = self._upgrade_text(column, text)
                else:
                    #error use cover art button
                    pass
            else: #is advanced
                #so for each frame verify
                if is_hashable(column):
                    #so verify all frames are unique
                    textFrames = text.split('|')
                    for aFrame in textFrames:
                        thisframe = \
                               ast.literal_eval(escape_tab_return_feed(aFrame))
                        if len(thisframe) != len(HASH_TAG_ON[column]):
                            #error message and give up
#                            pass
                            return
                    if False in self._list_different_frames(text, column):
                        #reject with not unique frames error message
                        pass
                    else:
                        parent.attrib[column] = text
                else:
                    #check if multiple frame in text even though not supported?
                    #so new text replaces old, format not checked here
                    thisframe = ast.literal_eval(escape_tab_return_feed(text))
                    if len(thisframe) != len(HASH_TAG_ON[column]):
                        #insufficient parameters error message
                        #show defalt form and give up
                        return
                    parent.attrib[column] = text

    def _list_different_frames(self, text, tag):
        """returns a list of True/False values, one for each frame in text.
        Each unique frame is True, each duplicate is False.
        for tags which support this (e.g. COMM, APIC,...)"""

        #so split text into list of separate frames
        textFrames = text.split('|')
        if len(textFrames) < 2: #is only one frame
            list_different_to_all = [True,]
        else:
            is_different_to_all = list()
            mash = dict()
            for aFrame in textFrames:
                #turn str into list of parameters
                textParams = ast.literal_eval(escape_tab_return_feed(aFrame))
                hash_tag = ''
                for apara in range(0, len(textParams)):
                    #so for each parameter, check if hashable,
                    #if so add to hash_tag
                    if HASH_TAG_ON[tag][apara]:
                        hash_tag += textParams[apara]
                if not hash_tag:
                    #not hashable error message
                    self.qr.put(('PRINT', "{} is not hashable!".format(tag)))
                    is_different_to_all.append(False)
                elif hash_tag not in mash:
                    mash[hash_tag] = True
                    is_different_to_all.append(True)
                else:
                    #is duplicate tag
                    is_different_to_all.append(False)
        return is_different_to_all

    def _is_different_hash(self, currentFrames, text, tag):
        """true if 'text' not in 'currentFrames' and tag is hashable"""
        #is text a valid frame
        thisframe = ast.literal_eval(escape_tab_return_feed(text))
        if len(thisframe) != len(HASH_TAG_ON[tag]):
            #insufficient parameters error message and give up
            return False
        else:
            testFrames = currentFrames + '|' + text
#        if False in self._list_different_frames(currentFrames, text, tag):
        if False in self._list_different_frames(testFrames, tag):
            return False
        else:
            return True


    def _on_generate_playlists(self):
        '''generate the playlists'''

        self.nodes = len(self.trout.find(".//I00001").xpath(".//*"))
        self.qr.put(('PROGMAX', self.nodes))
        self.qr.put(('STATUS', 'Creating playlists...'))
        project_path_ = '../{}/'.format(self.project)
        project_file_list = list()
        e_project = self.trout.find(".//I00001")
        self._create_play_list(e_project, project_path_, \
                                                          project_file_list)

        self.qr.put(('STATUS', ''))

    def _create_play_list(self, pid_item, ploc, glist):
        """create play list
            pid_item = collection node in etree
                ploc = path to collection
               glist = ancestors list/index to plists
               plistid index to plists which holds all play lists in
                              form [[name, [list/set of targetfilepaths]],]"""

        if pid_item.tag in ["I00001",]:
            webpage = os.path.normpath('../{}/index.html'.format(self.project))
        else:
            webpage = os.path.normpath('../{}/{}.html'.\
                                       format(self.project, pid_item.tag))
        #now open webpage and add header, css etc...
        webpath = os.path.normpath('{}/Temp/{}/{}'.\
                                            format(self.Pub2SD, self.project, \
                                                   os.path.basename(webpage)))
        page_links = list()
        if self.M3UorM3U8 == 1:
            #use m3u file
            page_links.insert(0, ['{}/Temp/{}/{}.M3U'.\
                                        format(self.Pub2SD, self.project, \
                                               pid_item.text), \
                                'Play all.'])
        else: #use m3u8 file
            page_links.insert(0, ['{}/Temp/{}/{}.M3U8'.\
                                        format(self.Pub2SD, self.project, \
                                               pid_item.text), \
                                'Play all.'])
        this_list = list() #list for this pid
        self.qr.put(('PROGSTEP', 1))
        self.qr.put(('STATUS{}', ('Creating playlist for {}', pid_item.text)))
        for child in pid_item.getchildren():
            if child.attrib['Type'] in ['collection', 'project']:
                cloc = ploc + child.text + '/'
                self._create_play_list(child, cloc, this_list)
                #add link to webpage for play list for this child collection
                #[href, text]
                page_links.append(['../{}/{}.html'.\
                                   format(self.project, child.text), \
                                   child.text])
            elif os.path.getsize(os.path.normpath(self.files[child.tag][0])) > 0:
                #is real mp3 file so...
                #belt and braces
                if '[' in child.attrib['TIT2']:
                    track_name = child.attrib['TIT2'].\
                        split('[')[2][1:].split(']')[0].replace('_', ' ')[:-1]
                else:
                    track_name = child.attrib['TIT2']
                if '[' in child.attrib['TALB']:
                    artist_name = child.attrib['TALB'].\
                        split('[')[2][1:].split(']')[0].replace('_', ' ')[:-1]
                else:
                    artist_name = child.attrib['TALB']
                this_list.append([os.path.normpath(self.files[child.tag][3]), \
                                                track_name, \
                                                artist_name, \
                                                str(self.files[child.tag][4])])
                #add link to webpage for this file?
                page_links.append([str(self.files[child.tag][3]), \
                                   child.text])
            else:
                #is zero length file so...
                pass
        #found all of my children so copy this list upto glist
        if this_list:
            glist.extend(this_list)
            #now make playlist for this collection
            playlist = ['#EXTM3U',]
            #write out to self.Pub2SD +/Temp/+ self.project/ collection name
            if self.M3UorM3U8 == 2:
                #is utf-8
                for item in this_list:#   secs,alb,title,location
                    playlist.append('#EXTINF:{},{} - {}\r\n../{}'.\
                                    format(item[3], item[2], item[1], \
                                           forward_slash_path(item[0])))
                filepath = Path(self.Pub2SD, 'Temp', self.project, \
                                                   (pid_item.text + '.M3U8'))
                filepath.write_text('\r\n'.join(playlist), encoding='utf-8')
            elif self.M3UorM3U8 == 1:
                #is legacy
                for item in this_list:
                    playlist.append('#EXTINF:{},{} - {}\r\n../{}'.\
                                format(item[3], self._my_unidecode(item[2]), \
                                           self._my_unidecode(item[1]), \
                                           forward_slash_path(item[0])))
                filepath = Path(self.Pub2SD, 'Temp', self.project, \
                                                   (pid_item.text + '.M3U'))
                filepath.write_text('\r\n'.join(playlist), encoding='cp1252')
            else:
                #is both
                utf8list = ['#EXTM3U',]
                playlist = ['#EXTM3U',]
                for item in this_list:#   secs,alb,title,location
                    utf8list.append('#EXTINF:{},{} - {}\r\n../{}'.\
                                    format(item[3], item[2], item[1], \
                                           forward_slash_path(item[0])))
                    playlist.append('#EXTINF:{},{}-{}\r\n../{}'.\
                                format(item[3], self._my_unidecode(item[2]), \
                                           self._my_unidecode(item[1]), \
                                           forward_slash_path(item[0])))
                #utf-8
                fileutf = Path(self.Pub2SD, 'Temp', self.project, \
                                                   (pid_item.text + '.M3U8'))
                fileutf.write_text('\r\n'.join(utf8list), encoding='utf-8')
                #legacy
                fileout = Path(self.Pub2SD, 'Temp', self.project, \
                                                   (pid_item.text + '.M3U'))
                fileout.write_text('\r\n'.join(playlist), encoding='cp1252')
            #this list not empty

        else:
            #no files in this collection with length greater than zero!
            #so skip it!!!
            pass
        webout = codecs.open(webpath, mode='w', encoding='utf-8')
        linesout = list()
        linesout.extend(STARTHEADER)
        linesout.append(MAINTITLE.format(webpage[:-4]))
        linesout.extend(MYCSSLATIN)
        linesout.extend(CLOSEHEADER)
        linesout.extend(['  <nav id="navbar">',\
        '    <img src="./images/image000.png" alt="Album cover art"' + \
                         'title="" align="bottom" width="270">',\
                         '    <div class="container col">',\
                         ])
        for alink in page_links:
            linesout.append(ANAVLINK.format(os.path.normpath(\
                                                        alink[0]), alink[1]))
        linesout.extend(['    </div>',\
                         '  </nav>',\
                         '</body>',\
                         '</html>',\
                         '',\
                         ])
        webout.write('\n'.join(linesout))
        webout.close()


    def _from_playlist_create_webpage(self, playlist=""):
        """Create web page for current 'playlist' all stored under project
        directory with pages named after node name, titles will be displayed
        on web page not in web page file name."""
#        self.qr.put(('PRINT', 'ploc is {}'.format(ploc)))
#        if not playlist:
#            fileout = '{}/Temp/{}/index.html'.format(self.Pub2SD, self.project)
#        else:
#            fileout =  '{}/Temp/{}/{}.html'.format(self.Pub2SD, self.project, \
#                                                    playlist)
        if not playlist:
            webpagefile = Path(self.Pub2SD, 'Temp', self.project, 'index.html')
        else:
            webpagefile = Path(self.Pub2SD, 'Temp', self.project, \
                                                    (playlist +'.html'))
#        self.qr.put(('PRINT', 'fileout is {}'.format(ploc)))
#        webpagefile = codecs.open(fileout, mode='w',encoding='utf-8')
        linesout = [codecs.BOM_UTF8.decode(),\
'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">', \
"<html><head>", \
'  <meta http-equiv="content-type" content="text/html;' + \
        ' charset=utf-8"><title>{}</title>'.format(webpagefile.stem), \
'  <style type="text/css">', \
'	<!--', \
'       /* global elements */',\
"       @import 'http://fonts.googleapis.com/css?family=' + \
                            'Andika:400,400italic&subset=latin,latin-ext';",\
"",\
'		p { font-family : "Andika SEB", geneva, arial, helvetica,' + \
                ' sans-serif; font-size : 13pt; font-style : normal;' + \
            'color: #000000; margin-top: 0.07in; margin-bottom: 0.07in }\n' + \
'		h1 { font-family : "Andika SEB", geneva, arial, helvetica,' + \
            ' sans-serif; font-size : 20pt; font-style : normal;' + \
            'color: #000000; margin-top: 0.07in; margin-bottom: 0.07in}\n' + \
'		h2 { font-family : "Andika SEB", geneva, arial, helvetica,' + \
            ' sans-serif; font-size : 16pt; font-style : normal;' + \
            ' color: #000000; margin-top: 0.07in; margin-bottom: 0.07in}\n' + \
'		a:link { font-family : "Andika SEB", geneva, arial, helvetica,' + \
            '  sans-serif; color: #0000ff }\n' + \
'		a:visited { font-family : "Andika SEB", geneva, arial,' + \
            ' helvetica, sans-serif; color: #800080 }\n' + \
'       table, td {', \
'          font-family : "Andika SEB", geneva, arial, helvetica, sans-serif;',\
'          font-size : 13pt; font-style : normal;',\
'         border: 1px solid LightGray;', \
'         border-collapse: collapse;', \
'         padding: 5px;', \
'         text-align: center;', \
'         color: #000000;', \
'         }', \
'       th{', \
'          font-family : "Andika SEB", geneva, arial, helvetica, sans-serif;',\
'          font-size : 13pt; font-style : normal;',\
'         border: 1px solid DarkGray;', \
'         border-collapse: collapse;', \
'         background: LightGray;', \
'         padding: 5px;', \
'         text-align: center;', \
'         }']

        linesout.extend(['	-->', \
'	</style></head>', \
'<body dir="ltr" style="background: transparent none repeat scroll 0% 50%;' + \
    ' color: rgb(0, 0, 0); -moz-background-clip: -moz-initial;' + \
    ' -moz-background-origin: -moz-initial; -moz-background-inline-policy:' + \
    ' -moz-initial;" lang="en-US">', \
'<h1 align="center"><b>{}</b></h1>'.format(webpagefile.stem), \
'', \
'<ul">', \
 ''])
        #open playlist
        #for now assume all are M3U8
        if not playlist:
            this_file = Path(self.Pub2SD, 'Temp', self.project, \
                             (self.project + '.M3U8'))
        else:
            this_file = Path(self.Pub2SD, 'Temp', self.project, playlist)
        this_list = this_file.read_text(encoding='utf-8').splitlines()
        #add playall button
        #for each item add play item button
        #add return to home(index) button
        for item in this_list:
#            self.qr.put(('PRINT', '\t{}'.format(item)))
            linesout.append('<a href="{}"><li>{}</li></a>'.format(\
                            item[0], item[1]))
        linesout.append('</ul>')
        linesout.append('</body>')
        linesout.append('</html>')
        linesout.append('')
        webpagefile.write_text('\n'.join(linesout), encoding='utf-8')

    def _attach_artwork_to(self, target, _picture_type, _desc, hash_tag, \
                           length, mime):
        """attaches the artwork to item in focus or to its dependants
                                                             if collection"""
        e_target = self.trout.find(".//" + target)
        #all data stored in advanced form, so ignore mode
        theParameters = '[{},"{}",{},"{}","{}"]'.\
                        format(3, mime, str(_picture_type), _desc, hash_tag)
        dumbPara = '[{},"{}",{},"{}","{}"]'.\
                        format(3, mime, str(_picture_type), _desc, length)
        if e_target.attrib['Type'] in ['file',]:
            if not hash_tag:
                e_target.attrib['APIC'] = '-'
                e_target.attrib['APIC_'] = '-'
            else:
                currentTag = e_target.attrib['APIC']
                if currentTag is '-' or self.mode == 0:
                    e_target.attrib['APIC'] = dumbPara
                    e_target.attrib['APIC_'] = theParameters
                else:
                    currentFrames = currentTag.split('|')
                    apic_frames = e_target.attrib['APIC'].split('|')
                    #I've split the frames apart
                    #so now test it the new frame is diffrent enough to
                    # justfiy own frame
                    if self._is_different_hash(currentFrames, theParameters, 'APIC'):
                        #so append
                        currentFrames.append(dumbPara)
                        apic_frames.append(theParameters)
                    else:
                        #replace first matching frame
#                        theList = self._list_different_frames(\
#                                            currentFrames, dumbPara, 'APIC')
                        theList = self._list_different_frames(\
                                            currentFrames, 'APIC')
                        if False in theList:
                            index = theList.index(False)
                            currentFrames[index] = dumbPara
                            apic_frames[index] = theParameters
                    e_target.attrib['APIC'] = '|'.join(currentFrames)
                    e_target.attrib['APIC_'] = '|'.join(apic_frames)
        else:
            #is collection, list children of focus and attach artwork to each
            children = e_target.getchildren()
            for child in children:
                self._attach_artwork_to(child.tag, _picture_type, _desc, \
                                        hash_tag, length, mime)

    def _on_publish_to_SD(self):
        """publish files and playlists to SDs"""

        threads = []
        self.usb_status = ['', '', '', '', '', '', '', '']
        self.qr.put(('PROGMAX', \
                     (2 * int(len(self.files)/20) * len(self.output_to))))

        i = 1
        currentThreadsActive = threading.activeCount()
        for atarget in self.output_to:
            if atarget:
                if os.path.exists(atarget):
                    target = atarget
                    threads.append(MyThread(target, \
                                            self.Pub2SD, self.project, \
                                            self.play_list_targets, \
                                            self.is_copy_playlists_to_top, \
                                            self.files, self.aqr[i-1]),\
                                            self.script_dir)
                    i += 1
                    threads[-1].start()
                    self.qr.put(('STATUS{}', ('{} Threads active', \
                                threading.activeCount()-currentThreadsActive)))
                else:
                    self.qr.put(('MESSAGEBOXSHOWERRORTHREADS', \
                                 ("Invalid path", "Can't find {}", atarget)))
#thinks... this is same as [athread.join() for athread in threads]
#        while len(threads):
        while threads:
            for athread in threads:
                if not athread.is_alive():
                    athread.join()
                    threads.remove(athread)
        self.qr.put(('PROGVALUE', 0))
        self.qr.put(('STATUS', "Output to SD('s) completed."))

    def _html_tree_from(self, _trout):
        if not _trout:
            tree = self.trout
            parent = ''
        else:
            tree = self.trout.find(".//" + _trout)
            parent = tree.tag
#        if len(tree):
        if tree:
            for child in tree.getchildren():
                vout = list()
                for k in self.columns:
                    if k not in ['adummy', ] and k in child.attrib:
                        if self.mode: #is advanced
                            vout.append(child.attrib[k])
                        else: #is idiot
                            data = self._downgrade_data(k, child)
                            vout.append(data)
                    else:
                        vout.append('-')
                if child.attrib['Type'] in ['file',]:
                    self.html_out.append('<tr>' + \
                            '<td>' + child.tag + '</td>' + \
                            '<td>' + (child.text if child.text else '-') + \
                            '.mp3'  + '</td>' + \
                       ''.join(['<td>' + v + '</td>' for v in vout]) + '</tr>')
                else: #is 'collection' or 'project'
                    self.html_out.append('<tr>' + \
                            '<td>' + child.tag + '</td>' + \
                            '<td>' + (child.text if child.text else '-') + \
                                '</td>' + '</tr>')
                self.qr.put(('PROGSTEP', 1))
                self._html_tree_from(child.tag)


    def _export_to_html(self):
        """produce html tree, showing final file/dir name,
        location of source, title and the rest of the display"""
        self.qr.put(('STATUS', "Exporting to HTML..."))
        the_headings = ['<th>Id Tag</th>', '<th>File/Dir</th>',]
        for c in self.columns:
            if c not in ['', ]:
                if c in ['Name',]:
                    the_headings.append('<th>' + 'Base' + '</th>')
                else:
                    the_headings.append('<th>' + c + '</th>')
#        fileout = os.path.normpath(self.Pub2SD + '/' + self.project + '.html')
        fileout = Path(self.Pub2SD / (self.project + '.html'))
        self.html_out = ['\ufeff<!DOCTYPE html>', \
                    '<html>', \
                    '<head>', \
                    '<title>' + self.project + '</title>', \
                    '<style>',\
                    'table, th, td {', \
                    '    border: 1px solid black;', \
                    '    border-collapse: collapse;', \
                    '}', \
                    'th {', \
                    '    padding: 5px 5px 5px 5px;', \
                    '    text-align: center;', \
                    '    vertical-align: top;', \
                    '    color: black;', \
                    '    font-family: Andika SEB;', \
                    '    font-size: 100%;', \
                    '}', \
                    'td, tr {', \
                    '    padding: 5px 5px 5px 5px;', \
                    '    text-align: left;', \
                    '    vertical-align: top;', \
                    '    color: black;', \
                    '    font-family: Andika SEB;', \
                    '    font-size: 100%;', \
                    '}', \
                    'td.spkr_no {', \
                    '    padding: 5px 5px 5px 5px;', \
                    '    text-align: center;', \
                    '    vertical-align: top;', \
                    '    color: black;', \
                    '    font-family: Andika SEB;', \
                    '    font-size: 100%;', \
                    '}', \
                    'h1 {', \
                    '    color: black;', \
                    '    font-family: Andika SEB;', \
                    '    font-size: 160%;', \
                    '}', \
                    '</style>', \
                    '</head>', \
                    '<body>', \
                        '<h1>' + self.project + '</h1>', \
                    '<table style="width:100%">', \
                    '<tr>' + ''.join(the_headings) + '</tr>']

        self._html_tree_from('')
        self.html_out.append('')
#        output = codecs.open(fileout, mode='w',encoding='utf-8')
#        output.write( '\n'.join(self.html_out))
#        output.flush()
#        output.close()
        fileout.write_text('\n'.join(self.html_out), encoding='utf-8')
        #now open in browser
#        url = os.path.normpath("file://" + fileout)
#        webbrowser.open(url)
        webbrowser.open(fileout.absolute().as_uri())
        self.qr.put(('PROGVALUE', 0))
        self.qr.put(('STATUS', ''))

#    def _hash_it(self, _data):
#        """ saves to dictionary and returns hash tag and length string"""
#        m = hashlib.sha256(_data)
#        if m.hexdigest() not in self.hashed_graphics:
#            self.hashed_graphics[m.hexdigest()] = _data
#        length = int(len(_data)/1024 + 0.5)
#        return  m.hexdigest(), "b'{}Kb'".format(length)


    def _extract_hashed_graphics(self):
        #try to make target dir, ok if it already exists
#        tt = os.path.normpath('{}/Temp/{}/images/'.\
#                                            format(self.Pub2SD, self.project))
        tt = str(Path(self.Pub2SD, 'Temp', self.project, 'images'))
#        self.qr.put(("PRINT", tt))
        os.makedirs(tt, exist_ok=True)
        self.list_images = \
           [self.hashed_graphics[m] for m in list(self.hashed_graphics.keys())]
        m = 0
        for data in self.list_images:
            fout = codecs.open('{}/image{:03d}.png'.format(tt, m), mode='wb')
            fout.write(data)
            fout.close()
            m += 1
        #now add css dir and file
#        cssdir = os.path.normpath(tt[:-6] + '/css/')
#        self.qr.put(("PRINT", cssdir))
#        os.makedirs(cssdir, exist_ok=True)
#        fout = codecs.open('{}/latin.css'.format(cssdir), mode='w', encoding="utf-8")
#        fout.write('\n'.join(FILECSSLATIN))
#        fout.close()
#        zipdir = os.path.normpath(self.script_dir + "/cssjs.zip")
        zipdir = Path(self.script_dir, "cssjs.zip")
        with zipfile.ZipFile(zipdir, "r") as zip_ref:
            zip_ref.extractall(Path(self.Pub2SD, 'Temp', self.project))

def get_rid_of_multiple_spaces(tin):
    """replace multiple spaces with single space and strip leading and
        trailing spaces"""
    return DOUBLE_SPACE_TO_SINGLE.sub(r' ', tin.strip())

def count_mp3_files_below(adir_path):
    """counts all mp3 files below given dir including subdirs"""
    matches = []
    for root, dirnames, filenames in os.walk(adir_path):
        for filename in fnmatch.filter(filenames, '*.mp3'):
            matches.append(os.path.join(root, filename))
    return len(matches)

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

def sort_key_for_filenames(filename):
    """build the sort key for imported file names, attempting to guess
       which order is implied by various numbering schemes
       (e.g. chapter numbers without leading zeros, etc...)"""
    if filename[0].isdigit():
        #starts with digit
        digits = FIND_LEADING_DIGITS.findall(filename)[0]
        postfix = FIND_TRAILING_DIGITS.findall(filename)[0] \
                        if FIND_TRAILING_DIGITS.findall(filename) else ''
        name = filename[len(digits):len(postfix)] \
                        if postfix else filename[len(digits):]
        if not postfix:
            lf = "{:05d}{}".format(int(digits), name)
        else:
            lf = "{:05d}{}{:05d}".format(int(digits), name, int(postfix))
    elif filename[0].isalpha():
        word = FIND_LEADING_ALPHANUM.findall(filename)[0] \
                    if FIND_LEADING_ALPHANUM.findall(filename) else ''
        word = word.split('_')[0]
        #grab trailing digits in word[0]
        digits = FIND_TRAILING_DIGITS.findall(word)[0] \
                        if FIND_TRAILING_DIGITS.findall(word) else ''
        prefix = word[:-len(digits)] if digits else word
        postfix = FIND_TRAILING_DIGITS.findall(filename)[0] \
                    if FIND_TRAILING_DIGITS.findall(filename) else ''
        name = filename[len(word):-len(postfix)] if postfix \
                                               else filename[len(word):]
        if digits:
            lf = "{}{:05d}{}{:05d}".format(prefix, int(digits), name, \
                                                          int(postfix)) \
                      if postfix \
                        else "{}{:05d}{}".format(prefix, int(digits), name)
        else:
            lf = "{}{}{:05d}".format(prefix, name, int(postfix)) \
                  if postfix else "{}{}".format(prefix, name)
    else:
        #only get here if filename starts with non alphanum '_' etc...
        lf = filename
    return lf

def to_alpha(anumber):
    """Convert a positive number n to its digit representation in base 26."""
    output = ''
    a_number = anumber
    if anumber == 0:
        pass
    else:
        while a_number > 0:
            output += chr(a_number % 26 + ord('A'))
            a_number = a_number // 26
    return output[::-1]


def is_hashable(tag):
    '''return true if tag hashable'''
    return True if True in HASH_TAG_ON[tag] else False

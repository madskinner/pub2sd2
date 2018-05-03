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
import codecs
from unidecode import unidecode
from mutagen.mp3 import MP3
import re
import ast
import shutil
import pickle

from lxml import etree

from tkinter import messagebox


from .myconst.regexs import FIND_LEADING_DIGITS, FIND_LEADING_ALPHANUM, \
                            FIND_TRAILING_DIGITS, TRIM_LEADING_DIGITS, \
                            TRIM_TRAILING_DIGITS, STRIPPERS
from .myconst.readTag import IDIOT_TAGS, READ_TAG_INFO, HASH_TAG_ON

from .myconst.therest import THIS_VERSION, THE_IDIOT_P, THE_P, LATIN1, \
                            PICTURE_TYPE, TF_TAGS#, PF,
from .myconst.localizedText import SET_TAGS, TRIM_TAG, DEFAULT_VALUES

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

class Backend(threading.Thread):
    """handle processing files"""

    def __init__(self, qc, qr, aqr, tl):
        threading.Thread.__init__(self)
        self.threadID = 1
        self.name = 'backend'
        self.qc = qc
        self.qr = qr
        self.aqr = aqr
        self.threadlock = tl
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
        self.to_be_inserted = dict()
        self.displayColumns = list()
        self.columns = list()
        self.to_be_renamed = dict()
        self.initial_digit = ''
        self.prefix = ''
        
        #bodge to get past WinPython....
        self.Pub2SD = os.path.normpath(os.path.expanduser('~') + '/Pub2SD')
        if platform.system() == 'Windows':
            temp = self.Pub2SD.split('\\')
            self.Pub2SD = '\\'.join(temp[:3]) + '\\Pub2SD'

        self.selected_tags = list()
        self.project = ''
        self.next_track = 0
        self.nos_tracks = 0
        self.ishide = 0
        self.files = dict()
        self.M3UorM3U8 = 2


#        self.maxcolumnwidths = [0, 0, 0, ]

    def run(self):
        while not self.exitFlag:
            acommand = self.qc.get()
            if 'EXIT' in acommand:
                self.exitFlag = 1
                self.qc.task_done()#                self.destroy()
                # self.exitFlag can be set by error condition in backend
            elif 'MODE' in acommand:
                self.mode = acommand[1]
                self.qc.task_done()
            elif 'INITIALDIGIT' in acommand:
                self.initial_digit = acommand[1].upper()
                self.prefix = acommand[1]
                self.qc.task_done()
            elif 'CONF_FILE' in acommand:
                self.qc.task_done()
                self.project = acommand[1]
                self._load_conf_file(acommand[1])
            elif 'LOAD_TEMPLATE' in acommand:
                self.template = acommand[1]
                self.qc.task_done()
            elif 'LOADTREEFROMTROUT' in acommand:
                self._on_reload_tree()
                self.qc.task_done()
            elif 'SELFPREF' in acommand:
                self.pref = acommand[1][0]
                self.pref_char = acommand[1][1]
                self.preferred = acommand[1][2]
                self.template = acommand[1][3]
                self.qc.task_done()
            elif 'DISPLAYCOLUMNS' in acommand:
                self.displayColumns, self.columns = acommand[1]
                self.qc.task_done()
            elif 'SELECTED_TAGS' in acommand:
                map(self.sf1.attrib.pop, self.sf1.attrib.keys())
                #put tag state into xml
                self.selected_tags = acommand[1]
                for i in range(0, len(self.selected_tags)):
                    self.sf1.attrib[self.selected_tags[i]] = 'show'
            elif 'STRIPTITLE' in acommand:
                to_strip, focus = acommand[1]
                self._on_strip(to_strip, focus)
                self.to_be_renamed = dict()
                self._rename_children_of(focus)
                self.qr.put(('RENAME_CHILDREN', self.to_be_renamed))
            elif 'HASHEDGRAPHICS' in acommand:
                self.hashed_graphics = acommand[1]
                self.qc.task_done()
            elif 'ADD_FOLDER' in acommand:
                self.qr.put(('LOCKGUI', None))
                self.to_be_inserted = dict()
                the_focus, adir_path = acommand[1]
                self.qr.put(('PROGMAX', count_mp3_files_below(adir_path) * 2))
                self._add_tree(the_focus, adir_path, False)
                self._on_reload_tree()
                self.qr.put(('STATUS', "Unpacking complete."))
                self.qr.put(('PROGVALUE', 0))
                self.qr.put(('UNLOCKGUI', None))
                self.qc.task_done()
            elif 'ADD_CONTENTS' in acommand:
                the_focus, adir_path = acommand[1]
                #if the_focus is I00001 then any .mp3 files in current folder
                # would be directly below project. Need to have at least one
                # collection in way
                self.qr.put(('LOCKGUI', None))
                self.qr.put(('PROGMAX', count_mp3_files_below(adir_path) * 2))
                self.to_be_inserted = dict()
                self._add_tree(the_focus, adir_path, True)
                self._on_reload_tree()
                self.qr.put(('STATUS', "Unpacking complete."))
                self.qr.put(('PROGVALUE', 0))
                self.qr.put(('UNLOCKGUI', None))
                self.qc.task_done()
            elif 'ADD_COLLECTION' in acommand:
                focus = acommand[1]
                self.qr.put(('LOCKGUI', None))
                self._add_collection(focus)
                self._on_reload_tree()
                self.qr.put(('STATUS', "Unpacking complete."))
                self.qr.put(('PROGVALUE', 0))
                self.qr.put(('UNLOCKGUI', None))
                self.qc.task_done()
            elif 'ADD_FILE' in acommand:
                focus, filenames = acommand[1]
                self.qr.put(('LOCKGUI', None))
                self.qr.put(('PROGMAX', len(filenames) * 2))
                self.to_be_inserted = dict()
                self._add_files(focus, filenames)
                self._on_reload_tree()
                self.qr.put(('UNLOCKGUI', None))
                self.qc.task_done()
            elif 'CHILDRENS_FILENAMES' in acommand:
                self.project_id, temp_path, project_path_ = acommand[1]
                #self.project_id should be set to 'I00001', but for safety
                self._childrens_filenames(self.trout.find(".//I00001"), temp_path, project_path_)
            elif 'FOLDERSIZE' in acommand:
                size_in_Mb = folder_size(os.path.normpath(\
                    self.Pub2SD + '/Temp/' + self.project))/(1024.0 * 1024.0)
                self.qr.put(('FOLDERSIZE', size_in_Mb))
            elif 'PUBLISHFILES' in acommand:
                self._on_publish_files(acommand[1])
            elif 'PREPARE_FILES' in acommand:
                self.qr.put(('LOCKGUI', None))
                self._on_prepare_files()
                self.qr.put(('UNLOCKGUI', None))
            elif 'ONSAVEPROJECT' in acommand:
                self._on_save_project(acommand[1])
            elif 'DELETE' in acommand:
                self._on_delete(acommand[1])
            elif 'MOVEUP' in acommand:
                self._on_move_up(acommand[1])
            elif 'MOVEDOWN' in acommand:
                self._on_move_down(acommand[1])
            elif 'PROMOTE' in acommand:
                self._on_promote(acommand[1])                
            elif 'DEMOTE' in acommand:
                self._on_demote(acommand[1])  
                self._on_reload_tree()
            elif 'ON_SET' in acommand:
                self._on_set(acommand[1])
            elif 'ATTACH_ARTWORK_TO' in acommand:
                focus, _picture_type, _desc, fart = acommand[1]
                self._attach_artwork_to(focus, _picture_type, _desc, fart)
                self._on_reload_tree()
            elif 'SETCOPYPLAYLISTS' in acommand:
                self.play_list_targets, self.is_copy_playlists_to_top = acommand[1]
            elif 'M3UorM3U8' in acommand:
                self.M3UorM3U8 = acommand[1]
            else:
                print('backend lost, acommand was {}'.format(acommand))
                self.qc.task_done()

    def _load_conf_file(self, aconf_file):
        """loads the old project file into etree tree"""
        the_file = os.path.normpath(self.Pub2SD + '/' + aconf_file + '.prj')
        if aconf_file and os.path.isfile(the_file):
            result = self._load_project(the_file)
        else:
            result = self._create_project()
        self.qr.put(('CONTINUE_F0_NEXT', result))

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
        if thefile:
            linesin = list()
            filein = codecs.open(thefile, mode='r', encoding='utf-8')
            for aline in filein.readlines():
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
            self._fix_old_proj_iid(self.trout)
                
            self.old_mode = dict(self.smode.attrib)
        idiot_case = self._get_idiot_case_mode_for_load_project()
        if idiot_case == 1:
            # downgrade
            self.mode = 0
            self.qr.put(('MESSAGEBOXASKOKCANCEL', ('Confirm Downgrade?', \
                        "This will downgrade this project from 'Advanced' " \
                        + "to 'Simple'. Some data may be lost." )))
            #if not OK give up
            if not self._wait_for_responce():
                return False
            #do downgrade!
            #remove all non idiot tags
            self.list_of_tags = set()
            difference = set(SET_TAGS['en-US'].keys()).\
                                            difference(set(IDIOT_TAGS.keys))
            etree.strip_attributes(self.trout, difference)
            etree.strip_attributes(self.sf1, difference)
            etree.strip_attributes(self.stemp, difference)
            self._downgrade_child_of(self.trout)
            pass
        elif idiot_case == 2:
            # upgrade:
            self.qr.put(('MESSAGEBOXASKOKCANCEL', ('Confirm Upgrade?', \
                        "This will upgrade this project from 'Simple' to " \
                        + "'Advanced'." )))
            #if not OK give up
            if not self._wait_for_responce():
                return False
            self.mode = 1
            self._upgrade_child_of(self.trout)
        else:
            pass
        self.template = dict(self.stemp.attrib)
        

        if self.mode == 0:
            self.smode.attrib['Idiot'] = 'True'
            self.list_of_tags = self.list_of_tags.union(set(IDIOT_TAGS.keys()))
            all_tags = self.recommendedTags + list(set(self.recommendedTags)\
                                        .difference(set(IDIOT_TAGS.keys())))
#            self._pdup_state('disabled')
        else:
            self.smode.attrib['Idiot'] = 'False'
            self.list_of_tags = self.list_of_tags.union(\
                                                set(SET_TAGS['en-US'].keys()))
            all_tags = self.recommendedTags + \
               list(set(self.recommendedTags).\
                                    difference(set(SET_TAGS['en-US'].keys())))
#            self._pdup_state('normal')
        self.preferred = int(self.smode.attrib['preferred'] == 'True')
        self.qr.put(('TXTPREFCHARDEL', (0.0, 9999.9999)))
        if self.sf2.text != None:
            self.qr.put(('TXTPREFCHARINSERT', (9999.9999, self.sf2.text)))

        #clear tagtree
        self.qr.put(('CLEARTAGTREE', None))
        self.qr.put(('INSERTTAGTREETAGS', all_tags))
        self.qr.put(('SETTAGTREE', 'TIT2'))
        #now select tags
        for item in self.sf1.attrib.keys():
            self.qr.put(('SELECTIONTAGTREE', item))
        #now add any additional tags in template
        for item in set(self.stemp.attrib.keys()).\
                                    difference(set(self.sf1.attrib.keys())):
            self.qr.put(('SELECTIONTAGTREE', item))
        #f4 feature phone folders
        self.qr.put(('ENTERLIST',self.sf4.get('folderList')))
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
                                              if os.path.isfile(picklein) \
                                              else dict()
        return True

    def _downgrade_child_of(self, parent):
        for child in parent.getchildren():
            if child.attrib['Type'] not in ['project', 'collection']:
                for tag in child.attrib.keys():
                    self.list_of_tags.add(tag)
                    child.attrib[tag] = self._downgrade_data(tag, child)
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
                if item in IDIOT_TAGS: 
                    param = ast.literal_eval(str(this_frame))
                    if item == 'APIC':
                        return param[-1]
                    elif item in TF_TAGS or item == 'COMM':
                        return param[-1][0]
                    elif item in ['WCOM', 'WCOP', 'WOAF', 'WOAR', 'WOAS', \
                                  'WORS', 'WPAY', 'WPUB', 'WXXX']:
                        return param[-1]
                    return this_frame
                else:
                    #not idiot tag so discard 'advanced' data
                    return ''
            else:# is 'empty' frame
                return this_frame
        return the_value

                
    def _upgrade_data(self, item, child):
        """smarten data up from simple(idiot) mode to advanced with encoding
           and full structure for each tag of the specified item.
                 e.g. on a text frame, 'a string' becomes [3, ['astring', ]]"""

        #for each frame in last value in the_values, smarten it up
#        this_frame = the_values[-1]
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
#                        a_frame = child.attrib['APIC_'].split('|')[0]
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
                        this_frame = "[3,{},{},{},{}]".\
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
                        this_frame = "[3,{},3,'',{}]".\
                                              format(_mime, a_frame)
                elif item == 'TBPM':
                    packit = '["' + a_frame + '"]'
                    this_frame = DEFAULT_VALUES['ide3v24'][item].\
                                                    replace('["0"]', packit)
                else:
                    packit = '["' + a_frame + '"]'
                    this_frame = DEFAULT_VALUES['ide3v24'][item].\
                                                    replace('[""]', packit)
#                this_frame = a_frame
            elif item == 'APIC_':
                #and return to last value in the_values
                this_frame = a_frame
            else:
                this_frame = a_frame
        else:
            this_frame = a_frame
        return this_frame

    def _create_project(self):
        """create new project"""

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
        self.old_mode = dict(self.smode.attrib)

        if self.mode == 0:
            self.list_of_tags = self.list_of_tags.union(set(IDIOT_TAGS.keys()))
#            self._pdup_state('disabled')
        else:
            self.list_of_tags = self.list_of_tags.union(\
                                                set(SET_TAGS['en-US'].keys()))
        self.qr.put(('INSERTTAGTREETAGS', self.list_of_tags))

        for atag in self.recommendedTags:
            self.sf1.attrib[atag] = 'show'
        self.qr.put(('SELECTIONTAGTREE', self.recommendedTags))
            
        self.sf2.text = ''

        self.stemp.text = ''

        self.sf4.attrib['folderList'] = ''
        self.sf4.attrib['is_copy_playlists_to_top'] = 'False'
        self.sf4.attrib['M3UorM3U8'] = '2'
        return True

    def _load_tree_from(self, _trout):
        if not _trout:
            tree = self.trout
            parent = ''
        else:
            tree = self.trout.find(".//" + _trout)
            parent = tree.tag
        if len(tree):
            for child in tree.getchildren():
                vout= list()
                for k in self.columns:
                    if k not in ['adummy', '_APIC'] and k in child.attrib:
                        if self.mode: #is advanced
                            vout.append(child.attrib[k])
                        else: #is idiot
                            data = self._downgrade_data(k, child)
                            vout.append(data)
                    else:
                        vout.append('-')
                self.to_be_inserted[child.tag] = (parent, vout, child.text if child.text else '')
                self._load_tree_from(child.tag)


    def _on_save_project(self, aproject):
        """save current project"""

        if os.path.exists(aproject):
            os.remove(aproject)

        if aproject:
            output = codecs.open(aproject, mode='w', encoding='utf-8')
            output.write(etree.tostring(self.root, encoding='unicode', \
                                         pretty_print=True))
            output.close()
            pickleout = aproject[:-4] + '.pkl'
            pout = open(pickleout, 'wb')
            pickle.dump(self.hashed_graphics, pout, pickle.HIGHEST_PROTOCOL)
            # list projects in Pub2SD and update list in self.ddnCurProject
            pout.close()
            self.qr.put(('LISTPROJECTS', os.path.basename(aproject[:-4])))
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
            self.qr.put(('STATUS{}', ('Unpacking{}', afile)))
            self._add_a_file(afile, node)
            self.qr.put(('PROGSTEP', 1))

    def _add_a_file(self, afile, e_parent):
        """loads a file into e_parent within self.trout"""
        #always hold data in advanced form, only choose to diplay as idiot
#        print('add=>{}< to >{}<'.format(afile, e_parent.tag))
        somevalues = self._read_mp3_tags(afile)
        iid = "I{:05X}".format(self.next_iid)
        self.next_iid += 1
        self.to_be_inserted[iid] = (e_parent.tag, somevalues, 'file')
        e_child = etree.SubElement(e_parent, iid)
        e_child.text = 'file'
        for c,v in zip(self.columns, somevalues):
            e_child.attrib[c] = v

    def _add_tree(self, the_focus, adir_path, noTop=False):
        """add folder and dependants, with or without creating a new
           collection of the same name as the folder at the current focus
           in the Treeview widget"""

        if noTop:
            thisdir = the_focus
            e_parent = self.trout.find(".//" + the_focus)
        else:
            vout = ['collection', '-', '-']
            if 'TIT2' in self.displayColumns:
                vout.extend([self._my_unidecode(os.path.split(adir_path)[-1]),])
            vout.extend(['-' for item in self.displayColumns[2:-1]])
            iid = "I{:05X}".format(self.next_iid)
            self.next_iid += 1
            self.to_be_inserted[iid] = (the_focus, vout, 'collection')
            thisdir = iid
            e_focus = self.trout.find(".//" + the_focus)
            e_parent = etree.SubElement(e_focus, iid)
            e_parent.text = 'collection'
            for c,v in zip(self.columns, vout):
                e_parent.attrib[c] = v

        _ff = dict()
        flist = dict()
        #step through a list of filepaths for all mp3 files in current dir only
        for f_ in [forward_slash_path(afile) \
                   for afile in glob.glob(adir_path + '/*.mp3')]:
#            print('sort key =>{}<, for {}'.format(sort_key_for_filenames(os.path.basename(f_)[:-4]), \
#                                                    os.path.basename(f_)[:-4]))
            _ff[sort_key_for_filenames(os.path.basename(f_)[:-4])] = \
                                                    os.path.basename(f_)[:-4]
            flist[os.path.basename(f_)[:-4]] = f_

        for _ll in sorted(_ff):
            self._add_a_file(flist[_ff[_ll]], e_parent)
            self.qr.put(('PROGSTEP', 1))
        # recurse through sub-dirs
        for adir in sorted([os.path.normpath(adir_path + '/' + d) \
                            for d in os.listdir(adir_path) \
                                if os.path.isdir(adir_path + '/' + d) \
                                            and len(d) > 0]):
            self.qr.put(('STATUS{}', ('Unpacking{}', adir)))
            self._add_tree(thisdir, adir)

    def _rename_children_of(self, parent):
        """rename all the children of parent, parents name is unchanged.
           Typicaly will always call on the top level project collection"""
        #rename all branches
        e_parent = self.trout.find(".//" + parent)
        if e_parent is None:
            return
        parent_attribs = e_parent.attrib
        children = list(e_parent)
        ancestor_name = parent_attribs['Name']
        my_isalpha = True
        if ancestor_name:
            if ancestor_name[-1] == '@':
                my_name = '@'
            else:
                my_name = 1
                my_isalpha = ancestor_name[-1].isdecimal()
        else:
            my_name = 1
            if self.initial_digit:
                my_isalpha = self.initial_digit[-1].isdecimal()
            else:
                my_name = 1
                my_isalpha = False
        my_num = 1
#        if my_isalpha:
#            nos_chars = len(to_alpha(len(children)))
#            pass
#        else:
#            nos_digits = (len(str(len(children)))-1) \
#                     if my_name == 1 else 0
        nos_chars = len(to_alpha(len(children))) if my_name == 1 else 0
        nos_digits = (len(str(len(children)))-1) if my_name == 1 else 0

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
                child.attrib['Name'] = ancestor_name + my_str
                child.text = "{0}{1}{2}-{3}".format(self.prefix, \
                                               ancestor_name, my_str, title)
                vout = [['Name', child.attrib['Name']], ['TIT2', title]]
                self.to_be_renamed[child.tag] = [vout, child.text]
                my_name += 1
                self._rename_children_of(child.tag)
            else: #is file so use
                size = os.path.getsize(child.attrib['Location']) \
                                if child.attrib['Location'] != '-' \
                                else 0
                if size == 0:
                    #fetch location, trim off path and '.mp3' extension,
                    #transliterate unicode(utf-8) to 7-bit ascii or Latin-1?
                    title = self._my_unidecode(os.path.basename(\
                                            child.attrib['Location'][:-4]))
                    #transliterate unicode(utf-8) to 7-bit ascii or Latin-1?
                    #replace spaces and punctuation  - done in my_unidecode
                    child.attrib['Name'] = ancestor_name + my_str
                    child.text = "{0}{1}{2}-{3}".format(self.prefix, \
                                   ancestor_name, my_str, title)
                    vout = [['Name', child.attrib['Name']], ['TIT2', title]]
                else: #idiot/not idiot always downgrade TIT2 to form title
                    tit2 = self._downgrade_data('TIT2', child)
                    title = self._my_unidecode(tit2)
                    child.attrib['Name'] = "{0}-{1:02d}".format(\
                                                     ancestor_name, my_num)
                    child.text="{0}{1}-{2:02d}-{3}".format(self.prefix, \
                                         ancestor_name, my_num, title)
                    if self.mode: #advanced
                        vout = [['Name', child.attrib['Name']],\
                                               ['TIT2', child.attrib['TIT2']]]
                    else: #simple
                        vout = [['Name', child.attrib['Name']],['TIT2', tit2]]
                self.to_be_renamed[child.tag] = [vout, child.text]
                my_num += 1
            self.qr.put(('PROGSTEP', 1))


    def _my_unidecode(self, text):
        """normalize strings to avoid unicode character which won't display
           correctly or whose use in filenames may crash filesystem"""
        l = list()
        if self.preferred != 1:
            self.pref = list()
        #fix eng/Eng 'bug' in unidecode
        if 'ŋ' not in [v[0] for v in self.pref]:
            self.pref.append(['ŋ', 'ng', re.compile('ŋ')])
        if 'Ŋ' not in [v[0] for v in self.pref]:
            self.pref.append(['Ŋ', 'Ng', re.compile('Ŋ')])
        #scan list of preffered character/string pairs
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

    def _read_mp3_process_atag(self, atag, k, apic_params, filepath):
        """process the (advanced) mp3 tag"""
        #force utf8 encoding, the form all text is held in internally
        atag.encoding = 3

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
        elif k in THE_P:
            theParameters = THE_P[k](atag, True)
        else:
            self.qr.put(('MESSAGEBOXSHOWERRORIN', ('Error in read_mp3_process atag()', \
                "{} is unrecognized  MP3 tag in {}".format(\
                                               atag, filepath))))
        return theParameters

    def _read_mp3_tags(self, filepath):
        """read in an mp3 files tags to Treeview wiget"""
#        print('in read mp3 tags')
        if os.path.getsize(filepath) > 0:
            audio = ID3(filepath)
            result = ['file', '', filepath]
            apic_params = list()
            for k in self.displayColumns[1:-1]:
                #list all instances of that tag
                list_tags = audio.getall(k)
                aresult = list()
                if list_tags:
                    for atag in list_tags:
                        theParameters = \
                                self._read_mp3_process_atag(atag, k, \
                                                        apic_params, filepath)
                        if theParameters != None:
                            aresult.extend([str(theParameters)])
                    result.extend(['|'.join(aresult)])
                else:
                    title = os.path.basename(filepath)[:-4]
                    result.extend(['[3, ["{}"]]'.format(title.strip())]\
                                         if k == 'TIT2' else ['-',])
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
#            print('full display columns is {}'.format(self.displayColumns))
#            print('zero length file, with display columns {}'.format(self.displayColumns[2:-1]))
#            if 'TIT2' in self.displayColumns[2:-1]:
            if 'TIT2' in self.displayColumns[1:-1]:
                result.extend(['[3, ["{}"]]'.format(\
                                     os.path.basename(filepath)[:-4])])
#        print(result)
        return result

#    def _read_idiot_mp3_process(self, atag, k, apic_params, filepath):
#        """process the idiot mp3 tag"""
#
#        theParameters = None
#        if k in THE_IDIOT_P:
#            theParameters = THE_P[k](atag, False)
#        elif k == 'APIC':
#            m = hashlib.sha256(atag.data)
#            if m.hexdigest() not in self.hashed_graphics:
#                self.hashed_graphics[m.hexdigest()] = atag.data
#            apic_params.extend([str([int(atag.encoding), \
#                                     atag.mime, \
#                                     int(atag.type), \
#                                        atag.desc, \
#                                        m.hexdigest()])])
#            length = int(len(atag.data)/1024 + 0.5)
#            theParameters = "b'{}Kb'".format(length)
#        else:
#            messagebox.showerror(\
#        'Error in read_idiot_mp3_tags()', \
#        "{} is unrecognized MP3 tag in simple mode in {}.".\
#             format(atag, filepath))
#            theParameters = ''
#        return theParameters
#
#    def _read_idiot_mp3_tags(self, filepath):
#        """read the mp3 tags of file in idiot mode"""
#        if os.path.getsize(filepath) > 0:
#            audio = ID3(filepath)
#            result = ['file', '', filepath]
#            apic_params = list()
#            for k in self.displayColumns[1:-1]:
#                list_tags = audio.getall(k)
#                #print(k, len(list_tags))
#                aresult = list()
#                if list_tags:
#                    atag = list_tags[0]
#                    theParameters = self._read_idiot_mp3_process(atag, k, \
#                                                        apic_params, filepath)
#                    if theParameters != None:
#                        aresult.extend([str(theParameters)])
#
#                    result.extend(['|'.join(aresult)])
#                else:
#                    if k == 'TIT2':
#                        title = os.path.basename(filepath[:-4]) \
#                                                if '/'in filepath else filepath
#                        result.extend(['{}'.format(title.strip())])
#                    else:
#                        result.extend(['-',])
#                if k in self.template.keys() \
#                         and self.template[k] and result[-1] == '-':
#                    result[-1] = self.template[k]
#            #insert empty string for adummy column
#            result.extend(['',])
#            if apic_params:
#                result.extend(['|'.join(apic_params)])
#        else: #zero length file No Tags!
#            result = ['file', '', filepath]
#            if 'TIT2' in self.displayColumns[1:-1]:
#                title = os.path.basename(filepath)[:-4]
#                result.extend(['{}'.format(title)])
#            else:
#                result.extend(['#',])
#        return result

    def _childrens_filenames(self, e_parent, temp_path, project_path_):
        '''form childrens file names'''
        children = e_parent.getchildren()
        for e_child in children:
            new_dir = e_child.text
            attributes = e_child.attrib

            if attributes['Type'] == 'collection':
                thispath = os.path.normpath(temp_path + '/' + new_dir)
                final_path = os.path.normpath(project_path_ + '/' + new_dir)
                os.makedirs(thispath, mode=0o777, exist_ok=True)
                self._childrens_filenames(e_child, thispath, final_path)
            else: #is file
                title = e_child.text.strip()
                thispath = os.path.normpath(temp_path + '/' + title + '.mp3')
                thatpath = os.path.normpath(project_path_ + '/' + \
                                            self._my_unidecode(title) + '.mp3')
                if ('APIC' in self.displayColumns) and ('APIC' in attributes.keys()):# and \
#                           (int(os.path.getsize(thispath)) > 0):
                    #                   [temp path,
                    #                   source path,
                    #                   Apic,
                    #                   target, ?,
                    #                   title]
                    self.files[e_child.tag] = [thispath, \
                                          attributes['Location'], \
                                          attributes['APIC'], \
                                          thatpath, '', \
                                          attributes['TIT2']]
                else:
                    self.files[e_child.tag] = [thispath, \
                                          attributes['Location'], \
                                          '', \
                                          thatpath, \
                                          '', \
                                          attributes['TIT2'] \
                                          if 'TIT2' in attributes.keys() \
                                          else os.path.basename(attributes['Location'])[:-4]]


    def _on_prepare_files(self):
        '''prepare files in temp folder'''

        self.qr.put(('PROGMAX', len(self.files)))
#        print('in on prepare files, display columns =>{}<'.format(self.displayColumns))
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
                print('{} is a zero length file! So...'.format(self.files[child.tag][1]))
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
#            print('in idiot, apic_params ={}'.format(apic_params))
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
            _data = open(os.path.normpath(atag), \
                                     'rb').read()
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
            _data = open(\
        os.path.normpath(param[4]), 'rb').read()
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
        self.qr.put(('STATUS', 'Removing any old project files...' ))
        if target[1:] != ':\\' and \
                 os.path.exists(os.path.normpath(target + '/' + self.project)):
            # remove if exists
            shutil.rmtree(os.path.normpath(target + '/' + self.project))

        tp = os.path.normpath(target + '/' + self.project)
        os.makedirs(tp, mode=0o777, exist_ok=True)
        target += '/'
        target = forward_slash_path(target)
        #decide if space avaialable on target - abort if not with error message
        self.qr.put(('STATUS', 'Calculating needed space...' ))
        _, _, free = shutil.disk_usage(os.path.normpath(target))
        needed = folder_size(\
                    os.path.normpath(self.Pub2SD + '/Temp/'+self. project)) / \
                             (1024.0 * 1024.0)
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
#            final_path = os.path.normpath(target + \
#                                '/'.join(self.files[child][3].split('/')[:-1]))
            final_path = os.path.dirname(\
                            os.path.normpath(target + self.files[child][3]))
            if final_path not in listpaths:
                os.makedirs(final_path, mode=0o777, exist_ok=True)
                listpaths.extend([final_path])
            self.qr.put(('PROGSTEP', 1))
        #now open all files at once to make create dates the same
        self.qr.put(('STATUS', 'Opening target files...'))
        for child in self.files:
            fileId[child] = open(os.path.normpath(target + \
                                              self.files[child][3]), mode='wb')
            self.qr.put(('PROGSTEP', 1))
        self.qr.put(('STATUS', 'Copying to target files...'))
        for child in sorted(self.files.keys()):
            filein = open(os.path.normpath(self.files[child][0]), mode='rb')
            fileId[child].write(filein.read())
            filein.close()
            self.qr.put(('PROGSTEP', 1))
        #close all files at once to make modified dates the same
        self.qr.put(('STATUS', 'Closing target files...'))
        for child in sorted(self.files.keys()):
            fileId[child].close()
            self.qr.put(('PROGSTEP', 1))
        self._on_copy_playlists(target)
        self.qr.put(('PROGMAX', 0))
        self.qr.put(('STATUS', "Publishing completed."))

    def _on_copy_playlists(self, target):
        """copy playlists to target, at locatons specified in
                                                         play_list_targets"""
        self.qr.put(('STATUS', 'Copying playlists...'))
        source = os.path.normpath(self.Pub2SD + '/Temp/'+ self.project + '/')
        playlists = [p for p in os.listdir(source) \
                     if p.endswith('.M3U8') or p.endswith('M3U')]
        self.qr.put(('PROGMAX', len(playlists) * ( 1 + self.is_copy_playlists_to_top + len(self.play_list_targets))))
        #main playlists
        for pp in playlists:
            shutil.copyfile(os.path.normpath(source + '/' + pp), \
                            os.path.normpath(target + self.project + '/' + pp))
            self.qr.put(('PROGSTEP', 1))
        #now top level?
        if self.is_copy_playlists_to_top:
            self.qr.put(('STATUS', 'Copying playlists to top folder...'))
            for pp in playlists:
                encode = 'utf-8' if pp.endswith('.M3U8') else 'cp1252'
                fin = codecs.open(os.path.normpath(source + '/'+ pp),\
                                          mode='r', encoding=encode)
                fout = codecs.open(os.path.normpath(target + pp), mode='w', \
                                   encoding=encode)

                fout.write(fin.read().replace('../', './'))
                fin.close()
                fout.close()
                self.qr.put(('PROGSTEP', 1))
        #now in list
        for tt in self.play_list_targets:
            if tt:
                self.qr.put(('STATUS', 'Copying playlists to target folders...'))
                os.makedirs(target + tt, mode=0o777, exist_ok=True)
                for pp in playlists:
                    shutil.copyfile(os.path.normpath(source + '/' + pp), \
                                    os.path.normpath(target + tt + '/' + pp))
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
            if len(parent):
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
            print("unrecognised stripper >{}<".format(to_strip))

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
                    
        self.qr.put(('UNLOCKGUI', None))

    def _is_promotable(self,gp,p,c):
        if (gp in ['project', 'collection']) and \
                    (p in ['collection',]) and \
                    (c in ['collection',]):
            return True
        elif (gp in ['collection',]) and \
                    (p in ['collection']) and \
                    (c in ['collection','file']):
            return True
        else:
            return False
            

    def _on_load_tree_from_trout(self):
        self.qr.put(('HASHEDGRAPHICS', self.hashed_graphics))
        self._rename_children_of(list(self.trout)[0].tag)
        self.to_be_inserted = dict()
        self._load_tree_from('')
        self.qr.put(('ADD_ITEMS', self.to_be_inserted))

    def _on_reload_tree(self):
        self.qr.put(('CLEARTREE', None))
        self._on_load_tree_from_trout()

    def _on_set(self, atuple):
        """set value of tag"""
        focus, column, text = atuple
        focus_item = self.trout.find(".//" + focus)
        name = focus_item.attrib['Name']
        location = focus_item.attrib['Location']
        if self.mode != 0:
            for test in text.split('|'):
                if len(HASH_TAG_ON[column]) != len(ast.literal_eval(test)):
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
            self.qr.put(('MESSAGEBOXWARNTRACK', ('', 'Set',' TRCK, >{}< {}', \
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
        res = urlparse(tempstr)
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
            children = parent.getchildren()
            for child in children:
                self._set_sort_(child)
        else:
            #is file so…
            name = parent.attrib['Name']
            if self.isHide == 1:
                name = '"' + name + '"'
            else:
                name = DEFAULT_VALUES['ide3v24'][column][0:5] + name + \
                                        DEFAULT_VALUES['ide3v24'][column][5:]
            parent.attrib[column] = name

    def _set_tag_(self, parent, column, text):
        """set tag specified in column with value in text, for current
           item or it's dependants"""
        if parent.attrib['Type'] in ['collection', 'project']:
            children = parent.getchildren()
            for child in children:
                self._set_tag_(child)
        else: #is file so…
            if not self.mode: # == 0 is idiot
                parent.attrib[column] = text
            else: #not idiot
                if is_hashable(column):
                    currentTag = parent.attrib[column]
                    currentFrames = str(currentTag).split('|')
                    textFrames = text.split('|')
                    if len(textFrames) > 1: #multiple frames
                        if textFrames is not currentFrames: #so replace them
                            parent.attrib[column] = text
                    else:
                        #text is single frame
                        if self._is_different_hash(currentFrames, text, column):
                            #so append
                            currentFrames.extend([text])
                        else: #replace a frame
                            currentFrames[\
                                    self._list_different_frames(currentFrames, \
                                            text, column).index(False)] = text
                        parent.attrib[column] = '|'.join(currentFrames)
                else:
                    parent.attrib[column] = text

    def _list_different_frames(self, currentFrames, text, tag):
        """list different frames, for tags which support this
                                                      (e.g. COMM, APIC,...)"""

#        lang = self.ddnGuiLanguage.get()
        is_different_to_all = list()
        textParams = ast.literal_eval(text)
        #test all frames have same length as text, flag error and return false
        for aFrame in currentFrames:
            if aFrame:
                frameParams = ast.literal_eval(aFrame)
                if len(frameParams) != len(textParams):
                    self.qr.put(('MESSAGEBOXSHOWWARNING2', \
                                                    ('', 'MissMatchedFrames')))
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


    def _on_generate_playlists(self):
        '''generate the playlists'''

        # this is where all labels changed modify for new prog
        # - just kept as example
#        self.nodes = 0
        self.nodes = len(self.trout.find(".//I00001").xpath(".//*"))
#        self._count_nodes('')
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

        this_list = list() #list for this pid
        self.qr.put(('PROGSTEP', 1))
        self.qr.put(('STATUS{}', ('Creating playlist for {}', pid_item.text)))
        for child in pid_item.getchildren():
            if child.attrib['Type'] in ['collection', 'project']:
                cloc = ploc + child.text + '/'
                self._create_play_list(child, cloc, this_list)
            elif os.path.getsize(os.path.normpath(self.files[child.tag][0])) > 0:
                #is real mp3 file so...
                this_list.append([os.path.normpath(self.files[child.tag][3]), \
                                                child.attrib['TIT2'], \
                                                child.attrib['TALB'], \
                                                str(self.files[child.tag][4])])
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
                    playlist.append('#EXTINF:{},{}-{}\r\n../{}'.\
                                    format(item[3], item[2], item[1], \
                                           forward_slash_path(item[0])))
                filepath = os.path.normpath('{}/Temp/{}/{}.M3U8'.\
                                            format(self.Pub2SD, self.project, \
                                                   pid_item.text))
                fileout = codecs.open(filepath, mode='w', encoding='utf-8')
                fileout.write('\r\n'.join(playlist))
                fileout.close()
            elif self.M3UorM3U8 == 1:
                #is legacy
                for item in this_list:
                    playlist.append('#EXTINF:{},{}-{}\r\n../{}'.\
                                    format(item[3], self._my_unidecode(item[2]), \
                                           self._my_unidecode(item[1]), \
                                                    forward_slash_path(item[0])))
                filepath = os.path.normpath('{}/Temp/{}/{}.M3U'.\
                                            format(self.Pub2SD, self.project, \
                                                   pid_item.text))
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
                                                   pid_item.text))
                fileutf = codecs.open(fileputf, mode='w', encoding='utf-8')
                fileutf.write('\r\n'.join(utf8list))
                fileutf.close()
                #legacy
                filepath = os.path.normpath('{}/Temp/{}/{}.M3U'.\
                                            format(self.Pub2SD, self.project, \
                                                   pid_item.text))
                fileout = codecs.open(filepath, mode='w', encoding='cp1252')
                fileout.write('\r\n'.join(playlist))
                fileout.close()
        else:
            #no files in this collection with length greater than zero!
            #so skip it!!!
            pass

    def _copy_old_columns_to_new_where_exist(self, child, idiot_case, \
                                                                old_columns):
        """copy data from columns in old project to the new project
           where the old column is still selected in the new project,
                                               for the specified file (item)"""
        the_values = list()
        for item in self.columns:
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

    def _attach_artwork_to(self, target, _picture_type, _desc, artwork):
        """attaches the artwork to item in focus or to its dependants
                                                             if collection"""
        e_target = self.trout.find(".//" + target)
        if self.mode == 0:
            #is idiot so...
            text = artwork if artwork else '-'
        else:
            #is NOT idiot so...
            if artwork:
                text = '[3,"{}",{},"{}","{}"]'.format(\
                    'image/png' \
                    if artwork[-4:] == '.png' else 'image/jpg', \
                    str(_picture_type), _desc, artwork)
            else:
                text = '-'
        if e_target.attrib['Type'] is 'file':
            currentTag = e_target.attrib['APIC']
            if currentTag is '-' or self.mode == 0:
                e_target.attrib['APIC'] = text
            else:
                currentFrames = currentTag.split('|')
                if self._is_different_hash(currentFrames, text, 'APIC'):
                    #so append
                    currentFrames.extend([text])
                else:
                    #replace a frame
                    currentFrames[self._list_different_frames(currentFrames, \
                                            text, 'APIC').index(False)] = text
                e_target.attrib['APIC'] = '|'.join(currentFrames)
        else:
            #is collection, list children of focus and attach artwork to each
            children = e_target.getchildren()
            for child in children:
                self._attach_artwork_to(child.tag, _picture_type, _desc, artwork)

    def _on_publish_to_SD(self):
        """publish files and playlists to SDs"""

        lang = self.ddnGuiLanguage.get()
        threads = []
        self.qr.put(('PROGMAX', (len(self.files) * 4 * len(self.output_to))))

        i = 1
        currentThreadsActive = threading.activeCount()
        for atarget in self.output_to:
            if atarget:
                if os.path.exists(atarget):
                    target = atarget
                    threads.append(MyThread(target, \
                                            self.ddnGuiLanguage.get(), \
                                            self.Pub2SD, self.project, \
                                            self.play_list_targets, \
                                            self.is_copy_playlists_to_top, \
                                            self.files, aqr[i-1]))
                    i += 1
                    threads[-1].start()
                    self.status['text'] = \
                               LOCALIZED_TEXT[lang]['{} Threads active'].\
                           format(threading.activeCount()-currentThreadsActive)
                else:
                    messagebox.showerror(\
                                        LOCALIZED_TEXT[lang]["Invalid path"], \
                                        LOCALIZED_TEXT[lang]["Can't find {}"].\
                                                      format(atarget))

        while threading.activeCount() > currentThreadsActive:
            self.status['text'] = LOCALIZED_TEXT[lang]['{} Threads active'].\
                       format(threading.activeCount()-currentThreadsActive)
        self.qr.put(('PROGSTOP', None))
        [athread.join() for athread in threads]

        self.qr.put(('PROGMAX', 0))
        self.qr.put(('STATUS', "Output to SD('s) completed."))


def get_rid_of_multiple_spaces(tin):
    """replace multiple spaces with single space and strip leading and
        trailing spaces"""
    return DOUBLE_SPACE_TO_SINGLE.sub(r' ', tin)

def count_mp3_files_below(adir_path):
    """counts all mp3 files below given dir including subdirs"""
    matches = []
    for root, dirnames, filenames in os.walk(adir_path):
        for filename in fnmatch.filter(filenames, '*.mp3'):
            matches.append(os.path.join(root, filename))
    return(len(matches))

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
    if anumber == 0:
        pass
    else:
        while anumber > 0:
            anumber = anumber
            output += chr(anumber % 26 + ord('A'))
            anumber = anumber // 26
    return output[::-1]


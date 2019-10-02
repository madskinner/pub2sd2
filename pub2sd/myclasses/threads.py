# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 04:16:33 2017

@author: marks
"""
import threading
import queue
import os
import shutil
import zipfile
from pathlib import Path

from .myconst.localizedText import LOCALIZED_TEXT

    
class MyThread(threading.Thread):
    """handle copying to multiple SD cards"""
    def __init__(self, target, pub2sd, project, \
                play_list_targets, is_copy_playlists_to_top, files, aqr):
        threading.Thread.__init__(self)
        self.target = target
#        self.lang = lang
        self.pub2sd = pub2sd
        self.project = project
        self.play_list_targets = play_list_targets
        self.is_copy_playlists_to_top = is_copy_playlists_to_top
        self.files = files
        self.aqr = aqr

    def run(self):
        """run the thread"""
        on_publish_files(self.target, self.pub2sd, \
                       self.project, self.play_list_targets, \
                       self.is_copy_playlists_to_top, self.files, self.aqr)

def on_publish_files(target, Pub2SD, project, play_list_targets, \
                     is_copy_playlists_to_top, files, aqr, scriptdir):
    #finally copy all file to final destination):
#    atarget = os.path.normpath(target)
#    this_dir = os.path.normpath(target + '/' + project)
    atarget = Path(target)
    this_dir = atarget / project
    grain = len(files)
#    grain = 20
    if target[1:] != ':\\' and \
             this_dir.exists():
        # remove if exists
        aqr.put((1, 'STATUS', '{} Deleting...'.format(target)))
        shutil.rmtree(this_dir)
    aqr.put((2, 'PROGSTEP', 1)) #remove old dirs
    os.makedirs(this_dir, mode=0o777, exist_ok=True)
#    target = forward_slash_path(target)
    os.makedirs(this_dir, mode=0o777, \
                exist_ok=True)

    aqr.put((1, 'STATUS', '{} Creating...'.format(atarget)))
    listpaths = {os.path.normpath(target + '/' + \
                                  os.path.dirname(files[child][3])) \
                                                    for child in files}
#    aqr.put(('PRINT', "make dirs in {}".format(target)))
    #now make temp dirs
    count = 0
    for final_path in listpaths:
        os.makedirs(final_path, mode=0o777, exist_ok=True)
        count += 1
        if count > 9:
            count = 0
            aqr.put((2, 'PROGSTEP', 1)) #made dirs
    #open all source files at once to save time later
#    filein = {child:open(files[child][0], mode='rb') for child in files}
#    aqr.put(('PROGSTEP', len(files)))
    aqr.clear()
    aqr.put((1, 'STATUS', '{} Opening...'.format(atarget)))
    count = 0
    filein = dict()
    fileId = dict()
    for child in files:
        filein[child] = open(files[child][0], mode='rb')
        fileId[child] = open(os.path.normpath(target + '/' + files[child][3]), \
                                                                     mode='wb')
        count += 1
        if count > int(len(files) / grain):
            count = 0
            aqr.put((2, 'PROGSTEP', 1)) #made dirs
    aqr.clear()
    aqr.put((1, 'STATUS', '{} Copying...'.format(atarget)))
    for child in files:
        fileId[child].write(filein[child].read())
        aqr.put((2, 'PROGSTEP', 1)) #made dirs
    #close target files
    aqr.clear()
    aqr.put((1, 'STATUS', '{} Closing...'.format(atarget)))
    for child in files:
        fileId[child].close()
        aqr.put((2, 'PROGSTEP', 1)) #made dirs
#    aqr.put(('PROGSTEP', 1))#closed files
    #and close source files
    for child in files:
        filein[child].close()
        aqr.put((2, 'PROGSTEP', 1)) #made dirs

    aqr.clear()
    aqr.put((1, 'STATUS', '{} Playlists...'.format(atarget)))
    on_copy_playlists(target, Pub2SD, project, play_list_targets, \
                                              is_copy_playlists_to_top, aqr, scriptdir)
    aqr.clear()

def on_copy_playlists(target, Pub2SD, project, play_list_targets, \
                                              is_copy_playlists_to_top, aqr, scriptdir):
    source = os.path.normpath(Pub2SD + '/Temp/'+ project + '/')
    playlists = [p for p in os.listdir(source) \
                     if p.endswith('.M3U8') or p.endswith('.M3U')]
    htmllists = [h for h in os.listdir(source) \
                 if h.endswith('.html') or h.endswith('htm')]
    #main playlists
    for pp in playlists:
        shutil.copyfile(os.path.normpath(source + '/' + pp), \
                        os.path.normpath(target + project + '/' + pp))
        aqr.put((2, 'PROGSTEP', 1))
    #main htmllists
    for hh in htmllists:
        shutil.copyfile(os.path.normpath(source + '/' + hh), \
                        os.path.normpath(target + project + '/' + hh))
    #now for css and js
    #copy css and js, actually just unpack from zip
    zipdir = os.path.normpath(self.script_dir + "/cssjs.zip")
    with zipfile.ZipFile(zipdir,"r") as zip_ref:
        zip_ref.extractall(os.path.normpath(target + self.project))        

    #now top level?
    if is_copy_playlists_to_top == 1:
        for pp in playlists:
            encode = 'utf-8' if pp.endswith('.M3U8') else 'cp1252'
            fin = codecs.open(os.path.normpath(source + '/'+ pp),\
                                      mode='r', encoding=encode)
            fout = codecs.open(os.path.normpath(target + '/' + pp), mode='w', \
                               encoding=encode)
            fout.write('\r\n'.join([aline.replace('../', './') \
                                    for aline in fin.readlines()]))
            fin.close()
            fout.close()
            aqr.put((2, 'PROGSTEP', 1))
        #now copy index.html to topas project.html
        fin = codecs.open(os.path.normpath(source + '/index.html'),\
                                      mode='r', encoding=encode)
        fout = codecs.open(os.path.normpath(target + project + '.html'), mode='w', \
                               encoding=encode)
        fout.write(fin.read().replace('../', './'))
        fin.close()
        fout.close()
    #now in list
    for tt in play_list_targets:
        if tt:
            os.makedirs(target + '/' + tt, mode=0o777, exist_ok=True)
            for pp in playlists:
                shutil.copyfile(os.path.normpath(source + '/' + pp), \
                                os.path.normpath(target + '/' + tt + '/' + pp))
                aqr.put((2, 'PROGSTEP', 1))

def forward_slash_path(apath):
    '''replace all backslashes with forward slash'''
    return '/'.join(apath.split('\\'))

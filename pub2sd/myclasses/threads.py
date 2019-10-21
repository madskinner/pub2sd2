# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 04:16:33 2017

@author: marks
"""
import threading
#import queue
import os
import shutil
import zipfile
import codecs
from pathlib import Path

from .myconst.localizedText import LOCALIZED_TEXT

class MyThread(threading.Thread):
    """handle copying to multiple SD cards"""
    def __init__(self, \
                 target, \
                 pub2sd, \
                 project, \
                 play_list_targets, \
                 is_copy_playlists_to_top, \
                 files, \
                 aqr, \
                 scriptdir, \
                 lang):
        threading.Thread.__init__(self)
        self.target = str(Path(target))
#        self.lang = lang
        self.pub2sd = pub2sd
        self.project = project
        self.play_list_targets = play_list_targets
        self.is_copy_playlists_to_top = is_copy_playlists_to_top
        self.files = files
        self.aqr = aqr
        self.scriptdir = scriptdir
        self.lang = lang
#        self.aqr.put(('PRINT', "initialized thread"))

    def run(self):
        """run the thread"""
#        self.aqr.put(('PRINT', "running thread"))
        self.on_publish_files()

    def on_publish_files(self):
        """finally copy all file to final destination"""
    #    atarget = os.path.normpath(target)
    #    this_dir = os.path.normpath(target + '/' + project)
        atarget = Path(self.target)
        this_dir = atarget / self.project
        grain = len(self.files)
    #    grain = 20
        if self.target[1:] != ':\\' and \
                 this_dir.exists():
            # remove if exists
    #        aqr.put((1, 'STATUS', '{} Deleting...'.format(target)))
            self.aqr.put(('STATUS', '{} Deleting...'.format(self.target)))
            shutil.rmtree(str(this_dir))
            #NB apr is array of queues!
    #    aqr.put((2, 'PROGSTEP', 1))
        self.aqr.put(('PROGSTEP', 1))
        #remove old dirs and content
    #    os.makedirs(this_dir, mode=0o777, exist_ok=True)# think this should be rmdir?
        #this_dir is Path object
        if this_dir.exists():
            shutil.rmtree(str(this_dir))
        os.makedirs(str(this_dir), mode=0o777, exist_ok=True)

    #    aqr.put((1, 'STATUS', '{} Creating...'.format(str(atarget))))
        self.aqr.put(('STATUS', '{} Creating...'.format(str(atarget))))
    #    listpaths = {os.path.normpath(target + '/' + \
    #                                  os.path.dirname(files[child][3])) \
    #                                                    for child in files}
    #    listpaths = {str(Path(target, os.path.dirname(files[child][3]))) \
    #                                                    for child in files}
    #    aqr.put(('PRINT', "make dirs in {}".format(target)))
        #now make temp dirs
        count = 0
    #    for final_path in listpaths:
        for final_path in {str(Path(self.target, \
                                    os.path.dirname(self.files[child][3]))) \
                                                    for child in self.files}:
            os.makedirs(final_path, mode=0o777, exist_ok=True)
            count += 1
            if count > 9:
                count = 0
    #            aqr.put((2, 'PROGSTEP', 1)) #made dirs
                self.aqr.put(('PROGSTEP', 1)) #made dirs
        #open all source files at once to save time later
    #    filein = {child:open(files[child][0], mode='rb') for child in files}
    #    aqr.put(('PROGSTEP', len(files)))
    #    aqr.clear()
    #    aqr.put((1, 'STATUS', '{} Opening...'.format(atarget)))
        self.aqr.put(('STATUS', LOCALIZED_TEXT[self.lang]['{} Opening...'].format(atarget)))
        count = 0
        filein = dict()
        fileId = dict()
        for child in self.files:
            filein[child] = codecs.open(self.files[child][0], mode='rb')
            fileId[child] = codecs.open(str(Path(self.target, \
                  self.files[child][3])), mode='wb')
            count += 1
            if count > int(len(self.files) / grain):
                count = 0
    #            aqr.put((2, 'PROGSTEP', 1)) #made dirs
                self.aqr.put(('PROGSTEP', 1)) #made dirs
    #    aqr.clear()
    #    aqr.put((1, 'STATUS', '{} Copying...'.format(atarget)))
        self.aqr.put(('STATUS', LOCALIZED_TEXT[self.lang]['{} Copying...'].format(atarget)))
        for child in self.files:
            fileId[child].write(filein[child].read())
    #        aqr.put((2, 'PROGSTEP', 1)) #made dirs
            self.aqr.put(('PROGSTEP', 1)) #made dirs
        #close target files
    #    aqr.clear()
    #    aqr.put((1, 'STATUS', '{} Closing...'.format(atarget)))
        self.aqr.put(('STATUS', LOCALIZED_TEXT[self.lang]['{} Closing...'].format(atarget)))
        for child in self.files:
            fileId[child].close()
    #        aqr.put((2, 'PROGSTEP', 1)) #made dirs
            self.aqr.put(('PROGSTEP', 1)) #made dirs
    #    aqr.put(('PROGSTEP', 1))#closed files
        #and close source files
        for child in self.files:
            filein[child].close()
    #        aqr.put((2, 'PROGSTEP', 1)) #made dirs
            self.aqr.put(('PROGSTEP', 1)) #made dirs
    #    aqr.clear()
    #    aqr.put((1, 'STATUS', '{} Playlists...'.format(atarget)))
        self.aqr.put(('STATUS', LOCALIZED_TEXT[self.lang]['{} Playlists...'].format(atarget)))
        self.on_copy_playlists()
        self.aqr.put(('STATUS', LOCALIZED_TEXT[self.lang]['Completed output to>'].format(atarget)))
    #    aqr.clear()

    def on_copy_playlists(self):
        """copy the playlists from temp to play_list_targets and top level dir
        if required, adjusting relative dir references as necessary"""
        source = str(Path(self.pub2sd, 'Temp', self.project))
        playlists = [p for p in os.listdir(source) \
                         if p.endswith('.M3U8') or p.endswith('.M3U')]
        htmllists = [h for h in os.listdir(source) \
                     if h.endswith('.html') or h.endswith('htm')]
        #main playlists
        for pp in playlists:
            shutil.copyfile(str(Path(source, pp)), \
                            str(Path(self.target, self.project, pp)))
    #        aqr.put((2, 'PROGSTEP', 1))
            self.aqr.put(('PROGSTEP', 1))
        #main htmllists
        for hh in htmllists:
            shutil.copyfile(str(Path(source, hh)), \
                            str(Path(self.target, self.project, hh)))
        #now for css and js
        #copy css and js, actually just unpack from zip
    #    zipdir = os.path.normpath(script_dir + "/cssjs.zip")
    #    zipdir = str(Path(script_dir, "cssjs.zip"))
        with zipfile.ZipFile(str(Path(self.scriptdir, "cssjs.zip")), "r") \
                                                                as zip_ref:
    #        zip_ref.extractall(os.path.normpath(target + project))
            zip_ref.extractall(str(Path(self.target, self.project)))

        #now top level?
        if self.is_copy_playlists_to_top == 1:
            for pp in playlists:
                encode = 'utf-8' if pp.endswith('.M3U8') else 'cp1252'

    #            Path(target, pp)).open(encoding=encode).write_text(\
    #                Path(source, pp).open(encoding=encode).read_text())
    #            fin = codecs.open(os.path.normpath(source + '/'+ pp),\
    #                                      mode='r', encoding=encode)
    #            fout = codecs.open(os.path.normpath(target + '/' + pp), mode='w', \
    #                               encoding=encode)
    #            fout.write('\r\n'.join([aline.replace('../', './') \
    #                                    for aline in fin.readlines()]))
    #            fin.close()
    #            fout.close()
                Path(self.target, pp).open(encoding=encode).write_text(\
                    Path(source, pp).open(encoding=encode).read_text())
    #            aqr.put((2, 'PROGSTEP', 1))
                self.aqr.put(('PROGSTEP', 1))
            #now copy index.html to top as project.html
    #        fin = codecs.open(os.path.normpath(source + '/index.html'),\
    #                                      mode='r', encoding=encode)
    #        fout = codecs.open(os.path.normpath(target + project + '.html'), mode='w', \
    #                               encoding=encode)
    #        fout.write(fin.read().replace('../', './'))
    #        fin.close()
    #        fout.close()
            Path(self.target, (self.project + '.html')).open(\
                encoding=encode).write_text(\
                Path((source + '/index.html')).open(\
                    encoding=encode).read_text(\
                     ).replace('../', './'))
        #now in list
        for tt in self.play_list_targets:
            if tt:
                os.makedirs(str(Path(self.target, tt)), mode=0o777, \
                            exist_ok=True)
                for pp in playlists:
    #                shutil.copyfile(os.path.normpath(source + '/' + pp), \
    #                                os.path.normpath(target + '/' + tt + '/' + pp))
                    shutil.copyfile(str(Path(source, pp)), \
                                    str(Path(self.target, tt, pp)))
    #                aqr.put((2, 'PROGSTEP', 1))
                    self.aqr.put(('PROGSTEP', 1))

#def forward_slash_path(apath):
#    '''replace all backslashes with forward slash'''
#    return '/'.join(apath.split('\\'))

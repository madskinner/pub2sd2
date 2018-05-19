# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 04:16:33 2017

@author: marks
"""
import threading
import queue
import os
import shutil

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
#        on_publish_files(self.target, self.lang, self.Pub2SD, \
#                       self.project, self.play_list_targets, \
#                       self.is_copy_playlists_to_top, self.files)
#        print("starting thread for {}".format(self.target))
        on_publish_files(self.target, self.pub2sd, \
                       self.project, self.play_list_targets, \
                       self.is_copy_playlists_to_top, self.files, self.aqr)
#        print("ready to leave thread for {}".format(self.target))

#def on_publish_files(target, lang, Pub2SD, project, play_list_targets, \
#                     is_copy_playlists_to_top, files):
def on_publish_files(target, Pub2SD, project, play_list_targets, \
                     is_copy_playlists_to_top, files, aqr):
#    print('publish {} files to {} used by MyThead class'.format(len(files), target))
    #finally copy all file to final destination):
#    print(target)
#    target += '/'
#    print(target)
    atarget = os.path.normpath(target)
#    print(atarget)
    this_dir = os.path.normpath(target + '/' + project)
#    print(this_dir)
    grain = len(files)
#    grain = 20
    if target[1:] != ':\\' and \
             os.path.exists(this_dir):
        # remove if exists
        aqr.put((1, 'STATUS', '{} Deleting...'.format(target)))
        shutil.rmtree(this_dir)
    aqr.put((2, 'PROGSTEP', 1)) #remove old dirs
#    this_dir = os.path.normpath(target + '/' + project)
    os.makedirs(this_dir, mode=0o777, exist_ok=True)
    target = forward_slash_path(target)
    #already checked before launching thread if sufficent room!
#    #decide if space avaialable on target - abort if not with error message
#    total, used, free = shutil.disk_usage(os.path.normpath(target))
#    _, _, free = shutil.disk_usage(os.path.normpath(target))
#    needed = folder_size(os.path.normpath(Pub2SD + '/Temp/'+ project)) / \
#                                                            (1024.0 * 1024.0)
#    free = free / (1024.0 * 1024.0)
#    if needed > free:
#        messagebox.showerror(\
#                LOCALIZED_TEXT[lang]["Insufficent space on target!"], \
#                LOCALIZED_TEXT[lang]["Needed {}Mb, but only {}Mb available"].\
#                              format(needed, free))
#        return
    os.makedirs(this_dir, mode=0o777, \
                exist_ok=True)

    #list all paths used and make them
#    listpaths = {os.path.normpath(target + \
#                                  '/'.join(files[child][3].split('/')[:-1])) \
#                                                    for child in files}
    aqr.put((1, 'STATUS', '{} Creating...'.format(atarget)))
    listpaths = {os.path.normpath(target + '/' + \
                                  os.path.dirname(files[child][3])) \
                                                    for child in files}
#    aqr.put(('PRINT', "make dirs in {}".format(target)))
    #now make temp dirs
#    [os.makedirs(final_path, mode=0o777, exist_ok=True) \
#                                                 for final_path in listpaths]
    count = 0
    for final_path in listpaths:
        os.makedirs(final_path, mode=0o777, exist_ok=True)
        count += 1
        if count > 9:
            count = 0
            aqr.put((2, 'PROGSTEP', 1)) #made dirs
#    print("open source files")
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
#    print("open target files")
    #open all target files at once to make create dates the same
#    fileId = {child: \
#              open(os.path.normpath(target + files[child][3]), mode='wb') \
#                                                          for child in files}
#    aqr.put(('PROGSTEP', 1)) #opened files
#    print("copy files")
    #open all source files copy to target
#    count = 0
    for child in files:
#        filein = open(files[child][0], mode='rb')
        fileId[child].write(filein[child].read())
#        count += 1
#        if count > int(len(files) / grain):
#            count = 0
        aqr.put((2, 'PROGSTEP', 1)) #made dirs
#    aqr.put(('PROGSTEP', 1)) #copied files
#        aqr.put(('PRINT', "copyied {}".format(files[child][0])))
#    print("close target files")
    #close target files
    aqr.clear()
    aqr.put((1, 'STATUS', '{} Closing...'.format(atarget)))
    for child in files:
        fileId[child].close()
#        count += 1
#        if count > int(len(files) / grain):
#            count = 0
        aqr.put((2, 'PROGSTEP', 1)) #made dirs
#    aqr.put(('PROGSTEP', 1))#closed files
    #and close source files
#    print("close source files")
    for child in files:
        filein[child].close()
#        count += 1
#        if count > int(len(files) / grain):
#            count = 0
        aqr.put((2, 'PROGSTEP', 1)) #made dirs
#    aqr.put(('PROGSTEP', 1))#closed files
#    aqr.put(('PROGSTEP', len(files)))
#    print("copying playlists")

    aqr.clear()
    aqr.put((1, 'STATUS', '{} Playlists...'.format(atarget)))
    on_copy_playlists(target, Pub2SD, project, play_list_targets, \
                                              is_copy_playlists_to_top, aqr)
    aqr.clear()
#    aqr.put((2, 'PROGSTEP', 1)) #copied playlists
#    print("done with {}".format(target))

def on_copy_playlists(target, Pub2SD, project, play_list_targets, \
                                              is_copy_playlists_to_top, aqr):
#    print('in copy playlists')
    source = os.path.normpath(Pub2SD + '/Temp/'+ project + '/')
#    listinsource = os.listdir(source)
    playlists = [p for p in os.listdir(source) \
                     if p.endswith('.M3U8') or p.endswith('.M3U')]
    #main playlists
    for pp in playlists:
        shutil.copyfile(os.path.normpath(source + '/' + pp), \
                        os.path.normpath(target + project + '/' + pp))
        aqr.put((2, 'PROGSTEP', 1))
    #now top level?
    if is_copy_playlists_to_top == 1:
        #shutil.copyfile(os.path.normpath(source + '/' + pp), os.path.normpath(target + pp))
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

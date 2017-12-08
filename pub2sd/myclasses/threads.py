# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 04:16:33 2017

@author: marks
"""
import threading
from .myconst.localizedText import LOCALIZED_TEXT

class MyThread(threading.Thread):
    """handle copying to multiple SD cards"""
    def __init__(self, target, lang, pub2sd, project, \
                play_list_targets, is_copy_playlists_to_top, files):
        threading.Thread.__init__(self)
        self.target = target
        self.lang = lang
        self.pub2sd = pub2sd
        self.project = project
        self.play_list_targets = play_list_targets
        self.is_copy_playlists_to_top = is_copy_playlists_to_top
        self.files = files

    def run(self):
        """run the thread"""
        on_publish_files(self.target, self.lang, self.Pub2SD, \
                       self.project, self.play_list_targets, \
                       self.is_copy_playlists_to_top, self.files)

def on_publish_files(target, lang, Pub2SD, project, play_list_targets, \
                     is_copy_playlists_to_top, files):
    '''publish files to target used by MyThead class'''
    #finally copy all file to final destination):
    target += '/'

    if target[1:] != ':\\/' and \
             os.path.exists(os.path.normpath(target +  project)):
        # remove if exists
        shutil.rmtree(os.path.normpath(target +  project))

    os.makedirs(os.path.normpath(target + project), mode=0o777, exist_ok=True)
    target = forward_slash_path(target)
    #decide if space avaialable on target - abort if not with error message
    total, used, free = shutil.disk_usage(os.path.normpath(target))
    needed = folder_size(os.path.normpath(Pub2SD + '/Temp/'+ project)) / \
                                                            (1024.0 * 1024.0)
    free = free / (1024.0 * 1024.0)
    if needed > free:
        messagebox.showerror(\
                LOCALIZED_TEXT[lang]["Insufficent space on target!"], \
                LOCALIZED_TEXT[lang]["Needed {}Mb, but only {}Mb available"].\
                              format(needed, free))
        return
    os.makedirs(os.path.normpath(target + '/' + project), mode=0o777, \
                exist_ok=True)

    #list all paths used and make them
    listpaths = {os.path.normpath(target + \
                                  '/'.join(files[child][3].split('/')[:-1])) \
                                                    for child in files}
    #now make temp dirs
    [os.makedirs(final_path, mode=0o777, exist_ok=True) \
                                                 for final_path in listpaths]
    #open all target files at once to make create dates the same
    fileId = {child: open(target + files[child][3], mode='wb') \
                                                          for child in files}
    #open all source files copy to target and close source files
    for child in files:
        filein = open(files[child][0], mode='rb')
        fileId[child].write(filein.read())
        filein.close()
    #close target files
    for child in files:
        fileId[child].close()

    on_copy_playlists(target, Pub2SD, project, play_list_targets, \
                      is_copy_playlists_to_top)

def on_copy_playlists(target, Pub2SD, project, play_list_targets, \
                                                     is_copy_playlists_to_top):
    '''copy playlists'''
    source = os.path.normpath(Pub2SD + '/Temp/'+ project + '/')
    listinsource = os.listdir(source)
    playlists = [p for p in os.listdir(source) \
                     if p.endswith('.M3U8') or p.endswith('.M3U')]
    #main playlists
    for pp in playlists:
        shutil.copyfile(os.path.normpath(source + '/' + pp), \
                        os.path.normpath(target + project + '/' + pp))
    #now top level?
    if is_copy_playlists_to_top == 1:
        #shutil.copyfile(os.path.normpath(source + '/' + pp), os.path.normpath(target + pp))
        for pp in playlists:
            encode = 'utf-8' if pp.endswith('.M3U8') else 'cp1252'
            fin = codecs.open(os.path.normpath(source + '/'+ pp),\
                                      mode='r', encoding=encode)
            fout = codecs.open(os.path.normpath(target + pp), mode='w', \
                               encoding=encode)
            fout.write('\r\n'.join([aline.replace('../', './') \
                                    for aline in fin.readlines()]))
            fin.close()
            fout.close()
    #now in list
    for tt in play_list_targets:
        if len(tt) > 0:
            os.makedirs(target + tt, mode=0o777, exist_ok=True)
            for pp in playlists:
                shutil.copyfile(os.path.normpath(source + '/' + pp), \
                                os.path.normpath(target + tt + '/' + pp))

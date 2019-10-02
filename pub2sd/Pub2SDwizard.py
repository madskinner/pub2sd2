# -*- coding: utf-8 -
#-------------------------------------------------------------------------------
# Name:        Pub2SD
#""" Purpose:     Assemble, massage and copy mp3 and artwork files to SD/USB.
#            Generating various playlist files."""
#
# Author:      marks
#
# Created:     27-04-2016
# Copyright:   (c)2016 SIL international
# Licence:     Creative Commons?
#-------------------------------------------------------------------------------

import sys
import os
import platform
from pathlib import Path

from tkinter import messagebox, PhotoImage

from pub2sd.myclasses.myconst.therest import THIS_VERSION
from pub2sd.myclasses.gui import GuiCore

#from pkg_resources import resource_filename
if __name__ == '__main__' and __package__ is None:
    os.sys.path.append(os.path.dirname(os.path.dirname(\
                                                os.path.abspath(__file__))))

def hello_world():
    '''idiot test function'''
    return 'Hello world!'

def get_script_directory():
    """return path to current script"""
#    return os.path.dirname(__file__)
    return Path(__file__).parent

SCRIPT_DIR = get_script_directory()


def main():
    """the main routine"""

    frozen = False
    if getattr(sys, 'frozen', False):
        # we are running in a bundle
        frozen = True
        bundle_dir = sys._MEIPASS
    else:
        # we are running in a normal Python environment
#        bundle_dir = os.path.dirname(os.path.abspath(__file__))
        bundle_dir = str(Path(__file__).resolve().parent)

    gui = GuiCore(None, bundle_dir) # see GuiCore's __init__ method
    gui.title(' Pub2SDwizard v{}'.format(THIS_VERSION))
#    print('in main() gui.script_dir {}'.format(gui.script_dir))
    if platform.system() == 'Windows':
#        gui.wm_iconbitmap(os.path.normpath((\
#                                    resource_filename(__name__, 'mainc.ico'))))
        gui.wm_iconbitmap(Path(SCRIPT_DIR, 'mainc.ico'))
#        gui.wm_iconbitmap(Path(SCRIPT_DIR, 'myclasses/myimages/mainc.ico'))
    elif platform.system() == 'Linux':
#        if Path(SCRIPT_DIR, 'myclasses/myimages/mainc.png').exists():
#            print("mainc.png exists!")
#        else:
#            print("mainc.png does not exist!")
        img = PhotoImage(\
                        file=str(Path(SCRIPT_DIR, 'mainc.png')))
#                        file=str(Path(SCRIPT_DIR, 'myclasses/myimages/mainc.png')))
#        img = PhotoImage(file=(get_script_directory() + '/images/mainc.png'))
        gui.tk.call('wm', 'iconphoto', gui._w, img)
    else:
        messagebox.showwarning('Warning', "Help I've been kidnaped by {}!!!".\
                               format(platform.system()))

    gui.mainloop()

if __name__ == '__main__':
    main()

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

from .myclasses.myconst.therest import THIS_VERSION
from .myclasses.gui import GuiCore

if __name__ == '__main__' and __package__ is None:
    os.sys.path.append(os.path.dirname(os.path.dirname(\
                                                os.path.abspath(__file__))))

def hello_world():
    '''idiot test function'''
    return 'Hello world!'

def get_script_directory():
    """return path to current script"""
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
        bundle_dir = str(Path(__file__).resolve().parent)

    gui = GuiCore(None, bundle_dir) # see GuiCore's __init__ method
    gui.title(' Pub2SDwizard v{}'.format(THIS_VERSION))
    if platform.system() == 'Windows':
        gui.wm_iconbitmap(Path(SCRIPT_DIR, 'mainc.ico'))
    elif platform.system() == 'Linux':
        img = PhotoImage(file=str(Path('/usr/share/pub2sdwizard/mainc.png')))
        gui.tk.call('wm', 'iconphoto', gui._w, img)
    else:
        messagebox.showwarning('Warning', "Help I've been kidnaped by {}!!!".\
                               format(platform.system()))

    gui.mainloop()

if __name__ == '__main__':
    main()

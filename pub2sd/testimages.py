# -*- coding: utf-8 -*-
"""
Created on Fri Sep 27 09:49:00 2019

@author: marks
"""

import sys
import os
import platform
from pathlib import Path

from tkinter import messagebox, PhotoImage

from pkg_resources import resource_filename
if __name__ == '__main__' and __package__ is None:
    os.sys.path.append(os.path.dirname(os.path.dirname(\
                                                os.path.abspath(__file__))))
from pub2sd.myclasses.myconst.therest import THIS_VERSION
from pub2sd.myclasses.gui import GuiCore

#import importlib.resources as pkg_resources
#from pub2sd.myclasses import myimages
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
        bundle_dir = Path(__file__).resolve().parent

    theicofile = Path(SCRIPT_DIR, 'myclasses/myimages/mainc.ico') 
    if theicofile.exists():
        print("got {}".format(theicofile))
    else:
        print("Oops")
#    print(pkg_resources.path(myimages,'mainc.ico'))
#    gui = GuiCore(None, bundle_dir ) # see GuiCore's __init__ method
#    gui.title(' Pub2SDwizard v{}'.format(THIS_VERSION))
##    print('in main() gui.script_dir {}'.format(gui.script_dir))
#    if platform.system() == 'Windows':
##        gui.wm_iconbitmap(os.path.normpath((\
##                                    resource_filename(__name__, 'mainc.ico'))))
#        gui.wm_iconbitmap(Path(resource_filename(__name__, 'mainc.ico'))


if __name__ == '__main__':
    main()


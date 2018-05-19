# -*- coding: utf-8 -*-
"""
Created on Tue May 15 11:05:03 2018

@author: marks
"""

import tkinter as tk
import tkinter.ttk as ttk
import random


def change_style():
    color = random.choice(['red', 'blue', 'yellow', 'dark gray', 'purple', 'cyan', 'brown', 'orange'])
    style.configure('Die.TButton', background=color)
    style.map('Die.TButton', background=[('active', active_color(color))])


def active_color(color):
    c = root.winfo_rgb(color)
    r = c[0] / 65535 * 255
    g = c[1] / 65535 * 255
    b = c[2] / 65535 * 255
    r += (255 - r) / 2
    g += (255 - g) / 2
    b += (255 - b) / 2
    return ("#%2.2x%2.2x%2.2x" % (round(r), round(g), round(b))).upper()


root = tk.Tk()

style = ttk.Style(root)

button = ttk.Button(root, text='Test', style='Die.TButton')
change_style()
button.pack()

ttk.Button(root, command=change_style, text='Change style').pack(padx=4, pady=10)

root.mainloop()
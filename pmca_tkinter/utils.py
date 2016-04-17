# coding: utf-8

from tkinter import *
from logging import getLogger
logger = getLogger(__name__)


class QUIT:
    def __init__(self, root):
        self.root = root

    def __call__(self):
        self.root.winfo_toplevel().destroy()
        self.root.quit()


class LISTBOX:
    def __init__(self, master=None):
        self.listbox = Listbox(master, height = 6, exportselection = 0, selectmode = SINGLE)
        self.listbox.yscroll = Scrollbar(master, orient = VERTICAL, command = self.listbox.yview)
        self.listbox.yscroll.pack(side = RIGHT, fill = Y, expand = 0)
        self.listbox["yscrollcommand"] = self.listbox.yscroll.set
        self.listbox.pack(fill = BOTH, expand=1)

    def set_entry(self, entry, sel = -1):
        if self.listbox.size()>0:
            self.listbox.delete(0, END)
        for i, x in enumerate(entry):
            self.listbox.insert(END, x)
        if sel >= 0:
            self.listbox.selection_set(sel)


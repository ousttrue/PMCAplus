from typing import Any
import tkinter.ttk
from .listbox import LISTBOX
import PyPMCA.pmca_data as pmca_data


class MaterialTab(tkinter.ttk.Frame):
    """
    +--------+------+
    |material|select|
    +--------+------+
    |comment        |
    +---------------+
    """

    def __init__(self, master: tkinter.Misc, data: pmca_data.PmcaData):
        super().__init__(master=master)
        self.data = data

        self.hbox = tkinter.ttk.Frame(self)
        self.l_tree = LISTBOX(self.hbox, "Material", self.mats_click)
        self.l_sel = LISTBOX(self.hbox, "Select", self.mats_sel_click)
        self.hbox.pack(padx=3, pady=3, side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        self.comment = tkinter.StringVar()
        self.comment.set("comment:")
        self.text_label = tkinter.ttk.Label(self, textvariable=self.comment)
        self.text_label.pack(padx=3, pady=3, side=tkinter.BOTTOM, fill=tkinter.X)

    def mats_click(self, sel_t: int):
        selected = self.data.mat_entry[1][sel_t]
        self.l_sel.set_entry(
            x.name for x in self.data.mat_rep.mat[selected].mat.entries
        )

        comment = self.data.select_mats(sel_t)
        self.comment.set("comment:%s" % comment)

    def mats_sel_click(self, sel: int):
        self.data.select_mats_sel(sel)

from typing import Any
import tkinter.ttk
from .listbox import LISTBOX


class MaterialTab(tkinter.ttk.Frame):
    """
    +--------+------+
    |material|select|
    +--------+------+
    |comment        |
    +---------------+
    """

    def __init__(self, master: tkinter.Misc):
        super().__init__(master=master)
        self.text = "Color"

        self.hbox = tkinter.ttk.Frame(self)
        self.l_tree = LISTBOX(self.hbox, "Material")
        self.l_tree.listbox.bind("<ButtonRelease-1>", self.mats_click)
        self.l_sel = LISTBOX(self.hbox, "Select")
        self.l_sel.listbox.bind("<ButtonRelease-1>", self.mats_sel_click)
        self.hbox.pack(padx=3, pady=3, side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        self.comment = tkinter.StringVar()
        self.comment.set("comment:")
        self.text_label = tkinter.ttk.Label(self, textvariable=self.comment)
        self.text_label.pack(padx=3, pady=3, side=tkinter.BOTTOM, fill=tkinter.X)

    def mats_click(self, _: Any):
        sel_t = int(self.l_tree.listbox.curselection()[0])
        print(sel_t)
        print(self.mat_rep.mat[self.mat_entry[1][sel_t]])

        tmp_list = []
        for x in self.mat_rep.mat[self.mat_entry[1][sel_t]].mat.entries:
            tmp_list.append(x.name)

        self.l_sel.set_entry(tmp_list)
        self.tab[0].l_sel.set_entry(
            self.parts_entry_k, sel=self.tree_list[sel_t].node.list_num
        )
        self.cur_mat = sel_t

        self.comment.set(
            "comment:%s" % (self.mat_rep.mat[self.mat_entry[1][sel_t]].mat.comment)
        )

    def mats_sel_click(self, event):
        print(self.mat_rep.mat[self.mat_entry[1][self.cur_mat]].sel)
        sel_t = int(self.l_sel.listbox.curselection()[0])
        self.mat_rep.mat[self.mat_entry[1][self.cur_mat]].sel = self.mat_rep.mat[
            self.mat_entry[1][self.cur_mat]
        ].mat.entries[sel_t]
        self.refresh(level=1)

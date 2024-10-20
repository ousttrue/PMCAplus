import tkinter.ttk
from .listbox import LISTBOX
import PyPMCA


class MaterialTab(tkinter.ttk.Frame):
    """
    +--------+------+
    |material|select|
    +--------+------+
    |comment        |
    +---------------+
    """

    def __init__(self, master: tkinter.Misc, data: PyPMCA.PmcaData):
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
        mats = self.data.get_mats(sel_t)
        self.l_sel.set_entry([e.name for e in mats.entries])
        self.comment.set(f"comment: {mats.comment}")

    def mats_sel_click(self, sel: int):
        self.data.select_mats_sel(sel)

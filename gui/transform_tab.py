from typing import Any
import tkinter.ttk
from .listbox import LISTBOX
import pmca_data
from . import dialogs


class TransformTab(tkinter.ttk.Frame):
    """
    +------+----+
    |groups|info|
    +------+----+
    """

    def __init__(self, master: tkinter.Misc, data: pmca_data.PmcaData):
        super().__init__(master=master)
        self.data = data
        self.tfgroup = LISTBOX(self, "Groups", self.tf_click)
        self.tfgroup.set_entry([x.name for x in data.transform_list])
        self.info_frame = tkinter.ttk.LabelFrame(self, text="Info")
        self.info_str = tkinter.StringVar()
        self.info_str.set("x=\ny=\nz=\n")
        self.label = tkinter.ttk.Label(
            self.info_frame, textvariable=self.info_str
        ).pack(side=tkinter.LEFT, anchor=tkinter.N)
        self.info_frame.pack(
            padx=3, pady=3, side=tkinter.LEFT, fill=tkinter.BOTH, expand=1
        )

    def tf_click(self, sel: int):
        root = dialogs.SCALE_DIALOG_FANC(self.data, sel)
        root.transient(self) # type: ignore
        root.mainloop()

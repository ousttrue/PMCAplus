from typing import Any
import tkinter
import tkinter.ttk


class LISTBOX(tkinter.Listbox):
    def __init__(self, parent: tkinter.ttk.LabelFrame):
        super().__init__(parent, height=6, exportselection=0, selectmode=tkinter.SINGLE)

        self.yscroll = tkinter.ttk.Scrollbar(
            parent,
            orient=tkinter.VERTICAL,
            command=self.yview,  # type: ignore
        )
        self.yscroll.pack(side=tkinter.RIGHT, fill=tkinter.Y, expand=0)
        self["yscrollcommand"] = self.yscroll.set
        self.pack(fill=tkinter.BOTH, expand=1)

    def set_entry(self, entry: list[Any], sel: int = -1) -> None:
        self.delete(0, tkinter.END)
        for x in entry:
            self.insert("end", x)
        if sel >= 0:
            self.selection_set(sel)

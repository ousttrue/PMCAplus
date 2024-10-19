from typing import Callable, Any, cast
import tkinter.ttk


class LISTBOX(tkinter.ttk.LabelFrame):
    def __init__(
        self, master: tkinter.Misc, text: str, select_callback: Callable[[int], None]
    ):
        super().__init__(master=master, text=text)
        self.listbox = tkinter.Listbox(
            self, height=6, exportselection=0, selectmode=tkinter.SINGLE
        )
        self.yscroll = tkinter.ttk.Scrollbar(
            self,
            orient=tkinter.VERTICAL,
            command=self.listbox.yview,  # type: ignore
        )
        self.yscroll.pack(side=tkinter.RIGHT, fill=tkinter.Y, expand=0)
        self.listbox["yscrollcommand"] = self.yscroll.set
        self.listbox.pack(fill=tkinter.BOTH, expand=1)
        self.pack(padx=3, pady=3, side=tkinter.LEFT, fill=tkinter.BOTH, expand=1)

        def on_click(_: Any):
            val = cast(
                str,
                self.listbox.curselection()[0],  # type: ignore
            )
            select_callback(int(val))

        self.listbox.bind("<ButtonRelease-1>", on_click)

    def set_entry(self, entry: list[str], sel: int = -1):
        self.listbox.delete(0, tkinter.END)
        for x in entry:
            self.listbox.insert("end", x)
        if sel >= 0:
            self.listbox.selection_set(sel)

    def current_sel(self) -> int:
        return int(self.listbox.curselection()[0])  # type: ignore

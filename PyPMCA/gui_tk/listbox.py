import tkinter


class LISTBOX:
    def __init__(self, master=None):
        self.listbox = tkinter.Listbox(
            master, height=6, exportselection=0, selectmode=tkinter.SINGLE
        )
        self.listbox.yscroll = tkinter.ttk.Scrollbar(
            master, orient=tkinter.VERTICAL, command=self.listbox.yview
        )
        self.listbox.yscroll.pack(side=tkinter.RIGHT, fill=tkinter.Y, expand=0)
        self.listbox["yscrollcommand"] = self.listbox.yscroll.set
        self.listbox.pack(fill=tkinter.BOTH, expand=1)

    def set_entry(self, entry, sel=-1):
        self.listbox.delete(0, tkinter.END)
        for x in entry:
            self.listbox.insert("end", x)
        if sel >= 0:
            self.listbox.selection_set(sel)

import tkinter.ttk
import PyPMCA


class InfoTab(tkinter.ttk.Frame):
    def __init__(self, master: tkinter.Misc, data: PyPMCA.PmcaData):
        super().__init__(master=master)

        self.comment = tkinter.Text(self, height=10)
        self.comment["state"] = "normal"
        self.yscroll = tkinter.ttk.Scrollbar(
            self,
            orient=tkinter.VERTICAL,
            command=self.comment.yview,  # type: ignore
        )
        self.yscroll.pack(
            side=tkinter.RIGHT, fill=tkinter.Y, expand=0, anchor=tkinter.E
        )
        self.comment["yscrollcommand"] = self.yscroll.set
        self.comment.pack(side=tkinter.RIGHT, fill=tkinter.BOTH, expand=1)

        self.name = tkinter.StringVar()
        self.name_entry = tkinter.ttk.Entry(self, textvariable=self.name)
        self.name_entry.pack(fill=tkinter.X)

        self.name_l = tkinter.StringVar()
        self.name_l_entry = tkinter.ttk.Entry(self, textvariable=self.name_l)
        self.name_l_entry.pack(fill=tkinter.X)

        self.text = tkinter.StringVar()
        self.text_label = tkinter.ttk.Label(self, textvariable=self.text)
        self.text_label.pack(fill=tkinter.X)

        self.pack(fill=tkinter.BOTH, expand=1)

        self.set_data(data)

    def set_data(self, data: PyPMCA.PmcaData) -> None:
        lines = data.cnl_lines
        for line in lines[2:]:
            if line == "PARTS":
                break
            elif line == "":
                pass
            else:
                self.comment.insert(tkinter.END, f"{line}\n")
        # self.name.set(lines[0])
        # self.name_l.set(lines[1])
        # self.name.set("PMCAモデル")
        # self.name_l.set("PMCAモデル")
        # self.comment.delete("1.0", tkinter.END)
        # self.comment.delete("1.0", tkinter.END)
        self.name.set(data.modelinfo.name)
        self.name_l.set(data.modelinfo.name)
        self.text.set(data.get_authors_and_licenses())

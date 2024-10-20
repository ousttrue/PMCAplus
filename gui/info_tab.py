import tkinter.ttk
import PyPMCA.pmca_data as pmca_data


class InfoTab(tkinter.ttk.Frame):
    """
    +--------+------+
    |material|select|
    +--------+------+
    |comment        |
    +---------------+
    """

    def __init__(self, master: tkinter.Misc, data: pmca_data.PmcaData):
        super().__init__(master=master)
        self.text = "Info"

        self.comment = tkinter.Text(self, height=10)
        self.comment["state"] = "normal"
        self.yscroll = tkinter.ttk.Scrollbar(
            self,
            orient=tkinter.VERTICAL,
            command=self.comment.yview,
        )
        self.yscroll.pack(
            side=tkinter.RIGHT, fill=tkinter.Y, expand=0, anchor=tkinter.E
        )
        self.comment["yscrollcommand"] = self.yscroll.set
        self.comment.pack(side=tkinter.RIGHT, fill=tkinter.BOTH, expand=1)

        self.name = tkinter.StringVar()
        self.name.set(data.modelinfo.name)
        self.name_entry = tkinter.ttk.Entry(self, textvariable=self.name)
        self.name_entry.pack(fill=tkinter.X)

        self.name_l = tkinter.StringVar()
        self.name_l.set(data.modelinfo.name)
        self.name_l_entry = tkinter.ttk.Entry(self, textvariable=self.name_l)
        self.name_l_entry.pack(fill=tkinter.X)

        str1 = ""
        str2 = ""
        for x in data.authors:
            str1 += "%s " % (x)
        for x in data.licenses:
            str2 += "%s " % (x)

        self.text = tkinter.StringVar()
        self.text.set("Author : %s\nLicense : %s" % (str1, str2))
        self.text_label = tkinter.ttk.Label(self, textvariable=self.text)
        self.text_label.pack(fill=tkinter.X)

        self.name.set("PMCAモデル")
        self.name_l.set("PMCAモデル")
        self.comment.delete("1.0", tkinter.END)

        self.pack(fill=tkinter.BOTH, expand=1)

import tkinter.ttk
from .. import renderer


class MODELINFO:
    def __init__(
        self,
        name: str = "PMCAモデル",
        name_l: str = "PMCAモデル",
        comment: str = "",
        name_eng: str = "PMCA model",
        name_l_eng: str = "PMCA generated model",
        comment_eng: str = "",
    ):
        self.name = name
        self.name_l = name_l
        self.comment = comment
        self.name_eng = name_eng
        self.name_l_eng = name_l_eng
        self.comment_eng = comment_eng


class InfoTab(tkinter.ttk.Frame):
    def __init__(self, root: tkinter.Tk) -> None:
        super().__init__(root)
        self.text = "Info"
        self.modelinfo = MODELINFO()

        self.frame = tkinter.ttk.Frame(self)
        self.frame.comment = tkinter.Text(self.frame, height=10)
        self.frame.comment["state"] = "normal"
        self.frame.yscroll = tkinter.ttk.Scrollbar(
            self.frame,
            orient=tkinter.VERTICAL,
            command=self.frame.comment.yview,
        )
        self.frame.yscroll.pack(
            side=tkinter.RIGHT, fill=tkinter.Y, expand=0, anchor=tkinter.E
        )
        self.frame.comment["yscrollcommand"] = self.frame.yscroll.set
        self.frame.comment.pack(side=tkinter.RIGHT, fill=tkinter.BOTH, expand=1)

        self.frame.name = tkinter.StringVar()
        self.frame.name.set(self.modelinfo.name)
        self.frame.name_entry = tkinter.ttk.Entry(self, textvariable=self.frame.name)
        self.frame.name_entry.pack(fill=tkinter.X)

        self.frame.name_l = tkinter.StringVar()
        self.frame.name_l.set(self.modelinfo.name)
        self.frame.name_l_entry = tkinter.ttk.Entry(
            self, textvariable=self.frame.name_l
        )
        self.frame.name_l_entry.pack(fill=tkinter.X)

        self.authors = []
        str1 = ""
        for x in self.authors:
            str1 += "%s " % (x)

        str2 = ""
        self.licenses = []
        for x in self.licenses:
            str2 += "%s " % (x)

        self.frame.text = tkinter.StringVar()
        self.frame.text.set("Author : %s\nLicense : %s" % (str1, str2))
        self.frame.text_label = tkinter.ttk.Label(self, textvariable=self.frame.text)
        self.frame.text_label.pack(fill=tkinter.X)

        self.frame.pack(fill=tkinter.BOTH, expand=1)

        self.frame.name.set("PMCAモデル")
        self.frame.name_l.set("PMCAモデル")
        self.frame.comment.delete("1.0", tkinter.END)

    def set_info(self, name: str, name_l: str, comment: list[str]) -> None:
        self.frame.name.set(name)
        self.frame.name_l.set(name_l)
        for line in comment:
            self.frame.comment.insert(END, line)
            self.frame.comment.insert(END, "\n")
        # else:
        #     self.frame.comment.delete("1.0", END)

    def refresh(self):
        str1 = ""
        str2 = ""
        for x in self.authors:
            str1 += "%s " % (x)
        for x in self.licenses:
            str2 += "%s " % (x)
        self.modelinfo.name = self.frame.name.get()
        self.modelinfo.name_l = self.frame.name_l.get()
        self.modelinfo.comment = self.frame.comment.get("1.0", tkinter.END)
        renderer.Set_Name_Comment(
            name=self.modelinfo.name,
            comment="%s\nAuthor:%s\nLicense:%s\n%s"
            % (self.modelinfo.name_l, str1, str2, self.modelinfo.comment),
            name_eng=self.modelinfo.name_eng,
            comment_eng="%s\nAuthor:%s\nLicense:%s\n%s"
            % (self.modelinfo.name_l_eng, str1, str2, self.modelinfo.comment_eng),
        )

        self.frame.text.set("Author : %s\nLicense : %s" % (str1, str2))

import tkinter.ttk
import PyPMCA.gui_tk.listbox as listbox


class ColorTab(tkinter.ttk.Frame):
    def __init__(self, root: tkinter.Tk) -> None:
        super().__init__(root)
        self.frame = tkinter.ttk.Frame(self)
        self.text = "Color"
        self.parts_frame = tkinter.ttk.LabelFrame(self.frame, text="Material")
        self.l_tree = listbox.LISTBOX(self.parts_frame)
        self.parts_frame.pack(
            padx=3, pady=3, side=tkinter.LEFT, fill=tkinter.BOTH, expand=1
        )
        self.l_tree.listbox.bind("<ButtonRelease-1>", self.mats_click)

        self.parts_frame = tkinter.ttk.LabelFrame(self.frame, text="Select")
        self.l_sel = listbox.LISTBOX(self.parts_frame)
        self.parts_frame.pack(
            padx=3, pady=3, side=tkinter.LEFT, fill=tkinter.BOTH, expand=1
        )
        self.l_sel.listbox.bind("<ButtonRelease-1>", self.mats_sel_click)

        self.frame.pack(padx=3, pady=3, side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        self.comment = tkinter.StringVar()
        self.comment.set("comment:")
        self.text_label = tkinter.ttk.Label(self, textvariable=self.comment)
        self.text_label.pack(padx=3, pady=3, side=tkinter.BOTTOM, fill=tkinter.X)

    def mats_click(self, event):
        sel_t = int(self.tab[1].l_tree.listbox.curselection()[0])

        tmp_list = []
        for x in self.mat_rep.mat[self.mat_entry[1][sel_t]].mat.entries:
            tmp_list.append(x.name)

        self.tab[1].l_sel.set_entry(tmp_list)
        self.tab[0].l_sel.set_entry(
            self.parts_entry_k, sel=self.tree_list[sel_t].node.list_num
        )
        self.cur_mat = sel_t

        self.tab[1].comment.set(
            "comment:%s" % (self.mat_rep.mat[self.mat_entry[1][sel_t]].mat.comment)
        )

    def mats_sel_click(self, event):
        sel_t = int(self.tab[1].l_sel.listbox.curselection()[0])
        self.mat_rep.mat[self.mat_entry[1][self.cur_mat]].sel = self.mat_rep.mat[
            self.mat_entry[1][self.cur_mat]
        ].mat.entries[sel_t]
        self.refresh(level=1)

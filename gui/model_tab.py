import tkinter.ttk
from .listbox import LISTBOX
import PyPMCA


class ModelTab(tkinter.ttk.Frame):
    """
    +-----+-----+
    |model|parts|
    +-----+-----+
    |comment    |
    +-----------+
    """

    def __init__(self, master: tkinter.Misc, data: PyPMCA.PmcaData):
        super().__init__(master=master)
        self.data = data
        #
        # top
        #

        self.hbox = tkinter.ttk.Frame(self)
        # top-left
        self.l_tree = LISTBOX(self.hbox, "Model", self.tree_click)
        self.l_tree.set_entry(
            [node.make_entry() for node in data.get_tree_node_list()], sel=0
        )

        # top-right
        self.l_sel = LISTBOX(self.hbox, "Parts", self.parts_sel_click)
        self.l_sel.set_entry(data.get_parts_entry())
        self.hbox.pack(padx=3, pady=3, side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        #
        # bottom
        #
        self.comment = tkinter.StringVar()
        self.comment.set("comment:")
        self.text_label = tkinter.ttk.Label(self, textvariable=self.comment)
        self.text_label.pack(padx=3, pady=3, side=tkinter.BOTTOM, fill=tkinter.X)

    def tree_click(self, sel_t: int):
        self.comment.set("comment:")
        parts_entry_k, sel = self.data.select_tree(sel_t)
        self.l_sel.set_entry(parts_entry_k, sel=sel)

    def parts_sel_click(self, sel: int):
        sel_t = self.l_tree.current_sel()
        comment = self.data.select_parts(sel_t, sel)
        self.comment.set("comment:%s" % (comment))

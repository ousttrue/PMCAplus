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
        self.l_tree = LISTBOX(self.hbox, "Model", self.tree_click)
        self.sel_t: int = 0
        self.l_sel = LISTBOX(self.hbox, "Parts", self.parts_sel_click)
        self.hbox.pack(padx=3, pady=3, side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
        #
        # bottom
        #
        self.comment = tkinter.StringVar()
        self.comment.set("comment:")
        self.text_label = tkinter.ttk.Label(self, textvariable=self.comment)
        self.text_label.pack(padx=3, pady=3, side=tkinter.BOTTOM, fill=tkinter.X)

    def set_node_list(self, node_list: list[PyPMCA.TreeNode]):
        self.l_tree.set_entry(
            [node.make_entry() for node in node_list],
            sel=self.sel_t,
        )
        self.set_parts_list(node_list[self.sel_t].joint)

    def set_parts_list(self, joint: PyPMCA.Joint):
        parts_list, sel = self.data.get_joint_parts_list(joint)
        self.l_sel.set_entry([parts.make_entry() for parts in parts_list], sel=sel)

    def tree_click(self, sel_t: int):
        self.comment.set("comment:")
        self.sel_t = sel_t
        node_list = self.data.get_tree_node_list()
        self.set_parts_list(node_list[self.sel_t].joint)

    def parts_sel_click(self, sel: int):
        comment = self.data.select_parts(self.sel_t, sel)
        self.comment.set("comment:%s" % (comment))

from typing import Any
import tkinter.ttk
from .listbox import LISTBOX
import pmca_data


class ModelTab(tkinter.ttk.Frame):
    """
    +-----+-----+
    |model|parts|
    +-----+-----+
    |comment    |
    +-----------+
    """

    def __init__(self, master: tkinter.Misc, data: pmca_data.PmcaData):
        super().__init__(master=master)
        self.text = "Model"
        self.tree_list = []

        #
        # top
        #
        self.hbox = tkinter.ttk.Frame(self)
        # top-left
        self.l_tree = LISTBOX(self.hbox, "Model")
        self.l_tree.listbox.bind("<ButtonRelease-1>", self.tree_click)
        self.l_tree.set_entry(data.tree_entry, sel=0)
        # top-right
        self.l_sel = LISTBOX(self.hbox, "Parts")
        self.l_sel.listbox.bind("<ButtonRelease-1>", self.parts_sel_click)
        self.l_sel.set_entry(data.parts_entry_k)
        self.hbox.pack(padx=3, pady=3, side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        #
        # bottom
        #
        self.comment = tkinter.StringVar()
        self.comment.set("comment:")
        self.text_label = tkinter.ttk.Label(self, textvariable=self.comment)
        self.text_label.pack(padx=3, pady=3, side=tkinter.BOTTOM, fill=tkinter.X)

    def tree_click(self, _: Any):
        self.comment.set("comment:")
        sel_t = int(self.l_tree.listbox.curselection()[0]) + 1
        print(sel_t)
        joint = self.tree_list[sel_t].node.parts.joint[self.tree_list[sel_t].c_num]
        print(joint)

        self.parts_entry_k = []
        self.parts_entry_p = []
        for x in self.parts_list:
            for y in x.type:
                if y == joint:
                    self.parts_entry_k.append(x.name)
                    self.parts_entry_p.append(x)
                    break
        self.parts_entry_k.append("#外部モデル読み込み")
        self.parts_entry_p.append("load")
        self.parts_entry_k.append("#None")
        self.parts_entry_p.append(None)
        self.l_sel.set_entry(
            self.parts_entry_k, sel=self.tree_list[sel_t].node.list_num
        )

    def parts_sel_click(self, _: Any):
        sel = int(self.l_sel.listbox.curselection()[0])
        sel_t = int(self.l_tree.listbox.curselection()[0]) + 1

        if self.parts_entry_p[sel] == None:  # Noneを選択した場合
            node = None

        elif self.parts_entry_p[sel] == "load":  # 外部モデル読み込み
            path = filedialog.askopenfilename(
                filetypes=[("Plygon Model Deta(for MMD)", ".pmd"), ("all", ".*")],
                defaultextension=".pmd",
            )
            if path != "":
                name = path.split("/")[-1]
                parts = PyPMCA.PARTS(name=name, path=path, props={})
                node = PyPMCA.NODE(
                    parts=parts, depth=self.tree_list[sel_t].node.depth + 1, child=[]
                )
                for x in node.parts.joint:
                    node.child.append(None)
            else:
                node = None

        else:
            print(self.parts_entry_p[sel].path)
            print(self.tree_list[sel_t].node.parts.name)

            node = PyPMCA.NODE(
                parts=self.parts_entry_p[sel],
                depth=self.tree_list[sel_t].node.depth + 1,
                child=[],
            )
            p_node = self.tree_list[sel_t].node.child[self.tree_list[sel_t].c_num]

            child_appended = []
            if p_node != None:
                for x in node.parts.joint:
                    node.child.append(None)
                    for j, y in enumerate(p_node.parts.joint):
                        if x == y:
                            for z in child_appended:
                                if z == y:
                                    break
                            else:
                                node.child[-1] = p_node.child[j]
                                child_appended.append(y)
                                break
            else:
                for x in node.parts.joint:
                    node.child.append(None)

            print(">>", node.parts.name, "\n")
        self.tree_list[sel_t].node.child[self.tree_list[sel_t].c_num] = node
        # self.tree_list[sel_t].node.list_num = sel
        if node == None:
            self.comment.set("comment:")
        else:
            self.comment.set("comment:%s" % (node.parts.comment))
        self.refresh()

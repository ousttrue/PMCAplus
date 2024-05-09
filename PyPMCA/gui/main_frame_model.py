from typing import Any, Literal
import logging
import tkinter.filedialog
import tkinter.ttk
import PyPMCA.gui.listbox as listbox
from .. import PMCA_data
from .. import renderer


LOGGER = logging.getLogger(__name__)


class ModelTab(tkinter.ttk.Frame):
    """
    +----+-----+
    |tree|parts|
    +----+-----+
    |comment   |
    +----------+
    """

    def __init__(self, root: tkinter.Tk, data: PMCA_data.PMCAData) -> None:
        super().__init__(root)
        self.text = "Model"

        self.frame = tkinter.ttk.Frame(self)

        # left
        self.parts_frame = tkinter.ttk.LabelFrame(self.frame, text="Model")
        self.l_tree = listbox.LISTBOX(self.parts_frame)
        self.parts_frame.pack(
            padx=3, pady=3, side=tkinter.LEFT, fill=tkinter.BOTH, expand=1
        )
        self.l_tree.listbox.bind("<ButtonRelease-1>", self.tree_click)

        # right
        self.parts_frame = tkinter.ttk.LabelFrame(self.frame, text="Parts")
        self.l_sel = listbox.LISTBOX(self.parts_frame)
        self.parts_frame.pack(
            padx=3, pady=3, side=tkinter.LEFT, fill=tkinter.BOTH, expand=1
        )
        self.l_sel.listbox.bind("<ButtonRelease-1>", self.parts_sel_click)

        self.frame.pack(padx=3, pady=3, side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        # comment
        self.comment = tkinter.StringVar()
        self.comment.set("comment:")
        self.text_label = tkinter.ttk.Label(self, textvariable=self.comment)
        self.text_label.pack(padx=3, pady=3, side=tkinter.BOTTOM, fill=tkinter.X)

        # init
        self.parts_entry: list[tuple[str, PMCA_data.PARTS | Literal["load"] | None]] = (
            []
        )
        self.data = data
        self.set_tree(self.data.tree)
        self.set_parts()

    def set_tree(self, node: PMCA_data.NODE, use_sel: bool = False):
        sel_t = int(self.l_tree.listbox.curselection()[0]) if use_sel else 0  # type: ignore

        tree_entry: list[str] = []
        for x in node.create_list():
            tree_entry.append(x.text)
        tree_entry = tree_entry[1:]

        self.l_tree.set_entry(tree_entry, sel=sel_t)  # type: ignore

    def set_parts(self):
        self.parts_entry.clear()
        for x in self.data.parts_list:
            for y in x.type:
                if y == "root":
                    self.parts_entry.append((x.name, x))
                    break
        self.parts_entry.append(("#外部モデル読み込み", "load"))
        self.l_sel.set_entry([k for k, _ in self.parts_entry])  # type: ignore

    def tree_click(self, _event: Any):
        self.comment.set("comment:")
        sel_t = int(self.l_tree.listbox.curselection()[0]) + 1  # type: ignore
        joint = self.data.tree_list[sel_t].node.parts.joint[
            self.data.tree_list[sel_t].c_num
        ]
        self.update_parts_entry(sel_t, joint)

    def update_parts_entry(self, sel_t: int | None = None, joint: str | None = None):
        self.parts_entry.clear()
        for x in self.data.parts_list:
            for y in x.type:
                if y == joint:
                    self.parts_entry.append((x.name, x))
                    break
        self.parts_entry.append(("#外部モデル読み込み", "load"))
        self.parts_entry.append(("#None", None))
        if sel_t != None:
            self.l_sel.set_entry(  # type: ignore
                [k for k, _ in self.parts_entry],
                sel=self.data.tree_list[sel_t].node.list_num,
            )

    def parts_sel_click(self, _event: Any):
        sel = int(self.l_sel.listbox.curselection()[0])  # type: ignore
        sel_t = int(self.l_tree.listbox.curselection()[0]) + 1  # type: ignore

        LOGGER.debug(sel)
        match self.parts_entry[sel][1]:
            case None:  # Noneを選択した場合
                node = None

            case "load":  # 外部モデル読み込み
                path = tkinter.filedialog.askopenfilename(
                    filetypes=[("Plygon Model Deta(for MMD)", ".pmd"), ("all", ".*")],
                    defaultextension=".pmd",
                )
                if path != "":
                    name = path.split("/")[-1]
                    parts = PMCA_data.PARTS(name=name, path=path, props={})
                    node = PMCA_data.NODE(
                        parts=parts,
                        depth=self.data.tree_list[sel_t].node.depth + 1,
                        children=[None for _ in parts.joint],
                    )
                else:
                    node = None

            case PMCA_data.PARTS() as parts:
                node = PMCA_data.NODE(
                    parts=parts,
                    depth=self.data.tree_list[sel_t].node.depth + 1,
                    children=[],
                )
                p_node = self.data.tree_list[sel_t].node.children[
                    self.data.tree_list[sel_t].c_num
                ]

                child_appended: list[str] = []
                if p_node != None:
                    for x in node.parts.joint:
                        node.children.append(None)
                        for j, y in enumerate(p_node.parts.joint):
                            if x == y:
                                for z in child_appended:
                                    if z == y:
                                        break
                                else:
                                    node.children[-1] = p_node.children[j]
                                    child_appended.append(y)
                                    break
                else:
                    for x in node.parts.joint:
                        node.children.append(None)

        self.data.tree_list[sel_t].node.children[
            self.data.tree_list[sel_t].c_num
        ] = node
        self.data.tree_list[sel_t].node.list_num = sel
        if node == None:
            self.comment.set("comment:")
        else:
            self.comment.set("comment:%s" % (node.parts.comment))

        renderer.refresh(self.data)

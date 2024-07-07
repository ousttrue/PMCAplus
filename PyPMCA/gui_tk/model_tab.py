from typing import Any, Literal
import logging
import tkinter.filedialog
import tkinter.ttk
from .listbox import LISTBOX
from .. import PMCA_asset
from .. import PMCA_cnl
from ..app import App

LOGGER = logging.getLogger(__name__)


class ModelTab(tkinter.ttk.Frame):
    """
    +----+-----+
    |tree|parts|
    +----+-----+
    |comment   |
    +----------+
    """

    def __init__(
        self,
        root: tkinter.Tk,
        app: App,
    ) -> None:
        super().__init__(root)
        self.text = "Model"
        self.app = app

        self.frame = tkinter.ttk.Frame(self)

        # left(joint selector)
        self.parts_frame = tkinter.ttk.LabelFrame(self.frame, text="Model")
        self.l_tree = LISTBOX(self.parts_frame)
        self.parts_frame.pack(
            padx=3, pady=3, side=tkinter.LEFT, fill=tkinter.BOTH, expand=1
        )
        self.l_tree.bind("<ButtonRelease-1>", self.tree_click)

        # right(parts list for joint)
        self.parts_frame = tkinter.ttk.LabelFrame(self.frame, text="Parts")
        self.l_sel = LISTBOX(self.parts_frame)
        self.parts_frame.pack(
            padx=3, pady=3, side=tkinter.LEFT, fill=tkinter.BOTH, expand=1
        )
        self.l_sel.bind("<ButtonRelease-1>", self.parts_sel_click)

        self.frame.pack(padx=3, pady=3, side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        # comment
        self.comment = tkinter.StringVar()
        self.comment.set("comment:")
        self.text_label = tkinter.ttk.Label(self, textvariable=self.comment)
        self.text_label.pack(padx=3, pady=3, side=tkinter.BOTTOM, fill=tkinter.X)

        # init
        self.parts_entry: list[
            tuple[str, PMCA_asset.PARTS | Literal["load"] | None]
        ] = []
        self.set_tree(self.app.cnl.tree)
        self.set_parts()

    def set_tree(self, node: PMCA_cnl.NODE, use_sel: bool = False):
        sel_t = int(self.l_tree.curselection()[0]) if use_sel else 0  # type: ignore

        tree_entry: list[str] = []
        for x, level in node.traverse():
            tree_entry.append(f'{"  " * level}{x}')
        tree_entry = tree_entry[1:]

        self.l_tree.set_entry(tree_entry, sel=sel_t)  # type: ignore

    def set_parts(self):
        self.parts_entry.clear()
        for x in self.app.data.parts_list:
            for y in x.type:
                if y == "root":
                    self.parts_entry.append((x.name, x))
                    break
        self.parts_entry.append(("#外部モデル読み込み", "load"))
        self.l_sel.set_entry([k for k, _ in self.parts_entry], sel=self.get_sel_parts(self.app.cnl.tree.children[0]))  # type: ignore

    def tree_click(self, _event: Any):
        self.comment.set("comment:")
        sel_t = int(self.l_tree.curselection()[0]) + 1  # type: ignore
        node = self.app.cnl.get_node(sel_t)
        self.update_parts_entry(node)

    def update_parts_entry(self, node: PMCA_cnl.NODE):
        assert node.parent
        self.parts_entry.clear()
        for parts in self.app.data.parts_list:
            if node.parent.joint in parts.type:
                self.parts_entry.append((parts.name, parts))
        self.parts_entry.append(("#外部モデル読み込み", "load"))
        if node.parent.joint != "root":
            self.parts_entry.append(("#None", None))
        self.l_sel.set_entry(  # type: ignore
            [k for k, _ in self.parts_entry],
            sel=self.get_sel_parts(node),
        )

    def get_sel_parts(self, node: PMCA_cnl.NODE) -> int:
        for i, (_, parts) in enumerate(self.parts_entry):
            if parts == node.parts:
                return i
        return -1

    def parts_sel_click(self, _event: Any):
        sel = int(self.l_sel.curselection()[0])  # type: ignore
        sel_t = int(self.l_tree.curselection()[0]) + 1  # type: ignore
        node = self.app.cnl.get_node(sel_t)
        assert node.parent

        match self.parts_entry[sel][1]:
            case None:
                new_node = PMCA_cnl.NODE(node.parent, None)
                node.parent.node.children[node.parent.joint_index] = new_node
                self.comment.set("comment: None")

            case PMCA_asset.PARTS() as parts:
                new_node = PMCA_cnl.NODE(
                    node.parent,
                    parts,
                )
                used: list[PMCA_cnl.NODE] = []
                for i, joint in enumerate(parts.joint):
                    for child, _ in node.traverse():
                        assert child.parent
                        if child.parent.joint == joint and child not in used:
                            new_node.connect(i, child)
                            used.append(child)
                            break
                node.parent.node.children[node.parent.joint_index] = new_node
                self.comment.set("comment:%s" % (parts.comment))

            case "load":  # 外部モデル読み込み
                LOGGER.warn(f"{sel_t} => load")
                # new_node = PMCA_cnl.NODE(node.joint, None, node.parent)
                # node.parent.children[joint_index] = new_node
                # self.comment.set("comment: None")

                # raise NotImplementedError()
                # path = tkinter.filedialog.askopenfilename(
                #     filetypes=[("Plygon Model Deta(for MMD)", ".pmd"), ("all", ".*")],
                #     defaultextension=".pmd",
                # )
                # if path != "":
                #     name = path.split("/")[-1]
                #     parts = PMCA_data.PARTS(name=name, path=path, props={})
                #     node = PMCA_data.NODE(
                #         parts=parts,
                #         depth=tree_node.node.depth + 1,
                #         children=[None for _ in parts.joint],
                #     )
                #     self.comment.set("comment:%s" % (node.parts.comment))
                # else:
                #     self.comment.set("comment:")
                #     node = None

        self.app.assemble()

from typing import Any, Literal
import logging
import tkinter.filedialog
import tkinter.ttk
import PyPMCA.gui_tk.listbox as listbox
from .. import PMCA_asset
from .. import native


LOGGER = logging.getLogger(__name__)


class ModelTab(tkinter.ttk.Frame):
    """
    +----+-----+
    |tree|parts|
    +----+-----+
    |comment   |
    +----------+
    """

    def __init__(self, root: tkinter.Tk, data: PMCA_asset.PMCAData) -> None:
        super().__init__(root)
        self.text = "Model"

        self.frame = tkinter.ttk.Frame(self)

        # left(joint selector)
        self.parts_frame = tkinter.ttk.LabelFrame(self.frame, text="Model")
        self.l_tree = listbox.LISTBOX(self.parts_frame)
        self.parts_frame.pack(
            padx=3, pady=3, side=tkinter.LEFT, fill=tkinter.BOTH, expand=1
        )
        self.l_tree.listbox.bind("<ButtonRelease-1>", self.tree_click)

        # right(parts list for joint)
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
        self.parts_entry: list[tuple[str, PMCA_asset.PARTS | Literal["load"] | None]] = (
            []
        )
        self.data = data
        self.set_tree(self.data.tree)
        self.set_parts()

    def set_tree(self, node: PMCA_asset.NODE, use_sel: bool = False):
        sel_t = int(self.l_tree.listbox.curselection()[0]) if use_sel else 0  # type: ignore

        tree_entry: list[str] = []
        for x, level in node.traverse():
            tree_entry.append(f'{"  " * level}{x}')
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
        self.l_sel.set_entry([k for k, _ in self.parts_entry], sel=self.get_sel_parts(self.data.tree.children[0]))  # type: ignore

    def tree_click(self, _event: Any):
        self.comment.set("comment:")
        sel_t = int(self.l_tree.listbox.curselection()[0]) + 1  # type: ignore
        node = self.data.get_node(sel_t)
        joint, joint_index = node.get_joint()
        self.update_parts_entry(node, joint, joint_index)

    def update_parts_entry(self, node: PMCA_asset.NODE, joint: str, joint_index: int):
        self.parts_entry.clear()
        for parts in self.data.parts_list:
            if joint in parts.type:
                self.parts_entry.append((parts.name, parts))
        self.parts_entry.append(("#外部モデル読み込み", "load"))
        if joint != "root":
            self.parts_entry.append(("#None", None))
        self.l_sel.set_entry(  # type: ignore
            [k for k, _ in self.parts_entry],
            sel=self.get_sel_parts(node),
        )

    def get_sel_parts(self, node: PMCA_asset.NODE) -> int:
        for i, (_, parts) in enumerate(self.parts_entry):
            if parts == node.parts:
                return i
        return -1

    def parts_sel_click(self, _event: Any):
        sel = int(self.l_sel.listbox.curselection()[0])  # type: ignore
        sel_t = int(self.l_tree.listbox.curselection()[0]) + 1  # type: ignore
        node = self.data.get_node(sel_t)
        assert node.parent
        joint, joint_index = node.get_joint()
        assert joint == node.joint

        match self.parts_entry[sel][1]:
            case None:
                new_node = PMCA_asset.NODE(node.joint, None, node.parent)
                node.parent.children[joint_index] = new_node
                self.comment.set("comment: None")

            case PMCA_asset.PARTS() as parts:
                new_node = PMCA_asset.NODE(
                    node.joint,
                    parts,
                    node.parent,
                )
                for joint in parts.joint:
                    assert joint.strip()
                    added = False
                    for child in node.children:
                        if child.joint == joint:
                            child.parent = new_node
                            new_node.children.append(child)
                            added = True
                            break
                    if not added:
                        new_node.children.append(PMCA_asset.NODE(joint, None, new_node))
                node.parent.children[joint_index] = new_node
                self.comment.set("comment:%s" % (parts.comment))

            case "load":  # 外部モデル読み込み
                LOGGER.warn(f"{sel_t} => load")
                new_node = PMCA_asset.NODE(node.joint, None, node.parent)
                node.parent.children[joint_index] = new_node
                self.comment.set("comment: None")

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

        native.refresh(self.data)

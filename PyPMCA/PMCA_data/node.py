import logging
from .parts import PARTS

LOGGER = logging.getLogger(__name__)


class TREE_LIST:
    def __init__(
        self,
        node: "NODE",
        depth: int = 0,
        text: str = "",
        c_num: int = -1,
    ):
        self.node = node
        self.depth = depth
        self.text = text
        self.c_num = c_num


class NODE:
    """
    モデルのパーツツリー
    """

    def __init__(
        self,
        joint: str,
        parts: PARTS | None,
        depth: int = 0,
        children: list["NODE"] = [],
        list_num: int = -1,
        parent: "NODE|None" = None,
    ):
        self.joint = joint
        self.parts = parts
        self.depth = depth
        self.children = children
        self.list_num = list_num
        self.parent = parent

    def __str__(self) -> str:
        if self.parts:
            return f"{self.joint}#{self.parts.name}"
        else:
            return f"{self.joint}#"

    def create_list(self) -> list["TREE_LIST"]:
        l: list[TREE_LIST] = [
            TREE_LIST(
                node=self, depth=self.depth, text="  " * self.depth + self.parts.name
            )
        ]
        for i, x in enumerate(self.children):
            if x != None:
                l.append(
                    TREE_LIST(
                        node=self,
                        depth=self.depth + 1,
                        text=("  " * (self.depth + 1)) + self.children[i].parts.name,
                        c_num=i,
                    )
                )
                x.list_add(l)
            elif self.parts.joint[i] != "":
                l.append(
                    TREE_LIST(
                        node=self,
                        depth=self.depth + 1,
                        text="  " * (self.depth + 1) + "#" + self.parts.joint[i],
                        c_num=i,
                    )
                )
        return l

    def list_add(self, list: list[TREE_LIST]) -> None:
        for i, x in enumerate(self.children):
            if self.children[i].parts:
                list.append(
                    TREE_LIST(
                        node=self,
                        depth=self.depth + 1,
                        text="  " * (self.depth + 1) + self.children[i].parts.name,
                        c_num=i,
                    )
                )
                x.list_add(list)
            elif self.parts.joint[i] != "":
                list.append(
                    TREE_LIST(
                        node=self,
                        depth=self.depth + 1,
                        text="  " * (self.depth + 1) + "#" + self.parts.joint[i],
                        c_num=i,
                    )
                )

    def recalc_depth(self, depth: int) -> None:
        self.depth = depth
        depth = depth + 1
        for x in self.children:
            if x != None:
                x.recalc_depth(depth)

    def node_to_text(self) -> list[str]:
        lines: list[str] = []
        lines.append("[Name] %s" % (self.parts.name))
        lines.append("[Path] %s" % (self.parts.path))
        lines.append("[Child]")
        for x in self.children:
            if x != None:
                lines.extend(x.node_to_text())
            else:
                lines.append("None")
        lines.append("[Parent]")
        return lines

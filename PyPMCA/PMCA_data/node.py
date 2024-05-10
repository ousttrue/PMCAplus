from typing import Iterator
import dataclasses
import logging
from .parts import PARTS

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class NODE:
    """
    モデルのパーツツリー
    """

    joint: str
    parts: PARTS | None
    parent: "NODE|None" = None
    children: list["NODE"] = dataclasses.field(default_factory=list)

    def __post_init__(self):
        pass
        # assert self.joint

    def __str__(self) -> str:
        if self.parts:
            return f"{self.joint}#{self.parts.name}"
        else:
            return f"{self.joint}#"

    def traverse(self, level: int = 0) -> Iterator[tuple["NODE", int]]:
        yield self, level
        for child in self.children:
            for x in child.traverse(level + 1):
                yield x

    def get_joint(self) -> tuple[str, int]:
        assert self.parent and self.parent.parts
        for i, (node, joint) in enumerate(
            zip(self.parent.children, self.parent.parts.joint)
        ):
            if node == self:
                return joint, i
        raise RuntimeError()

    # def create_list(self) -> list["TREE_LIST"]:
    #     l: list[TREE_LIST] = [
    #         TREE_LIST(
    #             node=self, depth=self.depth, text="  " * self.depth + self.parts.name
    #         )
    #     ]
    #     for i, x in enumerate(self.children):
    #         if x.parts:
    #             l.append(
    #                 TREE_LIST(
    #                     node=self,
    #                     depth=self.depth + 1,
    #                     text=("  " * (self.depth + 1)) + x.parts.name,
    #                     c_num=i,
    #                 )
    #             )
    #             x.list_add(l)
    #         elif self.parts.joint[i] != "":
    #             l.append(
    #                 TREE_LIST(
    #                     node=self,
    #                     depth=self.depth + 1,
    #                     text="  " * (self.depth + 1) + "#" + self.parts.joint[i],
    #                     c_num=i,
    #                 )
    #             )
    #     return l

    # def list_add(self, list: list[TREE_LIST]) -> None:
    #     for i, x in enumerate(self.children):
    #         if self.children[i].parts:
    #             list.append(
    #                 TREE_LIST(
    #                     node=self,
    #                     depth=self.depth + 1,
    #                     text="  " * (self.depth + 1) + self.children[i].parts.name,
    #                     c_num=i,
    #                 )
    #             )
    #             x.list_add(list)
    #         elif self.parts.joint[i] != "":
    #             list.append(
    #                 TREE_LIST(
    #                     node=self,
    #                     depth=self.depth + 1,
    #                     text="  " * (self.depth + 1) + "#" + self.parts.joint[i],
    #                     c_num=i,
    #                 )
    #             )

    def node_to_text(self) -> list[str]:
        lines: list[str] = []
        if self.parts:
            lines.append("[Name] %s" % (self.parts.name))
            lines.append("[Path] %s" % (self.parts.path))
            lines.append("[Child]")
            for x in self.children:
                if x.parts:
                    lines.extend(x.node_to_text())
                else:
                    lines.append("None")
            lines.append("[Parent]")
        return lines

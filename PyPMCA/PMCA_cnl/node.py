from typing import Iterator, NamedTuple
import dataclasses
import logging
from ..PMCA_asset.parts import PARTS

LOGGER = logging.getLogger(__name__)


class NodeParent(NamedTuple):
    node: "NODE"
    joint: str
    joint_index: int


@dataclasses.dataclass
class NODE:
    """
    モデルのパーツツリー
    """

    parent: NodeParent | None
    parts: PARTS | None
    children: list["NODE"] = dataclasses.field(default_factory=list)

    def __post_init__(self):
        if self.parent:
            assert isinstance(self.parent, NodeParent)
        if self.parts:
            for i, joint in enumerate(self.parts.joint):
                self.children.append(NODE(NodeParent(self, joint, i), None))

    def __str__(self) -> str:
        if not self.parent:
            return "__ROOT__"
        # joint, _ = self.get_joint()
        if self.parts:
            return f"{self.parent.joint}#{self.parts.name}"
        else:
            return f"{self.parent.joint}#"

    def connect(self, i: int, child: "NODE") -> None:
        assert self.parts and i < len(self.parts.joint)
        if child:
            if child.parent:
                child.parent.node.children[child.parent.joint_index] = NODE(
                    child.parent, None
                )
            child.parent = NodeParent(self, self.parts.joint[i], i)
            self.children[i] = child
        else:
            self.children[i] = NODE(NodeParent(self, self.parts.joint[i], i), None)

    def traverse(self, level: int = 0) -> Iterator[tuple["NODE", int]]:
        yield self, level
        for child in self.children:
            for x in child.traverse(level + 1):
                yield x

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

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
                assert node.joint == joint
                return joint, i
        raise RuntimeError()

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

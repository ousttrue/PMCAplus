from typing import Iterator, NamedTuple
import dataclasses
import logging
from .. import PMCA_asset


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
    parts: PMCA_asset.PARTS | None
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

    def parse(
        self,
        lines: list[str],
        parts_list: list[PMCA_asset.PARTS],
    ) -> list[str]:
        LOGGER.info("parse nodes")

        curnode = self
        parents: list[NODE] = [self]
        child_nums = [0]
        name = ""
        path = ""
        while len(lines) > 0 and len(parents) > 0:
            line = lines.pop(0)
            sp = line.split(" ")
            if sp[0] == "None":
                name = ""
                path = ""
                child_nums[-1] += 1

            elif sp[0] == "[Name]":
                name = sp[1]

            elif sp[0] == "[Path]":
                if len(sp) == 1:
                    path = ""
                else:
                    path = sp[1]

            elif sp[0] == "[Child]":

                tp: PMCA_asset.PARTS | None = None
                if name:
                    for y in parts_list:
                        if y.name == name:
                            tp = y
                            break
                    else:
                        for y in parts_list:
                            if y.path == path:
                                tp = y
                                break

                if tp:
                    assert curnode.parts
                    joint = curnode.parts.joint[child_nums[-1]]
                    curnode.children[child_nums[-1]] = NODE(
                        NodeParent(curnode, joint, child_nums[-1]), y
                    )
                    parents.append(curnode)
                    curnode = curnode.children[child_nums[-1]]
                    child_nums.append(0)
                else:
                    depc = 1
                    while depc == 0:
                        line = lines.pop(0)
                        if line == "[Child]":
                            depc += 1
                        if line == "[Parent]":
                            depc -= 1
                    parents.pop()
                    child_nums.pop()
                    child_nums[-1] += 1

            elif sp[0] == "[Parent]":
                curnode = parents.pop()
                child_nums.pop()
                if len(child_nums) > 0:
                    child_nums[-1] += 1
            elif sp[0] == "MATERIAL":
                return lines
            else:
                pass

        raise RuntimeError()

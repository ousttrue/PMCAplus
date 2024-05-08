from typing import NamedTuple
import logging
from .node import NODE
from .parts import PARTS


LOGGER = logging.getLogger(__name__)


class CnlInfo(NamedTuple):
    name: str
    name_l: str
    comment: list[str]


def read_info(lines: list[str]) -> tuple[list[str], CnlInfo]:
    name = lines.pop(0)
    name_l = lines.pop(0)
    comment: list[str] = []
    while len(lines) > 0:
        line = lines.pop(0)
        if line == "PARTS":
            return lines, CnlInfo(name, name_l, comment)
        elif line == "":
            pass
        else:
            comment.append(line)

    raise RuntimeError()


def read_parts(
    lines: list[str],
    self: NODE,
    parts_list: list[PARTS],
) -> list[str]:
    LOGGER.info("parse nodes")
    tmp = [None, None]
    curnode = self
    parents = [self]
    child_nums = [0]

    while len(lines) > 0 and len(parents) > 0:
        line = lines.pop(0)
        sp = line.split(" ")
        if sp[0] == "None":
            tmp = [None, None]
            child_nums[-1] += 1

        elif sp[0] == "[Name]":
            tmp[0] = sp[1]

        elif sp[0] == "[Path]":
            if len(sp) == 1:
                tmp[1] = ""
            else:
                tmp[1] = sp[1]

        elif sp[0] == "[Child]":

            tp = None
            if tmp[0] != None:
                for y in parts_list:
                    if y.name == tmp[0]:
                        tp = y
                        break
                else:
                    for y in parts_list:
                        if y.path == tmp[1]:
                            tp = y
                            break

            if tp != None:
                curnode.children[child_nums[-1]] = NODE(
                    parts=y, depth=curnode.depth + 1, children=[]
                )
                parents.append(curnode)
                curnode = curnode.children[child_nums[-1]]
                child_nums.append(0)
                for x in curnode.parts.joint:
                    curnode.children.append(None)

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

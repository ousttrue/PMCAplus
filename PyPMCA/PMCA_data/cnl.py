from typing import NamedTuple
import logging
from .node import NODE
from .parts import PARTS
from .mats import MATS, MAT_REP_DATA
from .model_transform_data import MODEL_TRANS_DATA, BONE_TRANS_DATA

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
            y: PARTS | None = None
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

            if tp:
                joint = curnode.parts.joint[child_nums[-1]]
                curnode.children[child_nums[-1]] = NODE(
                    joint,
                    parts=y,
                    children=[],
                    parent=curnode,
                )
                parents.append(curnode)
                curnode = curnode.children[child_nums[-1]]
                child_nums.append(0)
                if curnode.parts:
                    for joint in curnode.parts.joint:
                        curnode.children.append(
                            NODE(
                                joint,
                                parts=None,
                                children=[],
                                parent=curnode,
                            )
                        )

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


def read_mat_rep(
    lines: list[str], mat_list: list[MATS]
) -> tuple[list[str], dict[str, MAT_REP_DATA]]:
    LOGGER.info("parse material_rep")
    mat_rep: dict[str, MAT_REP_DATA] = {}
    tmp = ["", "", None]

    while len(lines) > 0:
        x = lines.pop(0)
        x = x.split(" ")
        if x[0] == "[Name]":
            tmp[0] = x[1]
        elif x[0] == "[Sel]":
            tmp[1] = x[1]
        elif x[0] == "NEXT":
            for y in mat_list:
                if y.name == tmp[0]:
                    tmp[2] = y
                    break
            else:
                tmp[2] = None
                continue

            for y in tmp[2].entries:
                if y.name == tmp[1]:
                    mat_rep[tmp[0]] = MAT_REP_DATA(num=-1, mat=tmp[2], sel=y)
                    break
        elif x[0] == "TRANSFORM":
            return lines, mat_rep

    raise RuntimeError()


def read_transform(lines: list[str], transform: MODEL_TRANS_DATA) -> None:
    LOGGER.info("体型調整読み込み")
    j = 0
    for j, x in enumerate(lines):
        x = x.split(" ")
        if x[0] == "[Name]":
            transform.name = x[1]
        elif x[0] == "[Scale]":
            transform.scale = float(x[1])
        elif x[0] == "[Pos]":
            transform.pos = (float(x[1]), float(x[2]), float(x[3]))
        elif x[0] == "[Rot]":
            transform.rot = (float(x[1]), float(x[2]), float(x[3]))
        elif x[0] == "BONES":
            break

    transform.bones.clear()
    transform.bones.append(BONE_TRANS_DATA())
    for x in lines[j:]:
        x = x.split(" ")
        if x[0] == "[Name]":
            transform.bones[-1].name = x[1]
        elif x[0] == "[Length]":
            transform.bones[-1].length = float(x[1])
        elif x[0] == "[Thick]":
            transform.bones[-1].thick = float(x[1])
        elif x[0] == "[Pos]":
            transform.bones[-1].pos[0] = float(x[1])
            transform.bones[-1].pos[1] = float(x[2])
            transform.bones[-1].pos[2] = float(x[3])
        elif x[0] == "[Rot]":
            transform.bones[-1].rot[0] = float(x[1])
            transform.bones[-1].rot[1] = float(x[2])
            transform.bones[-1].rot[2] = float(x[3])
        elif x[0] == "NEXT":
            if transform.bones[-1].name != "":
                transform.bones.append(BONE_TRANS_DATA())

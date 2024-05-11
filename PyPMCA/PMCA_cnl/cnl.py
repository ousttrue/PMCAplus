import dataclasses
import pathlib
import logging
from .. import PMCA_asset
from .mat_rep import MAT_REP, MAT_REP_DATA
from .node import NODE

LOGGER = logging.getLogger(__name__)


class CnlInfo:
    def __init__(self):
        self.name: str = ""
        self.name_l: str = ""
        self.comment: list[str] = dataclasses.field(default_factory=list)

        self.tree = NODE(
            "__root__",
            parts=PMCA_asset.PARTS(name="ROOT", joint=["root"]),
            children=[NODE("root", None, [])],
        )

        self.mat_rep = MAT_REP()
        self.mat_entry: tuple[list[str], list[str]] = ([], [])

        self.transform_data: list[PMCA_asset.MODEL_TRANS_DATA] = [
            PMCA_asset.MODEL_TRANS_DATA(scale=1.0, bones=[], props={})
        ]

    def get_node(self, target: int) -> NODE:
        for i, (node, _) in enumerate(self.tree.traverse()):
            if i == target:
                return node
        raise RuntimeError()

    def _read_info(self, lines: list[str]) -> list[str]:
        self.name = lines.pop(0)
        self.name_l = lines.pop(0)
        while len(lines) > 0:
            line = lines.pop(0)
            if line == "PARTS":
                return lines
            elif line == "":
                pass
            else:
                self.comment.append(line)

        raise RuntimeError()

    def _read_parts(
        self,
        lines: list[str],
        node: NODE,
        parts_list: list[PMCA_asset.PARTS],
    ) -> list[str]:
        LOGGER.info("parse nodes")
        tmp = [None, None]
        curnode = node
        parents = [node]
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

    def _read_mat_rep(
        self, lines: list[str], mat_list: list[PMCA_asset.MATS]
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

    def _read_transform(
        self, lines: list[str], transform: PMCA_asset.MODEL_TRANS_DATA
    ) -> None:
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
        transform.bones.append(PMCA_asset.BONE_TRANS_DATA())
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
                    transform.bones.append(PMCA_asset.BONE_TRANS_DATA())

    def load_CNL_File(self, file: pathlib.Path, data: PMCA_asset.PMCAData) -> None:
        lines = file.read_text(encoding="utf-8").splitlines()
        lines = self._read_info(lines)

        lines = self._read_parts(lines, self.tree, data.parts_list)

        assert self.mat_rep
        lines, mat_rep = self._read_mat_rep(lines, data.mats_list)
        self.mat_rep.mat = mat_rep

        assert len(self.transform_data) > 0
        self._read_transform(lines, self.transform_data[0])

    def save_CNL_File(
        self, file: pathlib.Path, name: str, name_l: str, comment: str
    ) -> bool:
        lines: list[str] = []
        lines.append(name)
        lines.append(name_l)
        lines.append(comment)

        lines.append("PARTS")
        lines.extend(self.tree.children[0].node_to_text())

        lines.append("MATERIAL")
        lines.extend(self.mat_rep.list_to_text())

        lines.append("TRANSFORM")
        lines.extend(self.transform_data[0].list_to_text())

        with file.open("w", encoding="utf-8") as fp:
            for x in lines:
                fp.write(x + "\n")

        return True

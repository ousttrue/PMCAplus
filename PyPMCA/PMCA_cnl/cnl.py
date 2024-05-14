from typing import Callable
import dataclasses
import pathlib
import logging
from .. import PMCA_asset
from .. import pmd_type
from .mat_rep import MAT_REP, MAT_REP_DATA
from .node import NODE


LOGGER = logging.getLogger(__name__)


class CnlInfo:
    def __init__(self, raise_refresh: Callable[["CnlInfo"], None]):
        self.name: str = ""
        self.name_l: str = ""
        self.comment: list[str] = dataclasses.field(default_factory=list)

        self.tree = NODE(None, PMCA_asset.PARTS(name="ROOT", joint=["root"]))
        self.mat_rep = MAT_REP()
        self.transform_data: list[PMCA_asset.MODEL_TRANS_DATA] = [
            PMCA_asset.MODEL_TRANS_DATA(scale=1.0, bones=[], props={})
        ]

        self._raise_refresh = raise_refresh
        self.on_reflesh: list[Callable[[], None]] = []

    def raise_refresh(self):
        self._raise_refresh(self)

    def on_refresh(self):
        for callback in self.on_reflesh:
            callback()

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

        lines = self.tree.parse(lines, data.parts_list)

        assert self.mat_rep
        lines, mat_rep = MAT_REP.parse(lines, data.mats_list)
        self.mat_rep.mat_map = mat_rep

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

    def update_mat_rep(
        self, data: PMCA_asset.PMCAData, materials: list[pmd_type.MATERIAL]
    ):
        self.mat_rep.mat_order.clear()

        for mat in materials:
            if mat.tex != "":
                if mat.tex not in self.mat_rep.mat_map:
                    for m in data.mats_list:
                        if m.name == mat.tex:
                            self.mat_rep.mat_map[mat.tex] = MAT_REP_DATA(
                                m, m.entries[0]
                            )
                            break
                if mat.tex in self.mat_rep.mat_map:
                    self.mat_rep.mat_order.append(mat.tex)

from typing import Callable
import pathlib
import logging
from .. import PMCA_asset
from .. import pmd_type
from .mat_rep import MAT_REP, MAT_REP_DATA
from .node import NODE


LOGGER = logging.getLogger(__name__)


class CnlInfo:
    def __init__(self):
        self.name: str = ""
        self.name_l: str = ""
        self.comment: list[str] = []
        self.tree = NODE(None, PMCA_asset.PARTS(name="ROOT", joint=["root"]))
        self.mat_rep = MAT_REP()
        self.transform_data_list: list[PMCA_asset.MODEL_TRANS_DATA] = [
            PMCA_asset.MODEL_TRANS_DATA("cnl")
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

    def _read_transform(
        self, lines: list[str], transform: PMCA_asset.MODEL_TRANS_DATA
    ) -> None:
        LOGGER.info("体型調整読み込み")
        j = 0
        for j, l in enumerate(lines):
            l = l.strip()
            if l == "":
                continue
            if l.startswith("#"):
                continue
            if l == "BONES":
                break

            k, v = [x.strip() for x in l.split(maxsplit=1)]
            match k:
                case "[Name]":
                    transform.name = v
                case "[Scale]":
                    transform.scale = float(v)
                case "[Pos]":
                    x, y, z = v.split()
                    transform.pos = (float(x), float(y), float(z))
                case "[Rot]":
                    x, y, z = v.split()
                    transform.rot = (float(x), float(y), float(z))
                case _:
                    raise RuntimeError()

        j += 1
        transform.bones.clear()
        for l in lines[j:]:
            l = l.strip()
            if l == "":
                continue
            if l.startswith("#"):
                continue
            if l == "NEXT":
                continue

            if l == "[Name]":
                # 無名
                transform.bones.append(PMCA_asset.BONE_TRANS_DATA(""))
                continue

            # print(l)
            k, v = [x.strip() for x in l.split(maxsplit=1)]
            match k:
                case "[Name]":
                    # transform.bones[-1].name = x[1]
                    transform.bones.append(PMCA_asset.BONE_TRANS_DATA(v))
                case "[Length]":
                    transform.bones[-1].length = float(v)
                case "[Thick]":
                    transform.bones[-1].thick = float(v)
                case "[Pos]":
                    x, y, z = v.split()
                    transform.bones[-1].pos = (float(x), float(y), float(z))
                case "[Rot]":
                    x, y, z = v.split()
                    transform.bones[-1].rot = (float(x), float(y), float(z))
                case _:
                    raise RuntimeError()

    def load_CNL_File(self, file: pathlib.Path, data: PMCA_asset.PMCAData) -> None:
        lines = file.read_text(encoding="utf-8").splitlines()
        lines = self._read_info(lines)

        lines = self.tree.parse(lines, data.parts_list)

        assert self.mat_rep
        lines, mat_rep = MAT_REP.parse(lines, data.mats_list)
        self.mat_rep.mat_map = mat_rep

        assert len(self.transform_data_list) > 0
        self._read_transform(lines, self.transform_data_list[0])

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
        lines.extend(self.transform_data_list[0].list_to_text())

        with file.open("w", encoding="utf-8") as fp:
            for x in lines:
                fp.write(x + "\n")

        return True

    def update_mat_rep(
        self, data: PMCA_asset.PMCAData, materials: list[pmd_type.Submesh]
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

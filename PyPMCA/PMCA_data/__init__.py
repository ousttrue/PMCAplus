from typing import List, NamedTuple, Optional, Tuple
import os
import pathlib
import logging

import PMCA  # type: ignore
from .. import PyPMCA
from .mats import MATS
from .parts import PARTS
from .model_transform_data import MODEL_TRANS_DATA


LOGGER = logging.getLogger(__name__)


class LIST(NamedTuple):
    b: Tuple[List[bytes], List[bytes]]
    s: Tuple[List[bytes], List[bytes]]
    g: Tuple[List[bytes], List[bytes]]

    @staticmethod
    def load_list(data: str) -> "LIST":

        bone: Tuple[List[bytes], List[bytes]] = [], []
        skin: Tuple[List[bytes], List[bytes]] = [], []
        group: Tuple[List[bytes], List[bytes]] = [], []

        lines = data.splitlines()
        line = lines.pop(0)
        line = lines.pop(0)

        current = "bone"
        for line in lines:
            match line:
                case "skin":
                    current = line
                case "bone_disp":
                    current = line
                case "end":
                    break
                case _:

                    match current:
                        case "bone":
                            tmp = line.split(" ")
                            bone[0].append(tmp[0].encode("cp932", "replace"))
                            bone[1].append(tmp[1].encode("cp932", "replace"))

                        case "skin":
                            tmp = line.split(" ")
                            skin[0].append(tmp[0].encode("cp932", "replace"))
                            skin[1].append(tmp[1].encode("cp932", "replace"))

                        case "bone_disp":
                            tmp = line.split(" ")
                            group[0].append(tmp[0].encode("cp932", "replace"))
                            group[1].append(tmp[1].encode("cp932", "replace"))

        return LIST(bone, skin, group)


class PMCAData:
    def __init__(self, dir: pathlib.Path) -> None:
        self.dir = dir
        LOGGER.info("PMCADATA: %s", self.dir.relative_to(pathlib.Path(".").absolute()))
        self.mats_list: List[PyPMCA.MATS] = []
        self.parts_list: List[PyPMCA.PARTS] = []
        self.transform_list: List[PyPMCA.MODEL_TRANS_DATA] = []

    def load(self):
        for x in self.dir.iterdir():
            if not x.is_file():
                continue
            if x.suffix == ".py":
                continue

            src = x.read_text(encoding="utf-8-sig")
            if x.name == "list.txt":
                LOGGER.info("list.txt")
                list = LIST.load_list(src)
                PMCA.Set_List(
                    len(list.b[0]),
                    list.b[0],
                    list.b[1],
                    len(list.s[0]),
                    list.s[0],
                    list.s[1],
                    len(list.g[0]),
                    list.g[0],
                    list.g[1],
                )
                continue

            lines = src.splitlines()
            if lines[0] == "PMCA Parts list v2.0":
                LOGGER.info("%s => [%s]", x.relative_to(self.dir), lines[0])
                self.parts_list = PARTS.load_list(lines)
                continue

            if lines[0] == "PMCA Materials list v2.0":
                LOGGER.info("%s => [%s]", x.relative_to(self.dir), lines[0])
                self.mats_list = MATS.load_list(lines)
                continue

            if lines[0] == "PMCA Transform list v2.0":
                LOGGER.info("%s => [%s]", x.relative_to(self.dir), lines[0])
                self.transform_list = MODEL_TRANS_DATA.load_list(lines)
                continue

            LOGGER.warn("skip: %s", x.relative_to(self.dir))

    def save_CNL_File(self, name):
        if self.tree_list[0].node.child[0] == None:
            return False

        lines = []
        lines.append(self.modelinfo.name)
        lines.append(self.modelinfo.name_l)
        lines.append(self.modelinfo.comment)

        lines.append("PARTS")
        lines.extend(self.tree_list[0].node.child[0].node_to_text())
        lines.append("MATERIAL")
        lines.extend(self.mat_rep.list_to_text())
        lines.append("TRANSFORM")
        lines.extend(self.transform_data[0].list_to_text())

        fp = open(name, "w", encoding="utf-8")
        for x in lines:
            fp.write(x + "\n")
        fp.close

        return True
from typing import NamedTuple, Callable
import logging
import pathlib

from .mats import MATS, MAT_REP
from .parts import PARTS
from .node import NODE, TREE_LIST
from .model_transform_data import MODEL_TRANS_DATA
from . import cnl

LOGGER = logging.getLogger(__name__)


class LIST(NamedTuple):
    b: tuple[list[bytes], list[bytes]]
    s: tuple[list[bytes], list[bytes]]
    g: tuple[list[bytes], list[bytes]]

    @staticmethod
    def load_list(data: str) -> "LIST":

        bone: tuple[list[bytes], list[bytes]] = [], []
        skin: tuple[list[bytes], list[bytes]] = [], []
        group: tuple[list[bytes], list[bytes]] = [], []

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
    def __init__(self) -> None:
        self.mats_list: list[MATS] = []
        self.parts_list: list[PARTS] = []
        self.transform_list: list[MODEL_TRANS_DATA] = []
        self.tree = NODE(
            "__root__",
            parts=PARTS(name="ROOT", joint=["root"]),
            depth=-1,
            children=[NODE("root", None)],
        )
        self.mat_rep = MAT_REP()
        self.mat_entry: tuple[list[str], list[str]] = ([], [])
        # self.transform_data = []
        self.transform_data: list[MODEL_TRANS_DATA] = [
            MODEL_TRANS_DATA(scale=1.0, bones=[], props={})
        ]
        self.tree_list: list[TREE_LIST] = []
        self.on_reflesh: list[Callable[[float, float, float], None]] = []

    def load_asset(self, dir: pathlib.Path) -> LIST | None:
        LOGGER.info("PMCADATA: %s", dir.relative_to(pathlib.Path(".").absolute()))
        list: LIST | None = None
        for x in dir.iterdir():
            if not x.is_file():
                continue
            if x.suffix == ".py":
                continue

            src = x.read_text(encoding="utf-8-sig")
            if x.name == "list.txt":
                LOGGER.info("list.txt")
                list = LIST.load_list(src)
                continue

            lines = src.splitlines()
            if lines[0] == "PMCA Parts list v2.0":
                LOGGER.info("%s => [%s]", x.relative_to(dir), lines[0])
                self.parts_list = PARTS.load_list(lines)
                continue

            if lines[0] == "PMCA Materials list v2.0":
                LOGGER.info("%s => [%s]", x.relative_to(dir), lines[0])
                self.mats_list = MATS.load_list(lines)
                continue

            if lines[0] == "PMCA Transform list v2.0":
                LOGGER.info("%s => [%s]", x.relative_to(dir), lines[0])
                self.transform_list = MODEL_TRANS_DATA.load_list(lines)
                continue

            LOGGER.warn("skip: %s", x.relative_to(dir))
        return list

    def load_CNL_File(self, file: pathlib.Path) -> cnl.CnlInfo:
        lines = file.read_text(encoding="utf-8").splitlines()
        lines, info = cnl.read_info(lines)

        lines = cnl.read_parts(lines, self.tree, self.parts_list)
        self.tree_list = self.tree.create_list()

        assert self.mat_rep
        lines, mat_rep = cnl.read_mat_rep(lines, self.mats_list)
        self.mat_rep.mat = mat_rep

        assert len(self.transform_data) > 0
        cnl.read_transform(lines, self.transform_data[0])

        return info

    def save_CNL_File(
        self, file: pathlib.Path, name: str, name_l: str, comment: str
    ) -> bool:
        if self.tree.children[0] == None:
            return False

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

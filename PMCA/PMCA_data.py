from typing import List
import pathlib
import os
import converter
import logging
import PyPMCA
import PMCA


LOGGER = logging.getLogger(__name__)


class PMCAData:
    def __init__(self) -> None:
        self.mats_list: List[PyPMCA.MATS] = []
        self.parts_list: List[PyPMCA.PARTS] = []
        self.transform_list: List[PyPMCA.MODEL_TRANS_DATA] = []

    def load(self, path: pathlib.Path):
        self.load_data(path)
        self.load_list()
        pass

    def load_v1(self, x: str):
        fp = open(x, "r", encoding="cp932")
        try:
            lines = fp.read()
            line = lines.split("\n")
            line = line[0].replace("\n", "")
            if (
                line == "PMCA Parts list v1.0"
                or line == "PMCA Materials list v1.1"
                or line == "PMCA Materials list v1.0"
                or line == "PMCA Textures list v1.0"
                or line == "PMCA Bone_Group list v1.0"
            ):
                fp.close()

                if os.name == "posix":
                    fp = open(x, "w", encoding="cp932")
                    fp.write(lines)
                    fp.close()
                    converter.v1_v2("./converter/PMCA_1.0-2.0converter", [x])
                elif os.name == "nt":
                    converter.v1_v2(".\\converter\\PMCA_1.0-2.0converter.exe", [x])
            if line == "bone":
                fp = open(x, "r", encoding="cp932")
                lines = fp.read()
                fp.close()

                fp = open(x, "w", encoding="utf-8")
                fp.write("PMCA list data v2.0\n")
                fp.write(lines)
                fp.close()

        except UnicodeDecodeError:
            fp.close()

    def load_partslist(self, x: str):
        with open(x, "r", encoding="utf-8-sig") as fp:
            line = fp.readline()
            if line == "PMCA Parts list v2.0\n":
                self.parts_list = PyPMCA.load_partslist(fp, self.parts_list)
            elif line == "PMCA Materials list v2.0\n":
                self.mats_list = PyPMCA.load_matslist(fp, self.mats_list)
            elif line == "PMCA Transform list v2.0\n":
                self.transform_list = PyPMCA.load_translist(fp, self.transform_list)

    def load_data(self, path: pathlib.Path):
        LOGGER.info("登録データ読み込み: %s", path)
        for x in os.listdir("./"):
            if not os.path.isfile(x):
                continue
            # LOGGER.debug(x)
            self.load_v1(x)
            self.load_partslist(x)

    def load_list(self):
        LOGGER.info("list.txt読み込み")
        fp = open("list.txt", "r", encoding="utf-8-sig")
        LIST = PyPMCA.load_list(fp)
        PMCA.Set_List(
            len(LIST["b"][0]),
            LIST["b"][0],
            LIST["b"][1],
            len(LIST["s"][0]),
            LIST["s"][0],
            LIST["s"][1],
            len(LIST["g"][0]),
            LIST["g"][0],
            LIST["g"][1],
        )
        fp.close()

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

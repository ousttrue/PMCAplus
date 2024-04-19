from typing import List, NamedTuple, Optional, Tuple
import os
import pathlib
import logging
import PyPMCA
import PMCA


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


class MATS_ENTRY:
    def __init__(self, name: str = "", props={}):
        self.name = name
        self.props = props


class MATS:
    """
    PMCA Materials list v2.0
    読み込み材質データ
    """

    def __init__(
        self,
        name: str = "",
        comment: str = "",
        entries: List[MATS_ENTRY] = [],
        props={},
    ):
        self.name = name
        self.comment = comment
        self.entries = entries
        self.props = props

    @staticmethod
    def load_list(lines: List[str]) -> List["MATS"]:
        directry = ""

        mats_list: List[MATS] = []
        mats_list.append(MATS(entries=[], props={}))

        line = lines.pop(0)
        mode = 0
        active = mats_list[-1]
        for l in lines:
            line = l.rstrip("\n").replace("\t", " ").split(" ", 1)
            # print(line)
            if line[0] == "":
                pass
            if line[0][:1] == "#":
                pass
            elif line[0] == "SETDIR":
                directry = line[1]

            elif line[0] == "NEXT":
                if len(active.entries) == 0:
                    mats_list.pop()
                mats_list.append(MATS(entries=[], props={}))
                active = mats_list[-1]
                mode = 0

            elif len(line) < 2:
                pass

            elif line[0] == "[ENTRY]":
                active.entries.append(MATS_ENTRY(name=line[1], props={}))
                mode = 1
            elif line[0] == "[name]":
                if mode == 0:
                    for x in mats_list:
                        if x.name == line[1]:
                            active = x
                            mats_list.pop()
                            break
                    else:
                        active.name = line[1]
            elif line[0] == "[comment]":
                if mode == 0:
                    active.comment = line[1]
            elif line[0] == "[tex]":
                active.entries[-1].props["tex"] = line[1]
                active.entries[-1].props["tex_path"] = directry + line[1]
            elif line[0] == "[sph]":
                active.entries[-1].props["sph"] = line[1]
                active.entries[-1].props["sph_path"] = directry + line[1]
            elif line[0][:1] == "[" and line[0][-5:] == "_rgb]":
                active.entries[-1].props[line[0][1:-1]] = line[1].split()
            elif line[0][:1] == "[" and line[0][-1:] == "]":
                if line[0][1:-1] in active.entries[-1].props:
                    active.entries[-1].props[line[0][1:-1]].append(line[1])
                else:
                    active.entries[-1].props[line[0][1:-1]] = [line[1]]

        return mats_list


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
                self.parts_list = PyPMCA.load_partslist(fp, self.parts_list)
                continue

            if lines[0] == "PMCA Materials list v2.0":
                LOGGER.info("%s => [%s]", x.relative_to(self.dir), lines[0])
                self.mats_list = MATS.load_list(lines)
                continue

            if lines[0] == "PMCA Transform list v2.0":
                LOGGER.info("%s => [%s]", x.relative_to(self.dir), lines[0])
                self.transform_list = PyPMCA.load_translist(fp, self.transform_list)
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

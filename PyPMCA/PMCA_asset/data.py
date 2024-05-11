from typing import NamedTuple, Callable
import logging
import pathlib

from .mats import MATS
from .parts import PARTS
from .model_transform_data import MODEL_TRANS_DATA


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
                self.parts_list = [parts for parts in PARTS.parse(lines)]
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

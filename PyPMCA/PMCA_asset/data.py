from typing import NamedTuple, Callable
import logging
import pathlib

from .mats import MATS
from .parts import PARTS
from .model_transform_data import MODEL_TRANS_DATA


LOGGER = logging.getLogger(__name__)

# void MODEL::translate(NameList *list, short mode) {
#   /*
#   モード1 英名追加
#   モード2 日本語名を英語名に(ボーン、スキンのみ)
#   モード3 英語名を日本語名に(ボーン、スキンのみ)
#   */
#
#   if (mode == 1) {
#
#     if (this->eng_support != 1) {
#       this->eng_support = 1;
#       this->header.name_eng = this->header.name;
#       this->header.comment_eng = this->header.comment;
#     }
#
#     for (int i = 0; i < this->bone.size(); i++) {
#       int j = 0;
#       for (; j < list->bone.size(); j++) {
#         if (strcmp(this->bone[i].name, list->bone[j].data()) == 0) {
#           strncpy(this->bone[i].name_eng, list->bone_eng[j].data(),
#           NAME_LEN); j = -1; break;
#         }
#       }
#       if (j != -1) {
#         if (this->bone[i].name[0] == '\0') {
#           strncpy(this->bone[i].name_eng, this->bone[i].name, NAME_LEN);
#         }
#       }
#     }
#
#     for (int i = 1; i < this->skin.size(); i++) {
#       int j = 1;
#       for (; j < list->skin.size(); j++) {
#         if (strcmp(this->skin[i].name, list->skin[j].data()) == 0) {
#           strncpy(this->skin[i].name_eng, list->skin_eng[j].data(),
#           NAME_LEN); j = -1; break;
#         }
#       }
#       if (j != -1) {
#         strncpy(this->skin[i].name_eng, this->skin[i].name, NAME_LEN);
#       }
#     }
#
#     for (int i = 0; i < this->bone_group.size(); i++) {
#       char str[NAME_LEN];
#       strncpy(str, this->bone_group[i].name, NAME_LEN);
#       auto p = strchr(str, '\n');
#       if (p != NULL)
#         *p = '\0';
#
#       int j = 0;
#       for (; j < list->disp.size(); j++) {
#         if (strcmp(str, list->disp[j].data()) == 0) {
#           strncpy(this->bone_group[i].name_eng, list->disp_eng[j].data(),
#                   NAME_LEN);
#           j = -1;
#           break;
#         }
#       }
# #ifdef DEBUG
#       printf("%d ", i);
# #endif
#       if (j != -1) {
#         strncpy(this->bone_group[i].name_eng, str, NAME_LEN);
#       }
#     }
#
# #ifdef DEBUG
#     printf("\nbone表示枠\n");
# #endif
#
#   } else if (mode == 2) {
#     for (int i = 0; i < this->bone.size(); i++) {
#       int j = 0;
#       for (; j < list->bone.size(); j++) {
#         if (strcmp(this->bone[i].name, list->bone[j].data()) == 0) {
#           strncpy(this->bone[i].name, list->bone_eng[j].data(), NAME_LEN);
#           j = -1;
#           break;
#         }
#       }
#       if (j != -1 && this->eng_support == 1) {
#         strncpy(this->bone[i].name, this->bone[i].name_eng, NAME_LEN);
#       }
#     }
#     for (int i = 0; i < this->skin.size(); i++) {
#       int j = 0;
#       for (; j < list->skin.size(); j++) {
#         if (strcmp(this->skin[i].name, list->skin[j].data()) == 0) {
#           strncpy(this->skin[i].name, list->skin_eng[j].data(), NAME_LEN);
#           j = -1;
#           break;
#         }
#       }
#       if (j != -1 && this->eng_support == 1) {
#         strncpy(this->skin[i].name, this->skin[i].name_eng, NAME_LEN);
#       }
#     }
#   } else if (mode == 3) {
#     for (int i = 0; i < this->bone.size(); i++) {
#       ;
#       for (int j = 0; j < list->bone.size(); j++) {
#         if (strcmp(this->bone[i].name, list->bone_eng[j].data()) == 0) {
#           strncpy(this->bone[i].name, list->bone[j].data(), NAME_LEN);
#           break;
#         }
#       }
#     }
#     for (int i = 0; i < this->skin.size(); i++) {
#       for (int j = 0; j < list->skin.size(); j++) {
#         if (strcmp(this->skin[i].name, list->skin_eng[j].data()) == 0) {
#           strncpy(this->skin[i].name, list->skin[j].data(), NAME_LEN);
#           break;
#         }
#       }
#     }
#   }
# }


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
        self.list: LIST | None = None
        self.asset_dir = pathlib.Path()

    def load_asset(self, dir: pathlib.Path) -> None:
        LOGGER.info("PMCADATA: %s", dir.relative_to(pathlib.Path(".").absolute()))
        self.asset_dir = dir
        for x in dir.iterdir():
            if not x.is_file():
                continue
            if x.suffix == ".py":
                continue

            src = x.read_text(encoding="utf-8-sig")
            if x.name == "list.txt":
                LOGGER.info("list.txt")
                self.list = LIST.load_list(src)
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

import dataclasses
import logging
import ctypes


LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class TranslationList:
    # bone
    bone_name_list: ctypes.Array[ctypes.c_char_p]
    bone_name_english_list: ctypes.Array[ctypes.c_char_p]
    # skin
    skin_name_list: ctypes.Array[ctypes.c_char_p]
    skin_name_english_list: ctypes.Array[ctypes.c_char_p]
    # group
    disp_name_list: ctypes.Array[ctypes.c_char_p]
    disp_name_english_list: ctypes.Array[ctypes.c_char_p]

    @staticmethod
    def load(path: str = "list.txt") -> "TranslationList":
        LOGGER.info(f"Translation.load: {path}")
        with open(path, "r", encoding="utf-8-sig") as fp:

            # bone
            bone_name_list: list[ctypes.c_char_p] = []
            bone_name_english_list: list[ctypes.c_char_p] = []
            # skin
            skin_name_list: list[ctypes.c_char_p] = []
            skin_name_english_list: list[ctypes.c_char_p] = []
            # group
            disp_name_list: list[ctypes.c_char_p] = []
            disp_name_english_list: list[ctypes.c_char_p] = []

            line = fp.readline()[:-1]
            line = fp.readline()[:-1]
            while line:
                line = fp.readline()[:-1]
                if line == "skin":
                    break
                tmp = line.split(" ")
                bone_name_list.append(
                    ctypes.c_char_p(tmp[0].encode("cp932", "replace"))
                )
                bone_name_english_list.append(
                    ctypes.c_char_p(tmp[1].encode("cp932", "replace"))
                )

            while line:
                line = fp.readline()[:-1]
                if line == "bone_disp":
                    break
                tmp = line.split(" ")
                skin_name_list.append(
                    ctypes.c_char_p(tmp[0].encode("cp932", "replace"))
                )
                skin_name_english_list.append(
                    ctypes.c_char_p(tmp[1].encode("cp932", "replace"))
                )

            while line:
                line = fp.readline()[:-1]
                if line == "end":
                    break
                tmp = line.split(" ")
                disp_name_list.append(
                    ctypes.c_char_p(tmp[0].encode("cp932", "replace"))
                )
                disp_name_english_list.append(
                    ctypes.c_char_p(tmp[1].encode("cp932", "replace"))
                )

            return TranslationList(
                (ctypes.c_char_p * len(bone_name_list))(*bone_name_list),
                (ctypes.c_char_p * len(bone_name_english_list))(
                    *bone_name_english_list
                ),
                (ctypes.c_char_p * len(skin_name_list))(*skin_name_list),
                (ctypes.c_char_p * len(skin_name_english_list))(
                    *skin_name_english_list
                ),
                (ctypes.c_char_p * len(disp_name_list))(*disp_name_list),
                (ctypes.c_char_p * len(disp_name_english_list))(
                    *disp_name_english_list
                ),
            )

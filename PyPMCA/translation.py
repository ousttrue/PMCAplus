import dataclasses
import logging


LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class TranslationList:
    # bone
    bone_name_list: list[bytes] = dataclasses.field(default_factory=list)
    bone_name_english_list: list[bytes] = dataclasses.field(default_factory=list)
    # skin
    skin_name_list: list[bytes] = dataclasses.field(default_factory=list)
    skin_name_english_list: list[bytes] = dataclasses.field(default_factory=list)
    # group
    bone_grup_name_list: list[bytes] = dataclasses.field(default_factory=list)
    bone_grop_name_english_list: list[bytes] = dataclasses.field(default_factory=list)

    @staticmethod
    def load(path: str = "list.txt") -> "TranslationList":
        LOGGER.info(f"Translation.load: {path}")
        with open(path, "r", encoding="utf-8-sig") as fp:

            t = TranslationList()

            line = fp.readline()[:-1]
            line = fp.readline()[:-1]
            while line:
                line = fp.readline()[:-1]
                if line == "skin":
                    break
                tmp = line.split(" ")
                t.bone_name_list.append(tmp[0].encode("cp932", "replace"))
                t.bone_name_english_list.append(tmp[1].encode("cp932", "replace"))

            while line:
                line = fp.readline()[:-1]
                if line == "bone_disp":
                    break
                tmp = line.split(" ")
                t.skin_name_list.append(tmp[0].encode("cp932", "replace"))
                t.skin_name_english_list.append(tmp[1].encode("cp932", "replace"))

            while line:
                line = fp.readline()[:-1]
                if line == "end":
                    break
                tmp = line.split(" ")
                t.bone_grup_name_list.append(tmp[0].encode("cp932", "replace"))
                t.bone_grop_name_english_list.append(tmp[1].encode("cp932", "replace"))

            return t

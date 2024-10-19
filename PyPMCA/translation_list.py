import dataclasses


@dataclasses.dataclass
class TranslationList:
    # bone
    b: tuple[list[str], list[str]]
    # skin
    s: tuple[list[str], list[str]]
    # group
    g: tuple[list[str], list[str]]

    @staticmethod
    def load(path: str = "list.txt") -> "TranslationList":
        with open(path, "r", encoding="utf-8-sig") as fp:

            bone: tuple[list[str], list[str]] = ([], [])
            skin: tuple[list[str], list[str]] = ([], [])
            group: tuple[list[str], list[str]] = ([], [])

            line = fp.readline()[:-1]
            line = fp.readline()[:-1]
            while line:
                line = fp.readline()[:-1]
                if line == "skin":
                    break
                tmp = line.split(" ")
                bone[0].append(tmp[0].encode("cp932", "replace"))
                bone[1].append(tmp[1].encode("cp932", "replace"))
                print(tmp)

            while line:
                line = fp.readline()[:-1]
                if line == "bone_disp":
                    break
                tmp = line.split(" ")
                skin[0].append(tmp[0].encode("cp932", "replace"))
                skin[1].append(tmp[1].encode("cp932", "replace"))
                print(tmp)

            while line:
                line = fp.readline()[:-1]
                if line == "end":
                    break
                tmp = line.split(" ")
                group[0].append(tmp[0].encode("cp932", "replace"))
                group[1].append(tmp[1].encode("cp932", "replace"))
                print(tmp)

            return TranslationList(bone, skin, group)

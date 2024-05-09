class BONE:
    def __init__(
        self,
        name: str | bytes,
        name_eng: str | bytes,
        parent: int,
        tail: int,
        btype: int,
        IK: int,
        loc: tuple[float, float, float],
    ):
        match name:
            case str():
                self.name = name
            case bytes():
                self.name = name.decode("cp932", "replace")
        match name_eng:
            case str():
                self.name_eng = name_eng
            case bytes():
                self.name_eng = name_eng.decode("cp932", "replace")
        self.parent = parent
        self.tail = tail
        self.type = btype
        self.IK = IK
        self.loc = loc


class BONE_GROUP:
    def __init__(self, name: bytes = b"", name_eng: bytes = b""):
        self.name = name.decode("cp932", "replace")
        self.name_eng = name_eng.decode("cp932", "replace")


class BONE_DISP:
    def __init__(self, index: int, bone_group: int):
        self.index = index
        self.group = bone_group

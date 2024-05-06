class BONE:
    def __init__(
        self, name: str, name_eng: str, parent: "BONE|None", tail, btype, IK, loc
    ):
        if type(name) == type(b""):
            name = name.decode("cp932", "replace")
        if type(name_eng) == type(b""):
            name_eng = name_eng.decode("cp932", "replace")
        self.name = name
        self.name_eng = name_eng
        self.parent = parent
        self.tail = tail
        self.type = btype
        self.IK = IK
        self.loc = loc

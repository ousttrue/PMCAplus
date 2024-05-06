from typing import TypedDict


class SkinDataData(TypedDict):
    index: int
    loc: tuple[float, float, float]


class SKIN:
    def __init__(
        self, name: bytes, name_eng: bytes, count: int, t: int, data: list[SkinDataData]
    ):
        self.name = name.decode("cp932", "replace")
        self.name_eng = name_eng.decode("cp932", "replace")
        self.count = count
        self.type = t
        self.data = data

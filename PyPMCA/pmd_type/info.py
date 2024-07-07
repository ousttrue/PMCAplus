import dataclasses


@dataclasses.dataclass
class INFO:
    name: str = ""
    name_eng: str = ""
    comment: str = ""
    comment_eng: str = ""
    eng_support: int = 1
    skin_index: list[int] = dataclasses.field(default_factory=list)

from typing import TypedDict
import dataclasses


class InfoData(TypedDict):
    name: bytes
    name_eng: bytes
    comment: bytes
    comment_eng: bytes
    eng_support: int
    skin_index: list[int]
    vt_count: int
    face_count: int
    mat_count: int
    bone_count: int
    IK_count: int
    skin_count: int
    bone_group_count: int
    bone_disp_count: int
    rb_count: int
    joint_count: int


@dataclasses.dataclass
class INFO:
    name: str = ""
    name_eng: str = ""
    comment: str = ""
    comment_eng: str = ""
    eng_support: int = 1
    skin_index: list[int] = dataclasses.field(default_factory=list)

    @staticmethod
    def from_data(data: InfoData) -> "INFO":
        return INFO(
            data["name"].decode("cp932"),
            data["name_eng"].decode("cp932"),
            data["comment"].decode("cp932"),
            data["comment_eng"].decode("cp932"),
            data["eng_support"],
            data["skin_index"],
        )

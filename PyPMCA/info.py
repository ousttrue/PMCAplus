from typing import TypedDict


class InfoData(TypedDict):
    name: bytes
    name_eng: bytes
    comment: bytes
    comment_eng: bytes
    vt_count: int
    face_count: int
    mat_count: int
    bone_count: int
    IK_count: int
    skin_count: int
    bone_group_count: int
    bone_disp_count: int
    eng_support: int
    rb_count: int
    joint_count: int
    skin_index: list[int]


class INFO:
    def __init__(self, dic: InfoData):
        self.name = dic["name"].decode("cp932", "replace")
        self.name_eng = dic["name_eng"].decode("cp932", "replace")
        self.comment = dic["comment"].decode("cp932", "replace")
        self.comment_eng = dic["comment_eng"].decode("cp932", "replace")
        self.eng_support = dic["eng_support"]
        self.skin_index = dic["skin_index"]
        self.data = dic

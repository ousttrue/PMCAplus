from typing import NamedTuple


class BONE_GROUP(NamedTuple):
    name: str
    name_eng: str


class BONE_DISP(NamedTuple):
    bone_index: int
    bone_group_index: int

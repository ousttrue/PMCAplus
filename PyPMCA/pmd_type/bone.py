from typing import NamedTuple
import dataclasses


class BONE_GROUP(NamedTuple):
    name: str
    name_eng: str


@dataclasses.dataclass
class BONE_DISP:
    bone_index: int
    bone_group_index: int

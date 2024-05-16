from typing import NamedTuple
import dataclasses
from .types import Float3


@dataclasses.dataclass
class BONE:
    name: str
    name_eng: str
    parent_index: int
    tail_index: int
    bone_type: int
    ik: int
    loc: Float3


class BONE_GROUP(NamedTuple):
    name: str
    name_eng: str


class BONE_DISP(NamedTuple):
    bone_index: int
    bone_group: int

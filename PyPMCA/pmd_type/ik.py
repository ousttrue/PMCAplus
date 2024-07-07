import dataclasses
import ctypes


@dataclasses.dataclass
class IK_LIST:
    bone_index: int
    target_bone_index: int
    iterations: int
    weight: float
    chain: ctypes.Array[ctypes.c_uint16]

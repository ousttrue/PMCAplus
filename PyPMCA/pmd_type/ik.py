import dataclasses
import ctypes


@dataclasses.dataclass
class IK_LIST:
    index: int
    target_index: int
    iterations: int
    weight: float
    chain: ctypes.Array[ctypes.c_uint16]

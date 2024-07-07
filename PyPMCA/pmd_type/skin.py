import dataclasses
import ctypes
from .types import MoprhVertex


@dataclasses.dataclass
class SKIN:
    name: str
    name_eng: str
    type: int
    data: ctypes.Array[MoprhVertex]

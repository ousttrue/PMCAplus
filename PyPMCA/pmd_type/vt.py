import dataclasses


@dataclasses.dataclass
class VT:
    loc = (0, 0, 0)
    nor = (0, 0, 0)
    uv = (0, 0)
    bone_num0 = 0
    bone_num1 = 0
    weight = 1
    edge = 0

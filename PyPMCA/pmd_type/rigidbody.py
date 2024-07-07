class RB:
    def __init__(
        self,
        name: bytes = b"",
        bone: int = 0,
        group: int = 0,
        target: int = 0,
        shape: int = 0,
        size: tuple[float, float, float] = (1.0, 1.0, 1.0),
        loc: tuple[float, float, float] = (0.0, 0.0, 0.0),
        rot: tuple[float, float, float] = (0.0, 0.0, 0.0),
        prop: tuple[float, float, float, float, float] = (0.0, 0.0, 0.0, 0.0, 0.0),
        t: int = 0,
    ):
        self.name = name.decode("cp932", "replace")
        self.bone = bone
        self.group = group
        self.target = target
        self.shape = shape
        self.size = size
        self.loc = loc
        self.rot = rot
        self.mass = prop[0]
        self.damp = prop[1]
        self.rdamp = prop[2]
        self.res = prop[3]
        self.fric = prop[4]
        self.type = t


class JOINT:
    def __init__(
        self,
        name: bytes = b"",
        rbody: tuple[int, int] = (0, 0),
        loc: tuple[float, float, float] = (0.0, 0.0, 0.0),
        rot: tuple[float, float, float] = (0.0, 0.0, 0.0),
        limit: tuple[
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
        ] = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        spring: tuple[float, float, float, float, float, float] = (
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
        ),
    ):
        self.name = name.decode("cp932", "replace")
        self.rb = rbody
        self.loc = loc
        self.rot = rot
        self.limit = limit
        self.spring = spring

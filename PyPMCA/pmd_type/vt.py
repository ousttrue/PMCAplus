class VT:
    def __init__(
        self,
        loc=[0, 0, 0],
        nor=[0, 0, 0],
        uv=[0, 0],
        bone_num1=0,
        bone_num2=0,
        weight=1,
        edge=0,
    ):
        self.loc = loc
        self.nor = nor
        self.uv = uv
        self.bone_num = [bone_num1, bone_num2]
        self.weight = weight
        self.edge = edge

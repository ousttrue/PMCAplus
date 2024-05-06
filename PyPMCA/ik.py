class IK_LIST:
    def __init__(
        self,
        index: int,
        t_index: int,
        length: int,
        ite: int,
        weight: float,
        c_index: int,
    ):
        self.index = index
        self.tail_index = t_index
        self.chain_len = length
        self.iterations = ite
        self.weight = weight
        self.child = c_index

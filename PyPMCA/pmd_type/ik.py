import dataclasses


@dataclasses.dataclass
class IK_LIST:
    index: int
    target_index: int
    iterations: int
    weight: float
    chain: list[int]

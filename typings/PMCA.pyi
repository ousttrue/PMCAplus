from typing import List

def setVt(
    num: int,
    i: int,
    loc: tuple[float, float, float],
    normal: tuple[float, float, float],
    uv: tuple[float, float],
    bone0: int,
    bone1: int,
    weight: int,
    edge: int,
) -> None:
    """
    Set Vertex of PMD"
    """
    ...

def setFace(num: int, i: int, face: tuple[int, int, int]) -> None:
    """
    Set Face of PMD"
    """
    ...

def setMat(
    num: int,
    i: int,
    diffuse: tuple[float, float, float],
    alpha: float,
    specular: float,
    specular_color: tuple[float, float, float],
    mirror_color: tuple[float, float, float],
    toon: int,
    edge: int,
    vertex_count: int,
    tex: bytes,
) -> None:
    """
    Set Material of PMD"
    """
    ...

def setBone(
    num: int,
    i: int,
    name: bytes,
    name_en: bytes,
    parent: int,
    tail: int,
    type: int,
    IK: int,
    loc: tuple[float, float, float],
) -> None:
    """
    Set Bone of PMD"
    """
    ...

def setIK(
    num: int,
    i: int,
    bone: int,
    target: int,
    chain_len: int,
    iteration: int,
    weight: float,
    chain: list[int],
) -> None:
    """
    Set IK_List of PMD"
    """
    ...

def setSkin(
    num: int, i: int, name: bytes, name_eng: bytes, length: int, skin_type: int
) -> None:
    """
    Set Skin of PMD"
    """
    ...

def setSkindata(
    num: int, i: int, j: int, index: int, vec3: tuple[float, float, float]
) -> None:
    """
    Set Skin_data of PMD"
    """
    ...

def setBone_group(num: int, i: int, name: bytes, name_eng: bytes) -> None:
    """
    Set Bone_group of PMD"
    """
    ...

def setBone_disp(num: int, i: int, x: int, y: int) -> None:
    """
    Set Bone_disp of PMD"
    """
    ...

def setToon(
    num: int,
    toon_list: tuple[
        bytes,
        bytes,
        bytes,
        bytes,
        bytes,
        bytes,
        bytes,
        bytes,
        bytes,
        bytes,
    ],
) -> None:
    """
    Set Toon textures of PMD"
    """
    ...

def setToonPath(
    num: int,
    toon_path_list: tuple[
        bytes,
        bytes,
        bytes,
        bytes,
        bytes,
        bytes,
        bytes,
        bytes,
        bytes,
        bytes,
    ],
) -> None:
    """
    Set Toon textures path of PMD"
    """
    ...

def setRb(
    num: int,
    i: int,
    name: bytes,
    bone: int,
    group: int,
    target: int,
    shape: int,
    size: tuple[float, float, float],
    loc: tuple[float, float, float],
    rot: tuple[float, float, float],
    mass: float,
    damp: float,
    rdamp: float,
    res: float,
    fric: float,
    type: int,
) -> None:
    """
    Set Rigid bodies of PMD"
    """
    ...

def setJoint(
    num: int,
    i: int,
    name: bytes,
    rb: tuple[int, int],
    loc: tuple[float, float, float],
    rot: tuple[float, float, float],
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
    ],
    spring: tuple[
        float,
        float,
        float,
        float,
        float,
        float,
    ],
) -> None:
    """
    Set Joints of PMD"
    """
    ...

def Set_List(
    bn: int,
    b0: List[bytes],
    b1: List[bytes],
    sn: int,
    s0: List[bytes],
    s1: List[bytes],
    gn: int,
    g0: List[bytes],
    g1: List[bytes],
) -> None:
    """
    Set List of bone or things"
    """
    ...

def Set_Name_Comment(
    num: int,
    name: bytes,
    comment: bytes,
    name_eng: bytes,
    comment_eng: bytes,
) -> None:
    """
    Set Name and Comment
    """
    ...

def Init_PMD() -> None:
    """
    Initialize"
    """
    ...

def Set_PMD(num: int, data: bytes) -> bytes:
    """
    Load PMD from file"
    """
    ...

def Add_PMD(a: bytes, b: bytes) -> bytes:
    """
    Add PMD from file"
    """
    ...

def Copy_PMD(src: int, dst: int) -> None:
    """
    Copy PMD"
    """
    ...

def Marge_PMD(data: bytes) -> bytes:
    """
    Marge PMD"
    """
    ...

def Sort_PMD(num: int) -> None:
    """
    Sort PMD"
    """
    ...

def PMD_view_set(num: int, mode: str) -> None:
    """
    Set selected PMD to dispray"
    """
    ...

def Get_PMD(num: int) -> bytes:
    """
    Get vertices, indices and vertex_count list
    """
    ...

def Resize_Model(num: int, scale: float) -> None:
    """
    Resize_Model"
    """
    ...

def Move_Model(num: int, x: float, y: float, z: float) -> None:
    """
    Move_Model"
    """
    ...

def Resize_Bone(num: int, name: bytes, length: float, thickness: float) -> None:
    """
    Resize_Bone"
    """
    ...

def Move_Bone(num: int, name: bytes, x: float, y: float, z: float) -> None:
    """
    Move_Bone"
    """
    ...

def Update_Skin(num: int) -> None:
    """
    Update_Skin"
    """
    ...

def Adjust_Joints(num: int) -> None:
    """
    Adjust_Joints"
    """
    ...

def getWHT(num: int) -> tuple[float, float, float]:
    """
    get height, width, thickness from model"
    """
    ...
